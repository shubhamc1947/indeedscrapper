import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'jobs_scraper'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
}

# Scraping Configuration
SCRAPING_CONFIG = {
    'max_pages': int(os.getenv('MAX_PAGES', 3)),
    'min_delay': int(os.getenv('MIN_DELAY', 12)),
    'max_delay': int(os.getenv('MAX_DELAY', 25)),
    'proxy_enabled': os.getenv('PROXY_ENABLED', 'True').lower() == 'true',
    'fuzzy_match_threshold': int(os.getenv('FUZZY_MATCH_THRESHOLD', 85)),
}

# Google API Configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Proxy Configuration
PROXY_LIST = [
    "http://fejxdsct:e36rq2djfzwr@64.137.73.123:5211",
    "http://fejxdsct:e36rq2djfzwr@45.41.162.192:6829",
    "http://fejxdsct:e36rq2djfzwr@45.127.250.173:5782",
    "http://fejxdsct:e36rq2djfzwr@45.151.161.152:6243",
    "http://fejxdsct:e36rq2djfzwr@104.253.13.50:5482",
    "http://fejxdsct:e36rq2djfzwr@45.131.95.9:5673",
]

# Indeed Configuration
INDEED_CONFIG = {
    'base_url': 'https://it.indeed.com',
    'default_location': 'Italy',
    'user_agents_rotation': True,
    'retry_attempts': 3,
    'retry_delay': 5,
}