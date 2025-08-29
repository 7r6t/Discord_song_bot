import discord
from discord.ext import commands
import asyncio
import yt_dlp
import os
import ssl
from config import *

# إصلاح مشكلة SSL
os.environ['PYTHONHTTPSVERIFY'] = '0'
ssl._create_default_https_context = ssl._create_unverified_context

# إعداد البوت
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=DISCORD_PREFIX, intents=intents)

# متغيرات عامة
voice_clients = {}
music_queues = {}
loop_states = {} # إضافة متغير لتتبع حالة تكرار الأغنية

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
    import time
    bot.start_time = time.time()  # تسجيل وقت بدء التشغيل
    
    print(f"✅ {bot.user} تم تشغيله بنجاح!")
    await bot.change_presence(activity=discord.Game(name="�� استمع للموسيقى"))

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

@bot.command(name="play")
async def play_english(ctx, *, query):
    """تشغيل أغنية من YouTube أو SoundCloud (بالإنجليزية)"""
    await play(ctx, query=query)

@bot.command(name="قصير")
async def play_short(ctx, *, query):
    """تشغيل أغنية قصيرة (اختصار لـ ش)"""
    await play(ctx, query=query)

@bot.command(name="س")
async def skip_song(ctx):
    """تخطي الأغنية الحالية"""
    guild_id = ctx.guild.id
    
    if guild_id not in voice_clients or not voice_clients[guild_id].is_playing():
        await ctx.send("❌ لا توجد أغنية تعمل حالياً!")
        return
    
    # إيقاف الأغنية الحالية (ستنتقل للأغنية التالية تلقائياً)
    voice_clients[guild_id].stop()
    await ctx.send("⏭️ تم تخطي الأغنية!")

@bot.command(name="skip")
async def skip_english(ctx):
    """تخطي الأغنية الحالية (بالإنجليزية)"""
    await skip_song(ctx)

@bot.command(name="قف")
async def pause(ctx):
    """إيقاف مؤقت للأغنية"""
    guild_id = ctx.guild.id
    
    if guild_id not in voice_clients or not voice_clients[guild_id].is_playing():
        await ctx.send("❌ لا توجد أغنية تعمل حالياً!")
        return
    
    if voice_clients[guild_id].is_paused():
        await ctx.send("⏸️ الأغنية متوقفة مؤقتاً بالفعل!")
        return
    
    voice_clients[guild_id].pause()
    await ctx.send("⏸️ تم إيقاف الأغنية مؤقتاً!")

@bot.command(name="pause")
async def pause_english(ctx):
    """إيقاف مؤقت للأغنية (بالإنجليزية)"""
    await pause(ctx)

@bot.command(name="شوي")
async def pause_short(ctx):
    """إيقاف مؤقت للأغنية (اختصار)"""
    await pause(ctx)

@bot.command(name="كمل")
async def resume(ctx):
    """استئناف الأغنية المتوقفة مؤقتاً"""
    guild_id = ctx.guild.id
    
    if guild_id not in voice_clients:
        await ctx.send("❌ البوت ليس في قناة صوتية!")
        return
    
    if not voice_clients[guild_id].is_paused():
        await ctx.send("▶️ الأغنية تعمل بالفعل!")
        return
    
    voice_clients[guild_id].resume()
    await ctx.send("▶️ تم استئناف الأغنية!")

@bot.command(name="resume")
async def resume_english(ctx):
    """استئناف الأغنية المتوقفة مؤقتاً (بالإنجليزية)"""
    await resume(ctx)

@bot.command(name="استمر")
async def resume_arabic(ctx):
    """استئناف الأغنية المتوقفة مؤقتاً (بالعربية)"""
    await resume(ctx)

@bot.command(name="كرر")
async def loop_song(ctx):
    """تفعيل تكرار الأغنية الحالية"""
    guild_id = ctx.guild.id
    
    if guild_id not in voice_clients or not voice_clients[guild_id].is_playing():
        await ctx.send("❌ لا توجد أغنية تعمل حالياً!")
        return
    
    if guild_id not in loop_states:
        loop_states[guild_id] = False
    
    loop_states[guild_id] = True
    await ctx.send("🔁 تم تفعيل تكرار الأغنية!")

@bot.command(name="loop")
async def loop_english(ctx):
    """تفعيل تكرار الأغنية الحالية (بالإنجليزية)"""
    await loop_song(ctx)

@bot.command(name="تكرار")
async def loop_arabic(ctx):
    """تفعيل تكرار الأغنية الحالية (بالعربية)"""
    await loop_song(ctx)

@bot.command(name="ا")
async def stop_loop(ctx):
    """إيقاف تكرار الأغنية"""
    guild_id = ctx.guild.id
    
    if guild_id not in loop_states or not loop_states[guild_id]:
        await ctx.send("❌ التكرار غير مفعل!")
        return
    
    loop_states[guild_id] = False
    await ctx.send("⏹️ تم إيقاف تكرار الأغنية!")

@bot.command(name="unloop")
async def unloop_english(ctx):
    """إيقاف تكرار الأغنية (بالإنجليزية)"""
    await stop_loop(ctx)

@bot.command(name="الغاء")
async def unloop_arabic(ctx):
    """إيقاف تكرار الأغنية (بالعربية)"""
    await stop_loop(ctx)

@bot.command(name="تست")
async def test(ctx):
    """اختبار البوت"""
    await ctx.send("✅ البوت يعمل بشكل طبيعي! 🎵")

@bot.command(name="test")
async def test_english(ctx):
    """اختبار البوت (بالإنجليزية)"""
    await test(ctx)

@bot.command(name="اختبار")
async def test_arabic(ctx):
    """اختبار البوت (بالعربية)"""
    await test(ctx)

@bot.command(name="volume")
async def volume_english(ctx, level: int = None):
    """تغيير مستوى الصوت (0-100) (بالإنجليزية)"""
    await volume_arabic(ctx, level=level)

@bot.command(name="صوت")
async def volume_arabic(ctx, level: int = None):
    """تغيير مستوى الصوت (0-100) (بالعربية)"""
    guild_id = ctx.guild.id
    
    if guild_id not in voice_clients:
        await ctx.send("❌ البوت ليس في قناة صوتية!")
        return
    
    if level is None:
        # عرض مستوى الصوت الحالي
        current_volume = getattr(voice_clients[guild_id], 'volume', 1.0)
        volume_percent = int(current_volume * 100)
        await ctx.send(f"🔊 مستوى الصوت الحالي: {volume_percent}%")
        return
    
    if not 0 <= level <= 100:
        await ctx.send("❌ مستوى الصوت يجب أن يكون بين 0 و 100!")
        return
    
    # تغيير مستوى الصوت
    volume_level = level / 100.0
    voice_clients[guild_id].volume = volume_level
    await ctx.send(f"🔊 تم تغيير مستوى الصوت إلى: {level}%")

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
                after_playing(ctx, guild_id, voice_channel), 
                bot.loop
            ) if e is None else None
        )
        
        await ctx.send(f"✅ تم تشغيل: **{song['title']}** ⏱️ المدة: {song['duration']}")
        
    except Exception as e:
        await ctx.send(f"❌ خطأ في تشغيل الأغنية: {str(e)}")

async def after_playing(ctx, guild_id, voice_channel):
    """ما يحدث بعد انتهاء الأغنية"""
    try:
        # التحقق من حالة التكرار
        if guild_id in loop_states and loop_states[guild_id]:
            # إعادة الأغنية للقائمة إذا كان التكرار مفعل
            if guild_id in music_queues and music_queues[guild_id]:
                last_song = music_queues[guild_id][-1]  # الأغنية التي انتهت
                music_queues[guild_id].insert(0, last_song)  # إعادتها للبداية
                await ctx.send("🔁 تم إعادة الأغنية بسبب التكرار!")
        
        # تشغيل الأغنية التالية
        if guild_id in music_queues and music_queues[guild_id]:
            await play_next(ctx, guild_id, voice_channel)
        else:
            await ctx.send("📝 انتهت قائمة التشغيل!")
            
    except Exception as e:
        print(f"خطأ في after_playing: {e}")

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

@bot.command(name="queue")
async def queue_english(ctx):
    """عرض قائمة التشغيل (بالإنجليزية)"""
    await queue(ctx)

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
    
    # مسح حالة التكرار
    if guild_id in loop_states:
        loop_states[guild_id] = False
    
    # الخروج من القناة
    await voice_clients[guild_id].disconnect()
    del voice_clients[guild_id]
    
    # مسح القائمة
    if guild_id in music_queues:
        music_queues[guild_id].clear()
    
    await ctx.send("⏹️ تم إيقاف الموسيقى والخروج من القناة!")

@bot.command(name="stop")
async def stop_english(ctx):
    """إيقاف الموسيقى والخروج من القناة (بالإنجليزية)"""
    await stop(ctx)



@bot.command(name="أوامر")
async def help_commands(ctx):
    """عرض أوامر البوت"""
    embed = discord.Embed(title="🎵 أوامر البوت", color=0x0099ff)
    
    commands_list = [
        ("ش [اسم الأغنية]", "تشغيل أغنية من YouTube أو SoundCloud"),
        ("س [اسم الأغنية]", "اختصار لـ ش"),
        ("ش [رابط]", "تشغيل أغنية من رابط مباشر"),
        ("قائمة", "عرض قائمة التشغيل"),
        ("تخطي", "تخطي الأغنية الحالية"),
        ("قف", "إيقاف مؤقت للأغنية"),
        ("كمل", "استئناف الأغنية المتوقفة"),
        ("كرر", "تفعيل تكرار الأغنية الحالية"),
        ("ا", "إيقاف تكرار الأغنية"),
        ("شوي [0-100]", "تغيير مستوى الصوت"),
        ("إيقاف", "إيقاف الموسيقى والخروج من القناة"),
        ("تست", "اختبار البوت"),
        ("أوامر", "عرض هذه القائمة")
    ]
    
    for cmd, desc in commands_list:
        embed.add_field(name=f"`{DISCORD_PREFIX}{cmd}`", value=desc, inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name="help_cmd")
async def help_english(ctx):
    """عرض أوامر البوت (بالإنجليزية)"""
    await help_commands(ctx)

@bot.command(name="help")
async def help_english_short(ctx):
    """عرض أوامر البوت (بالإنجليزية) - اختصار"""
    await help_commands(ctx)

@bot.command(name="ping")
async def ping(ctx):
    """اختبار سرعة استجابة البوت"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! سرعة الاستجابة: {latency}ms")

@bot.command(name="سرعة")
async def ping_arabic(ctx):
    """اختبار سرعة استجابة البوت (بالعربية)"""
    await ping(ctx)

@bot.command(name="clear")
async def clear_queue(ctx):
    """مسح قائمة التشغيل"""
    guild_id = ctx.guild.id
    
    if guild_id not in music_queues or not music_queues[guild_id]:
        await ctx.send("📝 قائمة التشغيل فارغة بالفعل!")
        return
    
    music_queues[guild_id].clear()
    await ctx.send("🗑️ تم مسح قائمة التشغيل!")

@bot.command(name="مسح")
async def clear_arabic(ctx):
    """مسح قائمة التشغيل (بالعربية)"""
    await clear_queue(ctx)

@bot.command(name="now")
async def now_playing(ctx):
    """عرض الأغنية الحالية"""
    guild_id = ctx.guild.id
    
    if guild_id not in voice_clients or not voice_clients[guild_id].is_playing():
        await ctx.send("❌ لا توجد أغنية تعمل حالياً!")
        return
    
    # البحث عن الأغنية الحالية في القائمة
    if guild_id in music_queues and music_queues[guild_id]:
        current_song = music_queues[guild_id][0]  # الأغنية الأولى في القائمة
        
        embed = discord.Embed(title="🎵 الأغنية الحالية", color=0x0099ff)
        embed.add_field(name="العنوان", value=current_song['title'], inline=False)
        embed.add_field(name="المدة", value=current_song['duration'], inline=True)
        embed.add_field(name="المصدر", value=current_song['source'], inline=True)
        embed.add_field(name="الطالب", value=current_song['requester'], inline=True)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ لا يمكن تحديد الأغنية الحالية!")

@bot.command(name="الآن")
async def now_arabic(ctx):
    """عرض الأغنية الحالية (بالعربية)"""
    await now_playing(ctx)

@bot.command(name="shuffle")
async def shuffle_queue(ctx):
    """خلط قائمة التشغيل"""
    guild_id = ctx.guild.id
    
    if guild_id not in music_queues or len(music_queues[guild_id]) < 2:
        await ctx.send("❌ تحتاج على الأقل أغنيين لخلط القائمة!")
        return
    
    import random
    random.shuffle(music_queues[guild_id])
    await ctx.send("🔀 تم خلط قائمة التشغيل!")

@bot.command(name="خلط")
async def shuffle_arabic(ctx):
    """خلط قائمة التشغيل (بالعربية)"""
    await shuffle_queue(ctx)

@bot.command(name="remove")
async def remove_song(ctx, position: int):
    """إزالة أغنية من قائمة التشغيل"""
    guild_id = ctx.guild.id
    
    if guild_id not in music_queues or not music_queues[guild_id]:
        await ctx.send("❌ قائمة التشغيل فارغة!")
        return
    
    if position < 1 or position > len(music_queues[guild_id]):
        await ctx.send(f"❌ الرقم يجب أن يكون بين 1 و {len(music_queues[guild_id])}!")
        return
    
    removed_song = music_queues[guild_id].pop(position - 1)
    await ctx.send(f"🗑️ تم إزالة: **{removed_song['title']}** من القائمة!")

@bot.command(name="إزالة")
async def remove_arabic(ctx, position: int):
    """إزالة أغنية من قائمة التشغيل (بالعربية)"""
    await remove_song(ctx, position)

@bot.command(name="move")
async def move_song(ctx, from_pos: int, to_pos: int):
    """نقل أغنية في قائمة التشغيل"""
    guild_id = ctx.guild.id
    
    if guild_id not in music_queues or not music_queues[guild_id]:
        await ctx.send("❌ قائمة التشغيل فارغة!")
        return
    
    if from_pos < 1 or from_pos > len(music_queues[guild_id]) or to_pos < 1 or to_pos > len(music_queues[guild_id]):
        await ctx.send(f"❌ المواقع يجب أن تكون بين 1 و {len(music_queues[guild_id])}!")
        return
    
    if from_pos == to_pos:
        await ctx.send("❌ المواقع متطابقة!")
        return
    
    # نقل الأغنية
    song = music_queues[guild_id].pop(from_pos - 1)
    music_queues[guild_id].insert(to_pos - 1, song)
    
    await ctx.send(f"🔄 تم نقل **{song['title']}** من الموقع {from_pos} إلى {to_pos}!")

@bot.command(name="نقل")
async def move_arabic(ctx, from_pos: int, to_pos: int):
    """نقل أغنية في قائمة التشغيل (بالعربية)"""
    await move_song(ctx, from_pos, to_pos)

@bot.command(name="search")
async def search_songs(ctx, *, query):
    """البحث عن أغاني وعرض نتائج متعددة"""
    try:
        await ctx.send(f"🔍 جاري البحث عن: {query}...")
        
        # البحث عن 5 نتائج
        search_query = f"ytsearch5:{query}"
        with yt_dlp.YoutubeDL(yt_dl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            
            if not info or 'entries' not in info or not info['entries']:
                await ctx.send("❌ لم يتم العثور على نتائج!")
                return
            
            embed = discord.Embed(title=f"🔍 نتائج البحث: {query}", color=0x0099ff)
            
            for i, entry in enumerate(info['entries'][:5], 1):
                duration = format_duration(entry.get('duration', 0))
                embed.add_field(
                    name=f"{i}. {entry.get('title', 'غير معروف')}",
                    value=f"⏱️ {duration} | 🌐 {entry.get('extractor', 'unknown')}",
                    inline=False
                )
            
            embed.set_footer(text="اكتب رقم الأغنية لإضافتها للقائمة")
            await ctx.send(embed=embed)
            
    except Exception as e:
        await ctx.send(f"❌ خطأ في البحث: {str(e)}")

@bot.command(name="بحث")
async def search_arabic(ctx, *, query):
    """البحث عن أغاني وعرض نتائج متعددة (بالعربية)"""
    await search_songs(ctx, query=query)

@bot.command(name="info")
async def bot_info(ctx):
    """عرض معلومات البوت"""
    embed = discord.Embed(title="ℹ️ معلومات البوت", color=0x0099ff)
    
    # معلومات عامة
    embed.add_field(name="اسم البوت", value=bot.user.name, inline=True)
    embed.add_field(name="معرف البوت", value=bot.user.id, inline=True)
    embed.add_field(name="تاريخ الإنشاء", value=bot.user.created_at.strftime("%Y-%m-%d"), inline=True)
    
    # معلومات الخادم
    embed.add_field(name="اسم الخادم", value=ctx.guild.name, inline=True)
    embed.add_field(name="عدد الأعضاء", value=ctx.guild.member_count, inline=True)
    embed.add_field(name="عدد القنوات", value=len(ctx.guild.channels), inline=True)
    
    # معلومات الموسيقى
    guild_id = ctx.guild.id
    queue_count = len(music_queues.get(guild_id, []))
    is_playing = guild_id in voice_clients and voice_clients[guild_id].is_playing()
    is_looping = loop_states.get(guild_id, False)
    
    embed.add_field(name="الأغاني في القائمة", value=queue_count, inline=True)
    embed.add_field(name="حالة التشغيل", value="▶️ يعمل" if is_playing else "⏸️ متوقف", inline=True)
    embed.add_field(name="حالة التكرار", value="🔁 مفعل" if is_looping else "⏹️ متوقف", inline=True)
    
    embed.set_footer(text="🎵 بوت موسيقى متطور")
    await ctx.send(embed=embed)

@bot.command(name="معلومات")
async def info_arabic(ctx):
    """عرض معلومات البوت (بالعربية)"""
    await bot_info(ctx)

@bot.command(name="stats")
async def bot_stats(ctx):
    """عرض إحصائيات البوت"""
    embed = discord.Embed(title="📊 إحصائيات البوت", color=0x0099ff)
    
    # إحصائيات عامة
    embed.add_field(name="عدد الخوادم", value=len(bot.guilds), inline=True)
    embed.add_field(name="عدد المستخدمين", value=len(bot.users), inline=True)
    embed.add_field(name="سرعة الاستجابة", value=f"{round(bot.latency * 1000)}ms", inline=True)
    
    # إحصائيات الموسيقى
    total_queues = len(music_queues)
    total_voice_clients = len(voice_clients)
    total_loops = sum(1 for state in loop_states.values() if state)
    
    embed.add_field(name="الخوادم النشطة", value=total_queues, inline=True)
    embed.add_field(name="القنوات الصوتية", value=total_voice_clients, inline=True)
    embed.add_field(name="التكرار المفعل", value=total_loops, inline=True)
    
    # معلومات النظام
    import psutil
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    
    embed.add_field(name="استخدام المعالج", value=f"{cpu_percent}%", inline=True)
    embed.add_field(name="استخدام الذاكرة", value=f"{memory_percent}%", inline=True)
    embed.add_field(name="الذاكرة المتاحة", value=f"{memory.available // (1024**3):.1f}GB", inline=True)
    
    embed.set_footer(text="📈 إحصائيات مباشرة")
    await ctx.send(embed=embed)

@bot.command(name="إحصائيات")
async def stats_arabic(ctx):
    """عرض إحصائيات البوت (بالعربية)"""
    await bot_stats(ctx)

@bot.command(name="invite")
async def invite_bot(ctx):
    """عرض رابط دعوة البوت"""
    embed = discord.Embed(title="🔗 دعوة البوت", color=0x0099ff)
    
    # إنشاء رابط الدعوة
    invite_url = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot"
    
    embed.add_field(
        name="رابط الدعوة", 
        value=f"[اضغط هنا لدعوة البوت]({invite_url})", 
        inline=False
    )
    
    embed.add_field(
        name="الصلاحيات المطلوبة",
        value="• إرسال الرسائل\n• إدارة القنوات الصوتية\n• استخدام الصوت\n• إرفاق الملفات",
        inline=False
    )
    
    embed.set_footer(text="🎵 أضف البوت لخادمك!")
    await ctx.send(embed=embed)

@bot.command(name="دعوة")
async def invite_arabic(ctx):
    """عرض رابط دعوة البوت (بالعربية)"""
    await invite_bot(ctx)

@bot.command(name="support")
async def support_info(ctx):
    """عرض معلومات الدعم"""
    embed = discord.Embed(title="🆘 معلومات الدعم", color=0x0099ff)
    
    embed.add_field(
        name="📋 الأوامر الأساسية",
        value="• `ش` - تشغيل أغنية\n• `قائمة` - عرض القائمة\n• `تخطي` - تخطي الأغنية\n• `إيقاف` - إيقاف البوت",
        inline=False
    )
    
    embed.add_field(
        name="🔧 الأوامر المتقدمة",
        value="• `كرر` - تكرار الأغنية\n• `شوي` - تغيير الصوت\n• `خلط` - خلط القائمة\n• `إزالة` - إزالة أغنية",
        inline=False
    )
    
    embed.add_field(
        name="❓ مشاكل شائعة",
        value="• تأكد من أن البوت في قناة صوتية\n• تأكد من أن لديك صلاحيات كافية\n• جرب إعادة تشغيل البوت",
        inline=False
    )
    
    embed.set_footer(text="🎵 للمساعدة، اكتب 'أوامر'")
    await ctx.send(embed=embed)

@bot.command(name="مساعدة")
async def support_arabic(ctx):
    """عرض معلومات الدعم (بالعربية)"""
    await support_info(ctx)

@bot.command(name="about")
async def about_bot(ctx):
    """عرض معلومات حول البوت"""
    embed = discord.Embed(title="ℹ️ حول البوت", color=0x0099ff)
    
    embed.add_field(
        name="🎵 وصف البوت",
        value="بوت موسيقى متطور يدعم YouTube و SoundCloud مع ميزات متقدمة مثل قائمة التشغيل والتكرار والخلط",
        inline=False
    )
    
    embed.add_field(
        name="🚀 المميزات",
        value="• دعم YouTube و SoundCloud\n• قائمة تشغيل متعددة\n• تكرار الأغاني\n• خلط القائمة\n• إدارة متقدمة للقائمة\n• جودة صوت عالية",
        inline=False
    )
    
    embed.add_field(
        name="🔧 التقنيات المستخدمة",
        value="• discord.py\n• yt-dlp\n• FFmpeg\n• Python 3.11+",
        inline=False
    )
    
    embed.add_field(
        name="📅 تاريخ الإصدار",
        value="الإصدار 2.0.0 - تم التطوير في 2025",
        inline=False
    )
    
    embed.set_footer(text="🎵 بوت موسيقى احترافي")
    await ctx.send(embed=embed)

@bot.command(name="حول")
async def about_arabic(ctx):
    """عرض معلومات حول البوت (بالعربية)"""
    await about_bot(ctx)

@bot.command(name="version")
async def version_info(ctx):
    """عرض إصدار البوت"""
    embed = discord.Embed(title="📋 إصدار البوت", color=0x0099ff)
    
    embed.add_field(name="الإصدار الحالي", value="2.0.0", inline=True)
    embed.add_field(name="تاريخ الإصدار", value="2025-01-20", inline=True)
    embed.add_field(name="حالة الإصدار", value="🟢 مستقر", inline=True)
    
    embed.add_field(
        name="📝 ملاحظات الإصدار",
        value="• إضافة جميع الأوامر القديمة\n• تحسين جودة الصوت\n• إضافة ميزة التكرار\n• إضافة إدارة متقدمة للقائمة\n• إضافة أوامر جديدة ومفيدة",
        inline=False
    )
    
    embed.add_field(
        name="🔮 الميزات القادمة",
        value="• دعم Spotify\n• حفظ القوائم المفضلة\n• إعدادات مخصصة\n• دعم اللغات المتعددة",
        inline=False
    )
    
    embed.set_footer(text="🎵 تم التطوير بواسطة فريق متخصص")
    await ctx.send(embed=embed)

@bot.command(name="إصدار")
async def version_arabic(ctx):
    """عرض إصدار البوت (بالعربية)"""
    await version_info(ctx)

@bot.command(name="credits")
async def show_credits(ctx):
    """عرض اعتمادات البوت"""
    embed = discord.Embed(title="👨‍💻 اعتمادات البوت", color=0x0099ff)
    
    embed.add_field(
        name="🛠️ المطورون",
        value="• المطور الرئيسي: فريق متخصص\n• المساعدون: مجتمع Discord\n• المختبرون: مستخدمو البيتا",
        inline=False
    )
    
    embed.add_field(
        name="📚 المكتبات المستخدمة",
        value="• discord.py - Discord API\n• yt-dlp - استخراج الفيديو\n• PyNaCl - تشفير الصوت\n• FFmpeg - معالجة الصوت",
        inline=False
    )
    
    embed.add_field(
        name="🌐 المصادر",
        value="• YouTube - مقاطع الفيديو\n• SoundCloud - المقاطع الصوتية\n• Discord - منصة البوت",
        inline=False
    )
    
    embed.add_field(
        name="💡 الأفكار والإلهام",
        value="• مجتمع Discord\n• مستخدمو البوت\n• المطورون الآخرون",
        inline=False
    )
    
    embed.set_footer(text="🎵 شكراً لجميع المساهمين!")
    await ctx.send(embed=embed)

@bot.command(name="اعتمادات")
async def credits_arabic(ctx):
    """عرض اعتمادات البوت (بالعربية)"""
    await show_credits(ctx)

@bot.command(name="donate")
async def show_donate(ctx):
    """عرض معلومات التبرع"""
    embed = discord.Embed(title="💝 دعم البوت", color=0x0099ff)
    
    embed.add_field(
        name="🎯 لماذا التبرع؟",
        value="• تطوير ميزات جديدة\n• تحسين الأداء\n• دعم الخوادم\n• صيانة البوت",
        inline=False
    )
    
    embed.add_field(
        name="💳 طرق التبرع",
        value="• PayPal\n• Bitcoin\n• Ethereum\n• بطاقات الائتمان",
        inline=False
    )
    
    embed.add_field(
        name="🎁 مزايا المتبرعين",
        value="• ميزات حصرية\n• أولوية في الدعم\n• إشعارات خاصة\n• شكر خاص",
        inline=False
    )
    
    embed.add_field(
        name="📞 للتواصل",
        value="• Discord: @username\n• Email: support@bot.com\n• Website: www.bot.com",
        inline=False
    )
    
    embed.set_footer(text="🎵 كل تبرع يساعد في تطوير البوت!")
    await ctx.send(embed=embed)

@bot.command(name="تبرع")
async def donate_arabic(ctx):
    """عرض معلومات التبرع (بالعربية)"""
    await show_donate(ctx)

@bot.command(name="status")
async def show_status(ctx):
    """عرض حالة البوت"""
    embed = discord.Embed(title="📊 حالة البوت", color=0x0099ff)
    
    # حالة الاتصال
    embed.add_field(name="🌐 حالة الاتصال", value="🟢 متصل", inline=True)
    embed.add_field(name="🏓 سرعة الاستجابة", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="⏰ وقت التشغيل", value="مستقر", inline=True)
    
    # حالة الخادم الحالي
    guild_id = ctx.guild.id
    is_connected = guild_id in voice_clients
    is_playing = is_connected and voice_clients[guild_id].is_playing()
    queue_length = len(music_queues.get(guild_id, []))
    
    embed.add_field(name="🔊 حالة الصوت", value="🟢 متصل" if is_connected else "🔴 غير متصل", inline=True)
    embed.add_field(name="🎵 حالة التشغيل", value="▶️ يعمل" if is_playing else "⏸️ متوقف", inline=True)
    embed.add_field(name="📝 طول القائمة", value=queue_length, inline=True)
    
    # معلومات النظام
    import platform
    embed.add_field(name="🐍 إصدار Python", value=platform.python_version(), inline=True)
    embed.add_field(name="💻 نظام التشغيل", value=platform.system(), inline=True)
    embed.add_field(name="🔧 إصدار Discord.py", value=discord.__version__, inline=True)
    
    embed.set_footer(text="🎵 البوت يعمل بشكل طبيعي")
    await ctx.send(embed=embed)

@bot.command(name="حالة")
async def status_arabic(ctx):
    """عرض حالة البوت (بالعربية)"""
    await show_status(ctx)

@bot.command(name="uptime")
async def show_uptime(ctx):
    """عرض وقت تشغيل البوت"""
    import time
    
    # حساب وقت التشغيل
    current_time = time.time()
    uptime_seconds = int(current_time - bot.start_time) if hasattr(bot, 'start_time') else 0
    
    # تحويل الوقت إلى أيام وساعات ودقائق
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    
    embed = discord.Embed(title="⏰ وقت تشغيل البوت", color=0x0099ff)
    
    if days > 0:
        embed.add_field(name="📅 الأيام", value=days, inline=True)
    if hours > 0:
        embed.add_field(name="🕐 الساعات", value=hours, inline=True)
    if minutes > 0:
        embed.add_field(name="⏱️ الدقائق", value=minutes, inline=True)
    embed.add_field(name="⏲️ الثواني", value=seconds, inline=True)
    
    embed.add_field(name="🔄 إعادة التشغيل", value="آخر مرة: اليوم", inline=False)
    embed.add_field(name="📊 الحالة", value="🟢 مستقر", inline=False)
    
    embed.set_footer(text="🎵 البوت يعمل بدون توقف!")
    await ctx.send(embed=embed)

@bot.command(name="وقت")
async def uptime_arabic(ctx):
    """عرض وقت تشغيل البوت (بالعربية)"""
    await show_uptime(ctx)

@bot.command(name="server")
async def server_info(ctx):
    """عرض معلومات الخادم"""
    guild = ctx.guild
    
    embed = discord.Embed(title=f"🏠 معلومات الخادم: {guild.name}", color=0x0099ff)
    
    # معلومات عامة
    embed.add_field(name="🆔 معرف الخادم", value=guild.id, inline=True)
    embed.add_field(name="👑 المالك", value=guild.owner.mention, inline=True)
    embed.add_field(name="📅 تاريخ الإنشاء", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    
    # إحصائيات الأعضاء
    embed.add_field(name="👥 إجمالي الأعضاء", value=guild.member_count, inline=True)
    embed.add_field(name="🟢 الأعضاء المتصلون", value=len([m for m in guild.members if m.status != discord.Status.offline]), inline=True)
    embed.add_field(name="🤖 البوتات", value=len([m for m in guild.members if m.bot]), inline=True)
    
    # إحصائيات القنوات
    text_channels = len([c for c in guild.channels if isinstance(c, discord.TextChannel)])
    voice_channels = len([c for c in guild.channels if isinstance(c, discord.VoiceChannel)])
    
    embed.add_field(name="💬 القنوات النصية", value=text_channels, inline=True)
    embed.add_field(name="🔊 القنوات الصوتية", value=voice_channels, inline=True)
    embed.add_field(name="🏷️ الرتب", value=len(guild.roles), inline=True)
    
    # معلومات إضافية
    embed.add_field(name="🌍 المنطقة الزمنية", value=guild.region if hasattr(guild, 'region') else "غير محدد", inline=True)
    embed.add_field(name="🔒 مستوى التحقق", value=str(guild.verification_level), inline=True)
    embed.add_field(name="📊 عدد الإيموجي", value=len(guild.emojis), inline=True)
    
    # صورة الخادم
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    embed.set_footer(text=f"🎵 {guild.name} - خادم موسيقى رائع!")
    await ctx.send(embed=embed)

@bot.command(name="خادم")
async def server_arabic(ctx):
    """عرض معلومات الخادم (بالعربية)"""
    await server_info(ctx)

@bot.command(name="user")
async def user_info(ctx, member: discord.Member = None):
    """عرض معلومات المستخدم"""
    if member is None:
        member = ctx.author
    
    embed = discord.Embed(title=f"👤 معلومات المستخدم: {member.name}", color=0x0099ff)
    
    # معلومات عامة
    embed.add_field(name="🆔 معرف المستخدم", value=member.id, inline=True)
    embed.add_field(name="📅 تاريخ الانضمام", value=member.joined_at.strftime("%Y-%m-%d") if member.joined_at else "غير محدد", inline=True)
    embed.add_field(name="📅 تاريخ إنشاء الحساب", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
    
    # معلومات الحالة
    status_emoji = {
        discord.Status.online: "🟢",
        discord.Status.idle: "🟡",
        discord.Status.dnd: "🔴",
        discord.Status.offline: "⚫"
    }
    
    embed.add_field(name="📊 الحالة", value=f"{status_emoji.get(member.status, '❓')} {str(member.status)}", inline=True)
    embed.add_field(name="🎮 النشاط", value=member.activity.name if member.activity else "لا يوجد", inline=True)
    embed.add_field(name="🎭 الحالة المخصصة", value=member.activity.state if member.activity and hasattr(member.activity, 'state') else "لا يوجد", inline=True)
    
    # معلومات الرتب
    roles = [role.mention for role in member.roles[1:]]  # استبعاد @everyone
    roles_text = " ".join(roles) if roles else "لا توجد رتب"
    
    embed.add_field(name="🏷️ الرتب", value=roles_text[:1024] if len(roles_text) <= 1024 else roles_text[:1021] + "...", inline=False)
    
    # معلومات إضافية
    embed.add_field(name="🎨 لون الرتب", value=str(member.color) if member.color != discord.Color.default() else "افتراضي", inline=True)
    embed.add_field(name="🤖 نوع الحساب", value="بوت" if member.bot else "مستخدم عادي", inline=True)
    embed.add_field(name="🔒 الحساب", value="متحقق" if member.verified else "غير متحقق", inline=True)
    
    # صورة المستخدم
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    
    embed.set_footer(text=f"🎵 {member.name} - مستخدم في {ctx.guild.name}")
    await ctx.send(embed=embed)

@bot.command(name="avatar")
async def show_avatar(ctx, member: discord.Member = None):
    """عرض صورة المستخدم"""
    if member is None:
        member = ctx.author
    
    embed = discord.Embed(title=f"🖼️ صورة {member.name}", color=0x0099ff)
    
    if member.avatar:
        embed.set_image(url=member.avatar.url)
        embed.add_field(name="🔗 رابط الصورة", value=f"[اضغط هنا]({member.avatar.url})", inline=False)
    else:
        embed.add_field(name="❌", value="هذا المستخدم لا يملك صورة!", inline=False)
    
    embed.add_field(name="👤 المستخدم", value=member.mention, inline=True)
    embed.add_field(name="🆔 المعرف", value=member.id, inline=True)
    embed.add_field(name="📅 تاريخ الإنشاء", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
    
    embed.set_footer(text=f"🎵 صورة {member.name}")
    await ctx.send(embed=embed)

@bot.command(name="banner")
async def show_banner(ctx):
    """عرض بانر الخادم"""
    guild = ctx.guild
    
    embed = discord.Embed(title=f"🎨 بانر {guild.name}", color=0x0099ff)
    
    if guild.banner:
        embed.set_image(url=guild.banner.url)
        embed.add_field(name="🔗 رابط البانر", value=f"[اضغط هنا]({guild.banner.url})", inline=False)
    else:
        embed.add_field(name="❌", value="هذا الخادم لا يملك بانر!", inline=False)
    
    embed.add_field(name="🏠 الخادم", value=guild.name, inline=True)
    embed.add_field(name="🆔 المعرف", value=guild.id, inline=True)
    embed.add_field(name="👑 المالك", value=guild.owner.mention, inline=True)
    
    embed.set_footer(text=f"🎵 بانر {guild.name}")
    await ctx.send(embed=embed)

@bot.command(name="emoji")
async def show_emoji(ctx, emoji_name: str):
    """عرض معلومات الإيموجي"""
    guild = ctx.guild
    
    # البحث عن الإيموجي
    emoji = discord.utils.get(guild.emojis, name=emoji_name)
    
    if not emoji:
        await ctx.send(f"❌ لم يتم العثور على الإيموجي: {emoji_name}")
        return
    
    embed = discord.Embed(title=f"😀 معلومات الإيموجي: {emoji.name}", color=0x0099ff)
    
    embed.set_image(url=emoji.url)
    embed.add_field(name="🆔 المعرف", value=emoji.id, inline=True)
    embed.add_field(name="📝 الاسم", value=emoji.name, inline=True)
    embed.add_field(name="🔗 الرابط", value=f"[اضغط هنا]({emoji.url})", inline=True)
    
    embed.add_field(name="🏠 الخادم", value=guild.name, inline=True)
    embed.add_field(name="📅 تاريخ الإنشاء", value=emoji.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="👤 المنشئ", value="غير محدد", inline=True)
    
    embed.set_footer(text=f"🎵 إيموجي {emoji.name}")
    await ctx.send(embed=embed)

@bot.command(name="role")
async def show_role(ctx, role_name: str):
    """عرض معلومات الرتبة"""
    guild = ctx.guild
    
    # البحث عن الرتبة
    role = discord.utils.get(guild.roles, name=role_name)
    
    if not role:
        await ctx.send(f"❌ لم يتم العثور على الرتبة: {role_name}")
        return
    
    embed = discord.Embed(title=f"🏷️ معلومات الرتبة: {role.name}", color=role.color)
    
    embed.add_field(name="🆔 المعرف", value=role.id, inline=True)
    embed.add_field(name="📝 الاسم", value=role.name, inline=True)
    embed.add_field(name="🎨 اللون", value=str(role.color), inline=True)
    
    embed.add_field(name="📊 الموقع", value=role.position, inline=True)
    embed.add_field(name="👥 عدد الأعضاء", value=len(role.members), inline=True)
    embed.add_field(name="🔒 منفصلة", value="نعم" if role.hoist else "لا", inline=True)
    
    # الصلاحيات
    permissions = []
    for perm, value in role.permissions:
        if value:
            permissions.append(f"✅ {perm}")
    
    permissions_text = "\n".join(permissions[:10])  # أول 10 صلاحيات
    if len(permissions) > 10:
        permissions_text += f"\n... و {len(permissions) - 10} صلاحيات أخرى"
    
    embed.add_field(name="🔑 الصلاحيات", value=permissions_text, inline=False)
    
    embed.add_field(name="🏠 الخادم", value=guild.name, inline=True)
    embed.add_field(name="📅 تاريخ الإنشاء", value=role.created_at.strftime("%Y-%m-%d"), inline=True)
    
    embed.set_footer(text=f"🎵 رتبة {role.name}")
    await ctx.send(embed=embed)

@bot.command(name="channel")
async def show_channel(ctx, channel_name: str = None):
    """عرض معلومات القناة"""
    if channel_name is None:
        channel = ctx.channel
    else:
        channel = discord.utils.get(ctx.guild.channels, name=channel_name)
    
    if not channel:
        await ctx.send(f"❌ لم يتم العثور على القناة: {channel_name}")
        return
    
    embed = discord.Embed(title=f"📺 معلومات القناة: {channel.name}", color=0x0099ff)
    
    embed.add_field(name="🆔 المعرف", value=channel.id, inline=True)
    embed.add_field(name="📝 الاسم", value=channel.name, inline=True)
    embed.add_field(name="📊 النوع", value=str(channel.type), inline=True)
    
    embed.add_field(name="🏠 الخادم", value=channel.guild.name, inline=True)
    embed.add_field(name="📅 تاريخ الإنشاء", value=channel.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="📍 الموقع", value=channel.position, inline=True)
    
    # معلومات إضافية حسب نوع القناة
    if isinstance(channel, discord.TextChannel):
        embed.add_field(name="💬 نوع القناة", value="نصية", inline=True)
        embed.add_field(name="📝 الموضوع", value=channel.topic if channel.topic else "لا يوجد", inline=True)
        embed.add_field(name="🔒 محمية", value="نعم" if channel.is_nsfw() else "لا", inline=True)
        
    elif isinstance(channel, discord.VoiceChannel):
        embed.add_field(name="🔊 نوع القناة", value="صوتية", inline=True)
        embed.add_field(name="👥 الحد الأقصى", value=channel.user_limit if channel.user_limit else "غير محدد", inline=True)
        embed.add_field(name="🔊 مستوى الصوت", value=f"{channel.bitrate // 1000}kbps", inline=True)
    
    embed.set_footer(text=f"🎵 قناة {channel.name}")
    await ctx.send(embed=embed)

@bot.command(name="bot")
async def show_bot_info(ctx):
    """عرض معلومات البوت"""
    embed = discord.Embed(title=f"🤖 معلومات البوت: {bot.user.name}", color=0x0099ff)
    
    embed.add_field(name="🆔 معرف البوت", value=bot.user.id, inline=True)
    embed.add_field(name="📝 الاسم", value=bot.user.name, inline=True)
    embed.add_field(name="🏷️ المعرف", value=bot.user.discriminator, inline=True)
    
    embed.add_field(name="🏠 عدد الخوادم", value=len(bot.guilds), inline=True)
    embed.add_field(name="👥 عدد المستخدمين", value=len(bot.users), inline=True)
    embed.add_field(name="🏓 سرعة الاستجابة", value=f"{round(bot.latency * 1000)}ms", inline=True)
    
    embed.add_field(name="📅 تاريخ الإنشاء", value=bot.user.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="🔗 رابط الدعوة", value=f"[اضغط هنا](https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot)", inline=True)
    embed.add_field(name="🌐 الموقع", value="https://discord.com", inline=True)
    
    # معلومات النظام
    import platform
    embed.add_field(name="🐍 إصدار Python", value=platform.python_version(), inline=True)
    embed.add_field(name="💻 نظام التشغيل", value=platform.system(), inline=True)
    embed.add_field(name="🔧 إصدار Discord.py", value=discord.__version__, inline=True)
    
    # صورة البوت
    if bot.user.avatar:
        embed.set_thumbnail(url=bot.user.avatar.url)
    
    embed.set_footer(text=f"🎵 {bot.user.name} - بوت موسيقى متطور")
    await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    """معالجة جميع الرسائل"""
    # تجاهل رسائل البوت
    if message.author == bot.user:
        return
    
    # معالجة الأوامر
    await bot.process_commands(message)
    
    # رسالة ترحيب
    if message.content.lower() in ['هلا', 'مرحبا', 'السلام عليكم', 'hello', 'hi']:
        await message.channel.send(f"🎵 أهلاً وسهلاً! استخدم `{DISCORD_PREFIX}أوامر` لرؤية الأوامر المتاحة")

@bot.event
async def on_command_error(ctx, error):
    """معالجة أخطاء الأوامر"""
    if isinstance(error, commands.CommandNotFound):
        return
    
    await ctx.send(f"❌ خطأ: {str(error)}")

@bot.command(name="test_simple")
async def test_simple_command(ctx):
    """اختبار بسيط للبوت"""
    await ctx.send("✅ البوت يعمل بشكل طبيعي! 🎵")
    print(f"✅ تم تنفيذ أمر اختبار من {ctx.author} في {ctx.guild.name}")

@bot.command(name="ping_simple")
async def ping_simple_command(ctx):
    """اختبار بسيط للسرعة"""
    await ctx.send("🏓 Pong! البوت يعمل!")
    print(f"🏓 تم تنفيذ أمر ping بسيط من {ctx.author} في {ctx.guild.name}")

@bot.command(name="hello")
async def hello_command(ctx):
    """أمر ترحيب بسيط"""
    await ctx.send("🎵 أهلاً وسهلاً! البوت يعمل بشكل طبيعي!")
    print(f"🎵 تم تنفيذ أمر ترحيب من {ctx.author} في {ctx.guild.name}")

@bot.command(name="مرحبا")
async def hello_arabic(ctx):
    """أمر ترحيب بسيط (بالعربية)"""
    await hello_command(ctx)

@bot.command(name="اختبار_صوت")
async def voice_test(ctx):
    """اختبار الاتصال الصوتي"""
    if not ctx.author.voice:
        await ctx.send("❌ يجب أن تكون في قناة صوتية!")
        return
    
    voice_channel = ctx.author.voice.channel
    guild_id = ctx.guild.id
    
    try:
        # محاولة الاتصال بالقناة الصوتية
        voice_client = await voice_channel.connect()
        voice_clients[guild_id] = voice_client
        
        await ctx.send(f"✅ تم الاتصال بنجاح! 🎵")
        await ctx.send(f"🔊 القناة: {voice_channel.name}")
        await ctx.send(f"👥 عدد الأعضاء: {len(voice_channel.members)}")
        
        # الخروج بعد 3 ثواني
        await asyncio.sleep(3)
        await voice_client.disconnect()
        del voice_clients[guild_id]
        
        await ctx.send("✅ تم اختبار الاتصال بنجاح! البوت يعمل بشكل طبيعي 🎵")
        
    except Exception as e:
        await ctx.send(f"❌ فشل في الاتصال: {str(e)}")
        if guild_id in voice_clients:
            del voice_clients[guild_id]

@bot.command(name="voice")
async def voice_test_english(ctx):
    """اختبار الاتصال الصوتي (بالإنجليزية)"""
    await voice_test(ctx)

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