# 🚀 البدء السريع

## 1. تعديل التكوين
```bash
# افتح config.py وعدل رمز البوت
DISCORD_TOKEN = "your_bot_token_here"
```

## 2. تشغيل محلي
```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل البوت
python main.py
```

## 3. تشغيل بـ Docker
```bash
# بناء وتشغيل
docker-compose up --build
```

## 4. النشر على Render.com
1. ارفع الكود إلى GitHub
2. اربط بـ Render.com
3. أضف `DISCORD_TOKEN` في Environment Variables
4. انشر!

## 📋 الأوامر
- `ش اسم_الأغنية` - تشغيل
- `س` - تخطي
- `قف` - إيقاف
- `كرر` - تكرار
- `ا` - إيقاف التكرار
- `تست` - اختبار
- `شوي` - إيقاف مؤقت
- `كمل` - استئناف
- `صلاحيات` - فحص الصلاحيات
- `سيرفر` - فحص إعدادات السيرفر
- `صوت` - اختبار الاتصال الصوتي 