import discord
from discord.ext import commands
import asyncio
import yt_dlp
import os
import ssl
import threading
from flask import Flask
from config import *

# إصلاح مشكلة SSL
os.environ['PYTHONHTTPSVERIFY'] = '0'
ssl._create_default_https_context = ssl._unverified_context

# إعداد البوت
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=DISCORD_PREFIX, intents=intents)

# متغيرات عامة
voice_clients = {}
music_queues = {}

# Flask App for Health Check
app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health_check():
    return 'OK', 200

def start_health_server():
    """بدء خادم health check باستخدام Flask"""
    try:
        port = int(os.environ.get('PORT', 8080))
        print(f"🌐 Starting Flask health check server on port {port}...")
        print(f"🔍 Server will respond to / and /health with 200 OK")
        
        # تشغيل Flask في وضع production مع إعدادات محسنة
        app.run(
            host='0.0.0.0', 
            port=port, 
            debug=False, 
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        print(f"❌ Failed to start Flask server: {e}")
        import traceback
        traceback.print_exc()

# بدء خادم health check في thread منفصل
print("🚀 Starting Discord Bot with Flask Health Check Server...")
print("🔍 Flask server will respond to / and /health with 200 OK")
health_thread = threading.Thread(target=start_health_server, daemon=True)
health_thread.start()

# إعدادات yt-dlp محسنة
yt_dl_opts = {
    'format': 'bestaudio[ext=mp3]/bestaudio[ext=m4a]/bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'ignoreerrors': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'no_check_certificate': True,
    'prefer_insecure': True,
    'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'extractor_args': {
        'youtube': {
            'skip': ['dash', 'live', 'hls'],
            'player_client': ['android', 'web', 'tv', 'ios']
        }
    },
    'geo_bypass': True,
    'geo_bypass_country': 'US',
    'geo_bypass_ip_block': '1.1.1.1/24',
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
        'Pragma': 'no-cache'
    },
    'extractor_retries': 3,
    'fragment_retries': 3,
    'retries': 3,
    'sleep_interval': 1,
    'max_sleep_interval': 3,
    'sleep_interval_requests': 1,
    'socket_timeout': 30,
    'max_downloads': 1,
    'prefer_ffmpeg': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }],
    'writesubtitles': False,
    'writeautomaticsub': False,
    'skip_download': False,
    'http_chunk_size': 10485760,
    'extract_flat': False,
    'verbose': False
}

@bot.event
async def on_ready():
    """حدث عند تشغيل البوت"""
    print(f"✅ {bot.user} تم تشغيله بنجاح!")
    await bot.change_presence(activity=discord.Game(name="🎵 استمع للموسيقى"))

@bot.command(name="ش")
async def play(ctx, *, query):
    """تشغيل أغنية من YouTube أو SoundCloud"""
    if not ctx.author.voice:
        await ctx.send("❌ يجب أن تكون في قناة صوتية!")
        return
    
    voice_channel = ctx.author.voice.channel
    guild_id = ctx.guild.id
    
    # إنشاء قائمة تشغيل إذا لم تكن موجودة
    if guild_id not in music_queues:
        music_queues[guild_id] = []
    
    # إضافة الأغنية للقائمة
    await add_to_queue(ctx, query, voice_channel, guild_id)

async def add_to_queue(ctx, query, voice_channel, guild_id):
    """إضافة أغنية لقائمة التشغيل"""
    try:
        await ctx.send(f"🔍 جاري البحث عن: {query}...")
        
        # البحث عن الأغنية
        song_info = await search_song(query)
        if not song_info:
            await ctx.send("❌ لم يتم العثور على الأغنية!")
            return
        
        # إضافة للقائمة
        music_queues[guild_id].append({
            'title': song_info['title'],
            'url': song_info['url'],
            'duration': song_info.get('duration', 'غير معروف'),
            'requester': ctx.author.display_name,
            'source': song_info['extractor']
        })
        
        await ctx.send(f"✅ تم إضافة: **{song_info['title']}** للقائمة")
        
        # تشغيل إذا لم تكن هناك أغنية تعمل
        if guild_id not in voice_clients or not voice_clients[guild_id].is_playing():
            await play_next(ctx, guild_id, voice_channel)
            
    except Exception as e:
        await ctx.send(f"❌ خطأ في إضافة الأغنية: {str(e)}")

async def search_song(query):
    """البحث عن أغنية"""
    try:
        # محاولة البحث المباشر
        if query.startswith(('http://', 'https://')):
            with yt_dlp.YoutubeDL(yt_dl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                return {
                    'title': info.get('title', 'غير معروف'),
                    'url': info.get('url', query),
                    'duration': format_duration(info.get('duration', 0)),
                    'extractor': info.get('extractor', 'unknown')
                }
        else:
            # البحث بالكلمات
            search_query = f"ytsearch1:{query}"
            with yt_dlp.YoutubeDL(yt_dl_opts) as ydl:
                info = ydl.extract_info(search_query, download=False)
                if info and 'entries' in info and info['entries']:
                    entry = info['entries'][0]
                    return {
                        'title': entry.get('title', 'غير معروف'),
                        'url': entry.get('url', ''),
                        'duration': format_duration(entry.get('duration', 0)),
                        'extractor': entry.get('extractor', 'unknown')
                    }
        
        return None
        
    except Exception as e:
        print(f"خطأ في البحث: {e}")
        return None

def format_duration(duration):
    """تنسيق المدة"""
    if not duration:
        return "غير معروف"
    
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    return f"{minutes}:{seconds:02d}"

async def play_next(ctx, guild_id, voice_channel):
    """تشغيل الأغنية التالية"""
    if not music_queues[guild_id]:
        return
    
    try:
        # الاتصال بالقناة الصوتية
        if guild_id not in voice_clients or not voice_clients[guild_id].is_connected():
            voice_client = await voice_channel.connect()
            voice_clients[guild_id] = voice_client
        else:
            voice_client = voice_clients[guild_id]
        
        # الحصول على الأغنية التالية
        song = music_queues[guild_id].pop(0)
        
        await ctx.send(f"🎵 جاري تشغيل: **{song['title']}**")
        
        # تشغيل الأغنية
        voice_client.play(
            discord.FFmpegPCMAudio(
                song['url'],
                options='-vn -b:a 192k'
            ),
            after=lambda e: asyncio.run_coroutine_threadsafe(
                play_next(ctx, guild_id, voice_channel), 
                bot.loop
            ) if e is None else None
        )
        
        await ctx.send(f"✅ تم تشغيل: **{song['title']}** ⏱️ المدة: {song['duration']}")
        
    except Exception as e:
        await ctx.send(f"❌ خطأ في تشغيل الأغنية: {str(e)}")

@bot.command(name="قائمة")
async def queue(ctx):
    """عرض قائمة التشغيل"""
    guild_id = ctx.guild.id
    
    if guild_id not in music_queues or not music_queues[guild_id]:
        await ctx.send("📝 قائمة التشغيل فارغة!")
        return
    
    embed = discord.Embed(title="📝 قائمة التشغيل", color=0x0099ff)
    
    for i, song in enumerate(music_queues[guild_id][:10], 1):
        embed.add_field(
            name=f"{i}. {song['title']}",
            value=f"⏱️ {song['duration']} | 👤 {song['requester']}",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name="تخطي")
async def skip(ctx):
    """تخطي الأغنية الحالية"""
    guild_id = ctx.guild.id
    
    if guild_id not in voice_clients or not voice_clients[guild_id].is_playing():
        await ctx.send("❌ لا توجد أغنية تعمل حالياً!")
        return
    
    voice_clients[guild_id].stop()
    await ctx.send("⏭️ تم تخطي الأغنية!")

@bot.command(name="إيقاف")
async def stop(ctx):
    """إيقاف الموسيقى والخروج من القناة"""
    guild_id = ctx.guild.id
    
    if guild_id not in voice_clients:
        await ctx.send("❌ البوت ليس في قناة صوتية!")
        return
    
    # إيقاف الموسيقى
    if voice_clients[guild_id].is_playing():
        voice_clients[guild_id].stop()
    
    # الخروج من القناة
    await voice_clients[guild_id].disconnect()
    del voice_clients[guild_id]
    
    # مسح القائمة
    if guild_id in music_queues:
        music_queues[guild_id].clear()
    
    await ctx.send("⏹️ تم إيقاف الموسيقى والخروج من القناة!")

@bot.command(name="أوامر")
async def help_commands(ctx):
    """عرض أوامر البوت"""
    embed = discord.Embed(title="🎵 أوامر البوت", color=0x0099ff)
    
    commands_list = [
        ("ش [اسم الأغنية]", "تشغيل أغنية من YouTube أو SoundCloud"),
        ("ش [رابط]", "تشغيل أغنية من رابط مباشر"),
        ("قائمة", "عرض قائمة التشغيل"),
        ("تخطي", "تخطي الأغنية الحالية"),
        ("إيقاف", "إيقاف الموسيقى والخروج من القناة"),
        ("أوامر", "عرض هذه القائمة")
    ]
    
    for cmd, desc in commands_list:
        embed.add_field(name=f"`{DISCORD_PREFIX}{cmd}`", value=desc, inline=False)
    
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    """معالجة أخطاء الأوامر"""
    if isinstance(error, commands.CommandNotFound):
        return
    
    await ctx.send(f"❌ خطأ: {str(error)}")

# تشغيل البوت
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ يرجى تعيين DISCORD_TOKEN في متغيرات البيئة")
        print("💡 في Railway، اذهب إلى Variables وأضف:")
        print("   DISCORD_TOKEN = your_bot_token_here")
    else:
        print("🚀 بدء Discord Bot...")
        print("🌐 منصة الاستضافة: Railway")
        
        try:
            bot.run(DISCORD_TOKEN)
        except Exception as e:
            print(f"❌ خطأ في تشغيل البوت: {e}")
            import traceback
            traceback.print_exc()