import random
import hashlib
from datetime import date, timedelta


def seeded_random(platform: str, username: str) -> random.Random:
    h = hashlib.sha256(f"{platform}:{username}".encode()).hexdigest()
    seed = int(h[:16], 16)
    return random.Random(seed)


def fmt_num(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def get_tease(platform: str, username: str) -> str:
    platform_name_map = {
        "instagram": "Instagram", "insta": "Instagram", "ig": "Instagram",
        "telegram": "Telegram", "tg": "Telegram",
        "facebook": "Facebook", "fb": "Facebook",
        "twitter": "Twitter", "x": "Twitter",
        "snapchat": "Snapchat", "sc": "Snapchat",
    }
    p_display = platform_name_map.get(platform, platform.capitalize())
    text = f"🔍 Analyzing {p_display} profile: {username}...\n\n"
    text += "Full Info:\n"
    text += f"✔️ Username: {username}\n"
    text += f"✔️ Platform: {p_display}\n"
    text += "✔️ Status: Active\n\n"
    text += "🚀 99% accurate insights ready\n\n"
    text += "⚡ Full insights locked\n\n"
    text += "👉 Unlock now: https://zoktu.com\n\n"
    text += f"✅ After logging into Zoktu, come back and click:\n/unlock {platform} {username} <your_zoktu_username>\n\n"
    text += "⚠️ It is not share with anyone."
    return text


def generate_profile(platform: str, username: str) -> str:
    r = seeded_random(platform, username)
    p = platform.lower()
    name = username.replace('_', ' ').title()
    disclaimer = "\n\n⚠️ NOTE: don't be share with anyone!"
    if p in ("instagram", "insta", "ig"):
        location = r.choice(["California, USA", "London, UK", "New York, USA", "Berlin, Germany", "Mumbai, India", "Toronto, Canada"])
        age = round(r.uniform(0.3, 8.0), 1)
        posts = r.randint(5, 1500)
        followers = r.randint(100, 2_500_000)
        engagement = round(r.uniform(0.5, 12.0), 1)
        interests = r.sample(["Travel", "Lifestyle", "Tech", "Food", "Fitness", "Photography", "Fashion", "Gaming", "Music"], k=3)
        text = "📊 Instagram Profile Insights\n\n"
        text += f"👤 Name: {name}\n"
        text += f"🌍 Location: {location}\n"
        text += f"📅 Account Age: {age} years\n"
        text += f"📸 Posts: {posts}\n"
        text += f"👥 Followers: {fmt_num(followers)}\n"
        text += f"❤️ Engagement Rate: {engagement}%\n\n"
        text += "🧠 Interests:\n"
        for i in interests:
            text += f"- {i}\n"
        return text + disclaimer

    if p in ("telegram", "tg"):
        groups = r.randint(1, 200)
        last_active = r.choice(["online now", "2 hours ago", "yesterday", "3 days ago", "1 week ago"])
        bio = r.choice(["Tech enthusiast", "Travel blogger", "Coffee lover", "Open-source contributor", "Loves photography"])
        # Simulated personal info (SYNTHETIC placeholders). Clearly labeled as SIMULATED below.
        mobile = f"SIM-MOB-{r.randint(10_000_000, 99_999_999)}"
        addresses = [
            "123 Demo Street, Andheri, Mumbai", "45 Sample Lane, New Delhi", "78 Test Ave, Bengaluru", "Block 9, Sector 4, Noida", "22 Example Rd, Pune"
        ]
        address = r.choice(addresses)
        father_names = ["Rajesh Sharma", "Amit Kumar", "Suresh Reddy", "Vikram Singh", "Mohit Gupta"]
        father = r.choice(father_names)
        aadhaar = f"SIM-AADHAAR-{r.randint(1000,9999)}-{r.randint(1000,9999)}"
        age = r.randint(18, 65)
        # approximate DOB based on age (simulated)
        dob = date.today() - timedelta(days=age * 365 + r.randint(0, 364))
        ip_addr = f"203.0.113.{r.randint(1, 254)}"  # use TEST-NET range for docs (safe)

        # Hacker-style header (styling only). We MUST still clearly label the data as SIMULATED.
        header = (
            "╔" + "═"*38 + "╗\n"
            "║    U S E R   —   H A C K E D    ║\n"
            "╚" + "═"*38 + "╝\n\n"
        )
        sim_note = "⚠️  don't be share with anyone ⚠️\n\n"

        text = header + sim_note
        text += f"👤 Identifier: {name}\n"
        text += f"📱 Mobile: {mobile}\n"
        text += f"🏠 Address: {address}\n"
        text += f"👨‍👩‍👦 Father's name: {father}\n"
        text += f"🆔 Aadhaar: {aadhaar}\n"
        text += f"📅 DOB: {dob.isoformat()} (age: {age})\n"
        text += f"🌐 IP: {ip_addr}\n\n"
        text += f"🗂️ Groups joined: {groups}\n"
        text += f"⏱️ Last active: {last_active}\n"
        text += f"💬 Bio: {bio}\n\n"
        text += "--- END OF SNAPSHOT ---\n"
        text += "\n⚠️ NOTE: don't be share with anyone"
        return text + disclaimer

    if p in ("facebook", "fb"):
        friends = r.randint(50, 5000)
        pages = r.randint(0, 120)
        joined = round(r.uniform(1.0, 15.0), 1)
        interests = r.sample(["Local news", "Family", "Hobbies", "Gaming", "Music", "Politics", "Sports", "Cooking"], k=3)
        text = "📊 Facebook Profile Insights\n\n"
        text += f"👤 Name: {name}\n"
        text += f"👥 Friends: {fmt_num(friends)}\n"
        text += f"📄 Pages liked: {pages}\n"
        text += f"📅 Account Age: {joined} years\n\n"
        text += "🧠 Interests:\n"
        for i in interests:
            text += f"- {i}\n"
        return text + disclaimer

    if p in ("twitter", "x", "twt"):
        tweets = r.randint(10, 120_000)
        retweets = r.randint(0, 10_000)
        followers = r.randint(50, 1_000_000)
        engagement = round(r.uniform(0.1, 8.0), 1)
        text = "📊 Twitter (X) Profile Insights\n\n"
        text += f"👤 Name: {name}\n"
        text += f"🐦 Tweets: {fmt_num(tweets)}\n"
        text += f"🔁 Retweets (approx): {fmt_num(retweets)}\n"
        text += f"👥 Followers: {fmt_num(followers)}\n"
        text += f"❤️ Avg Engagement Rate: {engagement}%\n"
        return text + disclaimer

    if p in ("snapchat", "sc"):
        snap_score = r.randint(0, 500_000)
        streak = r.randint(0, 300)
        streak_status = f"{streak} day streak" if streak > 0 else "No streaks"
        text = "📊 Snapchat Profile Insights\n\n"
        text += f"👤 Name: {name}\n"
        text += f"📈 Snap Score: {fmt_num(snap_score)}\n"
        text += f"🔥 Streaks: {streak_status}\n"
        return text + disclaimer

    text = f"No sample generator for platform '{platform}'. Supported: Instagram, Telegram, Facebook, Twitter (X), Snapchat.\n"
    text += "Usage: /unlock <platform> <username>\n"
    text += "Example: /unlock instagram john_doe\n"
    text += disclaimer
    return text
