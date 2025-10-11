#!/usr/bin/env python3
"""
Fixed Selenium Job Scraper - Python 3.13 Compatible
Uses regular Selenium with advanced stealth techniques
"""

import time
import random
import json
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import sys
from urllib.parse import quote_plus

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('selenium_scraper.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class StealthJobScraper:
    def __init__(self, headless=True):
        self.driver = None
        self.wait = None
        self.total_jobs_found = 0
        self.headless = headless
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome WebDriver with maximum stealth"""
        try:
            logger.info("Setting up Chrome WebDriver with stealth mode...")
            
            # Chrome options for maximum stealth
            options = Options()
            
            # Headless mode
            if self.headless:
                options.add_argument('--headless=new')
            
            # Basic stealth options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Advanced stealth options
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')
            options.add_argument('--disable-javascript')
            options.add_argument('--no-first-run')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-infobars')
            
            # Window and user agent
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Performance optimizations
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-logging')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-renderer-backgrounding')
            
            # Memory and process options
            options.add_argument('--memory-pressure-off')
            options.add_argument('--max_old_space_size=4096')
            
            # Create service with ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            
            # Create driver
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Execute stealth scripts
            stealth_js = """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            window.chrome = {
                runtime: {}
            };
            
            Object.defineProperty(navigator, 'permissions', {
                get: () => ({
                    query: () => Promise.resolve({ state: 'granted' }),
                }),
            });
            """
            
            self.driver.execute_script(stealth_js)
            
            self.wait = WebDriverWait(self.driver, 15)
            
            logger.info("Chrome WebDriver setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {e}")
            raise
    
    def human_like_delay(self, min_delay=2, max_delay=5):
        """Add realistic human delays"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def smooth_scroll(self, element=None):
        """Smooth human-like scrolling"""
        try:
            if element:
                # Scroll to specific element
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth'});", element)
            else:
                # Random scroll amounts
                scroll_amounts = [300, 500, 700, 1000]
                scroll_amount = random.choice(scroll_amounts)
                
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            logger.debug(f"Scroll failed: {e}")
    
    def scrape_indeed(self, query, location="", max_pages=3):
        """Scrape Indeed with advanced techniques"""
        logger.info(f"Scraping Indeed for '{query}' in '{location}' (max {max_pages} pages)")
        
        jobs = []
        
        try:
            # Build Indeed URL
            base_url = "https://indeed.com/jobs"
            params = f"?q={quote_plus(query)}&l={quote_plus(location)}&sort=date&fromage=7"
            url = base_url + params
            
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Wait longer for page load
            self.human_like_delay(5, 8)
            
            # Check for blocking
            page_title = self.driver.title.lower()
            if "blocked" in page_title or "access denied" in page_title:
                logger.warning("Detected blocking page")
                return jobs
            
            # Look for CAPTCHA
            if self.driver.find_elements(By.CSS_SELECTOR, '[class*="captcha"], [id*="captcha"]'):
                logger.warning("CAPTCHA detected")
                return jobs
            
            for page in range(max_pages):
                logger.info(f"Processing page {page + 1}")
                
                # Wait for job results
                try:
                    self.wait.until(
                        EC.any_of(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-jk]')),
                            EC.presence_of_element_located((By.CSS_SELECTOR, '.job_seen_beacon')),
                            EC.presence_of_element_located((By.CSS_SELECTOR, '.slider_container'))
                        )
                    )
                except TimeoutException:
                    logger.warning(f"Timeout waiting for job cards on page {page + 1}")
                    break
                
                # Smooth scroll to load content
                for _ in range(3):
                    self.smooth_scroll()
                    time.sleep(2)
                
                # Find job cards with multiple fallbacks
                job_cards = []
                selectors = [
                    '[data-jk]',
                    '.job_seen_beacon',
                    '.slider_container',
                    '.jobsearch-SerpJobCard',
                    'div[data-testid="job-result"]'
                ]
                
                for selector in selectors:
                    try:
                        job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if job_cards:
                            logger.info(f"Found {len(job_cards)} job cards with: {selector}")
                            break
                    except Exception as e:
                        continue
                
                if not job_cards:
                    logger.warning(f"No job cards found on page {page + 1}")
                    break
                
                # Extract jobs with error handling
                page_jobs = 0
                for i, card in enumerate(job_cards):
                    try:
                        # Scroll to job card before extracting
                        self.smooth_scroll(card)
                        time.sleep(random.uniform(0.5, 1.5))
                        
                        job_data = self.extract_indeed_job(card)
                        if job_data:
                            jobs.append(job_data)
                            self.log_job(job_data)
                            page_jobs += 1
                            
                    except Exception as e:
                        logger.debug(f"Error with job card {i+1}: {e}")
                        continue
                
                logger.info(f"Page {page + 1}: Extracted {page_jobs} jobs")
                
                # Go to next page
                if page < max_pages - 1:
                    try:
                        # Look for next button
                        next_selectors = [
                            'a[aria-label="Next Page"]',
                            'a[aria-label="Next"]',
                            'a[title="Next"]',
                            '.pn a[aria-label="Next"]'
                        ]
                        
                        next_button = None
                        for selector in next_selectors:
                            try:
                                next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                                break
                            except NoSuchElementException:
                                continue
                        
                        if next_button and next_button.is_enabled():
                            # Scroll to next button
                            self.smooth_scroll(next_button)
                            time.sleep(2)
                            
                            # Click using JavaScript to avoid interception
                            self.driver.execute_script("arguments[0].click();", next_button)
                            
                            # Wait for page to load
                            self.human_like_delay(3, 6)
                        else:
                            logger.info("No more pages available")
                            break
                            
                    except Exception as e:
                        logger.error(f"Error navigating to next page: {e}")
                        break
            
        except Exception as e:
            logger.error(f"Indeed scraping failed: {e}")
        
        logger.info(f"Indeed: {len(jobs)} jobs scraped successfully")
        return jobs
    
    def extract_indeed_job(self, card):
        """Extract job data from Indeed card with multiple fallbacks"""
        try:
            job_data = {'source': 'Indeed', 'scraped_at': datetime.now().isoformat()}
            
            # Title and URL with multiple selectors
            title_selectors = [
                'h2.jobTitle a span[title]',
                'h2.jobTitle a',
                '.jobTitle a span[title]',
                '.jobTitle a',
                'h2 a span[title]',
                'h2 a'
            ]
            
            for selector in title_selectors:
                try:
                    title_element = card.find_element(By.CSS_SELECTOR, selector)
                    job_data['title'] = title_element.get_attribute('title') or title_element.text.strip()
                    
                    # Get URL from parent link
                    if 'span[title]' in selector:
                        link_element = title_element.find_element(By.XPATH, './ancestor::a')
                    else:
                        link_element = title_element
                    
                    job_data['url'] = link_element.get_attribute('href')
                    break
                except NoSuchElementException:
                    continue
            
            if not job_data.get('title'):
                return None
            
            # Company with fallbacks
            company_selectors = [
                '.companyName a span[title]',
                '.companyName span[title]',
                '.companyName a',
                '.companyName',
                '[data-testid="company-name"]'
            ]
            
            for selector in company_selectors:
                try:
                    company_element = card.find_element(By.CSS_SELECTOR, selector)
                    job_data['company'] = company_element.get_attribute('title') or company_element.text.strip()
                    break
                except NoSuchElementException:
                    continue
                    
            # Location
            location_selectors = [
                '.companyLocation',
                '[data-testid="job-location"]',
                '.locationsContainer'
            ]
            
            for selector in location_selectors:
                try:
                    location_element = card.find_element(By.CSS_SELECTOR, selector)
                    job_data['location'] = location_element.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            # Salary
            salary_selectors = [
                '.salaryText',
                '[data-testid="attribute_snippet_testid"]',
                '.salary-snippet'
            ]
            
            job_data['salary'] = 'Not specified'
            for selector in salary_selectors:
                try:
                    salary_element = card.find_element(By.CSS_SELECTOR, selector)
                    job_data['salary'] = salary_element.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            # Description
            desc_selectors = [
                '.job-snippet',
                '[data-testid="job-snippet"]',
                '.summary'
            ]
            
            job_data['description'] = 'N/A'
            for selector in desc_selectors:
                try:
                    desc_element = card.find_element(By.CSS_SELECTOR, selector)
                    job_data['description'] = desc_element.text.strip()[:200]
                    break
                except NoSuchElementException:
                    continue
            
            # Set defaults
            for field in ['company', 'location']:
                if field not in job_data:
                    job_data[field] = 'N/A'
            
            return job_data
            
        except Exception as e:
            logger.debug(f"Error extracting job: {e}")
            return None
    
    def scrape_naukri(self, query, location=""):
        """Scrape Naukri.com (Indian job site)"""
        logger.info(f"Scraping Naukri for '{query}' in '{location}'")
        
        jobs = []
        
        try:
            # Naukri URL
            base_url = "https://www.naukri.com/jobs-in-india"
            params = f"?k={quote_plus(query)}&l={quote_plus(location)}"
            url = base_url + params
            
            logger.info(f"Navigating to Naukri: {url}")
            self.driver.get(url)
            
            self.human_like_delay(3, 6)
            
            # Scroll to load more jobs
            for _ in range(3):
                self.smooth_scroll()
                time.sleep(2)
            
            # Find job cards
            job_selectors = [
                '.jobTuple',
                '.jobTupleHeader',
                'article.jobTuple'
            ]
            
            job_cards = []
            for selector in job_selectors:
                try:
                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if job_cards:
                        logger.info(f"Found {len(job_cards)} Naukri job cards")
                        break
                except Exception as e:
                    continue
            
            # Extract job data
            for card in job_cards[:15]:  # Limit to 15 jobs
                try:
                    job_data = self.extract_naukri_job(card)
                    if job_data:
                        jobs.append(job_data)
                        self.log_job(job_data)
                        
                except Exception as e:
                    logger.debug(f"Error extracting Naukri job: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Naukri scraping failed: {e}")
        
        logger.info(f"Naukri: {len(jobs)} jobs scraped")
        return jobs
    
    def extract_naukri_job(self, card):
        """Extract job data from Naukri job card"""
        try:
            job_data = {'source': 'Naukri', 'scraped_at': datetime.now().isoformat()}
            
            # Title and URL
            try:
                title_element = card.find_element(By.CSS_SELECTOR, '.title a, h3 a, .jobTitle a')
                job_data['title'] = title_element.text.strip()
                job_data['url'] = title_element.get_attribute('href')
            except NoSuchElementException:
                return None
            
            # Company
            try:
                company_element = card.find_element(By.CSS_SELECTOR, '.companyInfo .subTitle, .companyName')
                job_data['company'] = company_element.text.strip()
            except NoSuchElementException:
                job_data['company'] = 'N/A'
            
            # Experience/Salary
            try:
                salary_element = card.find_element(By.CSS_SELECTOR, '.salary, .expwrap')
                job_data['salary'] = salary_element.text.strip()
            except NoSuchElementException:
                job_data['salary'] = 'Not specified'
            
            # Location
            try:
                location_element = card.find_element(By.CSS_SELECTOR, '.locWdth, .location')
                job_data['location'] = location_element.text.strip()
            except NoSuchElementException:
                job_data['location'] = 'N/A'
            
            job_data['description'] = 'N/A'
            
            return job_data
            
        except Exception as e:
            return None
    
    def search_all_sites(self, query, location=""):
        """Search multiple job sites"""
        logger.info(f"SELENIUM MULTI-SITE SEARCH: '{query}' in '{location}'")
        
        all_jobs = []
        
        # Sites to scrape
        scrapers = [
            ("Indeed", lambda: self.scrape_indeed(query, location, 2)),
            ("Naukri", lambda: self.scrape_naukri(query, location))
        ]
        
        for site_name, scraper_func in scrapers:
            try:
                logger.info(f"Starting {site_name} scraper...")
                
                jobs = scraper_func()
                all_jobs.extend(jobs)
                
                logger.info(f"{site_name} complete: {len(jobs)} jobs found")
                
                # Wait between sites
                self.human_like_delay(8, 15)
                
            except Exception as e:
                logger.error(f"{site_name} scraper failed: {e}")
                continue
        
        # Remove duplicates
        unique_jobs = self.remove_duplicates(all_jobs)
        
        # Save results
        if unique_jobs:
            filename = f"selenium_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(unique_jobs, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to: {filename}")
        
        return unique_jobs
    
    def remove_duplicates(self, jobs):
        """Remove duplicate jobs"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            key = (job.get('title', '').lower(), job.get('company', '').lower())
            if key not in seen and key != ('', ''):
                seen.add(key)
                unique_jobs.append(job)
        
        logger.info(f"Removed {len(jobs) - len(unique_jobs)} duplicates")
        return unique_jobs
    
    def log_job(self, job_data):
        """Log job data"""
        self.total_jobs_found += 1
        
        job_info = f"""
================================================================================
JOB #{self.total_jobs_found} - {job_data.get('source', 'Unknown')}
================================================================================
Title: {job_data.get('title', 'N/A')}
Company: {job_data.get('company', 'N/A')}
Location: {job_data.get('location', 'N/A')}
Salary: {job_data.get('salary', 'Not specified')}
URL: {job_data.get('url', 'N/A')}
================================================================================
"""
        logger.info(job_info)
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")

def main():
    """Main function"""
    logger.info("Starting FIXED Selenium Job Scraper...")
    
    scraper = None
    
    try:
        # Initialize scraper (set headless=False to watch it work)
        scraper = StealthJobScraper(headless=True)
        
        # Search configurations
        searches = [
            {
                "query": "python developer",
                "location": "Bengaluru"
            },
            {
                "query": "software engineer",
                "location": "Mumbai"
            }
        ]
        
        total_jobs = 0
        
        for i, search in enumerate(searches, 1):
            try:
                logger.info(f"\n{'#'*80}")
                logger.info(f"SEARCH {i}/{len(searches)}: {search['query']} in {search['location']}")
                logger.info(f"{'#'*80}")
                
                jobs = scraper.search_all_sites(
                    query=search["query"],
                    location=search["location"]
                )
                
                total_jobs += len(jobs)
                logger.info(f"Search {i} complete: {len(jobs)} unique jobs found")
                
            except Exception as e:
                logger.error(f"Search {i} failed: {e}")
                continue
        
        logger.info(f"\nSELENIUM SCRAPING COMPLETE!")
        logger.info(f"Total jobs found: {total_jobs}")
        logger.info(f"Check selenium_scraper.log and JSON files for results")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Scraper stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")