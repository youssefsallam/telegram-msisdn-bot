# استخدام صورة Python رسمية
FROM python:3.11-slim

# تعيين متغير العمل
WORKDIR /app

# تثبيت Tesseract OCR وDependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-ara \
    tesseract-ocr-eng \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات
COPY requirements.txt .

# تثبيت Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملفات المشروع
COPY config.py .
COPY ocr_processor.py .
COPY main.py .

# جعل main.py قابل للتنفيذ
RUN chmod +x main.py

# تشغيل البوت
CMD ["python", "main.py"]
