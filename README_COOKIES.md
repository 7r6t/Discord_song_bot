# 🔐 دليل إعداد Cookies لـ YouTube

## 📋 المشكلة
YouTube يكتشف البوت ويطلب تسجيل الدخول للتأكد من أنه ليس بوت.

### ⚠️ مشكلة Render.com
على Render.com، لا يوجد متصفح Chrome مثبت، لذا البوت لا يستطيع الوصول لـ cookies من المتصفح.

**الخطأ:**
```
ERROR: could not find chrome cookies database in "/root/.config/google-chrome"
```

## ✅ الحل: استخدام Cookies من ملف

### الطريقة الأولى: ملف cookies (مفضل)
البوت يستخدم ملف `youtube_cookies.txt` مع cookies صحيحة.

**المتطلبات:**
1. متصفح Chrome مثبت على جهازك
2. تسجيل الدخول في YouTube
3. تصدير cookies وحفظها في الملف

### الطريقة الثانية: يدوي
إنشاء ملف `youtube_cookies.txt` يدوياً.

## 🔧 كيفية إعداد Cookies

### 1. تسجيل الدخول في YouTube
- افتح Chrome
- اذهب إلى [youtube.com](https://youtube.com)
- سجل دخول بحسابك

### 2. تصدير Cookies
#### باستخدام Extension:
1. ثبت [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid)
2. اذهب إلى YouTube
3. انقر على Extension
4. انقر "Export"
5. احفظ الملف كـ `youtube_cookies.txt`

#### باستخدام Python:
```bash
pip install browser-cookie3
python -c "import browser_cookie3; browser_cookie3.chrome(domain_name='.youtube.com').save('youtube_cookies.txt')"
```

### 3. وضع الملف في مجلد البوت
```
fvq-songs/
├── main.py
├── youtube_cookies.txt  ← ضع الملف هنا
├── requirements.txt
└── ...
```

## 🚀 تشغيل البوت

### محلياً:
```bash
python main.py
```

### على Render.com:
1. اربط المستودع
2. أضف متغيرات البيئة
3. البوت سيعمل تلقائياً

## 📝 ملاحظات مهمة

- **لا تشارك ملف cookies** مع أحد
- **أعد إنشاء cookies** كل فترة
- **استخدم حساب شخصي** وليس حساب عمل
- **تأكد من تسجيل الدخول** في Chrome

## 🆘 إذا لم تعمل Cookies

### جرب هذه الحلول:
1. **أعد تسجيل الدخول** في YouTube
2. **امسح cookies** وأعد إنشاءها
3. **استخدم متصفح آخر** (Firefox, Edge)
4. **جرب البحث مرة أخرى** (البوت يحاول طرق بديلة)

### أوامر الاختبار:
```
يوتيوب - اختبار الاتصال بـ YouTube
تست - اختبار البوت
```

## 📞 الدعم
إذا استمرت المشكلة، جرب:
1. استخدام رابط مباشر بدلاً من البحث
2. انتظار قليل ثم المحاولة مرة أخرى
3. التأكد من أن YouTube متاح في بلدك 