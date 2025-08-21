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

# تثبيت المتطلبات
echo "📦 تثبيت المتطلبات..."
pip3 install -r requirements.txt

# تشغيل البوت
echo "🚀 تشغيل البوت..."
python3 main.py 