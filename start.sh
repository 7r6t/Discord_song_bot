#!/bin/bash

echo "🎵 بدء تشغيل بوت Discord للموسيقى..."

# التحقق من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 غير مثبت!"
    exit 1
fi

# التحقق من وجود ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ ffmpeg غير مثبت!"
    echo "📥 قم بتثبيت ffmpeg أولاً"
    exit 1
fi

# إنشاء مجلد السجلات
mkdir -p logs

# تعيين متغيرات البيئة
export PYTHONUNBUFFERED=1
export PYTHONHTTPSVERIFY=0
export PORT=8080

# تثبيت المتطلبات
echo "📦 تثبيت المتطلبات..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# تشغيل البوت مع إعادة المحاولة
echo "🚀 تشغيل البوت..."
max_attempts=5
attempt=1

while [ $attempt -le $max_attempts ]; do
    echo "🔄 محاولة $attempt من $max_attempts"
    
    if python3 main.py; then
        echo "✅ البوت يعمل بنجاح!"
        break
    else
        echo "❌ فشل في تشغيل البوت"
        
        if [ $attempt -lt $max_attempts ]; then
            delay=$((60 * attempt))  # تأخير متزايد
            echo "⏳ انتظار $delay ثانية قبل إعادة المحاولة..."
            sleep $delay
        else
            echo "💥 فشلت جميع المحاولات!"
            exit 1
        fi
    fi
    
    attempt=$((attempt + 1))
done 