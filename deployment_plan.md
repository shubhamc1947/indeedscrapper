# EC2 Deployment - Simple Setup

## One-Time Setup

```bash
# Connect to EC2
ssh -i your-key.pem ubuntu@YOUR-EC2-IP

# Install dependencies
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip git
sudo apt install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2

# Clone your repo
mkdir -p ~/scraper && cd ~/scraper
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git .

# Setup Python
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install python-dotenv
playwright install chromium

# Configure database - create .env file
nano .env
```

Add this to `.env`:
```
# PostgreSQL Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=jobs_scraper
DB_USER=postgres
DB_PASSWORD=admin

# Scraping Configuration
MAX_PAGES=3
MIN_DELAY=8
MAX_DELAY=15
PROXY_ENABLED=True
FUZZY_MATCH_THRESHOLD=85

# Google API (Optional - for fallback company matching)
GOOGLE_API_KEY=your_google_api_key_here

# Logging Configuration
LOG_LEVEL=INFO

# Italy-specific settings (optional overrides)
# DEFAULT_LOCATION=Milano, Italy
# DEFAULT_LOCATION=Roma, Italy  
# DEFAULT_LOCATION=Napoli, Italy
```

Test it works:
```bash
python main.py --query "" --tiers tier_1 --max-pages 1
```

## Setup Cron

Create script:
```bash
nano ~/scraper/run.sh
```

Add this:
```bash
#!/bin/bash
cd /home/ubuntu/scraper
source venv/bin/activate
export $(cat .env | xargs)
mkdir -p logs
python main.py --query "" --tiers tier_1 --max-pages 1 >> logs/$(date +\%Y\%m\%d_\%H\%M).log 2>&1
```

Make executable:
```bash
chmod +x ~/scraper/run.sh
```

Setup cron:
```bash
crontab -e
```

Add this line:
```
0 */6 * * * /home/ubuntu/scraper/run.sh
```

Done. Runs every 6 hours.

## Check Logs

```bash
tail -f ~/scraper/logs/*.log
```

## Update Code

```bash
cd ~/scraper
git pull
```



playwright install chromium
playwright install-deps chromium

sudo nano /etc/postgresql/16/main/postgresql.conf