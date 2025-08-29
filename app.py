#!/usr/bin/env python3
"""
Discord Music Bot - Railway Entry Point
This file is required by Railway to start the bot
"""

import subprocess
import sys
import os

def main():
    """Main entry point for Railway"""
    print("🚀 بدء Discord Music Bot...")
    print(f"📁 المجلد الحالي: {os.getcwd()}")
    print(f"📋 محتويات المجلد: {os.listdir('.')}")
    
    # تشغيل main.py
    try:
        result = subprocess.run([sys.executable, "main.py"], check=True)
        print(f"✅ تم تشغيل البوت بنجاح! Exit code: {result.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"❌ فشل في تشغيل البوت: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ ملف main.py غير موجود!")
        sys.exit(1)

if __name__ == "__main__":
    main()
