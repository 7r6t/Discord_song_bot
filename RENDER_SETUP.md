# 🚀 دليل النشر على Render.com

## 📋 المتطلبات

- حساب على [Render.com](https://render.com)
- مستودع GitHub يحتوي على الكود
- توكن Discord Bot

## 🔧 الخطوات

### 1️⃣ **إنشاء حساب Render**

1. اذهب إلى [render.com](https://render.com)
2. انقر على "Get Started"
3. سجل دخول باستخدام GitHub

### 2️⃣ **ربط GitHub**

1. في لوحة التحكم، انقر على "New +"
2. اختر "Web Service"
3. اربط حساب GitHub
4. اختر المستودع `7r6t/Discord_song_bot`

### 3️⃣ **إعداد الخدمة**

#### **معلومات أساسية:**
- **Name:** `discord-music-bot` (أو أي اسم تريده)
- **Environment:** `Python 3`
- **Region:** اختر الأقرب لك
- **Branch:** `main`

#### **Build Command:**
```bash
pip install -r requirements.txt
```

#### **Start Command:**
```bash
python main.py
```

### 4️⃣ **متغيرات البيئة**

أضف هذه المتغيرات في قسم "Environment Variables":

| المتغير | القيمة | الوصف |
|---------|--------|--------|
| `DISCORD_TOKEN` | `your_bot_token_here` | توكن Discord Bot |
| `PYTHONUNBUFFERED` | `1` | عرض السجلات مباشرة |
| `PYTHONHTTPSVERIFY` | `0` | إصلاح مشكلة SSL |

### 5️⃣ **إعدادات متقدمة**

#### **Health Check Path:**
```
/health
```

#### **Auto-Deploy:**
✅ فعّل "Auto-Deploy from Push"

## 🐳 **استخدام Docker (مُوصى به)**

### **Build Command:**
```bash
docker build -t discord-bot .
```

### **Start Command:**
```bash
docker run -p 8080:8080 discord-bot
```

### **مميزات Docker:**
- ✅ Health Checks تلقائية
- ✅ إدارة الموارد المحسنة
- ✅ نظام السجلات المحسن
- ✅ إعادة التشغيل التلقائي

## 🔍 **اختبار النشر**

### 1️⃣ **تحقق من البناء:**
- انتظر حتى ينتهي البناء
- تأكد من عدم وجود أخطاء

### 2️⃣ **تحقق من التشغيل:**
- انتظر حتى تظهر رسالة "Live"
- اذهب إلى الرابط المُنشأ

### 3️⃣ **اختبار البوت:**
- أضف البوت إلى سيرفر Discord
- جرب الأمر `تست`

## 🚨 **حل المشاكل**

### **مشكلة Rate Limiting (429):**
```
discord.errors.HTTPException: 429 Too Many Requests
```

**الحل:**
- البوت يتعامل تلقائياً مع هذه المشكلة
- انتظر 1-5 دقائق
- البوت سيعيد المحاولة تلقائياً

### **مشكلة SSL:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**الحل:**
- تأكد من إضافة `PYTHONHTTPSVERIFY=0`
- أعد تشغيل الخدمة

### **مشكلة YouTube:**
```
Sign in to confirm you're not a bot
```

**الحل:**
- أضف ملف `youtube_cookies.txt`
- اتبع دليل [README_COOKIES.md](README_COOKIES.md)

## 📊 **مراقبة الأداء**

### **Logs:**
- اذهب إلى "Logs" في لوحة التحكم
- راقب الأخطاء والتحذيرات

### **Metrics:**
- راقب استخدام CPU والذاكرة
- تأكد من عدم تجاوز الحدود

### **Health Checks:**
- تأكد من أن Health Check يعمل
- البوت يرسل ping كل 5 دقائق

## 🔄 **التحديثات**

### **تحديث تلقائي:**
- عند رفع كود جديد إلى GitHub
- Render سيعيد البناء تلقائياً

### **تحديث يدوي:**
- اذهب إلى "Manual Deploy"
- اختر "Deploy latest commit"

## 💰 **التكلفة**

### **Free Tier:**
- ✅ 750 ساعة شهرياً
- ✅ 512 MB RAM
- ✅ 0.1 CPU
- ✅ 1 GB Storage

### **Paid Plans:**
- من $7/شهر
- موارد أكبر
- دعم أفضل

## 🎯 **نصائح مهمة**

1. **استخدم Free Tier** للتجربة
2. **راقب السجلات** بانتظام
3. **أضف Health Checks** للتأكد من عمل البوت
4. **استخدم متغيرات البيئة** للبيانات الحساسة
5. **أعد تشغيل الخدمة** عند الحاجة

## 🔗 **روابط مفيدة**

- [Render Dashboard](https://dashboard.render.com)
- [Discord Developer Portal](https://discord.com/developers/applications)
- [GitHub Repository](https://github.com/7r6t/Discord_song_bot)

---

**ملاحظة:** تأكد من اتباع شروط خدمة Render.com وDiscord.