import os
from typing import Set
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ALLOWED_CHAT_IDS = set(
    int(chat_id.strip())
    for chat_id in os.getenv("ALLOWED_CHAT_IDS", "").split(",")
    if chat_id.strip()
)

# Application Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
POLLING_TIMEOUT = int(os.getenv("POLLING_TIMEOUT", "30"))
READ_TIMEOUT = int(os.getenv("READ_TIMEOUT", "60"))

# OCR Configuration
OCR_CONFIDENCE_THRESHOLD = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.3"))

# Validation
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

# In-memory cache for processed messages (to prevent duplicate replies)
PROCESSED_MESSAGES: Set[tuple] = set()
