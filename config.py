import os

from dotenv import load_dotenv

# Loads .env for local development. On Railway the variables come from the
# service's Variables tab, so this call simply does nothing there.
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_PATH = os.getenv("DATABASE_PATH", "fluentquiz.db")
DAILY_HOUR_UTC = int(os.getenv("DAILY_HOUR_UTC", "8"))

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN is not set. Add it to your .env file (local) "
        "or to the Railway Variables tab (production)."
    )
