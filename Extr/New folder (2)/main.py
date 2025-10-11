#!/usr/bin/env python3
"""
Stealth Indeed Job Scraper - Bypasses 403 blocks
Production-grade with anti-detection measures
"""

import requests
import time
import random
import json
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import re
from urllib.parse import urlencode, quote_plus
import sys
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('indeed_jobs.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class StealthIndeedScraper:
    def __init__(self):
        self.session = requests.Session()
        self.consecutive_failures = 0
        self.total_jobs_found = 0
        
        # More realistic user agents
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
        ]
        
        # Setup more realistic headers
        self.base_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
    
    def get_stealth_headers(self):
        """Generate realistic browser headers"""
        headers = self.base_headers.copy()
        headers['User-Agent'] = random.choice(self.user_agents)
        
        # Add some randomization
        if random.choice([True, False]):
            headers['Accept-CH'] = 'Sec-CH-UA, Sec-CH-UA-Mobile, Sec-CH-UA-Platform'
        
        return headers
    
    def wait_between_requests(self):
        """More human-like delays"""
        delay = random.uniform(3, 8)  # Longer delays
        time.sleep(delay)
    
    def make_request(self, url, params=None, retries=5):
        """Make HTTP request with advanced stealth"""
        
        for attempt in range(retries):
            try:
                # Reset session occasionally to avoid tracking
                if attempt > 0 and random.choice([True, False]):
                    self.session = requests.Session()
                
                headers = self.get_stealth_headers()
                
                # Add referer for subsequent requests
                if attempt > 0:
                    headers['Referer'] = 'https://indeed.com/'
                
                logger.info(f"Making request (attempt {attempt + 1}) with User-Agent: {headers['User-Agent'][:50]}...")
                
                response = self.session.get(
                    url, 
                    params=params, 
                    headers=headers,
                    timeout=30,
                    verify=False,  # Skip SSL verification
                    allow_redirects=True
                )
                
                logger.info(f"Response status: {response.status_code}")
                
                # Check for various blocking indicators
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Check for block indicators in content
                    block_indicators = [
                        'blocked', 'captcha', 'security check', 
                        'access denied', 'forbidden', 'bot detected'
                    ]
                    
                    if any(indicator in content for indicator in block_indicators):
                        logger.warning(f"Detected blocking content on attempt {attempt + 1}")
                        raise requests.exceptions.RequestException("Content indicates blocking")
                    
                    self.consecutive_failures = 0
                    return response
                
                elif response.status_code == 403:
                    logger.warning(f"403 Forbidden on attempt {attempt + 1}")
                    
                elif response.status_code == 429:
                    logger.warning(f"Rate limited on attempt {attempt + 1}")
                    
                else:
                    logger.warning(f"Status code {response.status_code} on attempt {attempt + 1}")
                    
            except Exception as e:
                logger.error(f"Request failed on attempt {attempt + 1}: {e}")
                
            self.consecutive_failures += 1
            
            if attempt < retries - 1:
                # Exponential backoff with more randomness
                wait_time = (2 ** attempt) + random.uniform(5, 15)
                logger.info(f"Waiting {wait_time:.2f}s before retry...")
                time.sleep(wait_time)
        
        return None
    
    def try_alternative_search(self, query, location=""):
        """Try alternative Indeed URLs"""
        
        alternative_urls = [
            "https://www.indeed.com/jobs",
            "https://indeed.com/jobs",
            f"https://www.indeed.com/q-{quote_plus(query)}-l-{quote_plus(location)}-jobs.html",
        ]
        
        for url in alternative_urls:
            logger.info(f"Trying alternative URL: {url}")
            
            params = {
                'q': query,
                'l': location,
                'sort': 'date'
            } if 'jobs.html' not in url else None
            
            response = self.make_request(url, params)
            if response:
                return response
                
        return None
    
    def extract_job_data(self, job_element):
        """Extract job data with multiple selector fallbacks"""
        try:
            job_data = {}
            
            # Multiple selectors for title
            title_selectors = [
                'h2.jobTitle a',
                '.jobTitle a', 
                '[data-jk] h2 a',
                '.jobTitle-color-purple',
                'h2 a[data-jk]'
            ]
            
            title_element = None
            for selector in title_selectors:
                title_element = job_element.select_one(selector)
                if title_element:
                    break
            
            if title_element:
                job_data['title'] = title_element.get_text(strip=True)
                href = title_element.get('href', '')
                if href:
                    job_data['url'] = 'https://indeed.com' + href if not href.startswith('http') else href
            
            # Multiple selectors for company
            company_selectors = [
                '.companyName',
                '[data-testid="company-name"]',
                'span[title]',
                '.companyName a'
            ]
            
            for selector in company_selectors:
                company_element = job_element.select_one(selector)
                if company_element:
                    job_data['company'] = company_element.get_text(strip=True)
                    break
            
            # Location
            location_selectors = [
                '.companyLocation',
                '[data-testid="job-location"]', 
                '.locationsContainer'
            ]
            
            for selector in location_selectors:
                location_element = job_element.select_one(selector)
                if location_element:
                    job_data['location'] = location_element.get_text(strip=True)
                    break
            
            # Salary
            salary_selectors = [
                '.salaryText',
                '[data-testid="attribute_snippet_testid"]',
                '.salary-snippet'
            ]
            
            for selector in salary_selectors:
                salary_element = job_element.select_one(selector)
                if salary_element:
                    job_data['salary'] = salary_element.get_text(strip=True)
                    break
            
            # Description
            desc_selectors = [
                '.job-snippet',
                '[data-testid="job-snippet"]',
                '.summary'
            ]
            
            for selector in desc_selectors:
                desc_element = job_element.select_one(selector)
                if desc_element:
                    job_data['description'] = desc_element.get_text(strip=True)
                    break
            
            # Posted date
            date_selectors = [
                '.date',
                '[data-testid="myJobsStateDate"]',
                '.dateLabel'
            ]
            
            for selector in date_selectors:
                date_element = job_element.select_one(selector)
                if date_element:
                    job_data['posted'] = date_element.get_text(strip=True)
                    break
            
            job_data['scraped_at'] = datetime.now().isoformat()
            
            # Only return if we got at least title and company
            if job_data.get('title') and job_data.get('company'):
                return job_data
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error extracting job data: {e}")
            return None
    
    def scrape_page(self, query, location="", page=0):
        """Scrape with multiple strategies"""
        
        logger.info(f"Scraping page {page + 1} for '{query}' in '{location}'")
        
        # First try normal approach
        params = {
            'q': query,
            'l': location,
            'start': page * 10,
            'sort': 'date'
        }
        
        response = self.make_request('https://indeed.com/jobs', params)
        
        # If failed, try alternatives
        if not response:
            logger.info("Normal approach failed, trying alternatives...")
            response = self.try_alternative_search(query, location)
        
        if not response:
            logger.error(f"All methods failed for page {page + 1}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Debug: log page title and check for blocks
        page_title = soup.title.string if soup.title else "No title"
        logger.info(f"Page title: {page_title}")
        
        # Check for blocking
        if any(word in page_title.lower() for word in ['blocked', 'access denied', 'captcha']):
            logger.error(f"Page indicates blocking: {page_title}")
            return []
        
        # Multiple strategies to find job cards
        job_card_selectors = [
            'div[data-jk]',
            '.job_seen_beacon',
            '.slider_container',
            '.jobsearch-SerpJobCard',
            '[data-testid="job-result"]',
            '.result'
        ]
        
        job_cards = []
        for selector in job_card_selectors:
            job_cards = soup.select(selector)
            if job_cards:
                logger.info(f"Found {len(job_cards)} job cards using selector: {selector}")
                break
        
        if not job_cards:
            logger.warning(f"No job cards found on page {page + 1}")
            # Log part of the page content for debugging
            logger.debug(f"Page content preview: {response.text[:500]}")
            return []
        
        jobs = []
        for i, card in enumerate(job_cards):
            job_data = self.extract_job_data(card)
            if job_data:
                jobs.append(job_data)
                self.log_job(job_data)
            else:
                logger.debug(f"Failed to extract data from job card {i+1}")
        
        logger.info(f"Successfully extracted {len(jobs)} jobs from page {page + 1}")
        return jobs
    
    def log_job(self, job_data):
        """Log job data in a structured format"""
        self.total_jobs_found += 1
        
        job_info = f"""
{'='*80}
JOB FOUND #{self.total_jobs_found}
{'='*80}
Title: {job_data.get('title', 'N/A')}
Company: {job_data.get('company', 'N/A')}
Location: {job_data.get('location', 'N/A')}
Salary: {job_data.get('salary', 'Not specified')}
Posted: {job_data.get('posted', 'N/A')}
URL: {job_data.get('url', 'N/A')}
Description: {job_data.get('description', 'N/A')[:200]}...
Scraped: {job_data.get('scraped_at', 'N/A')}
{'='*80}
"""
        logger.info(job_info)
    
    def search_jobs(self, query, location="", max_pages=3):
        """Main search function with enhanced error handling"""
        
        logger.info(f"Starting STEALTH job search: '{query}' in '{location}' (max {max_pages} pages)")
        
        all_jobs = []
        
        for page in range(max_pages):
            
            # Self-healing check
            if self.consecutive_failures > 15:
                logger.error("Too many consecutive failures, stopping")
                break
            
            try:
                jobs = self.scrape_page(query, location, page)
                
                if not jobs:
                    if page == 0:
                        logger.error("No jobs found on first page - might be blocked")
                    else:
                        logger.info("No more jobs found, stopping")
                    break
                
                all_jobs.extend(jobs)
                
                # Longer wait between pages
                if page < max_pages - 1:
                    wait_time = random.uniform(8, 15)
                    logger.info(f"Waiting {wait_time:.1f}s before next page...")
                    time.sleep(wait_time)
                
            except KeyboardInterrupt:
                logger.info("Scraping interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error on page {page + 1}: {e}")
                continue
        
        logger.info(f"SCRAPING COMPLETE! Total jobs found: {len(all_jobs)}")
        
        # Save results
        if all_jobs:
            summary_file = f"indeed_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_file, 'w') as f:
                json.dump(all_jobs, f, indent=2)
            logger.info(f"Results saved to: {summary_file}")
        
        return all_jobs

def main():
    """Main function with better error handling"""
    
    logger.info("🚀 Starting Stealth Indeed Scraper...")
    
    scraper = StealthIndeedScraper()
    
    # CUSTOMIZE YOUR SEARCH HERE
    search_configs = [
        {
            "query": "python developer",
            "location": "Bengaluru, IN", 
            "max_pages": 2
        },
        {
            "query": "software engineer",
            "location": "Mumbai, IN",
            "max_pages": 2
        }
    ]
    
    total_jobs_across_searches = 0
    
    for i, config in enumerate(search_configs, 1):
        try:
            logger.info(f"\n{'#'*100}")
            logger.info(f"SEARCH {i}/{len(search_configs)} - {config['query']} in {config['location']}")
            logger.info(f"{'#'*100}")
            
            jobs = scraper.search_jobs(
                query=config["query"],
                location=config["location"], 
                max_pages=config["max_pages"]
            )
            
            total_jobs_across_searches += len(jobs)
            logger.info(f"✅ Search {i} completed: {len(jobs)} jobs found")
            
            # Wait between different searches
            if i < len(search_configs):
                wait_time = random.uniform(10, 20)
                logger.info(f"Waiting {wait_time:.1f}s before next search...")
                time.sleep(wait_time)
            
        except Exception as e:
            logger.error(f"❌ Search {i} failed: {e}")
            continue
    
    logger.info(f"\n🎉 ALL SEARCHES COMPLETE!")
    logger.info(f"📊 Total jobs found across all searches: {total_jobs_across_searches}")
    logger.info(f"📁 Check indeed_jobs.log and JSON files for all results")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("👋 Scraper stopped by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")