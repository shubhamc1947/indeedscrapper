# Indeed Job Scraper with Company Matching

An automated Python pipeline for extracting job postings from Indeed.com with intelligent company matching against a corporate database.

## 🎯 Features

- **Daily Job Extraction**: Automated scraping of job postings from Indeed
- **Smart Company Matching**: 3-tier matching system (URL → Name → Google API)
- **Proxy Rotation**: Automatic proxy switching to avoid IP blocking
- **Database Integration**: PostgreSQL with auto-migration
- **Comprehensive Logging**: Detailed execution logs and statistics
- **Duplicate Detection**: Intelligent duplicate job detection
- **Batch Processing**: Efficient batch processing for large datasets

## 🏗️ Architecture

```
├── main.py                 # Entry point and pipeline orchestrator
├── config.py              # Configuration management
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
├── scripts/
│   └── import_companies.py    # Company data import utility
├── utils/
│   └── db_utils.py           # Database utilities and migrations
├── adapters/
│   └── indeed_adapter.py     # Indeed-specific scraping logic
├── models/
│   └── job_model.py          # Data models and database operations
└── services/
    └── company_matcher.py    # Company matching algorithms
```

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Chrome/Chromium browser (for Playwright)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd indeed-job-scraper
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**
   ```bash
   playwright install chromium
   ```

4. **Setup PostgreSQL database**
   - Create a PostgreSQL database
   - Update `.env` file with your database credentials

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## ⚙️ Configuration

### Environment Variables (.env)

```env
# PostgreSQL Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=jobs_scraper
DB_USER=postgres
DB_PASSWORD=your_password

# Scraping Configuration
MAX_PAGES=3
MIN_DELAY=8
MAX_DELAY=15
PROXY_ENABLED=True
FUZZY_MATCH_THRESHOLD=85

# Google API (Optional)
GOOGLE_API_KEY=your_google_api_key_here

# Logging Configuration
LOG_LEVEL=INFO
```

### Database Setup

The application automatically creates the required database and tables on first run. The schema includes:

- **`companies`**: Company master data with all fields from JSON
- **`it_indeed_scrapped_data`**: Raw scraped job data
- **`it_indeed_result_data`**: Processed jobs with company matching

## 📊 Usage

### 1. Import Company Data

First, import your company database:

```bash
python scripts/import_companies.py companies.json
```

### 2. Run Job Scraping

**Basic usage:**
```bash
python main.py "python developer"
```

**Advanced usage with options:**
```bash
python main.py "python developer" \
  --location "Mumbai, Maharashtra" \
  --max-pages 5 \
  --date-filter "1"
```

**Process existing jobs only (skip scraping):**
```bash
python main.py "python developer" --process-only
```

### 3. Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `query` | Job search query (required) | - |
| `--location, -l` | Location for job search | Mumbai, Maharashtra |
| `--max-pages, -p` | Maximum pages to scrape | 3 |
| `--date-filter, -d` | Date filter ("1"=24h, "3"=3days, "7"=1week) | "1" |
| `--process-only` | Only run processing phase | False |
| `--process-limit` | Limit number of jobs to process | None |

## 🔄 Pipeline Workflow

### Phase 1: Data Extraction
1. **Search Indeed** with specified parameters
2. **Extract job listings** from search results
3. **Fetch detailed information** from individual job pages
4. **Store raw data** in `it_indeed_scrapped_data` table

### Phase 2: Company Matching
The system uses a 3-tier matching strategy:

#### 🔴 Strategy 1: URL Matching (Highest Priority)
- Direct comparison between extracted company URLs and database URLs
- Includes URL normalization (removes www, trailing slashes, etc.)

#### 🟡 Strategy 2: Fuzzy Name Matching (Medium Priority)
- Uses fuzzy string matching between company names
- Matches against both `name` and `ragione_sociale` fields
- Configurable similarity threshold (default: 85%)

#### 🔵 Strategy 3: Google API + VAT Number (Low Priority)
- Searches for company VAT numbers using Google API
- Matches VAT numbers against `iva` field in database
- Requires Google API key

### Phase 3: Data Processing
1. **Process matched jobs** into final format
2. **Store results** in `it_indeed_result_data` table
3. **Generate statistics** and reports

## 📈 Output Format

Each processed job generates a record with the following structure:

```json
{
  "url_job_indeed": "https://in.indeed.com/viewjob?jk=abc123",
  "url_company_indeed": "https://in.indeed.com/cmp/company-name",
  "testo_offerta": "Full job description text...",
  "company_id": 123,
  "data_estrazione": "2025-09-28",
  "url_azienda": "https://company-website.com",
  "match_type": "url",
  "match_confidence": 95.5
}
```

## 📊 Monitoring and Logs

### Log Files
- Execution logs: `indeed_scraper_YYYYMMDD.log`
- Console output with color-coded messages
- Comprehensive error tracking and statistics

### Statistics Dashboard
The pipeline provides detailed statistics including:
- Jobs scraped vs. stored vs. processed
- Company matching success rates by strategy
- Processing errors and performance metrics
- Duplicate detection counts

### Database Queries

**Get today's scraping results:**
```sql
SELECT COUNT(*) FROM it_indeed_result_data 
WHERE data_estrazione = CURRENT_DATE;
```

**Check company matching statistics:**
```sql
SELECT match_type, COUNT(*) as count 
FROM it_indeed_result_data 
WHERE data_estrazione = CURRENT_DATE 
GROUP BY match_type;
```

## 🔧 Customization

### Adding New Job Sources
1. Create a new adapter in `adapters/` directory
2. Implement the required interface methods
3. Update `main.py` to include the new adapter

### Modifying Company Matching
1. Edit `services/company_matcher.py`
2. Add new matching strategies
3. Adjust fuzzy matching thresholds in `config.py`

### Database Schema Changes
1. Update migrations in `utils/db_utils.py`
2. Run the application to auto-apply migrations

## 🚨 Troubleshooting

### Common Issues

**Database Connection Errors:**
- Verify PostgreSQL is running
- Check credentials in `.env` file
- Ensure database exists or can be created

**Scraping Failures:**
- Check proxy configuration
- Verify Chrome/Chromium installation
- Increase delay settings for rate limiting

**Company Matching Issues:**
- Verify company data is imported correctly
- Check fuzzy matching threshold settings
- Review company name normalization logic

### Performance Optimization

**For Large Datasets:**
- Increase batch processing sizes
- Use more aggressive proxy rotation
- Implement parallel processing for company matching

**For Rate Limiting:**
- Increase delay ranges in configuration
- Use more proxies
- Implement exponential backoff

## 📝 Development

### Running Tests
```bash
# Add test commands when available
pytest tests/
```

### Code Style
```bash
# Format code
black .
flake8 .
```

## 📄 License

This project is intended for educational and research purposes. Please ensure compliance with Indeed's Terms of Service and applicable laws regarding web scraping.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review log files for detailed error information
3. Create an issue with relevant details and log excerpts

---

**Note**: This tool is designed for legitimate business use cases involving job market analysis and recruitment. Please use responsibly and in accordance with applicable terms of service and legal requirements.