import os
from pathlib import Path

# Sanitized settings for public repository copy.
# Do not include private credentials or require a local .env file.
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

try:
    from dotenv import load_dotenv
    if ENV_PATH.exists():
        load_dotenv(dotenv_path=ENV_PATH)
except Exception:
    pass

# Provide safe defaults so the repo can be public without secrets.
SE_EMAIL = os.getenv("SE_EMAIL", "you@example.com")
SE_PASSWORD = os.getenv("SE_PASSWORD", "changeme")
try:
    ROOM_ID = int(os.getenv("CHAT_ROOM_ID", "25999"))
except ValueError:
    ROOM_ID = 25999
SITE_NAME = os.getenv("SITE_NAME", "stackoverflow")
CHAT_HOST_MAP = {
    "stackoverflow": "stackoverflow.com",
    "meta.stackexchange": "meta.stackexchange.com",
    "stackexchange": "stackexchange.com",
    "stackoverflow.com": "stackoverflow.com",
    "meta.stackexchange.com": "meta.stackexchange.com",
    "stackexchange.com": "stackexchange.com",
}
CHAT_HOST = CHAT_HOST_MAP.get(SITE_NAME, "stackexchange.com")

SE_API_KEY = os.getenv("SE_API_KEY")
try:
    from stackapi import StackAPI
    if SE_API_KEY:
        SITE = StackAPI(SITE_NAME, key=SE_API_KEY)
    else:
        SITE = StackAPI(SITE_NAME)
except Exception:
    # In the public copy we avoid importing external services at import-time.
    SITE = None

AI_THRESHOLD = int(os.getenv("AI_THRESHOLD", "35"))
# Remove personal admin IDs from the public copy.
ADMIN_IDS = set()
