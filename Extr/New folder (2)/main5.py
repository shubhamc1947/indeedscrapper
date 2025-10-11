#!/usr/bin/env python3
"""
Auto-Healing Selenium Job Scraper with Adaptive Intelligence
Automatically adapts to HTML structure changes using pattern recognition
"""

import time
import random
import json
import logging
import os
import pickle
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote_plus
import difflib
import hashlib

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_heal_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SelectorLearningEngine:
    """AI-powered selector learning and adaptation engine"""
    
    def __init__(self, knowledge_file='selector_knowledge.pkl'):
        self.knowledge_file = knowledge_file
        self.selector_success_rates = defaultdict(lambda: {'success': 0, 'attempts': 0})
        self.html_patterns = defaultdict(list)
        self.field_patterns = {}
        self.last_successful_selectors = {}
        self.html_structure_history = []
        self.load_knowledge()
    
    def load_knowledge(self):
        """Load previous learning data"""
        try:
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, 'rb') as f:
                    data = pickle.load(f)
                    self.selector_success_rates.update(data.get('success_rates', {}))
                    self.html_patterns.update(data.get('html_patterns', {}))
                    self.field_patterns.update(data.get('field_patterns', {}))
                    self.last_successful_selectors.update(data.get('last_successful', {}))
                logger.info("Loaded previous selector knowledge")
        except Exception as e:
            logger.warning(f"Could not load knowledge: {e}")
    
    def save_knowledge(self):
        """Save learned patterns"""
        try:
            data = {
                'success_rates': dict(self.selector_success_rates),
                'html_patterns': dict(self.html_patterns),
                'field_patterns': self.field_patterns,
                'last_successful': self.last_successful_selectors,
                'updated': datetime.now().isoformat()
            }
            with open(self.knowledge_file, 'wb') as f:
                pickle.dump(data, f)
            logger.info("Saved selector knowledge")
        except Exception as e:
            logger.error(f"Could not save knowledge: {e}")
    
    def record_selector_result(self, field, selector, success, html_snippet=""):
        """Record whether a selector worked"""
        key = f"{field}:{selector}"
        self.selector_success_rates[key]['attempts'] += 1
        
        if success:
            self.selector_success_rates[key]['success'] += 1
            self.last_successful_selectors[field] = selector
            
            # Learn HTML patterns for successful extractions
            if html_snippet:
                pattern_hash = hashlib.md5(html_snippet.encode()).hexdigest()
                self.html_patterns[field].append({
                    'pattern': html_snippet[:200],
                    'selector': selector,
                    'timestamp': datetime.now().isoformat(),
                    'hash': pattern_hash
                })
    
    def get_success_rate(self, field, selector):
        """Get success rate for a selector"""
        key = f"{field}:{selector}"
        attempts = self.selector_success_rates[key]['attempts']
        if attempts == 0:
            return 0.5  # Unknown selector gets neutral rating
        return self.selector_success_rates[key]['success'] / attempts
    
    def get_ranked_selectors(self, field, base_selectors):
        """Get selectors ranked by success rate"""
        ranked = []
        for selector in base_selectors:
            success_rate = self.get_success_rate(field, selector)
            ranked.append((selector, success_rate))
        
        # Sort by success rate (highest first)
        ranked.sort(key=lambda x: x[1], reverse=True)
        return [selector for selector, rate in ranked]
    
    def generate_adaptive_selectors(self, field, html_content):
        """Generate new selectors based on HTML analysis"""
        adaptive_selectors = []
        
        # Analyze HTML structure for common patterns
        if field == 'title':
            patterns = [
                r'<[^>]*title[^>]*>([^<]+)',
                r'<h[1-6][^>]*>([^<]+)',
                r'<a[^>]*>([^<]*(?:developer|engineer|analyst)[^<]*)',
                r'<span[^>]*title="([^"]*)"'
            ]
        elif field == 'company':
            patterns = [
                r'<[^>]*company[^>]*>([^<]+)',
                r'<span[^>]*>([A-Z][a-zA-Z\s]+(?:Inc|LLC|Ltd|Corp|Company|Technologies))',
                r'<a[^>]*company[^>]*>([^<]+)'
            ]
        elif field == 'location':
            patterns = [
                r'<[^>]*location[^>]*>([^<]+)',
                r'<span[^>]*>([A-Z][a-z]+,?\s*[A-Z]{2,})',
                r'<div[^>]*>([^<]*(?:Mumbai|Delhi|Bangalore|Hyderabad|Chennai)[^<]*)'
            ]
        else:
            patterns = []
        
        # Extract potential selectors from patterns
        for pattern in patterns:
            matches = re.finditer(pattern, html_content, re.IGNORECASE)
            for match in matches:
                # Try to build selector from context
                context = html_content[max(0, match.start()-100):match.end()+100]
                potential_selectors = self._extract_selectors_from_context(context, field)
                adaptive_selectors.extend(potential_selectors)
        
        return list(set(adaptive_selectors))  # Remove duplicates
    
    def _extract_selectors_from_context(self, context, field):
        """Extract potential CSS selectors from HTML context"""
        selectors = []
        
        # Look for class patterns
        class_matches = re.finditer(r'class="([^"]*(?:' + field + r')[^"]*)"', context, re.IGNORECASE)
        for match in class_matches:
            class_name = match.group(1).split()[0]  # Take first class
            selectors.append(f'.{class_name}')
        
        # Look for data attributes
        data_matches = re.finditer(r'data-[^=]*="[^"]*(?:' + field + r')[^"]*"', context, re.IGNORECASE)
        for match in data_matches:
            attr = match.group(0).split('=')[0]
            selectors.append(f'[{attr}]')
        
        # Look for ID patterns
        id_matches = re.finditer(r'id="([^"]*(?:' + field + r')[^"]*)"', context, re.IGNORECASE)
        for match in id_matches:
            selectors.append(f'#{match.group(1)}')
        
        return selectors
    
    def detect_structure_change(self, current_html):
        """Detect if HTML structure has significantly changed"""
        if not self.html_structure_history:
            self.html_structure_history.append(current_html[:1000])
            return False
        
        # Compare with recent structures
        recent_structure = self.html_structure_history[-1]
        similarity = difflib.SequenceMatcher(None, recent_structure, current_html[:1000]).ratio()
        
        # If similarity is too low, structure has changed
        if similarity < 0.7:
            logger.warning(f"HTML structure change detected (similarity: {similarity:.2f})")
            self.html_structure_history.append(current_html[:1000])
            
            # Keep only recent history
            if len(self.html_structure_history) > 10:
                self.html_structure_history = self.html_structure_history[-10:]
            
            return True
        
        return False

class AutoHealingScraper:
    """Self-healing scraper that adapts to website changes"""
    
    def __init__(self, headless=False):
        self.driver = None
        self.wait = None
        self.total_jobs_found = 0
        self.headless = headless
        
        # Initialize learning engine
        self.learning_engine = SelectorLearningEngine()
        
        # Failure tracking
        self.consecutive_failures = 0
        self.max_consecutive_failures = 5
        self.healing_attempts = 0
        self.max_healing_attempts = 3
        
        # Performance tracking
        self.performance_metrics = {
            'extractions_attempted': 0,
            'extractions_successful': 0,
            'healing_events': 0,
            'structure_changes_detected': 0
        }
        
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome WebDriver with stealth"""
        try:
            logger.info("Setting up auto-healing Chrome WebDriver...")
            
            options = Options()
            if self.headless:
                options.add_argument('--headless=new')
            
            # Stealth options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-images')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Execute stealth script
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.chrome = {runtime: {}};
            """)
            
            self.wait = WebDriverWait(self.driver, 15)
            logger.info("Auto-healing driver setup complete")
            
        except Exception as e:
            logger.error(f"Driver setup failed: {e}")
            raise
    
    def smart_extract_field(self, card, field, base_selectors):
        """Intelligently extract field using adaptive learning"""
        self.performance_metrics['extractions_attempted'] += 1
        
        # Get HTML content for analysis
        card_html = card.get_attribute('outerHTML')
        
        # Detect structure changes
        if self.learning_engine.detect_structure_change(card_html):
            self.performance_metrics['structure_changes_detected'] += 1
            logger.info(f"Structure change detected, triggering healing for {field}")
            return self.heal_extraction(card, field, card_html)
        
        # Get ranked selectors based on success history
        ranked_selectors = self.learning_engine.get_ranked_selectors(field, base_selectors)
        
        # Try selectors in order of success rate
        for selector in ranked_selectors:
            try:
                element = card.find_element(By.CSS_SELECTOR, selector)
                extracted_text = element.get_attribute('title') or element.text.strip()
                
                if extracted_text and len(extracted_text) > 1:
                    # Success! Record it
                    self.learning_engine.record_selector_result(
                        field, selector, True, card_html[:500]
                    )
                    self.performance_metrics['extractions_successful'] += 1
                    self.consecutive_failures = 0
                    
                    logger.debug(f"Extracted {field}: '{extracted_text}' using {selector}")
                    return extracted_text
                    
            except NoSuchElementException:
                # Record failure
                self.learning_engine.record_selector_result(field, selector, False)
                continue
        
        # All base selectors failed, trigger healing
        self.consecutive_failures += 1
        logger.warning(f"All base selectors failed for {field}, triggering healing")
        return self.heal_extraction(card, field, card_html)
    
    def heal_extraction(self, card, field, card_html):
        """Auto-healing mechanism when extraction fails"""
        self.healing_attempts += 1
        self.performance_metrics['healing_events'] += 1
        
        logger.info(f"HEALING: Attempting auto-heal for {field} (attempt {self.healing_attempts})")
        
        if self.healing_attempts > self.max_healing_attempts:
            logger.error("Max healing attempts reached")
            return 'N/A'
        
        # Generate adaptive selectors
        adaptive_selectors = self.learning_engine.generate_adaptive_selectors(field, card_html)
        logger.info(f"Generated {len(adaptive_selectors)} adaptive selectors for {field}")
        
        # Try adaptive selectors
        for selector in adaptive_selectors:
            try:
                element = card.find_element(By.CSS_SELECTOR, selector)
                extracted_text = element.get_attribute('title') or element.text.strip()
                
                if extracted_text and len(extracted_text) > 1:
                    # Healing success!
                    logger.info(f"HEALING SUCCESS: Found {field} using adaptive selector: {selector}")
                    self.learning_engine.record_selector_result(field, selector, True, card_html[:500])
                    self.healing_attempts = 0
                    self.consecutive_failures = 0
                    return extracted_text
                    
            except NoSuchElementException:
                continue
        
        # Try fuzzy text matching as last resort
        return self.fuzzy_text_extraction(card, field)
    
    def fuzzy_text_extraction(self, card, field):
        """Last resort: fuzzy text matching"""
        try:
            all_text_elements = card.find_elements(By.CSS_SELECTOR, '*')
            
            field_keywords = {
                'title': ['developer', 'engineer', 'analyst', 'manager', 'specialist', 'consultant'],
                'company': ['inc', 'llc', 'ltd', 'corp', 'company', 'technologies', 'systems'],
                'location': ['mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 'pune']
            }
            
            keywords = field_keywords.get(field, [])
            
            for element in all_text_elements:
                text = element.text.strip().lower()
                if any(keyword in text for keyword in keywords) and len(text.split()) <= 10:
                    logger.info(f"FUZZY MATCH: Found {field} via text matching: {text}")
                    return element.text.strip()
            
        except Exception as e:
            logger.debug(f"Fuzzy extraction failed: {e}")
        
        return 'N/A'
    
    def extract_job_data(self, card):
        """Extract job data with auto-healing capabilities"""
        try:
            job_data = {'source': 'Indeed', 'scraped_at': datetime.now().isoformat()}
            
            # Field extraction with healing
            field_configs = {
                'title': [
                    'h2.jobTitle a span[title]',
                    'h2.jobTitle a',
                    '.jobTitle a span[title]',
                    '.jobTitle a',
                    'h2 a span[title]',
                    'h2 a',
                    '[data-testid="job-title"]'
                ],
                'company': [
                    'span[data-testid="company-name"]',
                    '.companyName a span[title]',
                    '.companyName span[title]',
                    '.companyName a',
                    '.companyName',
                    '[data-testid="company-name"]',
                    'a[data-testid="company-name"]'
                ],
                'location': [
                    'div[data-testid="job-location"]',
                    '.companyLocation',
                    '[data-testid="job-location"]',
                    '.locationsContainer'
                ]
            }
            
            # Extract each field
            for field, selectors in field_configs.items():
                job_data[field] = self.smart_extract_field(card, field, selectors)
            
            # Extract URL
            try:
                url_selectors = ['h2.jobTitle a', '.jobTitle a', 'h2 a']
                for selector in url_selectors:
                    try:
                        link_element = card.find_element(By.CSS_SELECTOR, selector)
                        job_data['url'] = link_element.get_attribute('href')
                        break
                    except NoSuchElementException:
                        continue
                else:
                    job_data['url'] = 'N/A'
            except Exception:
                job_data['url'] = 'N/A'
            
            # Set defaults and validate
            for field in ['title', 'company', 'location', 'url']:
                if field not in job_data or not job_data[field]:
                    job_data[field] = 'N/A'
            
            job_data['salary'] = 'Not specified'
            job_data['description'] = 'N/A'
            
            # Only return if we got essential data
            if job_data['title'] != 'N/A':
                return job_data
            else:
                logger.warning("Failed to extract essential job data")
                return None
                
        except Exception as e:
            logger.error(f"Job extraction error: {e}")
            return None
    
    def scrape_indeed_with_healing(self, query, location="", max_pages=2):
        """Scrape Indeed with auto-healing capabilities"""
        logger.info(f"Auto-healing scrape: '{query}' in '{location}' (max {max_pages} pages)")
        
        jobs = []
        
        try:
            # Build URL
            base_url = "https://indeed.com/jobs"
            params = f"?q={quote_plus(query)}&l={quote_plus(location)}&sort=date&fromage=7"
            url = base_url + params
            
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            time.sleep(random.uniform(3, 6))
            
            for page in range(max_pages):
                logger.info(f"Processing page {page + 1} with auto-healing")
                
                # Wait for job cards with multiple selectors
                job_card_selectors = ['[data-jk]', '.job_seen_beacon', '.slider_container']
                job_cards = []
                
                for selector in job_card_selectors:
                    try:
                        job_cards = self.wait.until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                        )
                        logger.info(f"Found {len(job_cards)} job cards with: {selector}")
                        break
                    except TimeoutException:
                        continue
                
                if not job_cards:
                    logger.warning(f"No job cards found on page {page + 1}")
                    break
                
                # Extract jobs with healing
                page_jobs = 0
                for i, card in enumerate(job_cards[:15]):  # Limit to 15 per page
                    try:
                        job_data = self.extract_job_data(card)
                        if job_data:
                            jobs.append(job_data)
                            self.log_job(job_data)
                            page_jobs += 1
                        
                        # Small delay between cards
                        time.sleep(random.uniform(0.3, 0.8))
                        
                    except Exception as e:
                        logger.debug(f"Error with job card {i+1}: {e}")
                        continue
                
                logger.info(f"Page {page + 1}: Extracted {page_jobs} jobs")
                
                # Navigate to next page
                if page < max_pages - 1:
                    try:
                        next_selectors = ['a[aria-label="Next Page"]', 'a[aria-label="Next"]']
                        for selector in next_selectors:
                            try:
                                next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                                if next_button.is_enabled():
                                    self.driver.execute_script("arguments[0].click();", next_button)
                                    time.sleep(random.uniform(3, 6))
                                    break
                            except NoSuchElementException:
                                continue
                        else:
                            logger.info("No next page found")
                            break
                    except Exception as e:
                        logger.error(f"Error navigating to next page: {e}")
                        break
            
        except Exception as e:
            logger.error(f"Scraping error: {e}")
        
        logger.info(f"Auto-healing scrape complete: {len(jobs)} jobs found")
        return jobs
    
    def get_performance_report(self):
        """Generate performance and healing report"""
        metrics = self.performance_metrics
        success_rate = (metrics['extractions_successful'] / max(metrics['extractions_attempted'], 1)) * 100
        
        report = f"""
=== AUTO-HEALING PERFORMANCE REPORT ===
Total Extractions Attempted: {metrics['extractions_attempted']}
Successful Extractions: {metrics['extractions_successful']}
Success Rate: {success_rate:.1f}%
Healing Events: {metrics['healing_events']}
Structure Changes Detected: {metrics['structure_changes_detected']}
Jobs Found: {self.total_jobs_found}
========================================
"""
        return report
    
    def log_job(self, job_data):
        """Log job with performance tracking"""
        self.total_jobs_found += 1
        
        job_info = f"""
================================================================================
AUTO-HEALED JOB #{self.total_jobs_found} - {job_data.get('source', 'Unknown')}
================================================================================
Title: {job_data.get('title', 'N/A')}
Company: {job_data.get('company', 'N/A')}
Location: {job_data.get('location', 'N/A')}
Salary: {job_data.get('salary', 'N/A')}
URL: {job_data.get('url', 'N/A')}
================================================================================
"""
        logger.info(job_info)
    
    def close(self):
        """Close browser and save learning data"""
        if self.driver:
            self.driver.quit()
        
        # Save learned patterns
        self.learning_engine.save_knowledge()
        
        # Print performance report
        logger.info(self.get_performance_report())
        logger.info("Browser closed and knowledge saved")

def main():
    """Main function with auto-healing"""
    logger.info("Starting AUTO-HEALING Selenium Job Scraper...")
    
    scraper = None
    
    try:
        scraper = AutoHealingScraper(headless=True)
        
        # Search configurations
        searches = [
            {"query": "python developer", "location": "Bengaluru"},
            {"query": "data scientist", "location": "Mumbai"},
            {"query": "software engineer", "location": "Delhi"}
        ]
        
        all_jobs = []
        
        for i, search in enumerate(searches, 1):
            try:
                logger.info(f"\n{'#'*80}")
                logger.info(f"AUTO-HEALING SEARCH {i}/{len(searches)}: {search['query']} in {search['location']}")
                logger.info(f"{'#'*80}")
                
                jobs = scraper.scrape_indeed_with_healing(
                    query=search["query"],
                    location=search["location"],
                    max_pages=2
                )
                
                all_jobs.extend(jobs)
                logger.info(f"Search {i} complete: {len(jobs)} jobs found")
                
                if i < len(searches):
                    time.sleep(random.uniform(8, 15))
                    
            except Exception as e:
                logger.error(f"Search {i} failed: {e}")
                continue
        
        # Save results
        if all_jobs:
            filename = f"auto_healed_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_jobs, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to: {filename}")
        
        logger.info(f"\nAUTO-HEALING SCRAPING COMPLETE!")
        logger.info(f"Total jobs found: {len(all_jobs)}")
        
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