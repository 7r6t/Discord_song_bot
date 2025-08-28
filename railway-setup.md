# 🚀 دليل النشر على Railway

## 📋 المتطلبات

1. حساب GitHub
2. حساب Discord Developer
3. Discord Bot Token

## 🔧 الخطوات

### 1. إنشاء Discord Bot

1. اذهب إلى [Discord Developer Portal](https://discord.com/developers/applications)
2. اضغط على "New Application"
3. أعطِ اسم للتطبيق (مثال: "Music Bot")
4. اذهب إلى قسم "Bot"
5. اضغط على "Add Bot"
6. انسخ Token (ستحتاجه لاحقاً)

### 2. إعداد صلاحيات البوت

في قسم "Bot"، فعّل:
- ✅ Message Content Intent
- ✅ Server Members Intent
- ✅ Presence Intent

في قسم "OAuth2 > URL Generator":
- اختر "bot" من Scopes
- اختر الصلاحيات:
  - ✅ Send Messages
  - ✅ Use Slash Commands
  - ✅ Connect
  - ✅ Speak
  - ✅ Use Voice Activity

### 3. دعوة البوت للسيرفر

انسخ الرابط المُنشأ وافتحه في المتصفح، ثم اختر السيرفر.

### 4. النشر على Railway

1. اذهب إلى [railway.app](https://railway.app)
2. سجل دخول باستخدام GitHub
3. اضغط على "New Project"
4. اختر "Deploy from GitHub repo"
5. اختر هذا المستودع
6. انتظر حتى ينتهي البناء

### 5. إعداد المتغيرات البيئية

في Railway، اذهب إلى "Variables" وأضف:

```
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_PREFIX=ش
```

### 6. تشغيل البوت

- Railway سيقوم بتشغيل البوت تلقائياً
- البوت سيعمل على مدار 24/7
- يمكنك رؤية السجلات في قسم "Deployments"

## 🎮 اختبار البوت

1. اذهب إلى السيرفر
2. اكتب `ش أوامر` لرؤية الأوامر
3. اذهب إلى قناة صوتية
4. اكتب `ش despacito` لتشغيل أغنية

## 🔍 استكشاف الأخطاء

### البوت لا يستجيب
- تأكد من صحة DISCORD_TOKEN
- تأكد من تفعيل Message Content Intent

### لا يمكن تشغيل الصوت
- تأكد من صلاحيات البوت
- تأكد من وجود البوت في قناة صوتية

### مشاكل في النشر
- تحقق من السجلات في Railway
- تأكد من صحة الملفات

## 📞 الدعم

إذا واجهت مشاكل:
1. تحقق من السجلات في Railway
2. تأكد من صحة Discord Token
3. تأكد من صلاحيات البوت
4. تأكد من وجود البوت في السيرفر

## 🎉 تم!

البوت الآن يعمل على Railway ويمكنه تشغيل الموسيقى من YouTube و SoundCloud!
