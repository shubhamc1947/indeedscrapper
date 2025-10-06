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
    "http://fejxdsct:e36rq2djfzwr@104.239.73.111:6654",
    "http://fejxdsct:e36rq2djfzwr@142.147.129.156:5765",
    "http://fejxdsct:e36rq2djfzwr@103.99.33.128:6123",
    "http://fejxdsct:e36rq2djfzwr@103.37.180.144:6538",
    "http://fejxdsct:e36rq2djfzwr@193.161.2.155:6578",
    "http://fejxdsct:e36rq2djfzwr@92.249.34.110:5792",
    "http://fejxdsct:e36rq2djfzwr@93.118.38.246:6390",
    "http://fejxdsct:e36rq2djfzwr@31.57.82.127:6708",
    "http://fejxdsct:e36rq2djfzwr@64.137.104.93:5703",
    "http://fejxdsct:e36rq2djfzwr@104.239.92.205:6845",
    "http://fejxdsct:e36rq2djfzwr@148.135.188.184:7216",
    "http://fejxdsct:e36rq2djfzwr@192.210.191.123:6109",
    "http://fejxdsct:e36rq2djfzwr@209.35.5.40:6731",
    "http://fejxdsct:e36rq2djfzwr@104.143.224.162:6023",
    "http://fejxdsct:e36rq2djfzwr@156.243.179.134:6622",
    "http://fejxdsct:e36rq2djfzwr@104.143.229.197:6125",
    "http://fejxdsct:e36rq2djfzwr@137.59.7.88:5632",
    "http://fejxdsct:e36rq2djfzwr@185.216.106.239:6316",
    "http://fejxdsct:e36rq2djfzwr@45.81.149.236:6668",
    "http://fejxdsct:e36rq2djfzwr@45.250.64.3:5640",
    "http://fejxdsct:e36rq2djfzwr@84.33.62.225:5761",
    "http://fejxdsct:e36rq2djfzwr@46.202.248.65:5559",
    "http://fejxdsct:e36rq2djfzwr@85.198.41.112:6038",
    "http://fejxdsct:e36rq2djfzwr@31.58.23.16:5589",
    "http://fejxdsct:e36rq2djfzwr@45.151.162.189:6591",
    "http://fejxdsct:e36rq2djfzwr@50.114.98.116:5600",
    "http://fejxdsct:e36rq2djfzwr@64.137.104.108:5718",
    "http://fejxdsct:e36rq2djfzwr@179.61.166.171:6594",
    "http://fejxdsct:e36rq2djfzwr@23.27.93.120:5699",
    "http://fejxdsct:e36rq2djfzwr@67.227.42.17:5994",
    "http://fejxdsct:e36rq2djfzwr@174.140.254.157:6748",
    "http://fejxdsct:e36rq2djfzwr@148.135.177.190:5724",
    "http://fejxdsct:e36rq2djfzwr@166.88.58.3:5728",
    "http://fejxdsct:e36rq2djfzwr@184.174.126.31:6323",
    "http://fejxdsct:e36rq2djfzwr@104.239.0.11:5712",
    "http://fejxdsct:e36rq2djfzwr@185.135.10.16:5530",
    "http://fejxdsct:e36rq2djfzwr@46.203.52.178:5701",
    "http://fejxdsct:e36rq2djfzwr@31.58.30.171:6753",
    "http://fejxdsct:e36rq2djfzwr@23.27.93.217:5796",
    "http://fejxdsct:e36rq2djfzwr@89.249.195.229:6984",
    "http://fejxdsct:e36rq2djfzwr@104.239.91.44:5768",
    "http://fejxdsct:e36rq2djfzwr@198.89.123.129:6671",
    "http://fejxdsct:e36rq2djfzwr@23.26.94.180:6162",
    "http://fejxdsct:e36rq2djfzwr@45.39.31.146:5573",
    "http://fejxdsct:e36rq2djfzwr@50.114.98.37:5521",
    "http://fejxdsct:e36rq2djfzwr@45.43.71.62:6660",
    "http://fejxdsct:e36rq2djfzwr@45.43.185.190:6196",
    "http://fejxdsct:e36rq2djfzwr@45.43.83.231:6514",
    "http://fejxdsct:e36rq2djfzwr@23.95.250.85:6358",
    "http://fejxdsct:e36rq2djfzwr@38.225.11.127:5408",
    "http://fejxdsct:e36rq2djfzwr@92.113.7.149:6875",
    "http://fejxdsct:e36rq2djfzwr@104.239.40.86:6705",
    "http://fejxdsct:e36rq2djfzwr@45.41.169.194:6855",
    "http://fejxdsct:e36rq2djfzwr@45.87.69.42:6047",
    "http://fejxdsct:e36rq2djfzwr@92.113.7.135:6861",
    "http://fejxdsct:e36rq2djfzwr@92.113.236.223:6808",
    "http://fejxdsct:e36rq2djfzwr@64.137.37.168:6758",
    "http://fejxdsct:e36rq2djfzwr@193.42.224.60:6261",
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

ITALY_LOCATIONS = {
    # Major cities - highest job density, scrape first
    'tier_1': [
        'Milano, Lombardia',
        'Roma, Lazio',
        'Torino, Piemonte',
        'Napoli, Campania',
        'Bologna, Emilia-Romagna',
        'Firenze, Toscana',
        'Genova, Liguria',
        'Venezia, Veneto',
    ],
    
    # Regional capitals and major secondary cities
    'tier_2': [
        'Bari, Puglia',
        'Palermo, Sicilia',
        'Catania, Sicilia',
        'Verona, Veneto',
        'Padova, Veneto',
        'Brescia, Lombardia',
        'Parma, Emilia-Romagna',
        'Modena, Emilia-Romagna',
        'Trieste, Friuli-Venezia Giulia',
        'Cagliari, Sardegna',
        'Perugia, Umbria',
        'Ancona, Marche',
        'Bergamo, Lombardia',
        'Monza, Lombardia',
        'Reggio Emilia, Emilia-Romagna',
    ],
    
    # Additional important cities
    'tier_3': [
        'Trento, Trentino-Alto Adige',
        'Bolzano, Trentino-Alto Adige',
        'Udine, Friuli-Venezia Giulia',
        'Salerno, Campania',
        'Pescara, Abruzzo',
        'Taranto, Puglia',
        'Prato, Toscana',
        'Livorno, Toscana',
        'Ravenna, Emilia-Romagna',
        'Ferrara, Emilia-Romagna',
        'Rimini, Emilia-Romagna',
        'Sassari, Sardegna',
        'Latina, Lazio',
        'Messina, Sicilia',
        'Siracusa, Sicilia',
    ],
    
    # Remote and nationwide searches
    'remote': [
        'Italia',  # Nationwide search
        'Lavoro da casa',  # Remote work specific
    ]
}

JOB_SEARCH_QUERIES = [
    'python developer',
    'software engineer',
    'data scientist',
    'full stack developer',
    'backend developer',
    'frontend developer',
    'devops engineer',
    'data engineer',
    'machine learning engineer',
    'web developer',
    'mobile developer',
    'cloud engineer',
    'system administrator',
    'database administrator',
    'network engineer',
    'security engineer',
    'QA engineer',
    'technical support',
    'IT manager',
    'project manager',
]

# Scraping strategy configuration
MULTI_LOCATION_CONFIG = {
    'enabled_tiers': ['tier_1', 'tier_2', 'remote'],  # Which tiers to scrape
    'max_pages_per_location': 5,  # Pages to scrape per location
    'delay_between_locations_min': 180,  # 3 minutes minimum
    'delay_between_locations_max': 300,  # 5 minutes maximum
    'delay_between_queries_min': 300,  # 5 minutes between different queries
    'delay_between_queries_max': 420,  # 7 minutes between different queries
    'max_retries_per_location': 2,  # Retry failed locations
    'continue_on_error': True,  # Continue to next location if one fails
}