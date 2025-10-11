#!/usr/bin/env python3
"""
Fixed Auto-Healing Selenium Job Scraper - Syntax Error Resolved
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
        
        # Enhanced pattern recognition with more aggressive matching
        if field == 'title':
            patterns = [
                r'span[^>]*title="([^"]*)"',  # Span with title attribute
                r'id="jobTitle-[^"]*"',  # JobTitle ID pattern
                r'class="[^"]*jobTitle[^"]*"',  # JobTitle class pattern
                r'class="jcs-JobTitle[^"]*"',  # Current jcs-JobTitle class
                r'data-testid="[^"]*title[^"]*"',  # Title testid
                r'<h[1-6][^>]*class="[^"]*jobTitle[^"]*"',  # H tags with jobTitle
                r'<span[^>]*id="jobTitle-[^"]*"[^>]*>([^<]+)',  # JobTitle span content
                r'aria-label="[^"]*(?:developer|engineer|analyst|manager)[^"]*"'  # Aria labels
            ]
        elif field == 'company':
            patterns = [
                r'data-testid="company-name"',  # Company name testid
                r'class="css-1ssrdda[^"]*"',  # Current company CSS class
                r'class="[^"]*company[^"]*"',  # Generic company class
                r'<span[^>]*data-testid="company-name"[^>]*>([^<]+)',  # Company span content
                r'elementtiming="significant-render"[^>]*>[^<]*<[^>]*data-testid="company-name"',  # Timing attribute
                r'class="company_location[^"]*"[^>]*>[^<]*data-testid="company-name"',  # Company location container
                r'<span[^>]*class="css-1ssrdda[^"]*"[^>]*>([^<]+)'  # CSS class content
            ]
        elif field == 'location':
            patterns = [
                r'data-testid="text-location"',  # Text location testid
                r'class="css-1f06pz4[^"]*"',  # Current location CSS class
                r'class="[^"]*location[^"]*"',  # Generic location class
                r'<div[^>]*data-testid="text-location"[^>]*>([^<]+)',  # Location div content
                r'<span[^>]*>(?:Remote|Mumbai|Delhi|Bengaluru|Bangalore|Hyderabad|Chennai|Pune|Kolkata|Gurgaon|Noida)',  # Indian cities
                r'data-location="[^"]*"',  # Data location attribute
                r'class="company_location[^"]*"[^>]*>[^<]*data-testid="text-location"',  # Company location container
                r'<span[^>]*class="css-1f06pz4[^"]*"[^>]*>([^<]+)'  # CSS class content
            ]
        else:
            patterns = []
        
        # Extract potential selectors with enhanced context analysis
        for pattern in patterns:
            matches = re.finditer(pattern, html_content, re.IGNORECASE)
            for match in matches:
                # Build selector from the match
                if pattern.startswith('id='):
                    # Extract ID selector
                    id_match = re.search(r'id="([^"]*)"', match.group(0))
                    if id_match:
                        adaptive_selectors.append(f'#{id_match.group(1)}')
                
                elif pattern.startswith('class='):
                    # Extract class selector
                    class_match = re.search(r'class="([^"]*)"', match.group(0))
                    if class_match:
                        classes = class_match.group(1).split()
                        for cls in classes:
                            if field.lower() in cls.lower():
                                adaptive_selectors.append(f'.{cls}')
                
                elif pattern.startswith('data-testid=') or pattern.startswith('data-'):
                    # Extract data attribute selector
                    data_match = re.search(r'(data-[^=]+)="([^"]*)"', match.group(0))
                    if data_match:
                        adaptive_selectors.append(f'[{data_match.group(1)}="{data_match.group(2)}"]')
                        adaptive_selectors.append(f'[{data_match.group(1)}]')
                
                # Also try to extract selectors from surrounding context
                context = html_content[max(0, match.start()-200):match.end()+200]
                context_selectors = self._extract_selectors_from_context(context, field)
                adaptive_selectors.extend(context_selectors)
        
        # Add common fallback selectors for each field
        fallback_selectors = {
            'title': ['[role="heading"]', 'h1', 'h2', 'h3', '.title', '[title]'],
            'company': ['[data-company]', '.company', '.employer', '.org', '[href*="company"]'],
            'location': ['[data-location]', '.location', '.city', '.locale', '[class*="loc"]']
        }
        
        if field in fallback_selectors:
            adaptive_selectors.extend(fallback_selectors[field])
        
        # Remove duplicates and return
        unique_selectors = list(set(adaptive_selectors))
        logger.info(f"Generated {len(unique_selectors)} adaptive selectors for {field}: {unique_selectors[:5]}")
        return unique_selectors
    
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
    
    def __init__(self, headless=True):
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
        """Enhanced fuzzy text matching with better patterns"""
        try:
            # Get all text elements from the card
            all_elements = card.find_elements(By.CSS_SELECTOR, '*')
            
            field_patterns = {
                'title': {
                    'keywords': ['developer', 'engineer', 'analyst', 'manager', 'specialist', 'consultant', 'architect', 'lead'],
                    'max_words': 10,
                    'min_words': 2,
                    'exclude_keywords': ['company', 'inc', 'ltd', 'corp', 'pvt', 'technologies']
                },
                'company': {
                    'keywords': ['inc', 'llc', 'ltd', 'corp', 'company', 'technologies', 'systems', 'solutions', 'services', 'group', 'pvt', 'software', 'tech', 'consulting', 'labs', 'global'],
                    'max_words': 6,
                    'min_words': 1,
                    'patterns': [
                        r'^[A-Z][a-zA-Z\s&\-]+(?:Inc|LLC|Ltd|Corp|Company|Technologies|Systems|Solutions|Services|Group|Pvt)\.?$',
                        r'^[A-Z][a-zA-Z\s&\-]+(?: Software| Tech| Labs| Global| Consulting)$',
                        r'^[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,3}$'
                    ],
                    'exclude_keywords': ['developer', 'engineer', 'analyst', 'manager', 'specialist', 'senior', 'junior', 'lead', 'python', 'java', 'data']
                },
                'location': {
                    'keywords': ['mumbai', 'delhi', 'bangalore', 'bengaluru', 'hyderabad', 'chennai', 'pune', 'kolkata', 'india', 'gurgaon', 'noida'],
                    'max_words': 5,
                    'min_words': 1,
                    'patterns': [
                        r'^[A-Z][a-z]+(?:,\s*[A-Z][A-Z]|,\s*India|\s+India)$', 
                        r'^[A-Z][a-z]+$',
                        r'^[A-Z][a-z]+,\s*[A-Z][a-z]+$'
                    ]
                }
            }
            
            if field not in field_patterns:
                return 'N/A'
            
            config = field_patterns[field]
            
            for element in all_elements:
                try:
                    text = element.text.strip()
                    if not text or len(text) > 100:  # Skip empty or very long text
                        continue
                    
                    text_lower = text.lower()
                    word_count = len(text.split())
                    
                    # Check word count limits
                    if word_count < config['min_words'] or word_count > config['max_words']:
                        continue
                    
                    # Check for keywords
                    has_keyword = any(keyword in text_lower for keyword in config['keywords'])
                    
                    # Check regex patterns if available
                    matches_pattern = False
                    if 'patterns' in config:
                        matches_pattern = any(re.match(pattern, text, re.IGNORECASE) for pattern in config['patterns'])
                    
                    # Check for exclusion keywords (don't match titles as companies)
                    has_exclusion = False
                    if 'exclude_keywords' in config:
                        has_exclusion = any(keyword in text_lower for keyword in config['exclude_keywords'])
                    
                    # Special handling for each field
                    if field == 'company' and not has_exclusion and (has_keyword or matches_pattern or (word_count <= 4 and text[0].isupper() and not any(job_word in text_lower for job_word in ['developer', 'engineer', 'analyst', 'manager']))):
                        logger.info(f"FUZZY MATCH: Found {field} via text matching: '{text}'")
                        return text
                    elif field == 'location' and (has_keyword or matches_pattern):
                        logger.info(f"FUZZY MATCH: Found {field} via text matching: '{text}'")
                        return text
                    elif field == 'title' and has_keyword and 2 <= word_count <= 8 and not has_exclusion:
                        logger.info(f"FUZZY MATCH: Found {field} via text matching: '{text}'")
                        return text
                        
                except Exception as e:
                    continue
            
            # If no fuzzy match found, try one more approach - look for elements with specific attributes
            attribute_searches = {
                'company': ['data-company', 'data-employer', 'class*=company', 'class*=employer'],
                'location': ['data-location', 'data-city', 'class*=location', 'class*=city'],
                'title': ['data-title', 'data-job', 'class*=title', 'class*=job']
            }
            
            if field in attribute_searches:
                for attr in attribute_searches[field]:
                    try:
                        if '*=' in attr:
                            # CSS attribute contains selector
                            elements = card.find_elements(By.CSS_SELECTOR, f'[{attr}]')
                        else:
                            # Exact attribute match
                            elements = card.find_elements(By.CSS_SELECTOR, f'[{attr}]')
                        
                        for elem in elements:
                            text = elem.text.strip() or elem.get_attribute('title') or elem.get_attribute('value')
                            if text and 1 <= len(text.split()) <= config['max_words']:
                                logger.info(f"ATTRIBUTE MATCH: Found {field} via attribute: '{text}'")
                                return text
                    except:
                        continue
        
        except Exception as e:
            logger.debug(f"Fuzzy extraction error for {field}: {e}")
        
        return 'N/A'
    
    def extract_job_data(self, card):
        """Extract job data with auto-healing capabilities"""
        try:
            job_data = {'source': 'Indeed', 'scraped_at': datetime.now().isoformat()}
            
            # Field extraction with healing
            field_configs = {
                'title': [
                    'span[title]',  # Main title span with title attribute
                    'span[id^="jobTitle-"]',  # Title span with jobTitle ID
                    'h2.jobTitle a span[title]',  # H2 jobTitle with span title
                    '.jcs-JobTitle span[title]',  # JobTitle class with span
                    'a.jcs-JobTitle span',  # Job title link span
                    'h2.jobTitle span',  # H2 jobTitle span
                    '.css-1baag51 span[title]',  # CSS module class
                    '[data-testid*="title"] span',  # Any title testid
                    'a[data-jk] span[title]'  # Data-jk link with title span
                ],
                'company': [
                    'span[data-testid="company-name"]',  # Main company name selector
                    '.css-1ssrdda',  # Company name CSS class
                    '[data-testid="company-name"]',  # Company testid
                    '.company_location span[data-testid="company-name"]',  # Company in location container
                    'div[data-testid="timing-attribute"] span[data-testid="company-name"]',  # Timing container
                    '.css-1afmp4o span[data-testid="company-name"]',  # CSS module with company
                    'span.css-1ssrdda',  # Direct CSS class
                    '.companyName',  # Legacy company selector
                    'a[data-testid="company-name"]'  # Company link
                ],
                'location': [
                    'div[data-testid="text-location"] span',  # Main location selector
                    '[data-testid="text-location"]',  # Location testid
                    '.css-1f06pz4 span',  # Location CSS class with span
                    '.css-1f06pz4',  # Direct location CSS class
                    'div[data-testid="text-location"]',  # Location div
                    '.company_location div[data-testid="text-location"]',  # Company location container
                    '.company_location span',  # Any span in company location
                    '.companyLocation',  # Legacy location selector
                    'div.css-1f06pz4'  # CSS module location
                ]
            }
            
            # Extract each field
            for field, selectors in field_configs.items():
                job_data[field] = self.smart_extract_field(card, field, selectors)
            
            # Extract URL - UPDATED FOR CURRENT STRUCTURE
            job_data['url'] = 'N/A'
            try:
                # Try multiple URL extraction strategies for current Indeed structure
                url_strategies = [
                    'a.jcs-JobTitle',  # Main job title link
                    'a[data-jk]',  # Link with data-jk attribute
                    'a.css-1baag51',  # CSS module job link
                    'h2.jobTitle a',  # H2 jobTitle link
                    'a[href*="/pagead/clk"]',  # Indeed pagead links
                    'a[href*="/clk"]',  # Generic clk links
                    'a[href*="/viewjob"]',  # Viewjob links
                    'a[role="button"]',  # Button role links
                    'a[data-mobtk]'  # Mobile tracking links
                ]
                
                for selector in url_strategies:
                    try:
                        link_element = card.find_element(By.CSS_SELECTOR, selector)
                        href = link_element.get_attribute('href')
                        if href and (href.startswith('http') or href.startswith('/')):
                            # Ensure full URL for Indeed links
                            if href.startswith('/'):
                                href = 'https://indeed.com' + href
                            job_data['url'] = href
                            logger.debug(f"Found URL with selector {selector}: {href[:80]}")
                            break
                    except NoSuchElementException:
                        continue
                
                # If still no URL found, try to construct from data-jk attribute
                if job_data['url'] == 'N/A':
                    try:
                        # Try to find data-jk on the job card or its children
                        data_jk_selectors = ['[data-jk]', 'a[data-jk]', '*[data-jk]']
                        for dj_selector in data_jk_selectors:
                            try:
                                jk_element = card.find_element(By.CSS_SELECTOR, dj_selector)
                                job_id = jk_element.get_attribute('data-jk')
                                if job_id:
                                    job_data['url'] = f"https://indeed.com/viewjob?jk={job_id}"
                                    logger.debug(f"Constructed URL from job ID: {job_id}")
                                    break
                            except NoSuchElementException:
                                continue
                    except Exception as e:
                        logger.debug(f"Data-jk extraction failed: {e}")
                        
            except Exception as e:
                logger.debug(f"URL extraction error: {e}")
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
                job_card_selectors = [
                    'li.css-1ac2h1w',  # Main job card container
                    '.job_seen_beacon',  # Job card wrapper
                    'div[data-testid="slider_container"]',  # Slider container
                    '.slider_container',  # Alternative slider
                    'div[data-jk]',  # Job cards with data-jk
                    '.result',  # Generic result
                    '.slider_item',  # Individual slider items
                    'li[class*="css-"]',  # CSS module classes
                    '.mosaic-provider-jobcards',  # Provider specific
                    'div.cardOutline'  # Card outline
                ]
                job_cards = []
                
                for selector in job_card_selectors:
                    try:
                        potential_cards = self.wait.until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                        )
                        # Filter out cards that are too small (likely not job cards)
                        job_cards = [card for card in potential_cards if card.size['height'] > 50]
                        if job_cards:
                            logger.info(f"Found {len(job_cards)} job cards with: {selector}")
                            break
                    except TimeoutException:
                        continue
                
                # Alternative: Try to find any container with job-related content
                if not job_cards:
                    try:
                        logger.info("Trying alternative job card detection...")
                        all_divs = self.driver.find_elements(By.TAG_NAME, 'div')
                        for div in all_divs:
                            text = div.text.lower()
                            if any(keyword in text for keyword in ['developer', 'engineer', 'job', 'position', 'role']) and len(text) > 50 and len(text) < 500:
                                job_cards.append(div)
                        if job_cards:
                            logger.info(f"Found {len(job_cards)} job cards via alternative method")
                            job_cards = job_cards[:15]  # Limit to 15
                    except Exception as e:
                        logger.error(f"Alternative detection failed: {e}")
                
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
    logger.info("Starting FIXED AUTO-HEALING Selenium Job Scraper...")
    
    scraper = None
    
    try:
        scraper = AutoHealingScraper(headless=True)
        
        # Search configurations
        searches = [
            {"query": "python developer", "location": "Bengaluru"},
            {"query": "Software Developer Engineer", "location": "Mumbai"},
            {"query": "software engineer", "location": "Delhi"},
            {"query": "software engineer", "location": ""}
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