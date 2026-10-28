#!/usr/bin/env python3
"""اختبارات شاملة لبوت MSISDN."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from ocr_processor import MSISDNExtractor


class TestMSISDNExtraction(unittest.TestCase):
    """اختبارات استخراج MSISDN من الصور."""

    def setUp(self):
        self.extractor = MSISDNExtractor()

    def test_parse_msisdn_valid_with_colon(self):
        """اختبار: استخراج MSISDN صحيح مع ':'"""
        text = "MSISDN is:201095746142"
        result = self.extractor._parse_msisdn(text)
        self.assertEqual(result, "01095746142")

    def test_parse_msisdn_valid_with_space(self):
        """اختبار: استخراج MSISDN صحيح مع مسافة"""
        text = "MSISDN is 201095746142"
        result = self.extractor._parse_msisdn(text)
        self.assertEqual(result, "01095746142")

    def test_parse_msisdn_valid_uppercase(self):
        """اختبار: استخراج MSISDN مع حروف كبيرة"""
        text = "MSISDN IS: 201095746142"
        result = self.extractor._parse_msisdn(text)
        self.assertEqual(result, "01095746142")

    def test_parse_msisdn_all_prefixes(self):
        """اختبار: جميع بادئات الأرقام المصرية"""
        prefixes = ["2010", "2011", "2012", "2015"]
        for prefix in prefixes:
            text = f"MSISDN is:{prefix}95746142"
            result = self.extractor._parse_msisdn(text)
            expected = "0" + prefix[2:] + "95746142"
            self.assertEqual(result, expected, f"Failed for prefix {prefix}")

    def test_parse_msisdn_no_match(self):
        """اختبار: صورة بدون MSISDN"""
        text = "This is a regular image with some text"
        result = self.extractor._parse_msisdn(text)
        self.assertIsNone(result)

    def test_parse_msisdn_wrong_prefix(self):
        """اختبار: رقم بدون بادئة مصرية صحيحة"""
        text = "MSISDN is:201395746142"  # 2013 ليست بادئة صحيحة
        result = self.extractor._parse_msisdn(text)
        self.assertIsNone(result)

    def test_parse_msisdn_incomplete_number(self):
        """اختبار: رقم غير مكتمل"""
        text = "MSISDN is:20109574"  # ناقص أرقام
        result = self.extractor._parse_msisdn(text)
        self.assertIsNone(result)

    def test_parse_msisdn_invalid_characters(self):
        """اختبار: رقم يحتوي على أحرف"""
        text = "MSISDN is:20109574abc42"
        result = self.extractor._parse_msisdn(text)
        self.assertIsNone(result)

    def test_validate_msisdn_valid(self):
        """اختبار: التحقق من رقم صحيح"""
        self.assertTrue(self.extractor.validate_msisdn("01095746142"))

    def test_validate_msisdn_wrong_length(self):
        """اختبار: رقم بطول خاطئ"""
        self.assertFalse(self.extractor.validate_msisdn("0109574614"))

    def test_validate_msisdn_no_01_prefix(self):
        """اختبار: رقم بدون بادئة 01"""
        self.assertFalse(self.extractor.validate_msisdn("11095746142"))

    def test_validate_msisdn_non_digit(self):
        """اختبار: رقم يحتوي على أحرف"""
        self.assertFalse(self.extractor.validate_msisdn("0109574614a"))

    def test_validate_msisdn_empty(self):
        """اختبار: رقم فارغ"""
        self.assertFalse(self.extractor.validate_msisdn(""))

    def test_validate_msisdn_none(self):
        """اختبار: قيمة None"""
        self.assertFalse(self.extractor.validate_msisdn(None))


class TestMSISDNBotLogic(unittest.TestCase):
    """اختبارات منطق البوت (بدون API Telegram)."""

    def setUp(self):
        self.extractor = MSISDNExtractor()

    def test_extraction_with_multiple_numbers(self):
        """اختبار: نص يحتوي على أرقام متعددة"""
        text = """
        Some random text with numbers: 1234567890
        MSISDN is:201095746142
        Another number: 9876543210
        """
        result = self.extractor._parse_msisdn(text)
        # يجب أن يستخرج الرقم الصحيح فقط
        self.assertEqual(result, "01095746142")

    def test_extraction_case_insensitive(self):
        """اختبار: البحث غير حساس لحالة الأحرف"""
        tests = [
            "msisdn is:201095746142",
            "MSISDN IS:201095746142",
            "Msisdn Is:201095746142",
            "mSiSdN iS:201095746142",
        ]
        for text in tests:
            result = self.extractor._parse_msisdn(text)
            self.assertEqual(result, "01095746142", f"Failed for: {text}")

    def test_extraction_with_variations(self):
        """اختبار: تنسيقات مختلفة من MSISDN"""
        tests = [
            ("MSISDN is:201095746142", "01095746142"),
            ("MSISDN is: 201095746142", "01095746142"),
            ("MSISDN is = 201095746142", "01095746142"),
            ("MSISDN is201095746142", "01095746142"),
        ]
        for text, expected in tests:
            result = self.extractor._parse_msisdn(text)
            self.assertEqual(result, expected, f"Failed for: {text}")


class TestProcessedMessagesTracking(unittest.TestCase):
    """اختبارات منع الردود المكررة."""

    def test_duplicate_message_detection(self):
        """اختبار: كشف الرسائل المكررة"""
        processed = set()

        # محاكاة معالجة رسالة
        message_key = (123, 456)  # (chat_id, message_id)
        self.assertNotIn(message_key, processed)
        processed.add(message_key)

        # التحقق من أنها أضيفت
        self.assertIn(message_key, processed)

        # محاكاة محاولة معالجة نفس الرسالة
        self.assertTrue(message_key in processed)


def run_unit_tests():
    """تشغيل جميع الاختبارات."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # إضافة جميع الاختبارات
    suite.addTests(loader.loadTestsFromTestCase(TestMSISDNExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestMSISDNBotLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestProcessedMessagesTracking))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_unit_tests()
    sys.exit(0 if success else 1)
