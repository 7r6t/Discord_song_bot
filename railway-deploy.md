# 🚀 دليل النشر السريع على Railway

## ⚡ النشر في 5 دقائق

### 1. ارفع الكود إلى GitHub
```bash
git add .
git commit -m "🚀 إعداد البوت للنشر على Railway"
git push origin main
```

### 2. اذهب إلى Railway
- [railway.app](https://railway.app)
- سجل دخول بـ GitHub

### 3. إنشاء مشروع جديد
- "New Project"
- "Deploy from GitHub repo"
- اختر المستودع

### 4. إضافة المتغيرات
في "Variables" أضف:
```
DISCORD_TOKEN=your_token_here
DISCORD_PREFIX=ش
```

### 5. انتظر البناء
- Railway سيبني البوت تلقائياً
- سترى "Deployment successful"

## 🎯 المميزات

✅ **نظام بناء محسن** - يستخدم nixpacks
✅ **FFmpeg مثبت تلقائياً** - لا حاجة لتثبيت يدوي
✅ **إعادة تشغيل تلقائي** - عند حدوث أخطاء
✅ **سجلات مفصلة** - لاستكشاف الأخطاء
✅ **عمل 24/7** - بدون انقطاع

## 🔧 الملفات المهمة

- `main.py` - الكود الرئيسي
- `nixpacks.toml` - إعدادات البناء
- `railway.json` - إعدادات Railway
- `railway-build.sh` - سكريبت البناء

## 🚨 استكشاف الأخطاء

### البناء فشل
- تحقق من `railway-build.sh`
- تأكد من صحة `requirements.txt`

### البوت لا يعمل
- تحقق من `DISCORD_TOKEN`
- تأكد من صلاحيات البوت

### لا يمكن تشغيل الصوت
- تأكد من وجود FFmpeg
- تحقق من صلاحيات البوت

## 📞 الدعم

إذا واجهت مشاكل:
1. تحقق من سجلات Railway
2. تأكد من صحة الملفات
3. راجع `railway-setup.md`

## 🎉 تم!

البوت الآن يعمل على Railway ويعزف الموسيقى!
