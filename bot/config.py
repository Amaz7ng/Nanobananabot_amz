import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")

    DB_URL: str = os.getenv("DB_URL")

    NANO_BANANA_API_KEY: str = os.getenv("NANO_BANANA_API_KEY")
    NANO_BANANA_URL: str = os.getenv("NANO_BANANA_URL")
    KIE_STATUS_URL: str = os.getenv("KIE_STATUS_URL")

    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ROOT_USER: str = os.getenv("MINIO_ROOT_USER", "minioadmin")
    MINIO_ROOT_PASSWORD: str = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin_password")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "photos")
    MINIO_PUBLIC_DOMAIN: str = os.getenv("MINIO_PUBLIC_DOMAIN", "localhost:9000")

config = Config()

if not config.BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")
if not config.DB_URL:
    raise ValueError("DB_URL не найден в .env")
if not config.NANO_BANANA_API_KEY:
    raise ValueError("NANO_BANANA_API_KEY не найден в .env")

print("ТЕКУЩИЙ URL ДЛЯ API:", config.NANO_BANANA_URL)