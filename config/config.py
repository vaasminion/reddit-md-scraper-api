import os

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
MD_FILES = os.path.join('.', 'mdfiles')
API_KEY = os.getenv('REDDIT_SCRAPER_API_KEY')  # set this env var to enable auth
