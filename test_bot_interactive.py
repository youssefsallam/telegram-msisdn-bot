#!/usr/bin/env python3
"""
🤖 اختبار تفاعلي للبوت - بدون الحاجة إلى Tesseract
Interactive Bot Testing - No Tesseract Required
"""

from ocr_processor import MSISDNExtractor

def test_bot():
    """اختبر البوت بشكل تفاعلي"""
    extractor = MSISDNExtractor()

    print("=" * 70)
    print("🤖 اختبار بوت MSISDN - Interactive Testing")
    print("=" * 70)
    print()
    print("أدخل النص الذي تريد اختباره (أو 'exit' للخروج)")
    print("Enter text to test (or 'exit' to quit)")
    print()

    test_cases = [
        ("MSISDN is:201095746142", "01095746142"),
        ("MSISDN is: 201095746142", "01095746142"),
        ("MSISDN is:201195123456", "01195123456"),
        ("MSISDN is:201295874561", "01295874561"),
        ("MSISDN is:201595555555", "01595555555"),
        ("random text 123456", None),
        ("MSISDN is:12345", None),
    ]

    print("\n📋 الاختبارات المدمجة - Built-in Tests:")
    print("-" * 70)

    passed = 0
    failed = 0

    for text, expected in test_cases:
        result = extractor._parse_msisdn(text)
        status = "✅ PASS" if result == expected else "❌ FAIL"

        if result == expected:
            passed += 1
        else:
            failed += 1

        print(f"{status} | Input: {text}")
        print(f"        Expected: {expected}, Got: {result}")
        print()

    print("-" * 70)
    print(f"📊 النتائج - Results: {passed} passed, {failed} failed")
    print("=" * 70)

    # اختبار تفاعلي
    print()
    print("\n🔍 الاختبار التفاعلي - Interactive Testing:")
    print("-" * 70)

    while True:
        user_input = input("\n📝 أدخل النص (Enter text): ").strip()

        if user_input.lower() == 'exit':
            print("\n👋 شكراً! Goodbye!")
            break

        if not user_input:
            print("⚠️ الرجاء إدخال نص!")
            continue

        result = extractor._parse_msisdn(user_input)

        print()
        if result:
            print(f"✅ النتيجة (Result): {result}")

            # تحقق من الصحة
            if extractor.validate_msisdn(result):
                print(f"✅ الرقم صحيح - Valid number!")
            else:
                print(f"❌ الرقم غير صحيح - Invalid number!")
        else:
            print(f"❌ لم يتم العثور على MSISDN - No MSISDN found")

        print()

if __name__ == "__main__":
    test_bot()
