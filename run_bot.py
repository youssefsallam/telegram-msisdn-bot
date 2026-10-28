#!/usr/bin/env python3
"""
سكريبت تشغيل بوت MSISDN مباشر
"""

import sys
import subprocess
import os

def main():
    print("=" * 60)
    print("🤖 بوت استخراج أرقام MSISDN من الصور")
    print("=" * 60)
    print()

    # التحقق من المكتبات
    print("📥 التحقق من المكتبات...")
    try:
        import telegram
        print("✅ python-telegram-bot مثبّت")
    except ImportError:
        print("⚠️ تثبيت المكتبات...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"])
        print("✅ تم التثبيت")

    print()
    print("=" * 60)
    print("🚀 بدء تشغيل البوت...")
    print("=" * 60)
    print()

    # تشغيل البوت
    try:
        from main import main as bot_main
        bot_main()
    except KeyboardInterrupt:
        print()
        print("=" * 60)
        print("🛑 تم إيقاف البوت")
        print("=" * 60)
        sys.exit(0)
    except Exception as e:
        print(f"❌ خطأ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
