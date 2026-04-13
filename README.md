# Zoktu User Info Bot (commands-only)

This is a lightweight Telegram bot that returns simulated sample profile summaries for a given username on supported platforms. It's for entertainment purposes only and does not access any real user data.

Supported platforms:
- Instagram
- Telegram
- Facebook
- Twitter (X)
- Snapchat

Key commands (commands-only, no buttons):
- /start — Welcome and examples
- /about — About & disclaimer
- /analyze <platform> <username> — Short teaser with unlock prompt
- /unlock <platform> <username> — Show full simulated profile (what you'd see after "unlock")

Example:

```bash
/analyze instagram john_doe
# After visiting https://zoktu.com and "unlocking":
/unlock instagram john_doe
```

Setup
1. Create a virtualenv and install requirements:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Add your Telegram bot token to `.env` or environment variable `TELEGRAM_BOT_TOKEN`.

3. Run the bot:

```bash
python bot.py
```

Important
- Always show the disclaimer: This profile is simulated for demonstration purposes only. No real personal data is accessed.
- This project intentionally generates simulated/sample data only — do not use it to target or deanonymize real people.

Note about added fields
- The Telegram profile output now includes extra simulated personal-info fields (mobile, address, father's name, Aadhaar, DOB, age, IP). These values are clearly marked as SIMULATED placeholders and must never be used to identify or contact real people.

Want changes?
- I can add persistence (unlock tokens), webhooks, or multi-platform connectors (Instagram API wrappers) — tell me which next. ❤️

## UI-only demo (client)

There's a small client-only demo included: `index.html`.

- Open `index.html` in your browser (no server needed). The demo shows only the "Unlock on Zoktu" button at first.
- When you click that button it opens the configured website (change the `TARGET_URL` variable inside `index.html`) and automatically reveals the second button: "I've unlocked — Show full profile".
- The demo persists the unlocked state in `localStorage` so the second button stays visible on reload. Use the Reset button to clear the state while testing.

This is a pure front-end flow (no server) to match the requested behaviour.

## Deploying to Render (recommended config)

If you want to run the project on Render (https://render.com), use these settings.

- Build command:

```bash
pip install -r requirements.txt
```

- Start command (Web Service for `server.py` — use gunicorn):

```bash
gunicorn server:app --bind 0.0.0.0:$PORT
```

- Start command (Background Worker for `bot.py` — separate service):

```bash
python bot.py
```

Notes:
- Add two services on Render if you want both the HTTP verification UI (`server.py`) and the Telegram bot to run: a Web Service (gunicorn) and a Background Worker (bot.py).
- Required environment variables on Render:
	- `TELEGRAM_BOT_TOKEN` — your bot token
	- `ADMIN_TELEGRAM_ID` — optional admin chat id
	- `ZOKTU_BASE_URL` — optional base URL if you host the auth flow
- Ensure `requirements.txt` contains `Flask` and `gunicorn` (already included).

