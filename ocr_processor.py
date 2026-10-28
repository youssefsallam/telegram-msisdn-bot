import re
import logging
from typing import Optional, TYPE_CHECKING
from io import BytesIO

import os
import shutil

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    Image = None

if TYPE_CHECKING:
    from PIL import Image

logger = logging.getLogger(__name__)


def _configure_tesseract_cmd():
    """تحديد مسار tesseract تلقائياً (مهم على ويندوز حيث لا يكون في PATH غالباً)."""
    if not TESSERACT_AVAILABLE:
        return
    # 1) متغير بيئة صريح له الأولوية (مفيد على Railway/Linux)
    env_cmd = os.getenv("TESSERACT_CMD")
    if env_cmd and os.path.isfile(env_cmd):
        pytesseract.pytesseract.tesseract_cmd = env_cmd
        return
    # 2) موجود في PATH بالفعل (حالة Linux/Docker الطبيعية)
    if shutil.which("tesseract"):
        return
    # 3) المسارات الشائعة على ويندوز
    for candidate in (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Tesseract-OCR\tesseract.exe"),
    ):
        if os.path.isfile(candidate):
            pytesseract.pytesseract.tesseract_cmd = candidate
            return


_configure_tesseract_cmd()


class MSISDNExtractor:
    """استخراج أرقام MSISDN من الصور باستخدام OCR."""

    # نمط البحث عن MSISDN (يدعم مسافات ومتغيرات الحروف)
    MSISDN_PATTERN = r"MSISDN\s*is\s*[:=]?\s*(\d+)"

    # أرقام مصرية معروفة (بداية صحيحة)
    EGYPTIAN_PREFIXES = ("2010", "2011", "2012", "2015")

    # طول الرقم المتوقع بعد التحويل
    EXPECTED_LENGTH = 11

    @staticmethod
    def extract_msisdn_from_image(image_bytes: bytes) -> Optional[str]:
        """
        استخراج رقم MSISDN من صورة باستخدام OCR.

        Args:
            image_bytes: بيانات الصورة (bytes)

        Returns:
            رقم موبايل مصري بالصيغة المحلية (01...) أو None
        """
        if not TESSERACT_AVAILABLE:
            logger.error("Tesseract OCR not available. Install pytesseract and tesseract-ocr")
            return None

        try:
            # فتح الصورة
            original = Image.open(BytesIO(image_bytes))

            # حفظ الصورة الأصلية للفحص (debug)
            debug_dir = os.getenv("OCR_DEBUG_DIR")
            if debug_dir:
                try:
                    os.makedirs(debug_dir, exist_ok=True)
                    save_path = os.path.join(debug_dir, "last_image.png")
                    original.convert("RGB").save(save_path)
                    logger.info(f"Saved incoming image for debug to {save_path}")
                except Exception as se:
                    logger.warning(f"Could not save debug image: {se}")

            # توليد عدة نسخ من الصورة (تدعم الدارك مود: نص فاتح على خلفية غامقة)
            variants = MSISDNExtractor._image_variants(original)

            # قصر القراءة على الحروف المتوقعة فقط يحسّن الدقة كثيراً
            whitelist = "MSISDNmsisdn0123456789:= "
            configs = (
                f"--psm 3 -c tessedit_char_whitelist={whitelist}",
                f"--psm 6 -c tessedit_char_whitelist={whitelist}",
            )

            best_text = ""
            for name, img in variants:
                for cfg in configs:
                    try:
                        text = pytesseract.image_to_string(img, lang="eng", config=cfg)
                    except Exception as oe:
                        logger.warning(f"OCR attempt {name} failed: {oe}")
                        continue
                    logger.info(f"OCR [{name} psm{cfg.split('--psm ')[1][0]}] -> {text!r}")
                    if len(text.strip()) > len(best_text.strip()):
                        best_text = text
                    msisdn = MSISDNExtractor._parse_msisdn(text)
                    if msisdn:
                        logger.info(f"Successfully extracted MSISDN: {msisdn}")
                        return msisdn

            logger.info(f"No valid MSISDN found. Best text was: {best_text!r}")
            return None

        except Exception as e:
            logger.error(f"Error extracting MSISDN from image: {e}", exc_info=True)
            return None

    @staticmethod
    def _image_variants(image: "Image.Image"):
        """
        توليد عدة نسخ معالَجة من الصورة لتحسين OCR.

        يتعامل مع صور الدارك مود (نص فاتح على خلفية غامقة) عن طريق تجربة
        النسخة العادية والمعكوسة والثنائية (أبيض/أسود).

        Returns:
            قائمة من (الاسم، صورة PIL)
        """
        try:
            from PIL import ImageOps

            # رمادي + تكبير الدقة ×3 (حاسم لقراءة النص الصغير بدقة)
            gray = image.convert("L")
            w, h = gray.size
            scale = 3 if max(w, h) < 1500 else (2 if max(w, h) < 3000 else 1)
            if scale > 1:
                gray = gray.resize((w * scale, h * scale), Image.LANCZOS)

            auto = ImageOps.autocontrast(gray, cutoff=1)

            # نسخ ثنائية بعتبات مختلفة تغطي الدارك مود والعادي
            variants = [("auto", auto)]
            for thr in (130, 160, 100):
                variants.append((f"bin{thr}", auto.point(lambda p, t=thr: 255 if p > t else 0)))

            return variants
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            return [("original", image.convert("L"))]

    @staticmethod
    def _parse_msisdn(text: str) -> Optional[str]:
        """
        فحص النص واستخراج رقم MSISDN.

        Args:
            text: النص المستخرج من الصورة

        Returns:
            رقم موبايل مصري بالصيغة المحلية أو None
        """
        # البحث عن MSISDN باستخدام regex
        match = re.search(MSISDNExtractor.MSISDN_PATTERN, text, re.IGNORECASE)

        if not match:
            return None

        msisdn = match.group(1).strip()

        # التحقق من أن الرقم يبدأ برقم مصري معروف
        if not any(msisdn.startswith(prefix) for prefix in MSISDNExtractor.EGYPTIAN_PREFIXES):
            logger.debug(f"MSISDN does not start with Egyptian prefix: {msisdn}")
            return None

        # تحويل من الصيغة الدولية (20...) إلى المحلية (0...)
        if msisdn.startswith("20"):
            msisdn = "0" + msisdn[2:]

        # التحقق من طول الرقم
        if len(msisdn) != MSISDNExtractor.EXPECTED_LENGTH:
            logger.debug(f"Invalid MSISDN length: {len(msisdn)} (expected {MSISDNExtractor.EXPECTED_LENGTH})")
            return None

        # التحقق من أن جميع الأحرف أرقام
        if not msisdn.isdigit():
            logger.debug(f"MSISDN contains non-digit characters: {msisdn}")
            return None

        return msisdn

    @staticmethod
    def validate_msisdn(msisdn: str) -> bool:
        """
        التحقق من صحة رقم MSISDN.

        Args:
            msisdn: رقم MSISDN

        Returns:
            True إذا كان صحيحاً، False خلاف ذلك
        """
        if not msisdn or not isinstance(msisdn, str):
            return False

        if not msisdn.isdigit():
            return False

        if len(msisdn) != MSISDNExtractor.EXPECTED_LENGTH:
            return False

        if not msisdn.startswith("01"):
            return False

        return True
