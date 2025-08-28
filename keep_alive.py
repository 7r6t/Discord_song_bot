import os
import time
import threading
import requests
from flask import Flask, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# إعدادات Keep Alive المحسنة
KEEP_ALIVE_URL = os.getenv('KEEP_ALIVE_URL', 'https://discord-music-bot.onrender.com')
PING_INTERVAL = int(os.getenv('KEEP_ALIVE_INTERVAL', 300))  # 5 دقائق افتراضياً
RENDER_SERVICE_NAME = os.getenv('RENDER_SERVICE_NAME', 'discord-music-bot')
PORT = int(os.getenv('PORT', 8080))

# إحصائيات Keep Alive
keep_alive_stats = {
    'start_time': time.time(),
    'ping_count': 0,
    'success_count': 0,
    'error_count': 0,
    'last_ping': None,
    'last_error': None
}

@app.route('/')
def home():
    """الصفحة الرئيسية مع معلومات البوت"""
    uptime = time.time() - keep_alive_stats['start_time']
    uptime_str = str(timedelta(seconds=int(uptime)))
    
    return jsonify({
        "status": "online",
        "message": "🎵 Discord Music Bot is running!",
        "service": RENDER_SERVICE_NAME,
        "uptime": uptime_str,
        "ping_count": keep_alive_stats['ping_count'],
        "success_rate": f"{(keep_alive_stats['success_count'] / max(keep_alive_stats['ping_count'], 1)) * 100:.1f}%",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    })

@app.route('/ping')
def ping():
    """فحص حالة البوت"""
    keep_alive_stats['ping_count'] += 1
    keep_alive_stats['last_ping'] = time.time()
    
    return jsonify({
        "status": "pong",
        "message": "🏓 Bot is alive and responding!",
        "ping_count": keep_alive_stats['ping_count'],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """فحص صحة البوت مع معلومات مفصلة"""
    uptime = time.time() - keep_alive_stats['start_time']
    uptime_str = str(timedelta(seconds=int(uptime)))
    
    # حساب معدل النجاح
    success_rate = (keep_alive_stats['success_count'] / max(keep_alive_stats['ping_count'], 1)) * 100
    
    # تقييم الصحة
    if success_rate >= 90:
        health_status = "excellent"
        health_color = "🟢"
    elif success_rate >= 75:
        health_status = "good"
        health_color = "🟡"
    else:
        health_status = "poor"
        health_color = "🔴"
    
    return jsonify({
        "status": "healthy",
        "health_level": health_status,
        "health_icon": health_color,
        "uptime": uptime_str,
        "ping_count": keep_alive_stats['ping_count'],
        "success_count": keep_alive_stats['success_count'],
        "error_count": keep_alive_stats['error_count'],
        "success_rate": f"{success_rate:.1f}%",
        "last_ping": datetime.fromtimestamp(keep_alive_stats['last_ping']).isoformat() if keep_alive_stats['last_ping'] else None,
        "last_error": datetime.fromtimestamp(keep_alive_stats['last_error']).isoformat() if keep_alive_stats['last_error'] else None,
        "service": RENDER_SERVICE_NAME,
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/stats')
def stats():
    """إحصائيات مفصلة للبوت"""
    uptime = time.time() - keep_alive_stats['start_time']
    
    return jsonify({
        "keep_alive_stats": keep_alive_stats,
        "system_info": {
            "platform": os.name,
            "python_version": os.sys.version,
            "environment": os.getenv('ENVIRONMENT', 'production'),
            "render_service": RENDER_SERVICE_NAME,
            "port": PORT
        },
        "uptime_seconds": int(uptime),
        "uptime_formatted": str(timedelta(seconds=int(uptime))),
        "timestamp": datetime.now().isoformat()
    })

def keep_alive():
    """إرسال ping كل فترة محددة لمنع الإغلاق"""
    while True:
        try:
            # إرسال ping للخادم
            response = requests.get(f"{KEEP_ALIVE_URL}/ping", timeout=10)
            if response.status_code == 200:
                keep_alive_stats['success_count'] += 1
                print(f"✅ Keep Alive #{keep_alive_stats['ping_count']}: البوت يعمل... [{datetime.now().strftime('%H:%M:%S')}]")
            else:
                keep_alive_stats['error_count'] += 1
                print(f"⚠️ Keep Alive #{keep_alive_stats['ping_count']}: Status {response.status_code}")
        except Exception as e:
            keep_alive_stats['error_count'] += 1
            keep_alive_stats['last_error'] = time.time()
            print(f"❌ Keep Alive #{keep_alive_stats['ping_count']}: Error - {e}")
        
        # انتظار قبل الإرسال التالي
        time.sleep(PING_INTERVAL)

def start_keep_alive():
    """بدء Keep Alive في خيط منفصل"""
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    
    print(f"🚀 بدء Keep Alive محسن لـ Render...")
    print(f"🔧 إعدادات Keep Alive:")
    print(f"   📍 URL: {KEEP_ALIVE_URL}")
    print(f"   ⏰ الفاصل: {PING_INTERVAL} ثانية")
    print(f"   🏷️ اسم الخدمة: {RENDER_SERVICE_NAME}")
    print(f"   🌐 المنفذ: {PORT}")
    
    return keep_alive_thread

if __name__ == '__main__':
    # بدء Keep Alive
    keep_alive_thread = start_keep_alive()
    
    # تشغيل Flask app
    print(f"🌐 بدء Flask app على المنفذ {PORT}")
    
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=False,
        threaded=True
    ) 