# 🎵 بوت Discord للموسيقى

بوت Discord بسيط لتشغيل الموسيقى مع أوامر عربية سهلة الاستخدام.

## ✨ المميزات

- 🎵 تشغيل الأغاني من YouTube
- ⏭️ تخطي الأغاني
- ⏸️ إيقاف مؤقت واستئناف
- 🔁 تكرار الأغاني
- 🛑 إيقاف البوت
- 🧪 اختبار البوت
- 🎨 واجهة جميلة مع Embeds

## 📋 الأوامر

| الأمر | الوصف |
|-------|--------|
| `ش اسم_الأغنية` | تشغيل أغنية (مثال: ش despacito) |
| `س` | تخطي الأغنية الحالية |
| `قف` | إيقاف البوت |
| `كرر` | تكرار الأغنية |
| `ا` | إيقاف التكرار |
| `تست` | اختبار البوت |
| `شوي` | إيقاف مؤقت للأغنية |
| `كمل` | استئناف الأغنية |
| `صلاحيات` | فحص صلاحيات البوت |
| `سيرفر` | فحص إعدادات السيرفر |
| `صوت` | اختبار الاتصال الصوتي |

## 🚀 التثبيت

### 1. إنشاء بوت Discord

1. اذهب إلى [Discord Developer Portal](https://discord.com/developers/applications)
2. انقر على "New Application"
3. أعطِ اسم للتطبيق
4. اذهب إلى قسم "Bot"
5. انقر على "Add Bot"
6. انسخ رمز البوت (Token)

### 2. إعداد البوت

1. في قسم "Bot"، فعّل الخيارات التالية:
   - Message Content Intent
   - Server Members Intent
   - Presence Intent

2. في قسم "OAuth2 > URL Generator":
   - اختر "bot" من Scopes
   - اختر الصلاحيات التالية:
     - Send Messages
     - Use Slash Commands
     - Connect
     - Speak
     - Use Voice Activity

### 3. دعوة البوت

انسخ الرابط المُنشأ وافتحه في المتصفح، ثم اختر السيرفر الذي تريد إضافة البوت إليه.

## ⚙️ التكوين

1. افتح ملف `config.py`
2. استبدل `your_discord_bot_token_here` برمز البوت الخاص بك

```python
DISCORD_TOKEN = "your_actual_bot_token_here"
```

## 🐳 النشر على Render.com

### الطريقة الأولى: استخدام Docker

1. ارفع الكود إلى GitHub
2. اربط GitHub بـ Render.com
3. اختر "New Web Service"
4. اختر المستودع
5. Render سيقوم ببناء وتشغيل البوت تلقائياً

### الطريقة الثانية: النشر المباشر

1. في Render.com، اختر "New Web Service"
2. اربط GitHub
3. اختر المستودع
4. في Environment Variables، أضف:
   - `DISCORD_TOKEN`: رمز البوت الخاص بك
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `python main.py`

## 📁 هيكل الملفات

```
├── main.py              # الكود الرئيسي للبوت
├── config.py            # ملف التكوين
├── requirements.txt     # المكتبات المطلوبة
├── Dockerfile          # ملف Docker
├── render.yaml         # تكوين Render.com
└── README.md           # هذا الملف
```

## 🔧 المتطلبات

- Python 3.8+
- discord.py
- yt-dlp
- PyNaCl
- ffmpeg

## 🚨 استكشاف الأخطاء

### البوت لا يستجيب
- تأكد من أن رمز البوت صحيح
- تأكد من تفعيل Message Content Intent

### لا يمكن تشغيل الصوت
- تأكد من أن البوت لديه صلاحية "Connect" و "Speak"
- تأكد من وجود ffmpeg

### مشاكل في البحث
- تأكد من أن yt-dlp محدث
- تحقق من اتصال الإنترنت

## 📝 ملاحظات

- البوت يحتاج إلى ffmpeg مثبت على النظام
- تأكد من أن البوت لديه الصلاحيات المطلوبة في السيرفر
- البوت يدعم تشغيل أغنية واحدة في كل سيرفر في نفس الوقت

## 🤝 المساهمة

نرحب بالمساهمات! يرجى إنشاء Issue أو Pull Request.

## 📄 الرخصة

هذا المشروع مفتوح المصدر ومتاح للجميع.

---

**ملاحظة**: تأكد من اتباع شروط خدمة Discord وYouTube عند استخدام هذا البوت. 