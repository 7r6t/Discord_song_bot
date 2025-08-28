import discord
from discord.ext import commands
import asyncio
import yt_dlp
import os
import ssl
import threading
import time
import requests
import json
from flask import Flask, jsonify

# قراءة التوكن من متغيرات البيئة أو من config.py
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN') or 'YOUR_DISCORD_BOT_TOKEN_HERE'
BOT_STATUS = "🎵 استمع للموسيقى"

# إصلاح مشكلة SSL
os.environ['PYTHONHTTPSVERIFY'] = '0'
ssl._create_default_https_context = ssl._create_unverified_context

# إعداد البوت
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='', intents=intents)

# إعدادات Discord.py محسنة لتجنب Rate Limiting
bot.http.rate_limit_strategy = "exponential"  # استراتيجية تأخير متزايد
bot.http.max_retries = 3  # عدد المحاولات الأقصى
bot.http.retry_after = 1.0  # تأخير أساسي بين المحاولات

# متغيرات عامة
voice_clients = {}
music_queues = {}  # قوائم التشغيل لكل سيرفر

# إعدادات yt-dlp محسنة لتجنب YouTube bot detection
yt_dl_opts = {
    'format': 'bestaudio[ext=mp3]/bestaudio[ext=m4a]/bestaudio[ext=wav]/bestaudio/best',
    'extractaudio': False,  # لا نستخرج الصوت
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': False,
    'no_warnings': False,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'no_check_certificate': True,
    'prefer_insecure': True,
    'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'cookiesfrombrowser': None,
    'extractor_args': {
        'youtube': {
            'skip': ['dash', 'live', 'hls'],
            'player_client': ['android', 'web', 'tv', 'ios'],
            'player_skip': ['webpage', 'configs'],
            'innertube_host': 'www.youtube.com',
            'innertube_key': 'AIzaSyA8eiZmM1FaDVjRy-df2KTyQ_vz_yYM39w'
        },
        'soundcloud': {
            'format': 'bestaudio[ext=mp3]/bestaudio[ext=m4a]/bestaudio[ext=wav]/bestaudio[abr>=192]/bestaudio[abr>=128]/bestaudio'
        }
    },
    'geo_bypass': True,
    'geo_bypass_country': 'US',
    'geo_bypass_ip_block': '1.1.1.1/24',
    'force_generic_extractor': False,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Sec-Fetch-Mode': 'navigate',
        'Dnt': '1',
        'Upgrade-Insecure-Requests': '1',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'https://www.youtube.com/',
        'Origin': 'https://www.youtube.com/'
    },
    'extractor_retries': 5,
    'fragment_retries': 5,
    'retries': 5,
    'sleep_interval': 1,
    'max_sleep_interval': 5,
    'sleep_interval_requests': 1,
    'socket_timeout': 30,
    'max_downloads': 1,
    'prefer_ffmpeg': False,  # لا نستخدم FFmpeg للاستخراج
    'postprocessors': [],  # لا نستخدم postprocessors
    'writesubtitles': False,
    'writeautomaticsub': False,
    'skip_download': True,
    'http_chunk_size': 10485760,
    'extract_flat': True,
    'verbose': False,
    'no_check_cookies': True,
    'mark_watched': False,
    'writeinfojson': False,
    'compat_opts': set()
}

# إعدادات FFmpeg محسنة لـ SoundCloud و YouTube
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -protocol_whitelist file,http,https,tcp,tls,crypto',
    'options': '-vn -filter:a "volume=1.0,highpass=f=50,lowpass=f=8000,equalizer=f=1000:width_type=o:width=2:g=-5,equalizer=f=3000:width_type=o:width=2:g=3,equalizer=f=5000:width_type=o:width=2:g=5,aresample=48000"'
}

# Flask app للـ Keep Alive محسن لـ Render
app = Flask(__name__)

@app.route('/')
def home():
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    uptime = time.time() - start_time if 'start_time' in globals() else 0
    return f"""
    <html>
    <head><title>Discord Music Bot - Running</title></head>
    <body style="font-family: Arial; text-align: center; margin-top: 50px;">
        <h1>🎵 Discord Music Bot is Running!</h1>
        <p><strong>Status:</strong> ✅ Active</p>
        <p><strong>Current Time:</strong> {current_time}</p>
        <p><strong>Uptime:</strong> {int(uptime/60)} minutes</p>
        <p><strong>Bot:</strong> fvq songs</p>
        <hr>
        <p style="color: green;">Keep Alive is working properly!</p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    uptime = time.time() - start_time if 'start_time' in globals() else 0
    return jsonify({
        "status": "healthy", 
        "bot": "running",
        "service": "fvq-songs-discord-bot",
        "timestamp": current_time,
        "uptime_minutes": int(uptime/60),
        "keep_alive": "active"
    })

@app.route('/ping')
def ping():
    return jsonify({"pong": True, "timestamp": time.time()})

# متغير لتتبع وقت البداية
start_time = time.time()

def start_web_server():
    """تشغيل الخادم الويب في خيط منفصل - محسن لـ Render"""
    try:
        port = int(os.environ.get("PORT", 8080))
        print(f"🌐 بدء الخادم الويب على المنفذ {port}...")
        print(f"🔗 الرابط: https://your-app-name.onrender.com")
        
        # إعدادات محسنة للخادم
        app.run(
            host="0.0.0.0", 
            port=port, 
            debug=False, 
            threaded=True,
            use_reloader=False,  # مهم لـ Render
            processes=1  # عملية واحدة فقط
        )
    except Exception as e:
        print(f"❌ فشل في بدء الخادم الويب: {e}")
        import traceback
        traceback.print_exc()

def start_keep_alive():
    """تشغيل Keep Alive محسن لـ Render"""
    def keep_alive():
        print("🚀 بدء Keep Alive محسن لـ Render...")
        ping_count = 0
        
        while True:
            try:
                # انتظار أقصر لمنع النوم
                time.sleep(25)  # كل 25 ثانية
                ping_count += 1
                current_time = time.strftime("%H:%M:%S")
                
                print(f"🔄 Keep Alive #{ping_count}: البوت يعمل... [{current_time}]")
                
                # محاولة ping للخادم المحلي أولاً
                try:
                    port = int(os.environ.get("PORT", 8080))
                    local_url = f"http://localhost:{port}/ping"
                    response = requests.get(local_url, timeout=3)
                    print(f"✅ Local ping: {response.status_code}")
                except Exception as local_e:
                    print(f"⚠️ Local ping failed: {local_e}")
                
                # محاولة ping للـ KEEP_ALIVE_URL إذا كان موجود
                keep_alive_url = os.environ.get("KEEP_ALIVE_URL")
                if keep_alive_url:
                    try:
                        response = requests.get(keep_alive_url, timeout=5)
                        print(f"✅ External Keep Alive ping: {response.status_code}")
                    except Exception as e:
                        print(f"❌ External Keep Alive ping failed: {e}")
                else:
                    # إنشاء URL تلقائي للـ Render
                    render_app_name = os.environ.get("RENDER_SERVICE_NAME")
                    if render_app_name:
                        auto_url = f"https://{render_app_name}.onrender.com/ping"
                        try:
                            response = requests.get(auto_url, timeout=5)
                            print(f"✅ Auto Render ping: {response.status_code}")
                        except Exception as e:
                            print(f"❌ Auto Render ping failed: {e}")
                    else:
                        print("ℹ️ KEEP_ALIVE_URL و RENDER_SERVICE_NAME غير محددين")
                
                # إحصائيات إضافية كل 10 pings
                if ping_count % 10 == 0:
                    uptime = time.time() - start_time
                    print(f"📊 Keep Alive Stats: {ping_count} pings, {int(uptime/60)} minutes uptime")
                    
            except Exception as e:
                print(f"❌ خطأ في Keep Alive: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(10)  # انتظار أطول عند الخطأ
    
    try:
        thread = threading.Thread(target=keep_alive, daemon=True, name="KeepAlive-Enhanced")
        thread.start()
        print("✅ Keep Alive Enhanced thread بدأ بنجاح")
    except Exception as e:
        print(f"❌ فشل في بدء Keep Alive: {e}")
        import traceback
        traceback.print_exc()

@bot.event
async def on_ready():
    print(f'✅ البوت متصل: {bot.user}')
    await bot.change_presence(activity=discord.Game(name=BOT_STATUS))
    
    print("🚀 بدء الخدمات...")
    
    # بدء Keep Alive
    try:
        start_keep_alive()
        print("✅ Keep Alive بدأ بنجاح")
    except Exception as e:
        print(f"❌ فشل في بدء Keep Alive: {e}")
    
    # بدء الخادم الويب
    try:
        web_thread = threading.Thread(target=start_web_server, daemon=True, name="WebServer")
        web_thread.start()
        print("✅ الخادم الويب بدأ بنجاح")
    except Exception as e:
        print(f"❌ فشل في بدء الخادم الويب: {e}")
    
    print("🎉 جميع الخدمات بدأت بنجاح!")

@bot.event
async def on_error(event, *args, **kwargs):
    if event == 'on_voice_state_update':
        print(f"خطأ في voice_state_update: {args}")
    else:
        print(f"خطأ في الحدث {event}: {args}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # أمر تشغيل الأغنية
    if message.content.startswith('ش'):
        await play_song(message)
        return

    # أمر تخطي الأغنية
    if message.content == 'س':
        await skip_song(message)
        return

    # أمر إيقاف البوت
    if message.content == 'قف':
        await stop_bot(message)
        return

    # أمر تكرار الأغنية
    if message.content == 'كرر':
        await loop_song(message)
        return

    # أمر إيقاف التكرار
    if message.content == 'ا':
        await stop_loop(message)
        return

    # أمر إضافة أغنية للقائمة
    if message.content.startswith('ضف'):
        await add_to_queue(message)
        return

    # أمر عرض القائمة
    if message.content == 'قائمة':
        await show_queue(message)
        return

    # أمر مسح القائمة
    if message.content == 'مسح':
        await clear_queue(message)
        return

    # أمر عرض الأوامر
    if message.content == 'اوامر':
        await show_commands(message)
        return

    # أمر اختبار البوت
    if message.content == 'تست':
        await test_bot(message)
        return

    # أمر إيقاف مؤقت
    if message.content == 'شوي':
        await pause_song(message)
        return

    # أمر استئناف التشغيل
    if message.content == 'كمل':
        await resume_song(message)
        return

    # أمر فحص الصلاحيات
    if message.content == 'صلاحيات':
        await check_permissions(message)
        return
        
    # أمر فحص السيرفر
    if message.content == 'سيرفر':
        await check_server_settings(message)
        return
        
    # أمر اختبار الاتصال الصوتي
    if message.content == 'صوت':
        await test_voice_connection(message)
        return
        
    # أمر اختبار YouTube
    if message.content == 'يوتيوب':
        await test_youtube_connection(message)
        return
        
    # أمر اختبار Cookies
    if message.content == 'كوكيز':
        await test_cookies(message)
        return

async def play_song(message):
    """تشغيل الأغنية مع timeout محسن"""
    try:
        # التحقق من وجود المستخدم في قناة صوتية
        if not message.author.voice:
            await message.channel.send("❌ يجب أن تكون في قناة صوتية!")
            return

        voice_channel = message.author.voice.channel
        guild_id = message.guild.id
        
        # التحقق من صلاحيات البوت
        bot_member = message.guild.get_member(bot.user.id)
        if not bot_member.guild_permissions.connect or not bot_member.guild_permissions.speak:
            await message.channel.send("❌ البوت يحتاج صلاحيات 'Connect' و 'Speak'!")
            return
            
        # فصل اسم الأغنية أو الرابط
        if len(message.content) < 2:
            await message.channel.send("❌ يرجى كتابة اسم الأغنية أو الرابط! مثال: ش despacito أو ش https://youtube.com/...")
            return
        
        song_input = message.content[1:].strip()
        if not song_input:
            await message.channel.send("❌ يرجى كتابة اسم الأغنية أو الرابط!")
            return

        # التحقق من نوع المدخل (رابط أم اسم)
        is_url = song_input.startswith(('http://', 'https://', 'www.', 'youtube.com', 'youtu.be', 'soundcloud.com'))
        
        if is_url:
            # إذا كان رابط، استخدمه مباشرة
            song_name = song_input
            await message.channel.send(f"🔗 جاري تشغيل الرابط المباشر: {song_name[:50]}...")
        else:
            # إذا كان اسم، ابحث عنه
            song_name = song_input

        # البحث مع timeout قصير
        video_info = None
        url = None
        title = "أغنية"
        duration = 0

        try:
            # إعدادات بحث محسنة
            fast_opts = yt_dl_opts.copy()
            fast_opts['socket_timeout'] = 20  # timeout أطول للبحث
            fast_opts['retries'] = 3  # محاولات أكثر للنجاح
            fast_opts['extract_flat'] = False
            fast_opts['skip_download'] = True
            fast_opts['sleep_interval'] = 1  # انتظار قصير بين الطلبات
            fast_opts['max_sleep_interval'] = 3  # انتظار أقصى قصير
            fast_opts['sleep_interval_requests'] = 1  # انتظار قصير بين الطلبات
            fast_opts['format'] = 'bestaudio[ext=mp3]/bestaudio[ext=m4a]/bestaudio[ext=wav]/bestaudio[abr>=192]/bestaudio[abr>=128]/bestaudio'

            # البحث أو تشغيل الرابط المباشر
            if is_url:
                # إذا كان رابط، استخدمه مباشرة
                url_embed = discord.Embed(
                    title="🔗 تشغيل الرابط المباشر",
                    description=f"**{song_name[:50]}...**",
                    color=0x00ff00
                )
                url_embed.add_field(name="⏱️ الوقت المتوقع", value="10 ثواني", inline=True)
                url_embed.add_field(name="🌐 المصدر", value="رابط مباشر", inline=True)
                await message.channel.send(embed=url_embed)
                
                try:
                    # استخراج معلومات الرابط المباشر
                    video_info = await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(
                            None, 
                            get_direct_url_info, song_name
                        ),
                        timeout=10  # timeout أطول للروابط
                    )
                    
                    # التحقق من أن video_info موجود وصحيح
                    if not video_info:
                        error_embed = discord.Embed(
                            title="❌ فشل في الحصول على معلومات الرابط",
                            description="لم يتم العثور على معلومات صحيحة",
                            color=0xff0000
                        )
                        error_embed.add_field(name="💡 نصائح", value="• تأكد من أن الرابط صحيح\n• جرب رابط آخر\n• تأكد من أن الرابط متاح", inline=False)
                        await message.channel.send(embed=error_embed)
                        return
                    
                    # التحقق من وجود URL
                    if 'url' not in video_info or not video_info['url']:
                        error_embed = discord.Embed(
                            title="❌ فشل في الحصول على رابط الصوت",
                            description="الرابط غير متوفر أو غير صحيح",
                            color=0xff0000
                        )
                        error_embed.add_field(name="🔍 معلومات", value=f"المحتوى: {str(video_info)[:200]}...", inline=False)
                        await message.channel.send(embed=error_embed)
                        return
                    
                    # استخراج المعلومات
                    url = video_info['url']
                    title = video_info.get('title', 'أغنية')
                    duration = video_info.get('duration', 0)
                    
                    # طباعة معلومات التشخيص
                    print(f"✅ معلومات الأغنية:")
                    print(f"   العنوان: {title}")
                    print(f"   الرابط: {url}")
                    print(f"   المدة: {duration}")
                    print(f"   المصدر: {video_info.get('extractor', 'غير معروف')}")
                    
                except asyncio.TimeoutError:
                    timeout_embed = discord.Embed(
                        title="⏰ انتهت مهلة استخراج الرابط",
                        description="استخراج الرابط استغرق أكثر من 10 ثواني",
                        color=0xff9900
                    )
                    await message.channel.send(embed=timeout_embed)
                    return
            else:
                # رسالة بحث مختصرة
                await message.channel.send(f"🔍 جاري البحث عن: **{song_name}**...")
                
                try:
                    # البحث في SoundCloud
                    video_info = await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(
                            None, 
                            search_youtube, song_name, fast_opts
                        ),
                        timeout=15  # timeout أطول للبحث
                    )
                except asyncio.TimeoutError:
                    timeout_embed = discord.Embed(
                        title="⏰ انتهت مهلة البحث",
                        description="البحث استغرق أكثر من 15 ثانية",
                        color=0xff9900
                    )
                    timeout_embed.add_field(name="💡 نصيحة", value="جرب مرة أخرى بكلمات مختلفة أو انتظر قليلاً", inline=False)
                    await message.channel.send(embed=timeout_embed)
                    return
                
                # التحقق من أن video_info موجود وصحيح
                if not video_info:
                    error_embed = discord.Embed(
                        title="❌ فشل في الحصول على معلومات الأغنية",
                        description="لم يتم العثور على معلومات صحيحة",
                        color=0xff0000
                    )
                    if is_url:
                        error_embed.add_field(name="💡 نصائح", value="• تأكد من أن الرابط صحيح\n• جرب رابط آخر\n• تأكد من أن الرابط متاح", inline=False)
                    else:
                        error_embed.add_field(name="💡 نصائح", value="• تأكد من كتابة اسم الأغنية بشكل صحيح\n• جرب كلمات مختلفة\n• تأكد من وجود اتصال إنترنت", inline=False)
                    
                    await message.channel.send(embed=error_embed)
                    return
                
                # التحقق من وجود URL
                if 'url' not in video_info or not video_info['url']:
                    error_embed = discord.Embed(
                        title="❌ فشل في الحصول على رابط الصوت",
                        description="الرابط غير متوفر أو غير صحيح",
                        color=0xff0000
                    )
                    error_embed.add_field(name="🔍 معلومات", value=f"المحتوى: {str(video_info)[:200]}...", inline=False)
                    await message.channel.send(embed=error_embed)
                    return
                
                # استخراج المعلومات
                url = video_info['url']
                title = video_info.get('title', 'أغنية')
                duration = video_info.get('duration', 0)
                
                # طباعة معلومات التشخيص
                print(f"✅ معلومات الأغنية:")
                print(f"   العنوان: {title}")
                print(f"   الرابط: {url}")
                print(f"   المدة: {duration}")
                print(f"   المصدر: {video_info.get('extractor', 'غير معروف')}")
                
                # لا نرسل رسالة نجاح البحث - سنرسل رسالة واحدة فقط عند التشغيل
                
                    
        except Exception as e:
            await message.channel.send(f"❌ خطأ في البحث: {str(e)[:100]}...")
            return

        # الاتصال بالقناة الصوتية
        try:
            if guild_id in voice_clients:
                voice_client = voice_clients[guild_id]
                if voice_client.is_connected():
                    if voice_client.channel != voice_channel:
                        await voice_client.move_to(voice_channel)
                    else:
                        pass  # البوت متصل بالفعل
                else:
                    voice_client = await voice_channel.connect(timeout=10.0)
                    voice_clients[guild_id] = voice_client
            else:
                voice_client = await voice_channel.connect(timeout=10.0)
                voice_clients[guild_id] = voice_client
                
        except Exception as e:
            await message.channel.send(f"❌ خطأ في الاتصال: {str(e)}")
            return

        # تشغيل الأغنية
        try:
            if voice_client.is_playing():
                voice_client.stop()
            
            # التحقق من أن المتغيرات موجودة
            if 'url' not in locals() or not url:
                await message.channel.send("❌ خطأ: رابط الصوت غير متوفر!")
                return
                
            if 'title' not in locals() or not title:
                title = "أغنية"
                
            if 'duration' not in locals():
                duration = 0
                
            audio_source = discord.FFmpegPCMAudio(url, **ffmpeg_options)
            
            def after_playing(error):
                if error:
                    print(f"خطأ في التشغيل: {error}")
                else:
                    print("تم انتهاء الأغنية بنجاح")
                    # التحقق من التكرار
                    if hasattr(voice_client, 'loop_enabled') and voice_client.loop_enabled:
                        print("🔄 التكرار مفعل - إعادة تشغيل الأغنية")
                        # إعادة تشغيل الأغنية
                        try:
                            new_audio_source = discord.FFmpegPCMAudio(url, **ffmpeg_options)
                            voice_client.play(new_audio_source, after=after_playing)
                        except Exception as e:
                            print(f"❌ خطأ في إعادة التشغيل: {e}")
            
            voice_client.play(audio_source, after=after_playing)
            
            # رسالة تأكيد واحدة فقط
            try:
                if duration > 0:
                    duration_minutes = int(duration // 60)
                    duration_seconds = int(duration % 60)
                    duration_str = f"{duration_minutes}:{duration_seconds:02d}"
                else:
                    duration_str = "غير معروف"
            except:
                duration_str = "غير معروف"
                
            # رسالة تشغيل مختصرة
            await message.channel.send(f"🎵 **{title}** | ⏱️ {duration_str} | 👤 {message.author.mention}")
            
        except Exception as e:
            await message.channel.send(f"❌ خطأ في تشغيل الأغنية: {str(e)}")
            return

    except Exception as e:
        await message.channel.send(f"❌ خطأ عام في تشغيل الأغنية: {str(e)}")

def search_youtube(query, opts):
    """البحث في SoundCloud فقط - الحل النهائي"""
    try:
        print(f"🔍 البحث عن: {query}")
        
        # البحث في SoundCloud فقط (تجنب YouTube تماماً)
        print("🔍 البحث في SoundCloud...")
        sc_result = search_soundcloud(query)
        if sc_result:
            print(f"✅ تم العثور على SoundCloud: {sc_result.get('title', 'بدون عنوان')}")
            return sc_result
        else:
            print("❌ لا توجد نتائج في SoundCloud")
            return None
        
    except Exception as e:
        print(f"❌ خطأ عام في البحث: {e}")
        return None

def get_direct_url_info(url):
    """استخراج معلومات من رابط مباشر - الحل النهائي"""
    try:
        print(f"🔗 استخراج معلومات من: {url}")
        
        # إذا كان رابط YouTube، استخدم SoundCloud فقط
        if any(domain in url.lower() for domain in ['youtube.com', 'youtu.be', 'youtube']):
            print("⚠️ رابط YouTube - سيتم تجاهله لتجنب مشاكل Bot Detection")
            return None
        
        # إعدادات محسنة للروابط المباشرة (SoundCloud فقط)
        url_opts = {
            'format': 'bestaudio[ext=mp3]/bestaudio[ext=m4a]/bestaudio[ext=wav]/bestaudio[abr>=192]/bestaudio[abr>=128]/bestaudio',
            'quiet': False,  # لرؤية الأخطاء
            'no_warnings': False,  # لرؤية التحذيرات
            'extract_flat': False,
            'skip_download': True,
            'extractaudio': False
        }
        
        with yt_dlp.YoutubeDL(url_opts) as ydl:
            # استخراج معلومات الرابط
            info = ydl.extract_info(url, download=False)
            print(f"🔍 معلومات الرابط: {info}")
            
            if info and 'title' in info:
                # التحقق من أن URL ليس OPUS
                if 'url' in info:
                    url_check = info['url']
                    if any(ext in url_check.lower() for ext in ['.opus', '.ogg', 'opus', 'ogg']):
                        print("⚠️ تم تجاهل رابط OPUS/OGG")
                        return None
                
                print(f"✅ تم استخراج: {info.get('title', 'بدون عنوان')}")
                print(f"🔗 URL: {info.get('url', 'غير متوفر')}")
                print(f"📊 المدة: {info.get('duration', 'غير متوفر')}")
                return info
            else:
                print("❌ فشل في استخراج معلومات الرابط")
                print(f"🔍 المحتوى: {info}")
                return None
                
    except Exception as e:
        print(f"❌ خطأ في استخراج الرابط: {e}")
        return None

def search_soundcloud(query):
    """البحث في SoundCloud مباشرة"""
    try:
        print(f"🔍 البحث في SoundCloud: {query}")
        
        # استخدام yt-dlp للبحث في SoundCloud
        sc_opts = {
            'format': 'bestaudio[ext=mp3]/bestaudio[ext=m4a]/bestaudio[ext=wav]/bestaudio[abr>=192]/bestaudio[abr>=128]/bestaudio',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True
        }
        
        with yt_dlp.YoutubeDL(sc_opts) as ydl:
            # البحث في SoundCloud
            sc_query = f"scsearch:{query}"
            info = ydl.extract_info(sc_query, download=False)
            
            if info and 'entries' in info and info['entries']:
                first_result = info['entries'][0]
                
                # التحقق من أن النتيجة ليست OPUS
                if 'url' in first_result:
                    url = first_result['url']
                    if any(ext in url.lower() for ext in ['.opus', '.ogg', 'opus', 'ogg']):
                        print("⚠️ تم تجاهل نتيجة OPUS/OGG")
                        return None
                
                print(f"✅ SoundCloud: {first_result.get('title', 'بدون عنوان')}")
                return first_result
            else:
                print("❌ لا توجد نتائج في SoundCloud")
                return None
                
    except Exception as e:
        print(f"❌ خطأ في SoundCloud: {e}")
        return None

def search_youtube_api(query):
    """البحث باستخدام YouTube API مباشرة"""
    try:
        # استخدام YouTube Data API v3
        api_key = "AIzaSyA8eiZmM1FaDVjRy-df2KTyQ_vz_yYM39w"
        search_url = f"https://www.googleapis.com/youtube/v3/search"
        
        params = {
            'part': 'snippet',
            'q': query,
            'key': api_key,
            'maxResults': 1,
            'type': 'video'
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'items' in data and data['items']:
                video_id = data['items'][0]['id']['videoId']
                title = data['items'][0]['snippet']['title']
                
                # الحصول على معلومات الفيديو
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                # استخدام yt-dlp للحصول على معلومات التشغيل
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    try:
                        video_info = ydl.extract_info(video_url, download=False)
                        if video_info and 'url' in video_info:
                            return video_info
                    except:
                        pass
                
                # إنشاء معلومات بسيطة إذا فشل yt-dlp
                return {
                    'id': video_id,
                    'title': title,
                    'url': video_url,
                    'duration': 0,
                    'webpage_url': video_url
                }
        
        return None
        
    except Exception as e:
        print(f"❌ خطأ في YouTube API: {e}")
        return None

async def skip_song(message):
    """تخطي الأغنية الحالية"""
    try:
        guild_id = message.guild.id
        if guild_id in voice_clients and voice_clients[guild_id].is_playing():
            voice_clients[guild_id].stop()
            await message.channel.send("⏭️ تم تخطي الأغنية")
        else:
            await message.channel.send("❌ لا توجد أغنية قيد التشغيل!")
    except Exception as e:
        await message.channel.send(f"❌ خطأ في تخطي الأغنية: {str(e)}")

async def stop_bot(message):
    """إيقاف البوت وقطع الاتصال"""
    try:
        guild_id = message.guild.id
        if guild_id in voice_clients:
            voice_client = voice_clients[guild_id]
            if voice_client.is_connected():
                await voice_client.disconnect()
            del voice_clients[guild_id]
        await message.channel.send("⏹️ تم إيقاف البوت وقطع الاتصال")
    except Exception as e:
        await message.channel.send(f"❌ خطأ في إيقاف البوت: {str(e)}")

async def loop_song(message):
    """تكرار الأغنية"""
    try:
        guild_id = message.guild.id
        if guild_id in voice_clients and voice_clients[guild_id].is_playing():
            # تفعيل التكرار
            if not hasattr(voice_clients[guild_id], 'loop_enabled'):
                voice_clients[guild_id].loop_enabled = False
            
            voice_clients[guild_id].loop_enabled = True
            await message.channel.send("🔁 تم تفعيل تكرار الأغنية")
        else:
            await message.channel.send("❌ لا توجد أغنية قيد التشغيل!")
    except Exception as e:
        await message.channel.send(f"❌ خطأ في تفعيل التكرار: {str(e)}")

async def stop_loop(message):
    """إيقاف تكرار الأغنية"""
    try:
        guild_id = message.guild.id
        if guild_id in voice_clients:
            if hasattr(voice_clients[guild_id], 'loop_enabled'):
                voice_clients[guild_id].loop_enabled = False
                await message.channel.send("⏹️ تم إيقاف تكرار الأغنية")
            else:
                await message.channel.send("❌ التكرار غير مفعل أصلاً!")
        else:
            await message.channel.send("❌ البوت غير متصل!")
    except Exception as e:
        await message.channel.send(f"❌ خطأ في إيقاف التكرار: {str(e)}")

async def add_to_queue(message):
    """إضافة أغنية لقائمة التشغيل"""
    try:
        if not message.content.startswith('ضف '):
            await message.channel.send("❌ استخدم: ضف اسم_الأغنية")
            return
        
        song_name = message.content[3:].strip()
        if not song_name:
            await message.channel.send("❌ اكتب اسم الأغنية!")
            return
        
        guild_id = message.guild.id
        
        # البحث عن الأغنية
        await message.channel.send(f"🔍 جاري البحث عن: **{song_name}**...")
        
        try:
            video_info = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, 
                    search_youtube, song_name, yt_dl_opts
                ),
                timeout=15
            )
        except asyncio.TimeoutError:
            await message.channel.send("⏰ انتهت مهلة البحث")
            return
        
        if not video_info or 'url' not in video_info:
            await message.channel.send("❌ لم يتم العثور على الأغنية")
            return
        
        # إضافة الأغنية للقائمة
        if guild_id not in music_queues:
            music_queues[guild_id] = []
        
        song_data = {
            'title': video_info.get('title', 'أغنية'),
            'url': video_info['url'],
            'duration': video_info.get('duration', 0),
            'requester': message.author.mention
        }
        
        music_queues[guild_id].append(song_data)
        
        # رسالة تأكيد
        duration_str = "غير معروف"
        if song_data['duration'] > 0:
            duration_minutes = int(song_data['duration'] // 60)
            duration_seconds = int(song_data['duration'] % 60)
            duration_str = f"{duration_minutes}:{duration_seconds:02d}"
        
        await message.channel.send(f"✅ تمت الإضافة: **{song_data['title']}** | ⏱️ {duration_str} | 👤 {message.author.mention}")
        
        # إذا لم تكن هناك أغنية تعمل، ابدأ التشغيل
        if guild_id not in voice_clients or not voice_clients[guild_id].is_playing():
            await play_next_song(message.guild)
            
    except Exception as e:
        await message.channel.send(f"❌ خطأ في إضافة الأغنية: {str(e)}")

async def show_queue(message):
    """عرض قائمة التشغيل"""
    try:
        guild_id = message.guild.id
        
        if guild_id not in music_queues or not music_queues[guild_id]:
            await message.channel.send("📋 قائمة التشغيل فارغة")
            return
        
        queue = music_queues[guild_id]
        embed = discord.Embed(title="📋 قائمة التشغيل", color=0x0099ff)
        
        for i, song in enumerate(queue[:10], 1):  # عرض أول 10 أغاني
            duration_str = "غير معروف"
            if song['duration'] > 0:
                duration_minutes = int(song['duration'] // 60)
                duration_seconds = int(song['duration'] % 60)
                duration_str = f"{duration_minutes}:{duration_seconds:02d}"
            
            embed.add_field(
                name=f"{i}. {song['title']}",
                value=f"⏱️ {duration_str} | 👤 {song['requester']}",
                inline=False
            )
        
        if len(queue) > 10:
            embed.add_field(name="...", value=f"و {len(queue) - 10} أغنية أخرى", inline=False)
        
        await message.channel.send(embed=embed)
        
    except Exception as e:
        await message.channel.send(f"❌ خطأ في عرض القائمة: {str(e)}")

async def clear_queue(message):
    """مسح قائمة التشغيل"""
    try:
        guild_id = message.guild.id
        
        if guild_id in music_queues:
            music_queues[guild_id].clear()
            await message.channel.send("🗑️ تم مسح قائمة التشغيل")
        else:
            await message.channel.send("📋 قائمة التشغيل فارغة أصلاً")
            
    except Exception as e:
        await message.channel.send(f"❌ خطأ في مسح القائمة: {str(e)}")

async def play_next_song(guild):
    """تشغيل الأغنية التالية في القائمة"""
    try:
        guild_id = guild.id
        
        if guild_id not in music_queues or not music_queues[guild_id]:
            return
        
        if guild_id not in voice_clients or not voice_clients[guild_id].is_connected():
            return
        
        # أخذ الأغنية التالية
        song_data = music_queues[guild_id].pop(0)
        
        # تشغيل الأغنية
        voice_client = voice_clients[guild_id]
        
        if voice_client.is_playing():
            voice_client.stop()
        
        audio_source = discord.FFmpegPCMAudio(song_data['url'], **ffmpeg_options)
        
        def after_playing(error):
            if error:
                print(f"خطأ في التشغيل: {error}")
            else:
                print("تم انتهاء الأغنية بنجاح")
                # التحقق من التكرار
                if hasattr(voice_client, 'loop_enabled') and voice_client.loop_enabled:
                    print("🔄 التكرار مفعل - إعادة تشغيل الأغنية")
                    try:
                        new_audio_source = discord.FFmpegPCMAudio(song_data['url'], **ffmpeg_options)
                        voice_client.play(new_audio_source, after=after_playing)
                    except Exception as e:
                        print(f"❌ خطأ في إعادة التشغيل: {e}")
                else:
                    # تشغيل الأغنية التالية
                    asyncio.create_task(play_next_song(guild))
        
        voice_client.play(audio_source, after=after_playing)
        
        # رسالة تأكيد
        duration_str = "غير معروف"
        if song_data['duration'] > 0:
            duration_minutes = int(song_data['duration'] // 60)
            duration_seconds = int(song_data['duration'] % 60)
            duration_str = f"{duration_minutes}:{duration_seconds:02d}"
        
        await guild.system_channel.send(f"🎵 **{song_data['title']}** | ⏱️ {duration_str} | 👤 {song_data['requester']}")
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل الأغنية التالية: {e}")

async def show_commands(message):
    """عرض جميع أوامر البوت"""
    try:
        embed = discord.Embed(
            title="🎵 أوامر بوت الموسيقى",
            description="جميع الأوامر المتاحة للبوت",
            color=0x00ff00
        )
        
        # أوامر التشغيل
        embed.add_field(
            name="🎵 أوامر التشغيل",
            value="""`ش اسم_الأغنية` - تشغيل أغنية
`ضف اسم_الأغنية` - إضافة أغنية للقائمة
`قائمة` - عرض قائمة التشغيل
`مسح` - مسح قائمة التشغيل""",
            inline=False
        )
        
        # أوامر التحكم
        embed.add_field(
            name="🎛️ أوامر التحكم",
            value="""`س` - تخطي الأغنية
`قف` - إيقاف البوت
`شوي` - إيقاف مؤقت
`كمل` - استئناف التشغيل
`كرر` - تكرار الأغنية
`ا` - إيقاف التكرار""",
            inline=False
        )
        
        # أوامر المعلومات
        embed.add_field(
            name="ℹ️ أوامر المعلومات",
            value="""`اوامر` - عرض هذه القائمة
`تست` - اختبار البوت
`صلاحيات` - فحص صلاحيات البوت
`سيرفر` - معلومات السيرفر
`صوت` - اختبار الاتصال الصوتي
`يوتيوب` - اختبار YouTube
`كوكيز` - اختبار Cookies""",
            inline=False
        )
        
        # معلومات إضافية
        embed.add_field(
            name="💡 معلومات مهمة",
            value="""• البوت يدعم SoundCloud فقط
• يمكنك إضافة عدة أغاني للقائمة
• الأغاني تشغل تلقائياً ورا بعض
• استخدم `كرر` لتكرار أغنية واحدة
• استخدم `ضف` لإضافة أغاني للقائمة""",
            inline=False
        )
        
        embed.set_footer(text="🎵 استمتع بالموسيقى!")
        
        await message.channel.send(embed=embed)
        
    except Exception as e:
        await message.channel.send(f"❌ خطأ في عرض الأوامر: {str(e)}")

async def pause_song(message):
    """إيقاف مؤقت للأغنية"""
    try:
        guild_id = message.guild.id
        if guild_id in voice_clients and voice_clients[guild_id].is_playing():
            voice_clients[guild_id].pause()
            await message.channel.send("⏸️ تم إيقاف الأغنية مؤقتاً")
        else:
            await message.channel.send("❌ لا توجد أغنية قيد التشغيل!")
    except Exception as e:
        await message.channel.send(f"❌ خطأ في إيقاف الأغنية: {str(e)}")

async def resume_song(message):
    """استئناف تشغيل الأغنية"""
    try:
        guild_id = message.guild.id
        if guild_id in voice_clients and voice_clients[guild_id].is_paused():
            voice_clients[guild_id].resume()
            await message.channel.send("▶️ تم استئناف تشغيل الأغنية")
        else:
            await message.channel.send("❌ لا توجد أغنية متوقفة!")
    except Exception as e:
        await message.channel.send(f"❌ خطأ في استئناف الأغنية: {str(e)}")

async def test_bot(message):
    """اختبار البوت"""
    embed = discord.Embed(title="🧪 اختبار البوت", color=0x00ff00)
    embed.add_field(name="✅ الحالة", value="البوت يعمل بشكل طبيعي", inline=False)
    embed.add_field(name="🏓 التأخير", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="🔗 الاتصال", value="متصل", inline=True)
    await message.channel.send(embed=embed)

async def check_permissions(message):
    """فحص صلاحيات البوت"""
    bot_member = message.guild.get_member(bot.user.id)
    perms = bot_member.guild_permissions
    
    embed = discord.Embed(title="🔐 صلاحيات البوت", color=0x0099ff)
    
    essential_perms = [
        ("Connect", perms.connect),
        ("Speak", perms.speak),
        ("Use Voice Activity", perms.use_voice_activation),
        ("Send Messages", perms.send_messages),
        ("Embed Links", perms.embed_links),
        ("Read Message History", perms.read_message_history)
    ]
    
    for perm_name, has_perm in essential_perms:
        status = "✅" if has_perm else "❌"
        embed.add_field(name=f"{status} {perm_name}", value="متوفر" if has_perm else "غير متوفر", inline=True)
    
    await message.channel.send(embed=embed)

async def check_server_settings(message):
    """فحص إعدادات السيرفر"""
    guild = message.guild
    embed = discord.Embed(title="🖥️ إعدادات السيرفر", color=0xff9900)
    embed.add_field(name="📛 اسم السيرفر", value=guild.name, inline=True)
    embed.add_field(name="👥 عدد الأعضاء", value=guild.member_count, inline=True)
    embed.add_field(name="🔊 القنوات الصوتية", value=len(guild.voice_channels), inline=True)
    await message.channel.send(embed=embed)

async def test_voice_connection(message):
    """اختبار الاتصال الصوتي"""
    if not message.author.voice:
        await message.channel.send("❌ يجب أن تكون في قناة صوتية لاختبار الاتصال!")
        return
    
    try:
        voice_channel = message.author.voice.channel
        test_voice = await voice_channel.connect(timeout=5.0)
        await message.channel.send("✅ اختبار الاتصال الصوتي نجح!")
        await test_voice.disconnect()
    except Exception as e:
        await message.channel.send(f"❌ فشل اختبار الاتصال الصوتي: {str(e)}")

async def test_youtube_connection(message):
    """اختبار الاتصال بـ YouTube"""
    try:
        await message.channel.send("🔍 جاري اختبار الاتصال بـ YouTube...")
        
        test_opts = yt_dl_opts.copy()
        test_opts['socket_timeout'] = 10
        test_opts['retries'] = 1
        
        with yt_dlp.YoutubeDL(test_opts) as ydl:
            info = ydl.extract_info("ytsearch1:test", download=False)
            if info and 'entries' in info and info['entries']:
                await message.channel.send("✅ الاتصال بـ YouTube يعمل!")
            else:
                await message.channel.send("❌ مشكلة في الاتصال بـ YouTube")
    except Exception as e:
        await message.channel.send(f"❌ خطأ في اختبار YouTube: {str(e)[:100]}...")

async def test_cookies(message):
    """اختبار ملف Cookies"""
    await message.channel.send("ℹ️ البوت لا يستخدم Cookies حالياً - تم إزالة الاعتماد عليها")

# تشغيل البوت مع إعدادات محسنة لـ Render
if __name__ == "__main__":
    if DISCORD_TOKEN == 'YOUR_DISCORD_BOT_TOKEN_HERE':
        print("❌ يرجى تعيين DISCORD_TOKEN في متغيرات البيئة")
        print("💡 في Render، اذهب إلى Environment Variables وأضف:")
        print("   DISCORD_TOKEN = your_bot_token_here")
    else:
        print("🚀 بدء Discord Bot...")
        print("🌐 منصة الاستضافة: Render")
        print("🔧 Keep Alive: محسن ومفعل")
        
        # بدء Keep Alive في خيط منفصل
        try:
            from keep_alive import start_keep_alive
            keep_alive_thread = start_keep_alive()
            print("✅ Keep Alive مفعل")
        except Exception as e:
            print(f"⚠️ Keep Alive غير متاح: {e}")
        
        # بدء خادم HTTP بسيط لفتح منفذ
        import threading
        import socket
        from http.server import HTTPServer, BaseHTTPRequestHandler
        
        class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    response = """
                    <html>
                    <head><title>Discord Music Bot</title></head>
                    <body>
                        <h1>🎵 Discord Music Bot is Running!</h1>
                        <p>Status: Online</p>
                        <p>Time: {}</p>
                    </body>
                    </html>
                    """.format(time.strftime('%Y-%m-%d %H:%M:%S'))
                    self.wfile.write(response.encode())
                elif self.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = '{"status": "healthy", "bot": "running"}'
                    self.wfile.write(response.encode())
                elif self.path == '/ping':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = '{"status": "pong", "message": "Bot is alive!"}'
                    self.wfile.write(response.encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                # إيقاف رسائل السجل
                pass
        
        def start_http_server():
            try:
                port = int(os.getenv('PORT', 8080))
                server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
                print(f"🌐 خادم HTTP يعمل على المنفذ {port}")
                server.serve_forever()
            except Exception as e:
                print(f"❌ فشل في بدء خادم HTTP: {e}")
        
        # بدء خادم HTTP في خيط منفصل
        http_thread = threading.Thread(target=start_http_server, daemon=True)
        http_thread.start()
        
        try:
            # تشغيل البوت مع معالجة الأخطاء
            bot.run(DISCORD_TOKEN, log_handler=None)
        except Exception as e:
            print(f"❌ خطأ في تشغيل البوت: {e}")
            import traceback
            traceback.print_exc()
            
            # نظام إعادة المحاولة الذكي
            max_retries = 5
            base_delay = 60  # بداية من دقيقة واحدة
            
            for attempt in range(max_retries):
                try:
                    print(f"🔄 محاولة {attempt + 1} من {max_retries}")
                    bot.run(DISCORD_TOKEN, log_handler=None)
                    break  # نجح الاتصال
                    
                except discord.errors.HTTPException as e2:
                    if e2.status == 429:  # Rate Limited
                        delay = base_delay * (2 ** attempt)  # تأخير متزايد
                        print(f"⚠️ Rate Limited من Discord - انتظار {delay} ثانية...")
                        print(f"💡 السبب: IP الخادم تم حظره مؤقتاً")
                        print(f"🔧 الحل: تغيير IP أو الانتظار")
                        time.sleep(delay)
                    else:
                        print(f"❌ خطأ HTTP: {e2}")
                        break
                        
                except Exception as e2:
                    print(f"❌ خطأ في إعادة المحاولة: {e2}")
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        print(f"🔄 إعادة المحاولة بعد {delay} ثانية...")
                        time.sleep(delay)
                    else:
                        print("❌ فشلت جميع المحاولات")
                        exit(1)