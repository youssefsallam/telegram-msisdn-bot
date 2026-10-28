# بوت Telegram لاستخراج أرقام MSISDN من الصور

بوت تلقائي يعمل في مجموعات Telegram، يستخرج أرقام الموبايل المصرية من الصور باستخدام تقنية OCR، ويرد برسالة مباشرة على الصورة الأصلية.

## المميزات

✅ **استخراج ذكي للأرقام**: يبحث عن نمط `MSISDN is` في الصور ويستخرج الرقم بدقة
✅ **تحويل تلقائي**: يحول الأرقام من الصيغة الدولية (20...) إلى المحلية (01...)
✅ **رد مباشر**: يرد كـ Reply مباشر على الصورة الأصلية في الجروب
✅ **منع النسخ المكررة**: يتذكر الصور التي تمت معالجتها ولا يرد عليها مرتين
✅ **معالجة آمنة**: لا يخزن البيانات الحساسة ولا يسجل الأرقام
✅ **سرعة عالية**: معالجة شبه لحظية للصور (1-3 ثوانٍ)
✅ **دعم اللغات**: يدعم النصوص بالعربية والإنجليزية

## المتطلبات

- Python 3.8+
- Tesseract OCR
- pytesseract
- python-telegram-bot
- Pillow

## التثبيت المحلي

### 1. استنساخ المشروع

```bash
cd ~/your-projects
git clone <your-repo-url> telegram-msisdn-bot
cd telegram-msisdn-bot
```

### 2. إنشاء بيئة افتراضية

```bash
python -m venv venv
source venv/bin/activate  # على Linux/Mac
# أو
venv\Scripts\activate  # على Windows
```

### 3. تثبيت المكتبات

```bash
pip install -r requirements.txt
```

### 4. تثبيت Tesseract OCR

**على Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-ara tesseract-ocr-eng
```

**على Mac:**
```bash
brew install tesseract
```

**على Windows:**
- حمّل من: https://github.com/UB-Mannheim/tesseract/wiki
- ثبّت البرنامج
- أضف مسار التثبيت إلى متغير البيئة `PATH`

### 5. إنشاء ملف `.env`

```bash
cp .env.example .env
```

ثم عدّل `.env` بإضافة:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
ALLOWED_CHAT_IDS=-1001234567890
LOG_LEVEL=INFO
```

## إعداد بوت Telegram

### 1. إنشاء بوت جديد مع BotFather

1. افتح Telegram وابحث عن `@BotFather`
2. أرسل الأمر `/newbot`
3. اتبع التعليمات لإعطاء اسم للبوت
4. سيعطيك الـ Token (احفظه)

مثال على الرد:
```
Use this token to access the HTTP API:
1234567890:ABCDefGhIjKlMnOpQrStUvWxYz...
```

### 2. تعطيل Privacy Mode

تعطيل Privacy Mode يسمح للبوت بقراءة الرسائل في الجروب:

1. أرسل `/setprivacy` إلى `@BotFather`
2. اختر البوت الخاص بك
3. اختر `Disabled` لتعطيل Privacy Mode

### 3. تعيين الأذونات

أرسل هذه الأوامر إلى `@BotFather`:

```
/setcommands
```

ثم اختر البوت (اختياري: لتعريف الأوامر)

### 4. إضافة البوت للجروب

1. افتح الجروب
2. اضغط على اسم الجروب → الأعضاء
3. اضغط "Add Member"
4. ابحث عن البوت واختره

## التشغيل المحلي

```bash
python main.py
```

إذا رأيت الرسالة التالية:
```
2026-10-28 10:00:00,000 - __main__ - INFO - Starting MSISDN Extraction Bot...
```

البوت يعمل بنجاح! 🎉

## الاختبار

### تشغيل اختبارات الوحدات

```bash
python test_bot.py
```

سيختبر:
- استخراج MSISDN من نصوص مختلفة
- التحقق من صحة الأرقام
- معالجة الحالات الخاصة والأخطاء
- منع النسخ المكررة

### الاختبار في Telegram

1. **اختبار أساسي**: أرسل صورة تحتوي على `MSISDN is:201095746142` في الجروب
   - النتيجة المتوقعة: البوت يرد برسالة مباشرة تحتوي على `01095746142`

2. **اختبار الصورة العادية**: أرسل أي صورة عادية
   - النتيجة المتوقعة: لا يرد نهائياً

3. **اختبار الصور المتعددة**: أرسل 10 صور متتالية، نصفها يحتوي على MSISDN
   - النتيجة المتوقعة: يرد على كل صورة مطابقة بشكل مستقل

4. **اختبار النسخ المكررة**: أرسل نفس الصورة مرتين
   - النتيجة المتوقعة: يرد على الأولى فقط

## النشر على Railway

### 1. إنشاء حساب Railway

- اذهب إلى https://railway.app
- سجّل دخول باستخدام GitHub
- انقر "Create New Project"

### 2. ربط المستودع

```bash
# في مجلد المشروع
git init
git add .
git commit -m "Initial commit: MSISDN extraction bot"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 3. إنشاء المشروع على Railway

1. في Railway، اختر "Deploy from GitHub"
2. اختر المستودع الخاص بك
3. انقر "Deploy"

### 4. تعيين متغيرات البيئة

1. في لوحة تحكم Railway، اذهب إلى "Variables"
2. أضف المتغيرات:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
ALLOWED_CHAT_IDS=-1001234567890
LOG_LEVEL=INFO
```

3. اضغط "Deploy"

### 5. مراقبة البوت

في Railway:
- اضغط على المشروع
- شاهد الـ "Logs" لمراقبة النشاط
- تأكد من عدم وجود أخطاء

## هيكل الملفات

```
telegram-msisdn-bot/
├── main.py              # الملف الرئيسي للبوت
├── config.py            # إعدادات التطبيق
├── ocr_processor.py     # معالج OCR واستخراج الأرقام
├── test_bot.py          # اختبارات شاملة
├── requirements.txt     # المكتبات المطلوبة
├── Dockerfile           # ملف Docker للنشر
├── .dockerignore        # ملفات لتجاهلها في Docker
├── .env.example         # نموذج متغيرات البيئة
└── README.md           # هذا الملف
```

## توثيق الدوال الرئيسية

### `MSISDNExtractor.extract_msisdn_from_image(image_bytes)`

استخراج رقم MSISDN من صورة.

**المعاملات:**
- `image_bytes` (bytes): بيانات الصورة

**الإرجاع:**
- `str`: رقم موبايل مصري (01...) أو `None` إذا لم يجد

**مثال:**
```python
from ocr_processor import MSISDNExtractor
extractor = MSISDNExtractor()
msisdn = extractor.extract_msisdn_from_image(image_data)
```

### `MSISDNExtractor.validate_msisdn(msisdn)`

التحقق من صحة رقم MSISDN.

**المعاملات:**
- `msisdn` (str): رقم موبايل

**الإرجاع:**
- `bool`: `True` إذا كان صحيحاً

**مثال:**
```python
if extractor.validate_msisdn("01095746142"):
    print("Valid number!")
```

## استكشاف الأخطاء

### البوت لا يستجيب

1. تحقق من `TELEGRAM_BOT_TOKEN` صحيح
2. تحقق من تعطيل Privacy Mode
3. تحقق من أن البوت إداري في الجروب
4. شاهد الـ Logs بحثاً عن أخطاء

### OCR لا يعمل

```bash
# تحقق من تثبيت Tesseract
tesseract --version

# على Linux
sudo apt-get install tesseract-ocr tesseract-ocr-ara

# على Mac
brew install tesseract
```

### البوت يعطل مع صور معينة

عادة ما تكون الصور ذات جودة منخفضة جداً. البوت مصمم لتجاهل الصور التي لا يمكن قراءتها بوضوح.

## الأداء

- **وقت الاستجابة**: 1-3 ثوانٍ في الظروف الطبيعية
- **الذاكرة**: ~100MB
- **CPU**: منخفض (معالجة صور)

## الأمان والخصوصية

✅ **لا تخزين الأرقام**: تُحذف من الذاكرة فوراً بعد الرد
✅ **لا تخزين الصور**: يتم حذفها بعد المعالجة
✅ **عدم تسجيل الأرقام**: الـ Logs تحتوي على رسائل عامة فقط
✅ **توكن آمن**: يُحفظ في متغيرات البيئة
✅ **معالجة الأخطاء**: الأخطاء لا تفضح معلومات حساسة

## المساهمة

إذا كان لديك اقتراحات أو تحسينات:

1. اصنع فرع جديد
2. قم بالتغييرات
3. أرسل Pull Request

## الترخيص

هذا المشروع متاح تحت رخصة MIT.

## الدعم

إذا واجهت مشاكل:

1. شاهد الـ Logs
2. تحقق من أن جميع المتطلبات مثبتة
3. جرّب الاختبارات: `python test_bot.py`
4. قراءة هذا الملف بعناية

---

**آخر تحديث:** 2026-10-28
