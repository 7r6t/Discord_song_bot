# ملف التكوين للبوت (اختياري)
# يمكنك استخدام متغيرات البيئة بدلاً من هذا الملف

# DISCORD_TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"
# BOT_PREFIX = ""
# BOT_STATUS = "🎵 استمع للموسيقى"

# ملاحظة: البوت يقرأ التوكن من متغيرات البيئة DISCORD_TOKEN 

# إعدادات Rate Limiting
RATE_LIMIT_RETRIES = 5
RATE_LIMIT_BASE_DELAY = 60  # ثانية
RATE_LIMIT_MAX_DELAY = 300  # 5 دقائق

# إعدادات Discord.py
DISCORD_MAX_RETRIES = 3
DISCORD_RETRY_AFTER = 1.0
DISCORD_RATE_LIMIT_STRATEGY = "exponential"

# إعدادات Keep Alive
KEEP_ALIVE_INTERVAL = 300  # 5 دقائق
KEEP_ALIVE_URL = "https://fvq-songs.onrender.com"

# إعدادات المنفذ
PORT = 8080
HOST = "0.0.0.0" 