# دليل النشر على Railway

هذا الدليل يشرح خطوات نشر بوت MSISDN على Railway خطوة بخطوة.

## المتطلبات

- حساب GitHub
- حساب Railway (مجاني)
- البوت Token من BotFather
- مستودع Git (public أو private)

## الخطوات

### 1. تحضير المستودع على GitHub

#### 1.1 إنشاء مستودع جديد على GitHub

1. اذهب إلى https://github.com/new
2. أدخل اسم المستودع: `telegram-msisdn-bot`
3. اختر "Public" أو "Private"
4. انقر "Create repository"

#### 1.2 دفع الكود إلى GitHub

في مجلد المشروع:

```bash
# تهيئة git إذا لم يكن مهيأً
git init

# إضافة جميع الملفات
git add .

# إنشاء أول commit
git commit -m "Initial commit: MSISDN extraction bot with OCR support"

# إضافة Remote (استبدل USERNAME و REPO_NAME)
git remote add origin https://github.com/USERNAME/REPO_NAME.git

# دفع الكود
git branch -M main
git push -u origin main
```

### 2. إنشاء حساب Railway ربط المستودع

#### 2.1 إنشاء حساب Railway

1. اذهب إلى https://railway.app
2. انقر "Login with GitHub"
3. وافق على صلاحيات التطبيق

#### 2.2 إنشاء مشروع جديد

1. انقر "New Project" أو "Create"
2. اختر "Deploy from GitHub repo"
3. اختر "Configure GitHub App"
4. اختر المستودع الخاص بك
5. انقر "Connect"

#### 2.3 إضافة البيانات المطلوبة

Railway سيبدأ النشر تلقائياً. خلال ذلك:

1. في لوحة تحكم Railway، اختر المشروع
2. انقر على "Variables"
3. أضف المتغيرات التالية:

```
TELEGRAM_BOT_TOKEN=your_actual_token_here
ALLOWED_CHAT_IDS=-1001234567890,-1009876543210
LOG_LEVEL=INFO
POLLING_TIMEOUT=30
READ_TIMEOUT=60
```

**الحصول على معرف الجروب:**

لمعرفة معرف جروبك:

1. أضف بوت مؤقت للجروب
2. اكتب رسالة في الجروب
3. اذهب إلى: `https://api.telegram.org/BOT_TOKEN/getUpdates`
4. ابحث عن `"chat":{"id":-1001234567890}`

### 3. التحقق من النشر

#### 3.1 مراقبة Logs

في لوحة تحكم Railway:

1. انقر على المشروع
2. اختر "Deployments"
3. اضغط على آخر deployment
4. شاهد "Build Logs" و "Deploy Logs"

#### 3.2 البحث عن الأخطاء

**رسالة نجاح:**
```
Starting MSISDN Extraction Bot...
```

**الأخطاء الشائعة:**

| الخطأ | الحل |
|------|------|
| `Tesseract not found` | Railway سيثبته تلقائياً من Dockerfile |
| `TELEGRAM_BOT_TOKEN not set` | أضف المتغير في Variables |
| `Connection refused` | انتظر دقيقة لبدء الخدمة |

### 4. تجربة البوت

#### 4.1 اختبار بسيط

1. افتح الجروب
2. أرسل صورة تحتوي على: `MSISDN is:201095746142`
3. الانتظار 1-3 ثوانٍ
4. البوت يجب أن يرد برسالة مباشرة: `01095746142`

#### 4.2 اختبارات إضافية

**اختبار الصور العادية:**
- أرسل أي صورة عادية
- النتيجة: لا يرد نهائياً

**اختبار الصور المتعددة:**
- أرسل 5 صور متتالية
- قيس سرعة الاستجابة

**اختبار النسخ المكررة:**
- أرسل نفس الصورة مرتين
- يجب أن يرد على الأولى فقط

### 5. إدارة النشر

#### 5.1 إعادة النشر

إذا قمت بتحديثات:

```bash
git add .
git commit -m "Update: improve OCR accuracy"
git push origin main
```

Railway سيعيد النشر تلقائياً.

#### 5.2 تحديث المتغيرات

1. في Railway، اختر "Variables"
2. عدّل المتغير
3. انقر "Deploy"

#### 5.3 إيقاف البوت

في Railway:

1. اضغط على المشروع
2. انقر الزر الأحمر "Delete Service"

## استكشاف الأخطاء

### الخطأ: `Build failed`

**الحل:**
1. شاهد Build Logs
2. تأكد من أن `requirements.txt` صحيح
3. تأكد من أن `Dockerfile` موجود

### الخطأ: `Bot doesn't respond`

**الحل:**
1. تحقق من `TELEGRAM_BOT_TOKEN` صحيح
2. تأكد من تعطيل Privacy Mode
3. تحقق من Deploy Logs في Railway

### الخطأ: `OCR errors`

**الحل:**
- Railway يثبت Tesseract تلقائياً من Dockerfile
- لا تحتاج لفعل شيء إضافي

## مراقبة الأداء

### مشاهدة الـ Logs الحية

في Railway:

1. اختر المشروع
2. انقر "Logs"
3. شاهد الرسائل الحية

### الرسائل المتوقعة

```
Starting MSISDN Extraction Bot...
Processing photo in chat -1001234567890, message 123, user 456
Valid MSISDN extracted: *** (masked for logging)
Reply sent successfully to message 123
```

## أفضل الممارسات

✅ **استخدم متغيرات البيئة** - لا تضع التوكن في الكود
✅ **فعّل اللوجينج** - لمراقبة النشاط
✅ **اختبر قبل الدفع** - جرّب محلياً أولاً
✅ **احتفظ بنسخة احتياطية** - احفظ التوكن في مكان آمن
✅ **راقب الـ Logs** - لاكتشاف المشاكل مبكراً

## التكاليف

Railway توفر:
- **$5/شهر** لكل project
- حد أقصى 20 deployments مجانياً
- بوت MSISDN يعمل طول الوقت بكفاءة

## الدعم

- توثيق Railway: https://docs.railway.app
- توثيق python-telegram-bot: https://python-telegram-bot.readthedocs.io

---

**آخر تحديث:** 2026-10-28
