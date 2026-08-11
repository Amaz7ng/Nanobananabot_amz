import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

DB_URL = os.getenv("DB_URL")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")
if not DB_URL:
    raise ValueError("DB_URL не найден в файле .env!")