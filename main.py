#!/usr/bin/env python3
import logging
import sys
from typing import Optional

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

from config import TELEGRAM_BOT_TOKEN, ALLOWED_CHAT_IDS, POLLING_TIMEOUT, READ_TIMEOUT, LOG_LEVEL, PROCESSED_MESSAGES
from ocr_processor import MSISDNExtractor


# إعداد السجل (Logging)
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)


class TelegramMSISDNBot:
    """بوت Telegram لاستخراج أرقام MSISDN من الصور والرد برسائل مباشرة."""

    def __init__(self):
        self.extractor = MSISDNExtractor()
        self.processed_messages = PROCESSED_MESSAGES

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        معالج الصور الجديدة.

        تحقق من:
        1. أن الصورة من الجروب المسموح به
        2. أن الرسالة لم تتم معالجتها من قبل
        3. استخراج MSISDN من الصورة
        4. الرد برسالة مباشرة على الصورة الأصلية
        """
        if not update.message or not update.message.photo:
            return

        chat_id = update.message.chat_id
        message_id = update.message.message_id
        user_id = update.message.from_user.id if update.message.from_user else None

        # التحقق من أن الجروب مسموح به
        if ALLOWED_CHAT_IDS and chat_id not in ALLOWED_CHAT_IDS:
            logger.debug(f"Message from unauthorized chat {chat_id}, ignoring")
            return

        # التحقق من عدم معالجة الرسالة مسبقاً (منع النسخ المكررة)
        message_key = (chat_id, message_id)
        if message_key in self.processed_messages:
            logger.debug(f"Message {message_id} in chat {chat_id} already processed, skipping")
            return

        # إضافة الرسالة إلى قائمة الرسائل المعالجة
        self.processed_messages.add(message_key)

        logger.info(f"Processing photo in chat {chat_id}, message {message_id}, user {user_id}")

        try:
            # الحصول على أفضل نسخة من الصورة (الدقة العالية)
            photo_file = await update.message.photo[-1].get_file()

            # تحميل الصورة من Telegram
            image_bytes = await photo_file.download_as_bytearray()

            # استخراج MSISDN من الصورة
            msisdn = self.extractor.extract_msisdn_from_image(bytes(image_bytes))

            # التحقق من صحة MSISDN
            if msisdn and self.extractor.validate_msisdn(msisdn):
                logger.info(f"Valid MSISDN extracted: {msisdn} (masked for logging)")

                # الرد برسالة مباشرة على الصورة الأصلية
                await self._send_reply(update, context, msisdn)
            else:
                logger.debug(f"No valid MSISDN found or validation failed for message {message_id}")

        except TelegramError as e:
            logger.error(f"Telegram API error: {e}", exc_info=False)
            # إزالة الرسالة من القائمة المعالجة في حالة الخطأ لإعادة المحاولة
            self.processed_messages.discard(message_key)
        except Exception as e:
            logger.error(f"Unexpected error processing message {message_id}: {e}", exc_info=True)
            # إزالة الرسالة من القائمة المعالجة في حالة الخطأ لإعادة المحاولة
            self.processed_messages.discard(message_key)

    async def _send_reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE, msisdn: str) -> None:
        """
        إرسال رسالة رد مباشرة على الصورة الأصلية.

        Args:
            update: كائن Update من Telegram
            context: كائن Context
            msisdn: رقم MSISDN المستخرج
        """
        try:
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text=msisdn,  # الرقم فقط، بدون نص إضافي
                reply_to_message_id=update.message.message_id,  # الرد على الصورة الأصلية
            )
            logger.info(f"Reply sent successfully to message {update.message.message_id}")
        except TelegramError as e:
            logger.error(f"Failed to send reply: {e}", exc_info=False)
            raise

    def run(self):
        """تشغيل البوت."""
        logger.info("Starting MSISDN Extraction Bot...")

        # إنشاء التطبيق
        app = Application.builder().token(TELEGRAM_BOT_TOKEN).read_timeout(READ_TIMEOUT).get_updates_read_timeout(POLLING_TIMEOUT).build()

        # إضافة معالج الصور
        app.add_handler(MessageHandler(filters.PHOTO & ~filters.FORWARDED, self.handle_photo))

        # بدء التطبيق
        app.run_polling(allowed_updates=["message"])


def main():
    """الدالة الرئيسية."""
    try:
        bot = TelegramMSISDNBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
