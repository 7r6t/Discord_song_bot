# 🎵 إعداد Discord Music Bot على Render

## خطوات الإعداد السريع:

### 1. إنشاء الخدمة في Render:
1. اذهب إلى [render.com](https://render.com)
2. اضغط "New" → "Web Service"
3. اربط مستودع GitHub الخاص بك
4. اختر الفرع `main`

### 2. إعدادات الخدمة:
```
Name: fvq-songs-bot
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: python main.py
```

### 3. متغيرات البيئة المطلوبة:
اذهب إلى Environment Variables وأضف:

```
DISCORD_TOKEN = your_discord_bot_token_here
PORT = 8080
KEEP_ALIVE_URL = https://fvq-songs-bot.onrender.com/ping
RENDER_SERVICE_NAME = fvq-songs-bot
```

### 4. إعدادات إضافية:
- **Auto Deploy**: مفعل
- **Health Check Path**: `/health`
- **Region**: Oregon (أسرع للشرق الأوسط)

## 🔧 ميزات Keep Alive المحسنة:

### ✅ Ping تلقائي كل 25 ثانية
### ✅ مراقبة Uptime والإحصائيات
### ✅ إعادة محاولة تلقائية عند الأخطاء
### ✅ صفحة ويب تُظهر حالة البوت
### ✅ API endpoints للمراقبة

## 📊 مراقبة البوت:

### الروابط المهمة:
- **الصفحة الرئيسية**: `https://your-app-name.onrender.com/`
- **صحة البوت**: `https://your-app-name.onrender.com/health`
- **Ping**: `https://your-app-name.onrender.com/ping`

### الـ Logs:
ستجد في logs الرسائل التالية:
```
🚀 بدء Keep Alive محسن لـ Render...
🔄 Keep Alive #1: البوت يعمل... [12:34:56]
✅ Local ping: 200
✅ Auto Render ping: 200
📊 Keep Alive Stats: 10 pings, 4 minutes uptime
```

## 🚨 استكشاف الأخطاء:

### إذا كان البوت لا يعمل:
1. تحقق من أن `DISCORD_TOKEN` صحيح
2. تحقق من Logs في Render
3. تأكد من أن البوت له صلاحيات في Discord

### إذا كان Keep Alive لا يعمل:
1. تحقق من أن `KEEP_ALIVE_URL` صحيح
2. تأكد من أن الخدمة تستجيب على `/ping`
3. راجع الـ logs للأخطاء

## 💡 نصائح للحصول على أفضل أداء:

### 1. استخدم Free Tier بحكمة:
- الخدمة المجانية تنام بعد 15 دقيقة من عدم النشاط
- Keep Alive يمنع النوم بـ ping كل 25 ثانية

### 2. مراقبة الاستخدام:
- تحقق من logs بانتظام
- راقب uptime من صفحة `/health`

### 3. إعدادات محسنة:
- الخدمة تعيد تشغيل نفسها عند الأخطاء
- timeout محسن لتجنب الانقطاع

## 🎵 الأوامر المتاحة:

```
ش [اسم الأغنية] - تشغيل أغنية
وقف - إيقاف التشغيل
تكرار - تكرار الأغنية الحالية
اضافة [اسم الأغنية] - إضافة للقائمة
قائمة - عرض قائمة التشغيل
مسح - مسح القائمة
اوامر - عرض جميع الأوامر
```

## 🔄 التحديث التلقائي:

عند push إلى GitHub، Render سيعيد تشغيل البوت تلقائياً.

---

**✅ البوت جاهز للعمل 24/7 على Render!**