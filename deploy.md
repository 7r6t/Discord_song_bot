# 🚀 دليل النشر على Render.com

## 📋 المتطلبات الأساسية

1. حساب على [GitHub](https://github.com)
2. حساب على [Render.com](https://render.com)
3. بوت Discord مُنشأ

## 🔧 الخطوات التفصيلية

### 1. إنشاء بوت Discord

#### أ. الذهاب إلى Discord Developer Portal
1. اذهب إلى [Discord Developer Portal](https://discord.com/developers/applications)
2. سجل دخول بحساب Discord الخاص بك

#### ب. إنشاء تطبيق جديد
1. انقر على "New Application"
2. أدخل اسم للتطبيق (مثال: "Music Bot")
3. انقر على "Create"

#### ج. إعداد البوت
1. في القائمة الجانبية، انقر على "Bot"
2. انقر على "Add Bot"
3. انقر على "Yes, do it!"

#### د. تكوين البوت
1. في قسم "Bot"، فعّل الخيارات التالية:
   - ✅ Message Content Intent
   - ✅ Server Members Intent
   - ✅ Presence Intent

2. انسخ رمز البوت (Token) - ستحتاجه لاحقاً

#### هـ. إنشاء رابط الدعوة
1. اذهب إلى "OAuth2" > "URL Generator"
2. في Scopes، اختر:
   - ✅ bot
3. في Bot Permissions، اختر:
   - ✅ Send Messages
   - ✅ Use Slash Commands
   - ✅ Connect
   - ✅ Speak
   - ✅ Use Voice Activity
   - ✅ Read Message History
4. انسخ الرابط المُنشأ

#### و. دعوة البوت
1. افتح الرابط المُنسخ في المتصفح
2. اختر السيرفر الذي تريد إضافة البوت إليه
3. انقر على "Authorize"

### 2. رفع الكود إلى GitHub

#### أ. إنشاء مستودع جديد
1. اذهب إلى [GitHub](https://github.com)
2. انقر على "New repository"
3. أدخل اسم المستودع (مثال: "discord-music-bot")
4. اختر "Public" أو "Private"
5. انقر على "Create repository"

#### ب. رفع الكود
```bash
# استنساخ المستودع
git clone https://github.com/username/discord-music-bot.git
cd discord-music-bot

# إضافة الملفات
git add .
git commit -m "Initial commit: Discord Music Bot"
git push origin main
```

### 3. النشر على Render.com

#### أ. إنشاء حساب
1. اذهب إلى [Render.com](https://render.com)
2. انقر على "Get Started"
3. سجل دخول بحساب GitHub

#### ب. إنشاء خدمة جديدة
1. في لوحة التحكم، انقر على "New +"
2. اختر "Web Service"
3. اربط GitHub واختر المستودع

#### ج. تكوين الخدمة
1. **Name**: `discord-music-bot` (أو أي اسم تريده)
2. **Environment**: `Docker`
3. **Region**: اختر الأقرب لك
4. **Branch**: `main`
5. **Build Command**: `docker build -t discord-bot .`
6. **Start Command**: `python main.py`

#### د. إضافة المتغيرات البيئية
1. في قسم "Environment Variables"، أضف:
   - **Key**: `DISCORD_TOKEN`
   - **Value**: `your_bot_token_here` (استبدل برمز البوت الحقيقي)

#### هـ. إنشاء الخدمة
1. انقر على "Create Web Service"
2. انتظر حتى ينتهي البناء (قد يستغرق 5-10 دقائق)

### 4. اختبار البوت

#### أ. التحقق من الحالة
1. في Render.com، تأكد من أن الخدمة تعمل (Status: Live)
2. تحقق من Logs للتأكد من عدم وجود أخطاء

#### ب. اختبار الأوامر
1. اذهب إلى Discord
2. اكتب `تست` للتأكد من أن البوت يعمل
3. جرب الأوامر الأخرى

## 🚨 استكشاف الأخطاء الشائعة

### البوت لا يستجيب
- **الحل**: تأكد من تفعيل Message Content Intent
- **الحل**: تحقق من أن رمز البوت صحيح

### خطأ في البناء
- **الحل**: تحقق من Dockerfile
- **الحل**: تأكد من صحة requirements.txt

### لا يمكن تشغيل الصوت
- **الحل**: تأكد من صلاحيات البوت
- **الحل**: تحقق من وجود ffmpeg

### مشاكل في الاتصال
- **الحل**: تحقق من Logs في Render.com
- **الحل**: تأكد من صحة الكود

## 📊 مراقبة الأداء

### في Render.com
- **Logs**: مراقبة السجلات في الوقت الفعلي
- **Metrics**: مراقبة استخدام الموارد
- **Alerts**: إعداد تنبيهات للأخطاء

### في Discord
- **Status**: مراقبة حالة البوت
- **Commands**: تتبع استخدام الأوامر

## 🔄 التحديثات

### تحديث الكود
```bash
# تعديل الكود
git add .
git commit -m "Update: description"
git push origin main
```

### Render.com سيقوم بالتحديث تلقائياً

## 📞 الدعم

إذا واجهت مشاكل:
1. تحقق من Logs في Render.com
2. راجع README.md
3. تحقق من صحة التكوين
4. تأكد من صلاحيات البوت

---

**ملاحظة**: تأكد من اتباع شروط خدمة Discord وRender.com 