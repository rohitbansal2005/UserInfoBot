import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from fake_data import get_tease, generate_profile


load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ZOKTU_BASE_URL = os.getenv("ZOKTU_BASE_URL", "https://zoktu.com")

if not TOKEN:
    print("Error: TELEGRAM_BOT_TOKEN not set. Add it to .env or environment and restart.")
    exit(1)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
# keep references to background tasks so they are not garbage-collected
background_tasks = set()


# Simple button-based flow without a heavy conversation handler:
# 1) /start -> platform buttons
# 2) User taps platform -> bot asks for username
# 3) User sends username -> bot returns tease + Unlock buttons (link + "I've unlocked")
# 4) "I've unlocked" button shows full simulated profile (directly; no server verification)


PLATFORMS_KEYBOARD = [
    [
        InlineKeyboardButton("📱 Telegram", callback_data="platform:telegram"),
        InlineKeyboardButton("📸 Instagram", callback_data="platform:instagram"),
    ],
    [
        InlineKeyboardButton("📘 Facebook", callback_data="platform:facebook"),
        InlineKeyboardButton("🐦 Twitter (X)", callback_data="platform:twitter"),
    ],
    [InlineKeyboardButton("👻 Snapchat", callback_data="platform:snapchat")],
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "😈 Welcome to User Info Bot\n\n"
        "Select a platform below to find user info:"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(PLATFORMS_KEYBOARD))
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(PLATFORMS_KEYBOARD))


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Zoktu User Info Bot — commands + buttons interface\n\n"
        "This bot generates simulated profile summaries for entertainment and growth-hack use. "
        "No real personal data is accessed or fetched.\n\n"
        "You can use the buttons (recommended) or the commands:\n"
        "/analyze <platform> <username>\n"
        "/unlock <platform> <username>\n\n"
        "⚠️ This profile is simulated for demonstration purposes only. No real personal data is accessed."
    )
    await update.message.reply_text(text)


async def platform_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    if not data.startswith("platform:"):
        return
    _, platform = data.split(":", 1)
    context.user_data["awaiting_username"] = platform
    await query.edit_message_text(f"👉 {platform.capitalize()} selected. Now send the username (e.g., john_doe).")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # If we asked for username, treat next text as the username
    platform = context.user_data.pop("awaiting_username", None)
    if not platform:
        await update.message.reply_text("Use /start and pick a platform (or /analyze <platform> <username>).")
        return
    username = update.message.text.strip().split()[0]
    tease = get_tease(platform, username)

    # Simpler flow: no server-side verification. Provide link + a direct "I've unlocked" button
    unlock_url = f"{ZOKTU_BASE_URL}/auth?platform={platform}&username={username}"

    # Avoid putting local URLs into inline button url (Telegram may reject them)
    is_local = (
        unlock_url.startswith("http://localhost")
        or unlock_url.startswith("http://127.")
        or unlock_url.startswith("http://192.168.")
        or unlock_url.startswith("http://10.")
        or unlock_url.startswith("http://172.")
        or unlock_url.startswith("http://[::1]")
    )

    # For local dev URLs, send the link as plain text (Telegram often rejects local URLs as button URLs).
    if is_local:
        message_text = tease + "\n\nOpen this link in your browser to unlock:\n" + unlock_url
        sent_msg = await update.message.reply_text(message_text)

        async def reveal_local_unlocked(chat_id, message_id, platform, username, bot, delay=60):
            await asyncio.sleep(delay)
            try:
                new_keyboard = [[InlineKeyboardButton("✅ I've unlocked — Show full profile", callback_data=f"unlock_direct:{platform}:{username}")]]
                await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=InlineKeyboardMarkup(new_keyboard))
            except Exception as e:
                logger.info("Could not add delayed unlocked button (local) (chat_id=%s, message_id=%s): %s", chat_id, message_id, e)

        try:
            task = asyncio.create_task(reveal_local_unlocked(sent_msg.chat_id, sent_msg.message_id, platform, username, context.bot, 60))
            background_tasks.add(task)
            task.add_done_callback(lambda t: background_tasks.discard(t))
        except Exception as e:
            logger.info("Failed to schedule delayed reveal task (local): %s", e)

        return

    # Production flow: send unlock URL button now, add the "I've unlocked" callback button after a delay.
    keyboard = [[InlineKeyboardButton("🔓 Unlock on Zoktu", url=unlock_url)]]
    message_text = tease
    sent_msg = await update.message.reply_text(message_text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def reveal_unlocked(chat_id, message_id, platform, username, url, bot, delay=60):
        await asyncio.sleep(delay)
        try:
            new_keyboard = [
                [InlineKeyboardButton("🔓 Unlock on Zoktu", url=url)],
                [InlineKeyboardButton("✅ I've unlocked — Show full profile", callback_data=f"unlock_direct:{platform}:{username}")],
            ]
            await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=InlineKeyboardMarkup(new_keyboard))
        except Exception as e:
            logger.info("Could not add delayed unlocked button (chat_id=%s, message_id=%s): %s", chat_id, message_id, e)

    try:
        task = asyncio.create_task(reveal_unlocked(sent_msg.chat_id, sent_msg.message_id, platform, username, unlock_url, context.bot, 60))
        background_tasks.add(task)
        task.add_done_callback(lambda t: background_tasks.discard(t))
    except Exception as e:
        logger.info("Failed to schedule delayed reveal task: %s", e)


async def unlock_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    # Direct unlock flow (no external verification server)
    if data.startswith("unlock_direct:"):
        parts = data.split(":", 2)
        if len(parts) != 3:
            await query.edit_message_text("Invalid unlock data.")
            return
        _, platform, username = parts
        profile = generate_profile(platform, username)
        keyboard = [[InlineKeyboardButton("🔁 Analyze another", callback_data="analyze_again")]]
        await query.edit_message_text(profile, reply_markup=InlineKeyboardMarkup(keyboard))


async def analyze_again_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Select a platform to analyze:", reply_markup=InlineKeyboardMarkup(PLATFORMS_KEYBOARD))


async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /analyze <platform> <username>\nExample: /analyze instagram john_doe")
        return
    platform = args[0].lower()
    username = args[1]
    tease = get_tease(platform, username)
    await update.message.reply_text(tease)


async def unlock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /unlock <platform> <username>\nExample: /unlock instagram john_doe")
        return
    platform = args[0].lower()
    username = args[1]
    profile = generate_profile(platform, username)
    await update.message.reply_text(profile)


def main() -> None:
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("analyze", analyze))
    app.add_handler(CommandHandler("unlock", unlock_cmd))

    # Callbacks and message flow
    app.add_handler(CallbackQueryHandler(platform_callback, pattern=r"^platform:"))
    app.add_handler(CallbackQueryHandler(unlock_callback, pattern=r"^unlock_direct:"))
    app.add_handler(CallbackQueryHandler(analyze_again_callback, pattern=r"^analyze_again$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    logger.info("Starting Zoktu bot with button UI...")
    app.run_polling()


if __name__ == "__main__":
    main()
