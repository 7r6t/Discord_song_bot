# 🔐 حل مشكلة YouTube Cookies

## 🚨 المشكلة

YouTube يكتشف البوت ويطلب تسجيل الدخول مع رسالة:
> "Sign in to confirm you're not a bot"

## 🔧 الحلول

### 1️⃣ **اختبار Cookies الحالية**

استخدم الأمر:
```
كوكيز
```

هذا الأمر يختبر إذا كانت Cookies تعمل.

### 2️⃣ **إنشاء Cookies جديدة (محلياً فقط)**

استخدم الأمر:
```
كوكيز_جديد
```

**⚠️ ملاحظة مهمة:** هذا الأمر يعمل **محلياً فقط** لأنه يحتاج إلى Chrome مثبت.

### 3️⃣ **إنشاء Cookies يدوياً (مُوصى به)**

#### الخطوات:

1. **ثبت Extension:**
   - اذهب إلى [Chrome Web Store](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid)
   - ابحث عن "Get cookies.txt"
   - ثبت Extension

2. **اذهب إلى YouTube:**
   - تأكد من تسجيل دخولك
   - استخدم حساب شخصي (ليس حساب عمل)

3. **استخرج Cookies:**
   - انقر على Extension
   - اختر "Export"
   - احفظ الملف كـ `youtube_cookies.txt`

4. **ضع الملف في مجلد المشروع:**
   ```
   📁 مشروع_البوت/
   ├── main.py
   ├── youtube_cookies.txt  ← ضع الملف هنا
   └── ...
   ```

## 🚀 **للنشر على Render.com**

### ❌ **لا تستخدم:**
```
كوكيز_جديد
```

### ✅ **استخدم:**
الطريقة الثالثة (يدوياً) - أنشئ Cookies محلياً ثم ارفع الملف.

## 📝 **ملف Cookies المثال**

يوجد ملف `youtube_cookies_example.txt` في المستودع:

```txt
# Netscape HTTP Cookie File
# https://curl.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.

.youtube.com	TRUE	/	FALSE	1735689600	[YOUR_COOKIE_VALUE]
```

**استبدل:**
- `[YOUR_COOKIE_VALUE]` بالقيم الحقيقية من Extension

## 🔄 **تحديث Cookies**

### متى تحدث:
- كل 30-60 يوم
- عند ظهور رسالة "Sign in to confirm you're not a bot"
- عند تغيير كلمة المرور

### كيفية التحديث:
1. اتبع الخطوات أعلاه
2. استبدل الملف القديم
3. أعد تشغيل البوت

## 🚨 **استكشاف الأخطاء**

### Cookies لا تعمل:
- تأكد من تسجيل دخولك في YouTube
- استخدم حساب شخصي
- تأكد من صحة تنسيق الملف

### Extension لا يعمل:
- تأكد من تثبيت Extension
- أعد تشغيل Chrome
- جرب Extension آخر

### البوت لا يقرأ Cookies:
- تأكد من اسم الملف: `youtube_cookies.txt`
- تأكد من مكان الملف (نفس مجلد `main.py`)
- تحقق من صلاحيات الملف

## 💡 **نصائح مهمة**

1. **استخدم حساب شخصي** - لا تستخدم حساب عمل
2. **لا تشارك Cookies** - احتفظ بها سرية
3. **حدث Cookies بانتظام** - كل 30-60 يوم
4. **احتفظ بنسخة احتياطية** - من Cookies العاملة

## 🔗 **روابط مفيدة**

- [Get cookies.txt Extension](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid)
- [YouTube](https://www.youtube.com)
- [Discord Developer Portal](https://discord.com/developers/applications)

---

**ملاحظة:** تأكد من اتباع شروط خدمة YouTube عند استخدام Cookies. 