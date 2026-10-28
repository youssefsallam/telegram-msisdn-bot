import re
import logging
from typing import Optional, TYPE_CHECKING
from io import BytesIO

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
            image = Image.open(BytesIO(image_bytes))

            # تطبيق preprocessing للحصول على نتائج أفضل
            image = MSISDNExtractor._preprocess_image(image)

            # استخراج النص من الصورة
            extracted_text = pytesseract.image_to_string(
                image,
                lang="eng+ara",  # دعم الإنجليزية والعربية
                config="--psm 6"  # معالج تلقائي للصفحات
            )

            logger.debug(f"Extracted text: {extracted_text[:100]}")

            # البحث عن MSISDN
            msisdn = MSISDNExtractor._parse_msisdn(extracted_text)

            if msisdn:
                logger.info(f"Successfully extracted MSISDN: {msisdn}")
                return msisdn
            else:
                logger.debug("No valid MSISDN found in extracted text")
                return None

        except Exception as e:
            logger.error(f"Error extracting MSISDN from image: {e}", exc_info=True)
            return None

    @staticmethod
    def _preprocess_image(image: "Image.Image") -> "Image.Image":
        """
        معالجة مسبقة للصورة لتحسين OCR.

        Args:
            image: كائن PIL Image

        Returns:
            صورة معالجة
        """
        try:
            from PIL import ImageEnhance

            # تحويل إلى RGB إذا لزم الأمر
            if image.mode != "RGB":
                image = image.convert("RGB")

            # تحسين التباين
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)

            # تحسين الحدة
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2)

            return image
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            return image

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
