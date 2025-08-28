import os
from dotenv import load_dotenv

load_dotenv()

# Discord Bot Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_PREFIX = os.getenv('DISCORD_PREFIX', 'ش')

# YouTube Configuration
YOUTUBE_COOKIES_FILE = 'youtube_cookies.txt'

# Audio Configuration
AUDIO_QUALITY = '192k'
MAX_DURATION = 600  # 10 minutes
MAX_QUEUE_SIZE = 50

# Search Configuration
SEARCH_TIMEOUT = 10
MAX_SEARCH_RESULTS = 5 