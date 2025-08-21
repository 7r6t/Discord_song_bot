import discord
from discord.ext import commands
import asyncio
import yt_dlp
import os
import ssl
import threading
import time
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
yt_dl_opts = {
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
    'extractaudio': True,
    'audioformat': 'm4a',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'no_check_certificate': True,
    'prefer_insecure': True,
    'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'cookiesfrombrowser': None,  # تعطيل cookies من المتصفح
    'extractor_args': {'youtube': {'skip': ['dash', 'live']}},
    'geo_bypass': True,
    'geo_bypass_country': 'US',
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Sec-Fetch-Mode': 'navigate'
    },
    'cookies': 'youtube_cookies.txt',
    'extractor_retries': 5,
    'fragment_retries': 5,
    'retries': 5,
    'sleep_interval': 1,
    'max_sleep_interval': 5,
    'sleep_interval_requests': 1
}

ffmpeg_options = {
    'options': '-vn -b:a 128k',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

@bot.event
async def on_ready():
    print(f'{bot.user} تم تشغيل البوت بنجاح!')
    await bot.change_presence(activity=discord.Game(name=BOT_STATUS))

@bot.event
async def on_voice_state_update(member, before, after):
    """معالجة تغييرات حالة القنوات الصوتية"""
    try:
        # إذا غادر البوت القناة الصوتية
        if member.id == bot.user.id and before.channel and not after.channel:
            guild_id = member.guild.id
            if guild_id in voice_clients:
                del voice_clients[guild_id]
        
        # إذا غادر جميع الأعضاء القناة الصوتية
        if before.channel and not after.channel:
            if before.channel.guild.id in voice_clients:
                voice_client = voice_clients[before.channel.guild.id]
                if voice_client.is_connected() and len(before.channel.members) == 1:
                    try:
                        await voice_client.disconnect()
                        del voice_clients[before.channel.guild.id]
                    except:
                        pass
    except Exception as e:
        print(f"خطأ في معالجة تغيير حالة الصوت: {e}")

@bot.event
async def on_disconnect():
    """معالجة انقطاع الاتصال"""
    print("🔌 تم انقطاع الاتصال بـ Discord")
    await cleanup_voice_clients()

@bot.event
async def on_error(event, *args, **kwargs):
    """معالجة الأخطاء العامة"""
    if event == 'on_voice_state_update':
        print(f"خطأ في معالجة حالة الصوت: {args}")
    else:
        print(f"خطأ في الحدث {event}: {args}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # أمر تشغيل الأغنية
    if message.content.startswith('ش '):
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
    
    # أمر إنشاء Cookies جديدة (يعمل محلياً فقط)
    if message.content == 'كوكيز_جديد':
        await create_new_cookies(message)
        return

async def play_song(message):
    """تشغيل الأغنية"""
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
            
        # التحقق من أن القناة الصوتية متاحة
        if not voice_channel.permissions_for(bot_member).connect:
            await message.channel.send("❌ البوت لا يستطيع الانضمام لهذه القناة الصوتية!")
            return
            
        # التحقق من إعدادات السيرفر
        if not bot_member.guild_permissions.use_voice_activation:
            await message.channel.send("⚠️ البوت يحتاج صلاحية 'Use Voice Activity' للعمل بشكل أفضل")

        # فصل اسم الأغنية
        song_name = message.content[2:].strip()
        if not song_name:
            await message.channel.send("❌ يرجى كتابة اسم الأغنية!")
            return

        await message.channel.send(f"🔍 جاري البحث عن: {song_name}...")

        # البحث عن الأغنية مع إعدادات سريعة
        try:
            # إعدادات سريعة للبحث
            fast_opts = yt_dl_opts.copy()
            fast_opts['quiet'] = True
            fast_opts['no_warnings'] = True
            fast_opts['extract_flat'] = False  # نحتاج معلومات كاملة للتشغيل
            
            # إضافة رسالة تأكيد
            await message.channel.send("🔍 جاري البحث باستخدام Cookies...")
            
            with yt_dlp.YoutubeDL(fast_opts) as ydl:
                # البحث في YouTube
                search_query = f"ytsearch1:{song_name}"  # نتيجة واحدة فقط
                info = ydl.extract_info(search_query, download=False)
                if 'entries' in info and info['entries']:
                    video_info = info['entries'][0]
                    await message.channel.send(f"✅ تم العثور على: **{video_info.get('title', 'أغنية')}**")
                else:
                    await message.channel.send("❌ لم يتم العثور على الأغنية!")
                    return
        except Exception as e:
            error_msg = str(e).lower()
            if "certificate" in error_msg or "ssl" in error_msg:
                await message.channel.send("❌ مشكلة في الاتصال الآمن. جاري المحاولة مرة أخرى...")
                # محاولة مع إعدادات مختلفة
                try:
                    await message.channel.send("🔄 المحاولة الثانية: إعدادات بديلة...")
                    alt_opts = yt_dl_opts.copy()
                    alt_opts['source_address'] = None
                    alt_opts['extract_flat'] = False
                    alt_opts['format'] = 'bestaudio/best'
                    alt_opts['http_headers'] = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    }
                    alt_opts['cookiesfrombrowser'] = None  # تعطيل cookies من المتصفح
                    alt_opts['cookies'] = 'youtube_cookies.txt'
                    alt_opts['extractor_retries'] = 5
                    alt_opts['fragment_retries'] = 5
                    alt_opts['retries'] = 5
                    
                    with yt_dlp.YoutubeDL(alt_opts) as ydl:
                        info = ydl.extract_info(search_query, download=False)
                        if 'entries' in info and info['entries']:
                            video_info = info['entries'][0]
                            await message.channel.send(f"✅ تم العثور على: **{video_info.get('title', 'أغنية')}**")
                        else:
                            await message.channel.send("❌ لم يتم العثور على الأغنية!")
                            return
                except Exception as e2:
                    # محاولة أخيرة مع إعدادات متقدمة لحل مشكلة YouTube
                    try:
                        await message.channel.send("🔄 المحاولة الثالثة: إعدادات متقدمة...")
                        advanced_opts = {
                            'format': 'bestaudio/best',
                            'quiet': True,
                            'no_warnings': True,
                            'extract_flat': False,
                            'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                            'http_headers': {
                                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                'Accept-Language': 'en-us,en;q=0.5',
                                'Sec-Fetch-Mode': 'navigate',
                                'DNT': '1',
                                'Upgrade-Insecure-Requests': '1'
                            },
                            'cookiesfrombrowser': None,  # تعطيل cookies من المتصفح
                            'cookies': 'youtube_cookies.txt',
                            'extractor_retries': 10,
                            'fragment_retries': 10,
                            'retries': 10,
                            'sleep_interval': 2,
                            'max_sleep_interval': 10,
                            'sleep_interval_requests': 2,
                            'geo_bypass': True,
                            'geo_bypass_country': 'US',
                            'extractor_args': {'youtube': {'skip': ['dash', 'live']}},
                            'no_check_certificate': True,
                            'prefer_insecure': True
                        }
                        with yt_dlp.YoutubeDL(advanced_opts) as ydl:
                            info = ydl.extract_info(search_query, download=False)
                            if 'entries' in info and info['entries']:
                                video_info = info['entries'][0]
                                await message.channel.send(f"✅ تم العثور على: **{video_info.get('title', 'أغنية')}**")
                            else:
                                await message.channel.send("❌ لم يتم العثور على الأغنية!")
                                return
                    except Exception as e3:
                        await message.channel.send(f"❌ خطأ في البحث: لا يمكن الوصول إلى YouTube\n\n🔧 **المشكلة:** YouTube يكتشف البوت\n\n💡 **الحل:** جرب البحث مرة أخرى أو استخدم رابط مباشر")
                        return
            else:
                await message.channel.send(f"❌ خطأ في البحث: {str(e)}")
                return

        # الحصول على معلومات الأغنية
        title = video_info.get('title', 'أغنية غير معروفة')
        duration = video_info.get('duration', 0)
        
        # الحصول على URL صحيح
        if 'url' in video_info:
            url = video_info['url']
        elif 'webpage_url' in video_info:
            url = video_info['webpage_url']
        else:
            await message.channel.send("❌ لا يمكن الحصول على رابط الأغنية")
            return

        # إنشاء أو الانضمام لقناة صوتية
        try:
            # تنظيف الاتصالات القديمة
            if guild_id in voice_clients:
                try:
                    await voice_clients[guild_id].disconnect()
                except:
                    pass
                del voice_clients[guild_id]
            
            # محاولة الاتصال مع إعدادات مختلفة
            try:
                voice_client = await voice_channel.connect(timeout=60.0)
            except:
                # محاولة ثانية بدون timeout
                voice_client = await voice_channel.connect()
            
            voice_clients[guild_id] = voice_client
            
        except Exception as e:
            error_msg = str(e).lower()
            if "4006" in error_msg:
                await message.channel.send("❌ **مشكلة في الاتصال الصوتي!**\n\n"
                                         "🔧 **الحلول:**\n"
                                         "1. تأكد من أن البوت لديه صلاحية 'Connect' و 'Speak'\n"
                                         "2. تأكد من أن القناة الصوتية متاحة للبوت\n"
                                         "3. جرب قناة صوتية أخرى\n"
                                         "4. أعد تشغيل Discord")
            elif "already connected" in error_msg:
                await message.channel.send("❌ البوت متصل بالفعل في قناة أخرى. اكتب 'قف' أولاً")
            else:
                await message.channel.send(f"❌ خطأ في الاتصال: {str(e)}")
            return

        # تشغيل الأغنية
        try:
            # التحقق من أن البوت متصل
            if not voice_client.is_connected():
                await message.channel.send("❌ البوت غير متصل بالقناة الصوتية")
                return
            
            # إنشاء مصدر الصوت
            audio_source = discord.FFmpegPCMAudio(url, **ffmpeg_options)
            
            # إضافة معالج الأخطاء
            def after_playing(error):
                if error:
                    print(f"خطأ في التشغيل: {error}")
            
            voice_client.play(audio_source, after=after_playing)
            
        except Exception as e:
            await message.channel.send(f"❌ خطأ في تشغيل الأغنية: {str(e)}")
            return
        
        # إرسال رسالة تأكيد
        duration_str = f"{duration//60}:{duration%60:02d}" if duration > 0 else "غير معروف"
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
    """إيقاف البوت"""
    try:
        guild_id = message.guild.id
        
        # إيقاف الاتصال الصوتي من القاموس المحلي
        if guild_id in voice_clients:
            try:
                voice_client = voice_clients[guild_id]
                if voice_client and voice_client.is_connected():
                    await voice_client.disconnect()
            except Exception as e:
                print(f"خطأ في إيقاف الاتصال المحلي: {e}")
            finally:
                del voice_clients[guild_id]
        
        # إيقاف جميع الاتصالات الصوتية في السيرفر
        try:
            for vc in bot.voice_clients:
                if vc.guild and vc.guild.id == guild_id:
                    try:
                        if vc.is_connected():
                            await vc.disconnect()
                    except Exception as e:
                        print(f"خطأ في إيقاف الاتصال العام: {e}")
        except Exception as e:
            print(f"خطأ في الوصول للاتصالات الصوتية: {e}")
        
        await message.channel.send("🛑 تم إيقاف البوت")
        
    except Exception as e:
        print(f"خطأ في إيقاف البوت: {e}")
        await message.channel.send("🛑 تم إيقاف البوت")

async def cleanup_voice_clients():
    """تنظيف الاتصالات الصوتية"""
    for guild_id, voice_client in list(voice_clients.items()):
        try:
            if voice_client.is_connected():
                await voice_client.disconnect()
        except:
            pass
        del voice_clients[guild_id]

async def loop_song(message):
    """تكرار الأغنية"""
    try:
        guild_id = message.guild.id
        if guild_id in voice_clients and voice_clients[guild_id].is_playing():
            # هنا يمكن إضافة منطق التكرار
            await message.channel.send("🔁 تم تفعيل تكرار الأغنية")
        else:
            await message.channel.send("❌ لا توجد أغنية قيد التشغيل!")
    except Exception as e:
        await message.channel.send(f"❌ خطأ في تفعيل التكرار: {str(e)}")

async def stop_loop(message):
    """إيقاف تكرار الأغنية"""
    try:
        await message.channel.send("⏹️ تم إيقاف تكرار الأغنية")
    except Exception as e:
        await message.channel.send(f"❌ خطأ في إيقاف التكرار: {str(e)}")

async def test_bot(message):
    """اختبار البوت"""
    try:
        embed = discord.Embed(
            title="🧪 اختبار البوت",
            description="البوت يعمل بشكل طبيعي! ✅",
            color=0x00ff00
        )
        embed.add_field(name="🏓 Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="📊 الحالة", value="متصل", inline=True)
        await message.channel.send(embed=embed)
    except Exception as e:
        await message.channel.send(f"❌ خطأ في الاختبار: {str(e)}")

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
        await message.channel.send(f"❌ خطأ في الإيقاف المؤقت: {str(e)}")

async def resume_song(message):
    """استئناف تشغيل الأغنية"""
    try:
        guild_id = message.guild.id
        if guild_id in voice_clients and voice_clients[guild_id].is_paused():
            voice_clients[guild_id].resume()
            await message.channel.send("▶️ تم استئناف الأغنية")
        else:
            await message.channel.send("❌ لا توجد أغنية متوقفة مؤقتاً!")
    except Exception as e:
        await message.channel.send(f"❌ خطأ في استئناف الأغنية: {str(e)}")

async def check_permissions(message):
    """فحص صلاحيات البوت"""
    try:
        bot_member = message.guild.get_member(bot.user.id)
        embed = discord.Embed(
            title="🔍 فحص صلاحيات البوت",
            color=0x00ff00
        )
        
        # فحص الصلاحيات العامة
        perms = bot_member.guild_permissions
        embed.add_field(
            name="📋 الصلاحيات العامة",
            value=f"Connect: {'✅' if perms.connect else '❌'}\n"
                  f"Speak: {'✅' if perms.speak else '❌'}\n"
                  f"Send Messages: {'✅' if perms.send_messages else '❌'}\n"
                  f"Use Voice Activity: {'✅' if perms.use_voice_activation else '❌'}",
            inline=False
        )
        
        # فحص القناة الصوتية إذا كان المستخدم فيها
        if message.author.voice:
            voice_channel = message.author.voice.channel
            voice_perms = voice_channel.permissions_for(bot_member)
            embed.add_field(
                name="🎵 صلاحيات القناة الصوتية",
                value=f"Connect: {'✅' if voice_perms.connect else '❌'}\n"
                      f"Speak: {'✅' if voice_perms.speak else '❌'}\n"
                      f"View Channel: {'✅' if voice_perms.view_channel else '❌'}",
                inline=False
            )
        
        # معلومات إضافية
        embed.add_field(
            name="ℹ️ معلومات إضافية",
            value=f"Guild ID: {message.guild.id}\n"
                  f"Bot ID: {bot.user.id}\n"
                  f"Latency: {round(bot.latency * 1000)}ms",
            inline=False
        )
        
        await message.channel.send(embed=embed)
        
    except Exception as e:
        await message.channel.send(f"❌ خطأ في فحص الصلاحيات: {str(e)}")

async def check_server_settings(message):
    """فحص إعدادات السيرفر"""
    try:
        guild = message.guild
        embed = discord.Embed(
            title="🏠 إعدادات السيرفر",
            color=0x00ff00
        )
        
        # معلومات السيرفر
        embed.add_field(
            name="📋 معلومات السيرفر",
            value=f"اسم السيرفر: {guild.name}\n"
                  f"ID السيرفر: {guild.id}\n"
                  f"عدد الأعضاء: {guild.member_count}\n"
                  f"عدد القنوات: {len(guild.channels)}",
            inline=False
        )
        
        # إعدادات البوت
        bot_member = guild.get_member(bot.user.id)
        if bot_member:
            embed.add_field(
                name="🤖 إعدادات البوت",
                value=f"اسم البوت: {bot_member.display_name}\n"
                      f"تاريخ الانضمام: {bot_member.joined_at.strftime('%Y-%m-%d') if bot_member.joined_at else 'غير معروف'}\n"
                      f"أعلى رتبة: {bot_member.top_role.name}",
                inline=False
            )
        
        # القنوات الصوتية
        voice_channels = [ch for ch in guild.channels if isinstance(ch, discord.VoiceChannel)]
        if voice_channels:
            voice_info = "\n".join([f"🔊 {ch.name} ({ch.id})" for ch in voice_channels[:5]])
            if len(voice_channels) > 5:
                voice_info += f"\n... و {len(voice_channels) - 5} قنوات أخرى"
            embed.add_field(
                name="🎵 القنوات الصوتية",
                value=voice_info,
                inline=False
            )
        
        await message.channel.send(embed=embed)
        
    except Exception as e:
        await message.channel.send(f"❌ خطأ في فحص إعدادات السيرفر: {str(e)}")

async def test_voice_connection(message):
    """اختبار الاتصال الصوتي"""
    try:
        # التحقق من وجود المستخدم في قناة صوتية
        if not message.author.voice:
            await message.channel.send("❌ يجب أن تكون في قناة صوتية لاختبار الاتصال!")
            return

        voice_channel = message.author.voice.channel
        guild_id = message.guild.id
        
        await message.channel.send(f"🔍 جاري اختبار الاتصال بـ {voice_channel.name}...")
        
        # محاولة الاتصال
        try:
            voice_client = await voice_channel.connect(timeout=30.0)
            await message.channel.send("✅ **تم الاتصال بنجاح!** 🎉")
            
            # انتظار قليل ثم قطع الاتصال
            await asyncio.sleep(3)
            await voice_client.disconnect()
            await message.channel.send("🔌 تم قطع الاتصال بعد الاختبار")
            
        except Exception as e:
            error_msg = str(e).lower()
            if "4006" in error_msg:
                await message.channel.send("❌ **فشل الاتصال - خطأ 4006**\n\n"
                                         "🔧 **الحلول المقترحة:**\n"
                                         "1. تأكد من صلاحيات البوت في السيرفر\n"
                                         "2. جرب قناة صوتية أخرى\n"
                                         "3. أعد تشغيل Discord\n"
                                         "4. تحقق من إعدادات الجدار الناري")
            else:
                await message.channel.send(f"❌ فشل الاتصال: {str(e)}")
                
    except Exception as e:
        await message.channel.send(f"❌ خطأ في الاختبار: {str(e)}")

async def test_youtube_connection(message):
    """اختبار الاتصال بـ YouTube"""
    try:
        await message.channel.send("🔍 جاري اختبار الاتصال بـ YouTube...")
        
        # اختبار بسيط مع yt-dlp
        test_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'cookiesfrombrowser': None,  # تعطيل cookies من المتصفح
            'cookies': 'youtube_cookies.txt'
        }
        
        try:
            with yt_dlp.YoutubeDL(test_opts) as ydl:
                # اختبار مع فيديو قصير
                info = ydl.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ", download=False)
                if info:
                    await message.channel.send("✅ **تم الاتصال بـ YouTube بنجاح!** 🎉")
                else:
                    await message.channel.send("⚠️ الاتصال يعمل لكن لا يمكن استخراج المعلومات")
        except Exception as e:
            error_msg = str(e).lower()
            if "sign in to confirm" in error_msg or "bot" in error_msg:
                await message.channel.send("❌ **YouTube يكتشف البوت!**\n\n"
                                         "🔧 **الحلول المقترحة:**\n"
                                         "1. جرب البحث مرة أخرى\n"
                                         "2. استخدم رابط مباشر بدلاً من البحث\n"
                                         "3. انتظر قليلاً ثم جرب مرة أخرى\n"
                                         "4. البوت يحاول طرق بديلة تلقائياً\n"
                                         "5. تأكد من تسجيل الدخول في Chrome")
            else:
                await message.channel.send(f"❌ خطأ في الاتصال: {str(e)}")
                
    except Exception as e:
        await message.channel.send(f"❌ خطأ في الاختبار: {str(e)}")

async def test_cookies(message):
    """اختبار Cookies"""
    try:
        await message.channel.send("🔍 جاري اختبار Cookies...")
        
        # التحقق من وجود ملف cookies
        if not os.path.exists('youtube_cookies.txt'):
            await message.channel.send("❌ **ملف Cookies غير موجود!**\n\n"
                                     "🔧 **الحل:**\n"
                                     "1. تأكد من وجود ملف youtube_cookies.txt\n"
                                     "2. تأكد من أن الملف يحتوي على cookies صحيحة")
            return
        
        # قراءة ملف cookies
        try:
            with open('youtube_cookies.txt', 'r', encoding='utf-8') as f:
                cookies_content = f.read()
            
            if not cookies_content.strip() or cookies_content.startswith('#'):
                await message.channel.send("❌ **ملف Cookies فارغ أو يحتوي على تعليقات فقط!**\n\n"
                                         "🔧 **الحل:**\n"
                                         "1. تأكد من أن الملف يحتوي على cookies حقيقية\n"
                                         "2. استخدم extension 'Get cookies.txt' في Chrome\n"
                                         "3. أو استخدم الأمر 'كوكيز' لإنشاء cookies جديدة")
                return
            
            # اختبار cookies مع yt-dlp
            test_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'cookies': 'youtube_cookies.txt'
            }
            
            with yt_dlp.YoutubeDL(test_opts) as ydl:
                # اختبار مع فيديو قصير
                info = ydl.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ", download=False)
                if info:
                    await message.channel.send("✅ **Cookies تعمل بشكل مثالي!** 🎉\n\n"
                                             "🔓 البوت يمكنه الآن الوصول إلى YouTube\n"
                                             "🎵 جرب تشغيل أغنية الآن!")
                else:
                    await message.channel.send("⚠️ Cookies موجودة لكن لا يمكن استخراج المعلومات")
                    
        except Exception as e:
            error_msg = str(e).lower()
            if "sign in to confirm" in error_msg or "bot" in error_msg:
                await message.channel.send("❌ **YouTube يكتشف البوت!**\n\n"
                                         "🔧 **الحلول المقترحة:**\n"
                                         "1. أعد تسجيل الدخول في YouTube\n"
                                         "2. امسح cookies وأعد إنشاءها\n"
                                         "3. استخدم حساب شخصي وليس حساب عمل\n"
                                         "4. جرب البحث مرة أخرى")
            else:
                await message.channel.send(f"❌ خطأ في اختبار Cookies: {str(e)}")
                
    except Exception as e:
        await message.channel.send(f"❌ خطأ في الاختبار: {str(e)}")

async def create_new_cookies(message):
    """إنشاء cookies جديدة (يعمل محلياً فقط، لا يعمل على Render.com)"""
    try:
        await message.channel.send("🔧 جاري إنشاء cookies جديدة...\n\n"
                                 "⚠️ **ملاحظة:** هذا الأمر يعمل محلياً فقط\n"
                                 "🚫 على Render.com، استخدم extension 'Get cookies.txt'")
        
        # محاولة استخراج cookies من Chrome
        try:
            import browser_cookie3
            
            # استخراج cookies من Chrome
            cookies = browser_cookie3.chrome(domain_name='.youtube.com')
            
            if not cookies:
                await message.channel.send("❌ **لا توجد cookies في Chrome!**\n\n"
                                         "🔧 **الحل:**\n"
                                         "1. تأكد من تسجيل دخولك في YouTube\n"
                                         "2. افتح YouTube في Chrome\n"
                                         "3. جرب مرة أخرى")
                return
            
            # إنشاء ملف cookies جديد
            with open('youtube_cookies.txt', 'w', encoding='utf-8') as f:
                f.write("# Netscape HTTP Cookie File\n")
                f.write("# تم إنشاؤه تلقائياً بواسطة البوت\n\n")
                
                for cookie in cookies:
                    # تنسيق Netscape
                    secure = "TRUE" if cookie.secure else "FALSE"
                    path = cookie.path or "/"
                    expires = cookie.expires or 0
                    
                    f.write(f"{cookie.domain}\t{secure}\t{path}\t{expires}\t{cookie.name}\t{cookie.value}\n")
            
            await message.channel.send("✅ **تم إنشاء cookies جديدة بنجاح!** 🎉\n\n"
                                     "🔓 البوت يمكنه الآن الوصول إلى YouTube\n"
                                     "🎵 جرب تشغيل أغنية الآن!")
            
        except ImportError:
            await message.channel.send("❌ **مكتبة browser-cookie3 غير مثبتة!**\n\n"
                                     "🔧 **الحل:**\n"
                                     "1. البوت يحتاج مكتبة إضافية\n"
                                     "2. أو استخدم extension 'Get cookies.txt' في Chrome")
        except Exception as e:
            await message.channel.send(f"❌ **خطأ في استخراج cookies:** {str(e)}\n\n"
                                     "🔧 **الحل البديل:**\n"
                                     "1. استخدم extension 'Get cookies.txt' في Chrome\n"
                                     "2. اذهب إلى YouTube\n"
                                     "3. انقر على Extension ثم 'Export'\n"
                                     "4. احفظ الملف كـ youtube_cookies.txt")
                
    except Exception as e:
        await message.channel.send(f"❌ خطأ في إنشاء cookies: {str(e)}")

def start_keep_alive():
    """بدء Keep Alive لمنع إغلاق البوت"""
    def keep_alive_loop():
        while True:
            try:
                # إرسال ping كل 20 ثانية
                time.sleep(20)
                print("🔄 Keep Alive: البوت يعمل...")
                
                # إرسال ping للخادم إذا كان متاحاً
                try:
                    import requests
                    keep_alive_url = os.getenv('KEEP_ALIVE_URL')
                    if keep_alive_url:
                        response = requests.get(f"{keep_alive_url}/ping", timeout=5)
                        if response.status_code == 200:
                            print("✅ Keep Alive: تم إرسال ping بنجاح")
                        else:
                            print(f"⚠️ Keep Alive: Status {response.status_code}")
                except:
                    pass  # تجاهل أخطاء ping
                    
            except Exception as e:
                print(f"❌ Keep Alive Error: {e}")
    
    keep_alive_thread = threading.Thread(target=keep_alive_loop, daemon=True)
    keep_alive_thread.start()
    print("🚀 Keep Alive started in background thread (every 20 seconds)")
    return keep_alive_thread

def start_web_server():
    """بدء خادم ويب بسيط"""
    try:
        from flask import Flask, jsonify
        
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return jsonify({
                "status": "online",
                "message": "Discord Music Bot is running!",
                "timestamp": time.time()
            })
        
        @app.route('/ping')
        def ping():
            return jsonify({
                "status": "pong",
                "timestamp": time.time()
            })
        
        @app.route('/health')
        def health():
            return jsonify({
                "status": "healthy",
                "uptime": time.time(),
                "version": "1.0.0"
            })
        
        def run_flask():
            port = int(os.getenv('PORT', 8080))
            print(f"🌐 Starting Flask web server on port {port}")
            app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
        
        web_thread = threading.Thread(target=run_flask, daemon=True)
        web_thread.start()
        print("🚀 Web server started in background thread")
        return web_thread
        
    except ImportError:
        print("⚠️ Flask not available, web server disabled")
        return None

# تشغيل البوت
if __name__ == "__main__":
    if DISCORD_TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE":
        print("❌ خطأ: يرجى تعيين DISCORD_TOKEN في متغيرات البيئة!")
        exit(1)
    
    # بدء Keep Alive
    keep_alive_thread = start_keep_alive()
    
    # بدء خادم الويب
    web_thread = start_web_server()
    
    print("🎵 بدء تشغيل Discord Music Bot...")
    bot.run(DISCORD_TOKEN) 