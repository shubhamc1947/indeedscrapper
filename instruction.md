   # Process existing jobs only
   python main.py "python developer" --process-only
🎯 System Highlights:
3-Tier Company Matching System:

🔴 URL Matching (Priority 1) - Direct URL comparison with normalization
🟡 Fuzzy Name Matching (Priority 2) - 85% similarity threshold using fuzzywuzzy
🔵 Google API + VAT (Priority 3) - Fallback option (requires API key)

Smart Data Processing:

Phase 1: Scrape → Store in it_indeed_scrapped_data
Phase 2: Match companies → Store in it_indeed_result_data
Phase 3: Generate statistics and reports

Robust Error Handling:

Automatic retry mechanisms (3 attempts)
Proxy rotation with failover
Comprehensive logging system
Failed job tracking with reasons

📊 Output Format (Exactly as requested):
json{
  "url_job_indeed": "https://in.indeed.com/viewjob?jk=abc123",
  "url_company_indeed": "https://in.indeed.com/cmp/company-name", 
  "testo_offerta": "Full job description...",
  "company_id": 123,
  "data_estrazione": "2025-09-28",
  "url_azienda": "https://company-website.com",
  "match_type": "url",
  "match_confidence": 95.5
}
🛠️ Advanced Features:
Intelligent Scraping:

Human-like behavior simulation
Random delays and mouse movements
Stealth mode to avoid detection
Rotating user agents

Data Quality:

URL normalization for company matching
Skills extraction from job descriptions
Remote work detection
Experience level parsing

Monitoring & Analytics:

Real-time progress logging
Comprehensive execution reports
Database statistics
Company matching success rates

📈 Sample Usage Scenarios:
Daily Production Run:
# Scrape today's Python jobs in Mumbai
python main.py "python developer" --date-filter "1" --max-pages 10
Bulk Processing:
# Process backlog of unprocessed jobs
python main.py "any query" --process-only --process-limit 1000
Testing Setup:
# Quick test with minimal data
python main.py "software engineer" --max-pages 1
🔍 System Benefits:

Scalable: Handles thousands of jobs efficiently
Reliable: Built-in retry and error recovery
Maintainable: Clean adapter-based architecture
Flexible: Easy to add new job sources
Comprehensive: Full logging and statistics
Production-Ready: Handles edge cases and failures

🎨 Next Steps for You:

Setup Environment:

Configure PostgreSQL database
Update .env with your credentials
Test database connection


Import Company Data:

Place your companies.json file in the project root
Run the import script to populate the database


Test the System:

Start with a small test run (1 page)
Verify data is being stored correctly
Check company matching results


Production Deployment:

Set up daily cron jobs
Monitor logs for any issues
Fine-tune proxy and delay settings



The system is now ready to use! It follows all your requirements:

✅ PostgreSQL database with auto-migrations
✅ Company import script for JSON data
✅ 3-tier company matching strategy
✅ Proxy rotation and retry mechanisms
✅ Proper table structure with date tracking
✅ Comprehensive logging and statistics
✅ Adapter-based architecture for future extensions

Would you like me to explain any specific part in more detail or help you with the initial setup?



# Process existing jobs only
python main.py "python developer" --process-only


# Scrape today's Python jobs in Mumbai
python main.py "python developer" --date-filter "1" --max-pages 10

# Process backlog of unprocessed jobs
python main.py "any query" --process-only --process-limit 1000

# Quick test with minimal data
python main.py "software engineer" --max-pages 1


# Quick import the companies name in the db
python scripts/import_companies.py companies.json


# new commands
# Test with Italian jobs
python main.py "software engineer" --max-pages 1

# Test with specific Italian location
python main.py "sviluppatore python" --location "Milano, Italy" --max-pages 1

# Test with Italian job title
python main.py "ingegnere software" --location "Roma, Italy" --max-pages 1



# new commands 

Indeed Multi-Location Scraper - Usage Guide
Quick Start
1. Basic Single Query, Single Location (Backwards Compatible)
python main.py --query "python developer" --location "Milano, Lombardia"
2. Single Query, Multiple Locations (Tier 1 cities)
python main.py --query "python developer" --tiers tier_1
3. Single Query, All Major Cities + Remote
python main.py --query "software engineer" --tiers tier_1 tier_2 remote
4. Multiple Queries, Multiple Locations
python main.py --queries "python developer" "data scientist" "devops engineer" --tiers tier_1 remote
5. All Predefined Queries, All Locations
python main.py --all-queries --all-tiers
Command Line Arguments
Query Options

--query, -q: Single job search query (e.g., "python developer")
--queries, -Q: Multiple queries (space-separated)
--all-queries: Use all 20 predefined queries from config

Location Options

--location, -l: Single specific location (legacy mode)
`--tiers



# NEW Instruction 

# Indeed Multi-Location Scraper - Usage Guide

## Quick Start

### 1. Basic Single Query, Single Location (Backwards Compatible)
```bash
python main.py --query "python developer" --location "Milano, Lombardia"
```

### 2. Single Query, Multiple Locations (Tier 1 cities)
```bash
python main.py --query "python developer" --tiers tier_1
```

### 3. Single Query, All Major Cities + Remote
```bash
python main.py --query "software engineer" --tiers tier_1 tier_2 remote
```

### 4. Multiple Queries, Multiple Locations
```bash
python main.py --queries "python developer" "data scientist" "devops engineer" --tiers tier_1 remote
```

### 5. All Predefined Queries, All Locations
```bash
python main.py --all-queries --all-tiers
```

## Command Line Arguments

### Query Options
- `--query, -q`: Single job search query (e.g., "python developer")
- `--queries, -Q`: Multiple queries (space-separated)
- `--all-queries`: Use all 20 predefined queries from config

### Location Options
- `--location, -l`: Single specific location (legacy mode)
- `--tiers