# ⚡ دليل البدء السريع

## 🚀 **تشغيل البوت في 5 دقائق**

### 1️⃣ **تحميل الكود**
```bash
git clone https://github.com/7r6t/Discord_song_bot.git
cd Discord_song_bot
```

### 2️⃣ **تثبيت المتطلبات**
```bash
pip install -r requirements.txt
```

### 3️⃣ **إعداد Discord Bot**
1. اذهب إلى [Discord Developer Portal](https://discord.com/developers/applications)
2. أنشئ تطبيق جديد
3. اذهب إلى قسم "Bot"
4. انسخ التوكن

### 4️⃣ **إعداد التوكن**
```bash
export DISCORD_TOKEN="your_bot_token_here"
```

### 5️⃣ **تشغيل البوت**
```bash
python main.py
```

## 🐳 **استخدام Docker (أسرع)**

### **بناء وتشغيل:**
```bash
docker build -t discord-bot .
docker run -e DISCORD_TOKEN="your_token" discord-bot
```

### **أو باستخدام Docker Compose:**
```bash
docker-compose up --build
```

## 🔧 **إعدادات سريعة**

### **ملف config.py:**
```python
DISCORD_TOKEN = "your_bot_token_here"
BOT_PREFIX = ""
BOT_STATUS = "🎵 استمع للموسيقى"
```

### **متغيرات البيئة:**
```bash
export DISCORD_TOKEN="your_token"
export PYTHONUNBUFFERED=1
export PYTHONHTTPSVERIFY=0
```

## 📋 **الأوامر الأساسية**

| الأمر | الوصف |
|-------|--------|
| `ش despacito` | تشغيل أغنية |
| `س` | تخطي |
| `قف` | إيقاف |
| `تست` | اختبار البوت |

## 🚨 **حل المشاكل السريع**

### **Rate Limiting (429):**
- البوت يحل المشكلة تلقائياً
- انتظر 1-5 دقائق

### **YouTube Bot Detection:**
- أضف ملف `youtube_cookies.txt`
- اتبع [README_COOKIES.md](README_COOKIES.md)

### **SSL Errors:**
```bash
export PYTHONHTTPSVERIFY=0
```

## 🌐 **النشر على Render.com**

### **1. اربط GitHub بـ Render**
### **2. أضف متغيرات البيئة:**
- `DISCORD_TOKEN`
- `PYTHONUNBUFFERED=1`
- `PYTHONHTTPSVERIFY=0`

### **3. Build Command:**
```bash
pip install -r requirements.txt
```

### **4. Start Command:**
```bash
python main.py
```

## 📱 **إضافة البوت للسيرفر**

1. انسخ رابط الدعوة من Developer Portal
2. افتح الرابط في المتصفح
3. اختر السيرفر
4. تأكد من الصلاحيات

## 🔍 **اختبار البوت**

### **أوامر الاختبار:**
```
تست - اختبار البوت
يوتيوب - اختبار YouTube
صوت - اختبار الصوت
صلاحيات - فحص الصلاحيات
```

## 💡 **نصائح سريعة**

1. **استخدم Docker** للتشغيل السريع
2. **أضف Cookies** لتجنب مشاكل YouTube
3. **راقب السجلات** للتأكد من العمل
4. **استخدم Health Checks** على Render

## 🆘 **الدعم السريع**

### **المشاكل الشائعة:**
- [Rate Limiting](README.md#-مشكلة-rate-limiting-429-too-many-requests)
- [YouTube Cookies](README_COOKIES.md)
- [Render Setup](RENDER_SETUP.md)

### **أوامر التشخيص:**
```
تست - اختبار شامل
يوتيوب - اختبار YouTube
كوكيز - اختبار Cookies
```

---

**🎯 البوت جاهز للعمل في 5 دقائق!** 