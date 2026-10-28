# البدء السريع 🚀

دليل سريع جداً لتشغيل البوت في دقائق معدودة.

## الخطوة 1: الحصول على Bot Token (5 دقائق)

1. افتح Telegram وابحث عن `@BotFather`
2. أرسل `/newbot`
3. اتبع التعليمات، اختر اسم البوت (مثلاً: `MyMSISDNBot`)
4. سيعطيك Token مثل: `1234567890:ABCDefGhIjKlMnOpQrStUvWxYz`
5. **احفظ هذا الـ Token!**

## الخطوة 2: تعطيل Privacy Mode (2 دقيقة)

1. أرسل `/setprivacy` إلى `@BotFather`
2. اختر البوت الخاص بك
3. اختر `Disabled`

**السبب:** يسمح للبوت بقراءة الصور في الجروب

## الخطوة 3: التشغيل المحلي (5 دقائق)

### على Windows:

```bash
# 1. انسخ المجلد
cd C:\Users\salla\Desktop\bot-raeding

# 2. انشئ بيئة افتراضية
python -m venv venv
venv\Scripts\activate

# 3. ثبّت المكتبات
pip install -r requirements.txt

# 4. نسخ الإعدادات
copy .env.example .env

# 5. عدّل .env بإضافة التوكن
# افتح .env بمحرر النصوص وأضف:
# TELEGRAM_BOT_TOKEN=your_token_here

# 6. شغّل البوت
python main.py
```

### على Mac/Linux:

```bash
cd ~/telegram-msisdn-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# عدّل .env
python main.py
```

## الخطوة 4: الاختبار (5 دقائق)

1. في الجروب، أرسل صورة تحتوي على:
   ```
   MSISDN is:201095746142
   ```

2. البوت يجب أن يرد برسالة مباشرة:
   ```
   01095746142
   ```

3. إذا عمل ✅ → تهانينا!

## النشر على Railway (10 دقائق)

### 1. دفع الكود إلى GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/telegram-msisdn-bot.git
git push -u origin main
```

### 2. إنشاء مشروع على Railway

1. اذهب إلى https://railway.app
2. انقر "New Project" → "Deploy from GitHub"
3. اختر المستودع الخاص بك
4. Railway سيبدأ النشر

### 3. تعيين المتغيرات

في لوحة تحكم Railway:

```
TELEGRAM_BOT_TOKEN=your_token_here
ALLOWED_CHAT_IDS=-1001234567890
LOG_LEVEL=INFO
```

### 4. اختبر مرة أخرى ✅

أرسل صورة في الجروب → البوت يرد تلقائياً

## الملفات المهمة

| الملف | الوصف |
|------|-------|
| `main.py` | البوت الرئيسي |
| `ocr_processor.py` | معالج استخراج الأرقام |
| `config.py` | الإعدادات |
| `.env` | متغيرات البيئة (سرية) |
| `Dockerfile` | للنشر على Railway |

## الأخطاء الشائعة

| الخطأ | الحل |
|------|------|
| `ModuleNotFoundError: No module named 'telegram'` | شغّل `pip install -r requirements.txt` |
| `TELEGRAM_BOT_TOKEN not set` | أضف التوكن في `.env` |
| `Bot doesn't respond` | تأكد من تعطيل Privacy Mode |
| `OCR errors` | ثبّت Tesseract: `pip install pytesseract` |

## الخطوات التالية

- اقرأ `README.md` للتفاصيل الكاملة
- اقرأ `DEPLOYMENT.md` لنشر متقدم
- شاهد `test_bot.py` للاختبارات
- راقب الـ logs من Railway

---

**تم! البوت الآن يعمل 24/7 🎉**
