import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

DB_URL = os.getenv("DB_URL")

KIE_STATUS_URL = os.getenv("KIE_STATUS_URL")
NANO_BANANA_URL = os.getenv("NANO_BANANA_URL")
NANO_BANANA_API_KEY = os.getenv("NANO_BANANA_API_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")
if not DB_URL:
    raise ValueError("DB_URL не найден в файле .env")
if not NANO_BANANA_API_KEY:
    raise ValueError("NANO_BANANA_API_KEY не найден в .env")
if not NANO_BANANA_URL:
    raise ValueError("NANO_BANANA_URL не найден в .env")
if not KIE_STATUS_URL:
    raise ValueError("KIE_STATUS_URL не найден в .env")