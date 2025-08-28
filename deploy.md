# 🚀 دليل النشر الشامل

## 📋 **الخيارات المتاحة**

### 1️⃣ **Render.com (مُوصى به للمبتدئين)**
- ✅ سهل الاستخدام
- ✅ Free Tier متاح
- ✅ تكامل مع GitHub
- ✅ إعادة نشر تلقائي

### 2️⃣ **Railway.app**
- ✅ سهل الاستخدام
- ✅ Free Tier متاح
- ✅ أداء جيد

### 3️⃣ **Heroku**
- ❌ لا يوجد Free Tier
- ✅ موثوق ومستقر
- ✅ أداء ممتاز

### 4️⃣ **VPS/خادم خاص**
- ✅ تحكم كامل
- ✅ أداء عالي
- ❌ يحتاج خبرة تقنية

## 🌐 **النشر على Render.com**

### **الخطوات:**

#### **1. إنشاء حساب:**
1. اذهب إلى [render.com](https://render.com)
2. سجل دخول باستخدام GitHub

#### **2. إنشاء خدمة جديدة:**
1. انقر على "New +"
2. اختر "Web Service"
3. اربط GitHub
4. اختر المستودع `7r6t/Discord_song_bot`

#### **3. إعدادات الخدمة:**
```
Name: discord-music-bot
Environment: Python 3
Region: Oregon (أسرع للشرق الأوسط)
Branch: main
```

#### **4. أوامر البناء والتشغيل:**
```bash
# Build Command
pip install -r requirements.txt

# Start Command
python main.py
```

#### **5. متغيرات البيئة:**
| المتغير | القيمة | الوصف |
|---------|--------|--------|
| `DISCORD_TOKEN` | `your_bot_token` | توكن Discord Bot |
| `PYTHONUNBUFFERED` | `1` | عرض السجلات |
| `PYTHONHTTPSVERIFY` | `0` | إصلاح SSL |

#### **6. إعدادات متقدمة:**
- ✅ Auto-Deploy from Push
- Health Check Path: `/health`
- Plan: Free

### **مميزات Render:**
- 🆓 Free Tier: 750 ساعة شهرياً
- 🔄 نشر تلقائي
- 📊 مراقبة الأداء
- 🐳 دعم Docker
- 🔍 Health Checks

## 🚂 **النشر على Railway.app**

### **الخطوات:**

#### **1. إنشاء حساب:**
1. اذهب إلى [railway.app](https://railway.app)
2. سجل دخول باستخدام GitHub

#### **2. إنشاء مشروع:**
1. انقر على "Start a New Project"
2. اختر "Deploy from GitHub repo"
3. اختر المستودع

#### **3. إعدادات الخدمة:**
```bash
# Build Command
pip install -r requirements.txt

# Start Command
python main.py
```

#### **4. متغيرات البيئة:**
```bash
DISCORD_TOKEN=your_bot_token
PYTHONUNBUFFERED=1
PYTHONHTTPSVERIFY=0
```

### **مميزات Railway:**
- 🆓 Free Tier: $5 شهرياً
- 🚀 نشر سريع
- 🔄 تحديث تلقائي
- 📱 تطبيق موبايل

## 🐳 **النشر باستخدام Docker**

### **ملف Dockerfile:**
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "-u", "main.py"]
```

### **ملف docker-compose.yml:**
```yaml
version: '3.8'
services:
  discord-bot:
    build: .
    restart: unless-stopped
    environment:
      - DISCORD_TOKEN=${DISCORD_TOKEN}
      - PYTHONUNBUFFERED=1
    ports:
      - "8080:8080"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 🖥️ **النشر على VPS**

### **الخطوات:**

#### **1. إعداد الخادم:**
```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Python و FFmpeg
sudo apt install python3 python3-pip ffmpeg -y

# تثبيت Git
sudo apt install git -y
```

#### **2. تحميل الكود:**
```bash
git clone https://github.com/7r6t/Discord_song_bot.git
cd Discord_song_bot
```

#### **3. تثبيت المتطلبات:**
```bash
pip3 install -r requirements.txt
```

#### **4. إعداد التوكن:**
```bash
export DISCORD_TOKEN="your_bot_token"
echo "export DISCORD_TOKEN='your_bot_token'" >> ~/.bashrc
```

#### **5. تشغيل البوت:**
```bash
python3 main.py
```

#### **6. استخدام Screen (للعمل في الخلفية):**
```bash
screen -S discord-bot
python3 main.py
# اضغط Ctrl+A ثم D للخروج
```

#### **7. العودة للجلسة:**
```bash
screen -r discord-bot
```

## 🔧 **إعدادات متقدمة**

### **Systemd Service (VPS):**
```ini
[Unit]
Description=Discord Music Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Discord_song_bot
Environment=DISCORD_TOKEN=your_bot_token
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### **تفعيل الخدمة:**
```bash
sudo systemctl enable discord-bot
sudo systemctl start discord-bot
sudo systemctl status discord-bot
```

## 📊 **مراقبة الأداء**

### **أوامر مفيدة:**
```bash
# مراقبة استخدام الموارد
htop

# مراقبة السجلات
tail -f logs/bot.log

# مراقبة العمليات
ps aux | grep python

# مراقبة الذاكرة
free -h
```

### **Health Checks:**
```bash
# اختبار البوت
curl http://localhost:8080/health

# اختبار Ping
curl http://localhost:8080/ping
```

## 🚨 **حل المشاكل**

### **مشكلة Rate Limiting:**
- البوت يحل المشكلة تلقائياً
- انتظر 1-5 دقائق
- استخدم خادم مختلف إذا استمرت المشكلة

### **مشكلة SSL:**
```bash
export PYTHONHTTPSVERIFY=0
```

### **مشكلة الذاكرة:**
- راقب استخدام الذاكرة
- أعد تشغيل البوت عند الحاجة
- استخدم swap إذا لزم الأمر

## 💰 **التكلفة المقارنة**

| المنصة | Free Tier | Paid Plans | الصعوبة |
|--------|-----------|------------|---------|
| Render | ✅ 750 ساعة | $7+/شهر | ⭐ |
| Railway | ✅ $5/شهر | $20+/شهر | ⭐⭐ |
| Heroku | ❌ | $7+/شهر | ⭐⭐ |
| VPS | ❌ | $5+/شهر | ⭐⭐⭐⭐ |

## 🎯 **التوصيات**

### **للمبتدئين:**
- استخدم **Render.com** - سهل ومجاني

### **للمتوسطين:**
- استخدم **Railway.app** - سريع وموثوق

### **للمتقدمين:**
- استخدم **VPS** - تحكم كامل وأداء عالي

---

**🚀 اختر المنصة المناسبة لك وابدأ النشر!** 