import os
import time
import threading
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# إعدادات Keep Alive
KEEP_ALIVE_URL = os.getenv('KEEP_ALIVE_URL', 'https://your-app-name.onrender.com')
PING_INTERVAL = 20  # ثانية

@app.route('/')
def home():
    """الصفحة الرئيسية"""
    return jsonify({
        "status": "online",
        "message": "Discord Music Bot is running!",
        "timestamp": time.time()
    })

@app.route('/ping')
def ping():
    """فحص حالة البوت"""
    return jsonify({
        "status": "pong",
        "timestamp": time.time()
    })

@app.route('/health')
def health():
    """فحص صحة البوت"""
    return jsonify({
        "status": "healthy",
        "uptime": time.time(),
        "version": "1.0.0"
    })

def keep_alive():
    """إرسال ping كل 30 ثانية لمنع الإغلاق"""
    while True:
        try:
            # إرسال ping للخادم
            response = requests.get(f"{KEEP_ALIVE_URL}/ping", timeout=10)
            if response.status_code == 200:
                print(f"✅ Keep Alive: {response.json()}")
            else:
                print(f"⚠️ Keep Alive: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Keep Alive Error: {e}")
        
        # انتظار قبل الإرسال التالي
        time.sleep(PING_INTERVAL)

def start_keep_alive():
    """بدء Keep Alive في خيط منفصل"""
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    print("🚀 Keep Alive started in background thread")
    return keep_alive_thread

if __name__ == '__main__':
    # بدء Keep Alive
    keep_alive_thread = start_keep_alive()
    
    # تشغيل Flask app
    port = int(os.getenv('PORT', 8080))
    print(f"🌐 Starting Flask app on port {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    ) 