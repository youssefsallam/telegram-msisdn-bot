#!/usr/bin/env python3
import html
import logging
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CopyTextButton,
    ForceReply,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
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

# التوقيت المحلي (القاهرة) لعرض تواريخ الإيداعات
CAIRO_TZ = ZoneInfo("Africa/Cairo")

# بادئة بيانات زر الإيداع
DEPOSIT_PREFIX = "dep:"


def _build_text(number: str, deposits: list[str]) -> str:
    """بناء نص رسالة الرد: الرقم عادي (أزرق) + الإيداعات باللون الأخضر."""
    # الرقم كنص عادي — تيليجرام يحوّله لرابط أزرق قابل للنقر
    parts = [html.escape(number)]
    if deposits:
        parts.append("💰 <b>الإيداعات:</b>")
        # كتلة كود بلغة diff: كل سطر يبدأ بـ + يظهر باللون الأخضر
        lines = "\n".join(f"+ {html.escape(d)}" for d in deposits)
        parts.append(f'<pre><code class="language-diff">{lines}</code></pre>')
    return "\n".join(parts)


def _keyboard(number: str, latest: str = "") -> InlineKeyboardMarkup:
    """أزرار تحت الرقم: نسخ + تسجيل إيداع.

    بعد تسجيل أول إيداع، يتحوّل نص زر الإيداع إلى آخر مبلغ تم إدخاله.
    """
    dep_label = f"💰 {latest}" if latest else "💰 تسجيل إيداع"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 نسخ الرقم", copy_text=CopyTextButton(text=number))],
        [InlineKeyboardButton(dep_label, callback_data=f"{DEPOSIT_PREFIX}{number}")],
    ])


def _parse_deposits(text: str, number: str = "") -> list[str]:
    """استخراج الإيداعات الحالية من نص الرسالة.

    يدعم الصيغة الجديدة (أسطر تبدأ بـ +) والقديمة (أسطر تبدأ بـ •)،
    مع تجاهل سطر الرقم نفسه.
    """
    deposits = []
    for line in (text or "").splitlines():
        line = line.strip()
        if line.startswith("•"):
            entry = line.lstrip("•").strip()
        elif line.startswith("+"):
            entry = line[1:].strip()
        else:
            continue
        if entry and entry != number:
            deposits.append(entry)
    return deposits


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
        إرسال رسالة رد مباشرة على الصورة الأصلية — بالرقم الأخضر وأزرار النسخ والإيداع.
        """
        try:
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text=_build_text(msisdn, []),
                reply_to_message_id=update.message.message_id,  # الرد على الصورة الأصلية
                parse_mode=ParseMode.HTML,
                reply_markup=_keyboard(msisdn),
            )
            logger.info(f"Reply sent successfully to message {update.message.message_id}")
        except TelegramError as e:
            logger.error(f"Failed to send reply: {e}", exc_info=False)
            raise

    async def on_deposit_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """عند الضغط على زر «تسجيل إيداع» — نطلب من المستخدم كتابة المبلغ."""
        query = update.callback_query
        if not query or not query.data or not query.data.startswith(DEPOSIT_PREFIX):
            return

        number = query.data[len(DEPOSIT_PREFIX):]
        await query.answer()

        # إرسال طلب كتابة المبلغ (رد إجباري على هذه الرسالة)
        prompt = await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"💰 اكتب مبلغ الإيداع للرقم {number}\n(ردّ على هذه الرسالة بالمبلغ)",
            reply_to_message_id=query.message.message_id,
            reply_markup=ForceReply(selective=True),
        )

        # نحفظ مؤقتاً: هذا الطلب مرتبط برسالة الرقم والإيداعات الحالية فيها
        pending = context.chat_data.setdefault("pending_deposits", {})
        pending[prompt.message_id] = {
            "target_msg": query.message.message_id,
            "number": number,
            "deposits": _parse_deposits(query.message.text or "", number),
        }

    async def on_deposit_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """التقاط المبلغ الذي كتبه المستخدم ردًّا على طلب الإيداع، وتسجيله في الرسالة."""
        msg = update.message
        if not msg or not msg.text or not msg.reply_to_message:
            return

        pending = context.chat_data.get("pending_deposits", {})
        info = pending.get(msg.reply_to_message.message_id)
        if not info:
            return  # ليست ردًّا على طلب إيداع — نتجاهلها

        amount = msg.text.strip()
        number = info["number"]
        target_id = info["target_msg"]
        now = datetime.now(CAIRO_TZ).strftime("%d/%m %H:%M")
        deposits = info["deposits"] + [f"{amount} — {now}"]

        try:
            await context.bot.edit_message_text(
                chat_id=msg.chat_id,
                message_id=target_id,
                text=_build_text(number, deposits),
                parse_mode=ParseMode.HTML,
                reply_markup=_keyboard(number, latest=amount),
            )
            logger.info(f"Deposit recorded for {number}: {amount}")
        except TelegramError as e:
            logger.error(f"Failed to record deposit: {e}", exc_info=False)
        finally:
            pending.pop(msg.reply_to_message.message_id, None)

        # تنظيف الزحام: نحذف رسالة الطلب ورسالة المستخدم (حذف رسالة المستخدم
        # يتطلب أن يكون البوت أدمن في الجروب؛ في الخاص لا يمكن حذف رسائل المستخدم)
        for mid in (msg.reply_to_message.message_id, msg.message_id):
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=mid)
            except TelegramError:
                pass

    async def on_error(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """معالج أخطاء عام يمنع توقف البوت ويسجّل الخطأ فقط."""
        logger.error("Exception while handling an update:", exc_info=context.error)

    def run(self):
        """تشغيل البوت."""
        logger.info("Starting MSISDN Extraction Bot...")

        # إنشاء التطبيق
        app = Application.builder().token(TELEGRAM_BOT_TOKEN).read_timeout(READ_TIMEOUT).get_updates_read_timeout(POLLING_TIMEOUT).build()

        # معالج الصور
        app.add_handler(MessageHandler(filters.PHOTO & ~filters.FORWARDED, self.handle_photo))
        # معالج زر الإيداع
        app.add_handler(CallbackQueryHandler(self.on_deposit_button, pattern=f"^{DEPOSIT_PREFIX}"))
        # معالج الرد بكتابة مبلغ الإيداع
        app.add_handler(MessageHandler(filters.TEXT & filters.REPLY & ~filters.COMMAND, self.on_deposit_amount))
        # معالج الأخطاء العام
        app.add_error_handler(self.on_error)

        # بدء التطبيق (نستقبل الرسائل وضغطات الأزرار)
        app.run_polling(allowed_updates=["message", "callback_query"])


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
