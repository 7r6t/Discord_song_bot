#!/bin/bash

echo "🚀 بدء بناء Discord Music Bot على Railway..."

# تحديث pip
echo "📦 تحديث pip..."
pip install --upgrade pip

# تثبيت المتطلبات
echo "📦 تثبيت المتطلبات..."
pip install -r requirements.txt

# التحقق من تثبيت FFmpeg
echo "🔧 التحقق من FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg مثبت"
    ffmpeg -version | head -n 1
else
    echo "❌ FFmpeg غير مثبت - سيتم تثبيته..."
    # Railway يستخدم nixpacks الذي يثبت FFmpeg تلقائياً
fi

# التحقق من Python
echo "🐍 التحقق من Python..."
python --version

echo "✅ تم الانتهاء من البناء!"
echo "🎵 البوت جاهز للتشغيل!"
