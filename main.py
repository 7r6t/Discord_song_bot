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

# متغيرات عامة
voice_clients = {}

# إعدادات yt-dlp محسنة لتجنب YouTube bot detection
yt_dl_opts = {
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
    'extractaudio': True,
    'audioformat': 'm4a',
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
        'Origin': 'https://www.youtube.com'
    },
    'extractor_retries': 5,
    'fragment_retries': 5,
    'retries': 5,
    'sleep_interval': 1,
    'max_sleep_interval': 5,
    'sleep_interval_requests': 1,
    'socket_timeout': 30,
    'max_downloads': 1,
    'prefer_ffmpeg': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
        'preferredquality': '192'
    }],
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
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -allowed_extensions ALL',
    'options': '-vn -filter:a "volume=0.5" -f m4a'
}

# Flask app للـ Keep Alive
app = Flask(__name__)

@app.route('/')
def home():
    return "Discord Bot is running!"

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "bot": "running"})

def start_web_server():
    """تشغيل الخادم الويب في خيط منفصل"""
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)

def start_keep_alive():
    """تشغيل Keep Alive في خيط منفصل"""
    def keep_alive():
        while True:
            try:
                time.sleep(20)
                print("🔄 Keep Alive: البوت يعمل...")
                
                # إرسال ping للخادم إذا كان متاحاً
                keep_alive_url = os.environ.get("KEEP_ALIVE_URL")
                if keep_alive_url:
                    try:
                        requests.get(keep_alive_url, timeout=5)
                    except:
                        pass
            except:
                pass
    
    thread = threading.Thread(target=keep_alive, daemon=True)
    thread.start()

@bot.event
async def on_ready():
    print(f'✅ البوت متصل: {bot.user}')
    await bot.change_presence(activity=discord.Game(name=BOT_STATUS))
    
    # بدء Keep Alive والخادم الويب
    start_keep_alive()
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    
    print("🌐 الخادم الويب يعمل للـ Keep Alive")

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
            await message.channel.send(f"🔍 جاري البحث عن: {song_name}...")

        # البحث مع timeout قصير
        video_info = None
        url = None
        title = "أغنية"
        duration = 0

        try:
            # إعدادات بحث سريعة
            fast_opts = yt_dl_opts.copy()
            fast_opts['socket_timeout'] = 10  # timeout أقصر
            fast_opts['retries'] = 1  # محاولة واحدة فقط
            fast_opts['extract_flat'] = False
            fast_opts['skip_download'] = False
            fast_opts['sleep_interval'] = 0  # بدون انتظار
            fast_opts['max_sleep_interval'] = 0  # بدون انتظار
            fast_opts['sleep_interval_requests'] = 0  # بدون انتظار

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
                except asyncio.TimeoutError:
                    timeout_embed = discord.Embed(
                        title="⏰ انتهت مهلة استخراج الرابط",
                        description="استخراج الرابط استغرق أكثر من 10 ثواني",
                        color=0xff9900
                    )
                    await message.channel.send(embed=timeout_embed)
                    return
            else:
                # إذا كان اسم، ابحث عنه
                search_embed = discord.Embed(
                    title="🔍 البحث عن الأغنية",
                    description=f"**{song_name}**",
                    color=0x0099ff
                )
                search_embed.add_field(name="⏱️ الوقت المتوقع", value="5 ثواني", inline=True)
                search_embed.add_field(name="🌐 المصدر", value="SoundCloud + YouTube", inline=True)
                await message.channel.send(embed=search_embed)
                
                try:
                    # البحث في SoundCloud و YouTube
                    video_info = await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(
                            None, 
                            search_youtube, song_name, fast_opts
                        ),
                        timeout=5
                    )
                except asyncio.TimeoutError:
                    timeout_embed = discord.Embed(
                        title="⏰ انتهت مهلة البحث",
                        description="البحث استغرق أكثر من 5 ثواني",
                        color=0xff9900
                    )
                    timeout_embed.add_field(name="💡 نصيحة", value="جرب مرة أخرى بكلمات مختلفة أو انتظر قليلاً", inline=False)
                    await message.channel.send(embed=timeout_embed)
                    return
                
                if video_info and 'url' in video_info:
                    url = video_info['url']
                    title = video_info.get('title', 'أغنية')
                    duration = video_info.get('duration', 0)
                    
                    # رسالة نجاح البحث جميلة
                    try:
                        if duration > 0:
                            duration_minutes = int(duration // 60)
                            duration_seconds = int(duration % 60)
                            duration_str = f"{duration_minutes}:{duration_seconds:02d}"
                        else:
                            duration_str = "غير معروف"
                    except:
                        duration_str = "غير معروف"
                    
                    success_embed = discord.Embed(
                        title="✅ تم العثور على الأغنية!",
                        description=f"**{title}**",
                        color=0x00ff00
                    )
                    success_embed.add_field(name="🎵 المصدر", value=video_info.get('extractor', 'غير معروف'), inline=True)
                    success_embed.add_field(name="⏱️ المدة", value=duration_str, inline=True)
                    await message.channel.send(embed=success_embed)
                    
                    await message.channel.send("🔗 جاري الاتصال بالقناة الصوتية...")
                else:
                    # رسالة فشل البحث جميلة
                    error_embed = discord.Embed(
                        title="❌ لم يتم العثور على الأغنية",
                        description="فشل البحث في جميع المصادر",
                        color=0xff0000
                    )
                    error_embed.add_field(name="💡 نصائح", value="• تأكد من كتابة اسم الأغنية بشكل صحيح\n• جرب كلمات مختلفة\n• تأكد من وجود اتصال إنترنت", inline=False)
                    await message.channel.send(embed=error_embed)
                    return
                    
        except Exception as e:
            await message.channel.send(f"❌ خطأ في البحث: {str(e)[:100]}...")
            return

        # الاتصال بالقناة الصوتية
        try:
            await message.channel.send("🔗 جاري الاتصال بالقناة الصوتية...")
            
            if guild_id in voice_clients:
                voice_client = voice_clients[guild_id]
                if voice_client.is_connected():
                    if voice_client.channel != voice_channel:
                        await message.channel.send("🔄 نقل البوت إلى القناة الصوتية...")
                        await voice_client.move_to(voice_channel)
                    else:
                        await message.channel.send("✅ البوت متصل بالفعل")
                else:
                    await message.channel.send("🔌 إعادة الاتصال بالقناة الصوتية...")
                    await voice_client.disconnect()
                    voice_client = await voice_channel.connect(timeout=10.0)
                    voice_clients[guild_id] = voice_client
            else:
                await message.channel.send("🔌 إنشاء اتصال جديد...")
                voice_client = await voice_channel.connect(timeout=10.0)
                voice_clients[guild_id] = voice_client
                
            await message.channel.send("✅ تم الاتصال بالقناة الصوتية بنجاح!")
            
        except Exception as e:
            await message.channel.send(f"❌ خطأ في الاتصال: {str(e)}")
            return

        # تشغيل الأغنية
        try:
            await message.channel.send("🎵 جاري تشغيل الأغنية...")
            
            if voice_client.is_playing():
                await message.channel.send("⏹️ إيقاف الأغنية الحالية...")
                voice_client.stop()
                
            await message.channel.send(f"🔗 جاري تحميل: {url[:100]}...")
            audio_source = discord.FFmpegPCMAudio(url, **ffmpeg_options)
            
            def after_playing(error):
                if error:
                    print(f"خطأ في التشغيل: {error}")
                    asyncio.create_task(message.channel.send(f"❌ خطأ في التشغيل: {error}"))
                else:
                    print("تم انتهاء الأغنية بنجاح")
            
            voice_client.play(audio_source, after=after_playing)
            await message.channel.send("▶️ تم بدء تشغيل الأغنية!")
            
            # إرسال رسالة تأكيد
            try:
                if duration > 0:
                    duration_minutes = int(duration // 60)
                    duration_seconds = int(duration % 60)
                    duration_str = f"{duration_minutes}:{duration_seconds:02d}"
                else:
                    duration_str = "غير معروف"
            except:
                duration_str = "غير معروف"
            embed = discord.Embed(
                title="🎵 تم تشغيل الأغنية",
                description=f"**{title}**",
                color=0x00ff00
            )
            embed.add_field(name="⏱️ المدة", value=duration_str, inline=True)
            embed.add_field(name="👤 الطالب", value=message.author.mention, inline=True)
            await message.channel.send(embed=embed)
            
        except Exception as e:
            await message.channel.send(f"❌ خطأ في تشغيل الأغنية: {str(e)}")
            return

    except Exception as e:
        await message.channel.send(f"❌ خطأ عام في تشغيل الأغنية: {str(e)}")

def search_youtube(query, opts):
    """البحث في YouTube و SoundCloud - الحل الشامل"""
    try:
        print(f"🔍 البحث عن: {query}")
        
        # محاولة 1: البحث في SoundCloud (الأسهل)
        print("🔍 المحاولة 1: SoundCloud")
        sc_result = search_soundcloud(query)
        if sc_result:
            print(f"✅ تم العثور على SoundCloud: {sc_result.get('title', 'بدون عنوان')}")
            return sc_result
        
        # محاولة 2: YouTube API مباشر
        print("🔍 المحاولة 2: YouTube API مباشر")
        api_result = search_youtube_api(query)
        if api_result:
            print(f"✅ تم العثور على YouTube: {api_result.get('title', 'بدون عنوان')}")
            return api_result
        
        # محاولة 3: yt-dlp مع إعدادات بسيطة
        print("🔍 المحاولة 3: yt-dlp بسيط")
        simple_opts = {
            'format': 'bestaudio',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True
        }
        
        with yt_dlp.YoutubeDL(simple_opts) as ydl:
            try:
                # البحث في SoundCloud أولاً
                sc_query = f"scsearch:{query}"
                info = ydl.extract_info(sc_query, download=False)
                if info and 'entries' in info and info['entries']:
                    first_result = info['entries'][0]
                    print(f"✅ تم العثور على SoundCloud: {first_result.get('title', 'بدون عنوان')}")
                    return first_result
            except Exception as e:
                print(f"❌ خطأ في SoundCloud: {e}")
            
            try:
                # البحث في YouTube
                yt_query = f"ytsearch:{query}"
                info = ydl.extract_info(yt_query, download=False)
                if info and 'entries' in info and info['entries']:
                    first_result = info['entries'][0]
                    print(f"✅ تم العثور على YouTube: {first_result.get('title', 'بدون عنوان')}")
                    return first_result
            except Exception as e:
                print(f"❌ خطأ في YouTube: {e}")
        
        print("❌ فشل البحث في جميع المصادر")
        return None
        
    except Exception as e:
        print(f"❌ خطأ عام في البحث: {e}")
        return None

def get_direct_url_info(url):
    """استخراج معلومات من رابط مباشر"""
    try:
        print(f"🔗 استخراج معلومات من: {url}")
        
        # إعدادات بسيطة للروابط المباشرة
        url_opts = {
            'format': 'bestaudio',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True
        }
        
        with yt_dlp.YoutubeDL(url_opts) as ydl:
            # استخراج معلومات الرابط
            info = ydl.extract_info(url, download=False)
            
            if info and 'title' in info:
                print(f"✅ تم استخراج: {info.get('title', 'بدون عنوان')}")
                return info
            else:
                print("❌ فشل في استخراج معلومات الرابط")
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
            'format': 'bestaudio',
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
    await message.channel.send("🔄 ميزة التكرار غير متوفرة حالياً")

async def stop_loop(message):
    """إيقاف تكرار الأغنية"""
    await message.channel.send("🔄 ميزة التكرار غير متوفرة حالياً")

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

# تشغيل البوت
if __name__ == "__main__":
    if DISCORD_TOKEN == 'YOUR_DISCORD_BOT_TOKEN_HERE':
        print("❌ يرجى تعيين DISCORD_TOKEN في متغيرات البيئة")
    else:
        bot.run(DISCORD_TOKEN)