import os
from zoneinfo import ZoneInfo

# ==========================================
# SF ARMY 10K GIVEAWAY BOT
# ==========================================

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

ADMIN_IDS = [
    123456789,  # Replace with your Telegram Admin ID
]

# ==========================================
# REQUIRED CHANNELS & GROUPS
# ==========================================

CHANNELS = [
    {
        "name": "🦅 SF ARMY 💓🤍",
        "chat_id": "-1002334256951",
        "url": "https://t.me/+qboCxP7VbFQ5YzM1",
    },
    {
        "name": "Secret World 🙈",
        "chat_id": "-1004346974389",
        "url": "https://t.me/+bwvTgAiI3hw4MWUx",
    },
    {
        "name": "🤍💓ANUSHAR 🌷",
        "chat_id": "-1003746793908",
        "url": "https://t.me/+kkjsBE3OfypmNTc1",
    },
    {
        "name": "ANUSHAR ARMY 🪖",
        "chat_id": "-1003689156772",
        "url": "https://t.me/+6qmbICUUy0dmMTY1",
    },
    {
        "name": "EXPOSE MAFIA 😎",
        "chat_id": "-1003040006163",
        "url": "https://t.me/+aOrE_A-_KadkZjhl",
    },
    {
        "name": "SF TOOL GC 🧑🏻‍🔧",
        "chat_id": "-1002708620916",
        "url": "https://t.me/+PwAfcam-4ycxZGU1",
    },
]

# ==========================================
# COIN SYSTEM
# ==========================================

WELCOME_BONUS = 5
REFERRAL_REWARD = 10
DAILY_BONUS = 5

# ==========================================
# GIVEAWAY QUALIFICATION
# ==========================================

QUALIFICATION_REFERRALS = 6

LEADERBOARD_LIMIT = 50
LEADERBOARD_PAGE_SIZE = 25

# ==========================================
# TIMEZONE
# ==========================================

TIMEZONE = ZoneInfo("Asia/Kolkata")

# ==========================================
# DATABASE & BACKUP
# ==========================================

DATA_DIR = "data"
BACKUP_DIR = "backups"

DATABASE_FILE = os.path.join(DATA_DIR, "giveaway.db")

BACKUP_HOUR = 0
BACKUP_MINUTE = 0

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# ==========================================
# GIVEAWAY END TIME
# Set later after confirmation.
# ==========================================

GIVEAWAY_END_AT = None

# ==========================================
# REWARD SYSTEM
# ==========================================

REWARD_SYSTEM_ENABLED = False
REWARD_COMING_SOON_TEXT = "🎁 Reward System Coming Soon!"
