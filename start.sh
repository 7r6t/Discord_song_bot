#!/bin/bash

echo "🚀 Starting Discord Bot Setup..."

# تثبيت المكتبات
echo "📦 Installing dependencies..."
pip install --user --break-system-packages -r requirements.txt

# التحقق من تثبيت المكتبات
echo "🔍 Checking installed packages..."
pip list --user

# تشغيل البوت
echo "🎵 Starting Discord Bot..."
python main.py
