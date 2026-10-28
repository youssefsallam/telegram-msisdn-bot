# استكشاف الأخطاء والمشاكل

دليل شامل لحل جميع المشاكل المحتملة.

## 🔴 البوت لا يرد على الصور

### المشكلة: البوت لا يستجيب نهائياً

**الأسباب المحتملة:**

#### 1️⃣ التوكن خاطئ أو غير مفعّل
```bash
# تحقق من التوكن
echo $TELEGRAM_BOT_TOKEN
# يجب أن يظهر شيء مثل: 1234567890:ABCDefGhIjKlMnOpQrStUvWxYz
```

**الحل:**
- احصل على توكن جديد من `@BotFather`
- تأكد من نسخه بشكل صحيح (بدون مسافات)
- أضفه في `.env`:
  ```
  TELEGRAM_BOT_TOKEN=your_exact_token_here
  ```
- أعد تشغيل البوت

#### 2️⃣ Privacy Mode مفعّل
البوت لا يستطيع قراءة رسائل الجروب إذا كان Privacy Mode مفعّلاً.

**الحل:**
1. اذهب إلى `@BotFather`
2. أرسل `/setprivacy`
3. اختر البوت الخاص بك
4. اختر `Disabled`

**التحقق:**
```
✅ BotFather يقول: "Privacy mode is disabled"
```

#### 3️⃣ البوت ليس إداري في الجروب
البوت يحتاج لصلاحيات لإرسال الرسائل.

**الحل:**
1. افتح الجروب
2. اضغط على اسم الجروب
3. اختر "Administrators"
4. أضف البوت كمدير
5. أعطه الصلاحيات:
   - ✅ Send Messages
   - ✅ Delete Messages
   - ✅ Edit Messages

#### 4️⃣ Chat ID خاطئ أو غير مسموح
```
ALLOWED_CHAT_IDS=wrong_id_here
```

**الحل:**
- اتركه فارغاً لقبول جميع الجروبات مؤقتاً
- اتبع [GET_CHAT_ID.md](GET_CHAT_ID.md) لمعرفة الـ Chat ID الصحيح

#### 5️⃣ البوت معطّل أو متوقف
```bash
# على Railway
railway logs | grep ERROR

# محلياً
python main.py
# شاهد الأخطاء
```

**الحل:** شاهل الـ logs وابحث عن رسائل الخطأ

---

## 🔴 البوت يرد لكن بشكل خاطئ

### المشكلة: البوت يرد بـ "None" أو أرقام غلط

**السبب:** OCR لم يستطع قراءة الصورة بشكل صحيح.

**الحل:**
1. تأكد من جودة الصورة (واضحة وليست مشوشة)
2. تأكد من أن النص يقول `MSISDN is:` بالضبط
3. تأكد من أن الرقم مكتمل (11 رقم)

### المشكلة: البوت يرد على صور غير صحيحة

**السبب:** قد يكون النمط regex غير دقيق.

**الحل:**
عدّل pattern في `ocr_processor.py`:
```python
MSISDN_PATTERN = r"MSISDN\s*is\s*[:=]?\s*(\d+)"
```

أضف اختبار:
```bash
python test_bot.py
```

---

## 🔴 أخطاء OCR و Tesseract

### المشكلة: `Tesseract not found`

```
Error: tesseract is not installed
```

**الحل:**

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
1. اذهب إلى https://github.com/UB-Mannheim/tesseract/wiki
2. حمّل `tesseract-ocr-w64-setup-*.exe`
3. ثبّت البرنامج (اختر المسار الافتراضي)
4. أضف للمسار (PATH):
   ```
   C:\Program Files\Tesseract-OCR
   ```
5. أعد تشغيل الكمبيوتر

**التحقق:**
```bash
tesseract --version
# يجب أن يظهر إصدار Tesseract
```

### المشكلة: `pytesseract not installed`

```
ModuleNotFoundError: No module named 'pytesseract'
```

**الحل:**
```bash
pip install pytesseract
```

### المشكلة: OCR بطيء جداً

**السبب:** معالجة صور عالية الدقة.

**الحل:**
عدّل `ocr_processor.py`:
```python
# ضغط الصورة قبل المعالجة
image.thumbnail((1280, 720))
```

---

## 🔴 مشاكل Docker والنشر

### المشكلة: `Build failed`

```
ERROR: failed to solve with frontend dockerfile.v0
```

**الحل:**
```bash
# تحقق من Dockerfile
docker build -t test . --no-cache

# شاهل الخطأ الفعلي
```

### المشكلة: البوت معطّل على Railway

```
Error: Bot failed to start
```

**الحل:**
1. اذهب إلى Railway Dashboard
2. اختر المشروع
3. شاهد "Logs"
4. ابحث عن السطر الأول من الخطأ

### المشكلة: متغيرات البيئة لا تعمل

```
TELEGRAM_BOT_TOKEN not set
```

**الحل:**
1. في Railway: اضغط على "Variables"
2. تأكد من اسم المتغير صحيح:
   ```
   TELEGRAM_BOT_TOKEN
   ```
3. تأكد من القيمة صحيحة (بدون علامات)
4. اضغط "Save Configuration"
5. اضغط "Redeploy"

---

## 🔴 مشاكل Git والنشر

### المشكلة: `fatal: not a git repository`

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/username/repo.git
git push -u origin main
```

### المشكلة: Token معروض في Git

```bash
# افعل هذا فوراً!
git rm --cached .env
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"
git push

# غيّر التوكن على Telegram!
```

---

## 🟡 مشاكل الأداء والموارد

### المشكلة: البوت بطيء أو معطّل

**الأسباب:**
- معالجة صور كبيرة جداً
- عدة صور في نفس الوقت
- مشكلة في الذاكرة

**الحل:**
```python
# في main.py
import gc
gc.collect()  # تحرير الذاكرة بعد معالجة كل صورة
```

### المشكلة: استهلاك الذاكرة عالي

**الحل:**
```bash
# شاهل استهلاك الذاكرة
docker stats

# إعادة تشغيل:
docker restart container_id
```

---

## 🟡 مشاكل الشبكة والـ API

### المشكلة: `Connection timeout`

```
Error: Connection timed out
```

**الحل:**
- تحقق من الإنترنت
- تحقق من جدران النار
- أعد تشغيل البوت

### المشكلة: `Rate Limited`

```
429: Too Many Requests
```

**الحل:**
البوت سيحاول مرة أخرى تلقائياً.
أو أبطئ معدل الطلبات:

```python
await asyncio.sleep(1)  # انتظر 1 ثانية
```

---

## 🟢 الحالات الطبيعية (ليست أخطاء)

### ✅ "No MSISDN found"

هذا طبيعي! معنى أن الصورة لا تحتوي على `MSISDN is`.
البوت يتجاهلها كما هو متوقع.

### ✅ "Message already processed"

البوت رأى نفس الرسالة سابقاً.
لا يرسل نسخة مكررة. وهذا صحيح!

### ✅ "Image preprocessing failed"

الصورة منخفضة الجودة.
البوت سيحاول بدون معالجة مسبقة.

---

## 📋 قائمة التحقق

استخدم هذه القائمة لحل 90% من المشاكل:

- [ ] التوكن صحيح ومثبت في `.env`
- [ ] Privacy Mode معطّل
- [ ] البوت إداري في الجروب
- [ ] Chat ID صحيح (أو فارغ)
- [ ] Tesseract مثبت وعامل
- [ ] المشروع يعمل محلياً بدون أخطاء
- [ ] جميع الاختبارات تنجح: `python test_bot.py`
- [ ] متغيرات البيئة صحيحة على Railway
- [ ] الـ Logs لا تحتوي على أخطاء حمراء

---

## 🆘 الحصول على المساعدة

إذا لم يحل شيء من هنا:

1. **اقرأ الـ Logs بعناية:**
   ```bash
   # Railway
   railway logs
   
   # Docker
   docker logs -f container_id
   
   # محلياً
   python main.py
   ```

2. **شغّل الاختبارات:**
   ```bash
   python test_bot.py
   ```

3. **اقرأ التوثيق:**
   - [README.md](README.md) - عام
   - [QUICKSTART.md](QUICKSTART.md) - سريع
   - [DEPLOYMENT.md](DEPLOYMENT.md) - النشر
   - [GET_CHAT_ID.md](GET_CHAT_ID.md) - Chat ID

4. **تحقق من:**
   - [توثيق python-telegram-bot](https://python-telegram-bot.readthedocs.io)
   - [توثيق Railway](https://docs.railway.app)

---

**آخر تحديث:** 2026-10-28

**النسخة:** 1.0.0
