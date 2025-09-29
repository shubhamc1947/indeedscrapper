import asyncio
import random
import time
import json
import re
import logging
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Union
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import dateparser

from config import SCRAPING_CONFIG, INDEED_CONFIG, PROXY_LIST
from models.job_model import JobListing

logger = logging.getLogger(__name__)

class IndeedAdapter:
    def __init__(self):
        self.ua = UserAgent()
        self.base_url = INDEED_CONFIG['base_url']
        self.current_proxy_index = 0
        self.retry_attempts = INDEED_CONFIG['retry_attempts']
        self.retry_delay = INDEED_CONFIG['retry_delay']
        self.jobs_processed_with_current_proxy = 0
        self.proxy_switch_threshold = random.randint(3, 7)  # Switch proxy every 3-7 jobs
    
    def get_rotating_headers(self):
        """Get rotating headers for requests"""
        headers_list = [
            {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9,hi-IN;q=0.8,hi;q=0.7',
            },
        ]
        base_headers = {
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'Connection': 'keep-alive',
        }
        selected = random.choice(headers_list)
        return {**selected, **base_headers}
    
    def get_next_proxy(self) -> Optional[str]:
        """Get next proxy from the rotation"""
        if not SCRAPING_CONFIG['proxy_enabled'] or not PROXY_LIST:
            return None
        
        proxy = PROXY_LIST[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(PROXY_LIST)
        return proxy
    
    def should_switch_proxy(self) -> bool:
        """Determine if we should switch proxy based on job count"""
        self.jobs_processed_with_current_proxy += 1
        if self.jobs_processed_with_current_proxy >= self.proxy_switch_threshold:
            self.jobs_processed_with_current_proxy = 0
            self.proxy_switch_threshold = random.randint(3, 7)  # Reset threshold
            return True
        return False
    
    def build_search_url(self, query: str, location: str, start: int = 0, date_filter: str = "1") -> str:
        """Build Indeed search URL with date filtering"""
        formatted_query = query.replace(' ', '+')
        formatted_location = location.replace(', ', '%2C+').replace(' ', '+')
        
        # Build URL with proper parameters for Italian Indeed
        params = {
            'q': formatted_query,
            'l': formatted_location,
            'start': start,
            'sort': 'date',
            'fromage': date_filter
        }
        
        # Add additional parameters for better pagination support
        if start > 0:
            params['from'] = 'searchOnDesktopSerp'
        
        search_url = f"{self.base_url}/jobs?" + "&".join([f"{k}={v}" for k, v in params.items()])
        return search_url
    
    async def scrape_jobs(self, query: str, location: str = None, max_pages: int = None, date_filter: str = "1") -> List[JobListing]:
        """Main method to scrape jobs from Indeed"""
        if location is None:
            location = INDEED_CONFIG['default_location']
        if max_pages is None:
            max_pages = SCRAPING_CONFIG['max_pages']
        
        logger.info(f"Starting Indeed scraping: {query} in {location}, max_pages: {max_pages}")
        
        all_jobs = []
        retry_count = 0
        
        while retry_count < self.retry_attempts:
            try:
                jobs = await self.scrape_with_playwright(query, location, max_pages, date_filter)
                all_jobs.extend(jobs)
                break
                
            except Exception as e:
                retry_count += 1
                logger.error(f"Scraping attempt {retry_count} failed: {e}")
                
                if retry_count < self.retry_attempts:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error("All retry attempts failed")
                    raise
        
        logger.info(f"Scraping completed. Found {len(all_jobs)} jobs")
        return all_jobs
    
    async def scrape_with_playwright(self, query: str, location: str, max_pages: int, date_filter: str) -> List[JobListing]:
        """Scrape using Playwright with proxy rotation"""
        proxy = self.get_next_proxy()
        
        # Parse proxy if available
        proxy_config = None
        if proxy:
            try:
                # Extract user:pass@ip:port from http://user:pass@ip:port
                proxy_parts = proxy.replace('http://', '').split('@')
                if len(proxy_parts) == 2:
                    credentials, server = proxy_parts
                    username, password = credentials.split(':')
                    ip, port = server.split(':')
                    
                    proxy_config = {
                        'server': f'http://{ip}:{port}',
                        'username': username,
                        'password': password
                    }
                    logger.info(f"Using proxy: {ip}:{port}")
            except Exception as e:
                logger.warning(f"Failed to parse proxy {proxy}: {e}")
                proxy_config = None
        
        async with async_playwright() as p:
            browser_args = [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-default-apps',
                '--window-size=1366,768',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-dev-shm-usage',
                '--no-first-run',
                '--disable-gpu',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding'
            ]
            
            browser = await p.chromium.launch(
                headless=False,
                args=browser_args,
                proxy=proxy_config
            )
            
            context = await browser.new_context(
                viewport={'width': 1366, 'height': 768},
                locale='it-IT',
                timezone_id='Europe/Rome',
                user_agent=self.ua.random
            )
            
            # Add stealth scripts
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'languages', {get: () => ['it-IT', 'it', 'en-US', 'en']});
                Object.defineProperty(navigator, 'plugins', {
                    get: () => Array.from({length: 5}, (_, i) => ({name: `Plugin ${i}`}))
                });
                Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
                Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 4});
                window.chrome = {runtime: {}};
                delete window.navigator.webdriver;
                
                // Override canvas fingerprinting
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(type) {
                    const shift = Math.floor(Math.random() * 10);
                    this.getContext('2d').fillStyle = `rgb(${100 + shift}, ${100 + shift}, ${100 + shift})`;
                    return originalToDataURL.apply(this, arguments);
                };
                
                // Override WebGL fingerprinting
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) return 'Intel Inc.';
                    if (parameter === 37446) return 'Intel(R) HD Graphics';
                    return getParameter.apply(this, arguments);
                };
            """)
            
            page = await context.new_page()
            await page.set_extra_http_headers(self.get_rotating_headers())
            
            all_jobs = []
            
            for page_num in range(max_pages):
                try:
                    start = page_num * 10
                    search_url = self.build_search_url(query, location, start, date_filter)
                    
                    logger.info(f"Scraping page {page_num + 1}: {search_url}")
                    
                    await page.goto(search_url, wait_until='networkidle', timeout=60000)
                    await page.wait_for_load_state('domcontentloaded')
                    await self.simulate_human_behavior(page)
                    
                    html_content = await page.content()
                    jobs = self.parse_search_results(html_content)
                    
                    logger.info(f"Found {len(jobs)} jobs on page {page_num + 1}")
                    
                    # For each job, visit the detail page and get full description
                    job_count = 0
                    for job_data in jobs:
                        job_count += 1
                        
                        if job_data.get('job_url_indeed'):
                            try:
                                # Check if we need to create a new context with different proxy
                                current_context = context
                                if self.should_switch_proxy() and SCRAPING_CONFIG['proxy_enabled']:
                                    logger.info(f"Creating new browser context with different proxy for job {job_count}")
                                    current_context = await self.create_new_context_with_proxy(browser)
                                
                                # Skip job detail fetching after too many Cloudflare hits
                                if len(all_jobs) > 15 and len([j for j in all_jobs if j.full_description]) < 5:
                                    logger.warning("Too many Cloudflare blocks, skipping detailed fetching for remaining jobs")
                                    job = JobListing(
                                        title=job_data.get('title', ''),
                                        company_name=job_data.get('company_name', ''),
                                        location=job_data.get('location', ''),
                                        description=job_data.get('description', ''),
                                        job_url_indeed=job_data.get('job_url_indeed', ''),
                                        salary=job_data.get('salary'),
                                        date_posted=job_data.get('date_posted'),
                                        remote=job_data.get('remote', False)
                                    )
                                    all_jobs.append(job)
                                    continue
                                
                                full_details = await self.fetch_job_details(job_data['job_url_indeed'], current_context, proxy)
                                
                                # Close the new context if we created one
                                if current_context != context:
                                    await current_context.close()
                                
                                # Update job data with full details
                                job_data.update(full_details)
                                
                                # Update job data with full details
                                job_data.update(full_details)
                                
                                # Create JobListing object
                                job = JobListing(
                                    title=job_data.get('title', ''),
                                    company_name=job_data.get('company_name', ''),
                                    location=job_data.get('location', ''),
                                    description=job_data.get('description', ''),
                                    job_url_indeed=job_data.get('job_url_indeed', ''),
                                    salary=job_data.get('salary'),
                                    date_posted=job_data.get('date_posted'),
                                    job_type=job_data.get('job_type'),
                                    remote=job_data.get('remote', False),
                                    skills=job_data.get('skills'),
                                    experience_level=job_data.get('experience_level'),
                                    employment_type=job_data.get('employment_type'),
                                    company_rating=job_data.get('company_rating'),
                                    full_description=job_data.get('full_description'),
                                    company_url_indeed=job_data.get('company_url_indeed')
                                )
                                
                                all_jobs.append(job)
                                
                            except Exception as e:
                                logger.warning(f"Failed to fetch details for job {job_data.get('job_url_indeed')}: {e}")
                                # Still add the job with basic info
                                job = JobListing(
                                    title=job_data.get('title', ''),
                                    company_name=job_data.get('company_name', ''),
                                    location=job_data.get('location', ''),
                                    description=job_data.get('description', ''),
                                    job_url_indeed=job_data.get('job_url_indeed', ''),
                                    salary=job_data.get('salary'),
                                    date_posted=job_data.get('date_posted'),
                                    remote=job_data.get('remote', False)
                                )
                                all_jobs.append(job)
                            
                            # Adaptive delay - shorter for early jobs, longer as we get more jobs
                            base_delay = 8 if len(all_jobs) < 10 else 15
                            delay = random.uniform(base_delay, base_delay + 8) + random.uniform(0, 3)
                            logger.info(f"Waiting {delay:.1f} seconds before next job (job #{len(all_jobs) + 1})...")
                            await asyncio.sleep(delay)
                    
                    # Delay between pages with more randomization
                    delay = random.uniform(
                        SCRAPING_CONFIG['min_delay'], 
                        SCRAPING_CONFIG['max_delay']
                    ) + (page_num * random.uniform(3, 8))  # Increased delay
                    
                    logger.info(f"Waiting {delay:.1f} seconds before next page...")
                    await asyncio.sleep(delay)
                    
                except Exception as e:
                    logger.error(f"Error on page {page_num + 1}: {e}")
                    await asyncio.sleep(random.uniform(20, 30))
                    continue
            
            await browser.close()
            return all_jobs
    
    async def fetch_job_details(self, job_url: str, context, current_proxy: str = None) -> Dict:
        """Fetch detailed job information from job page"""
        page = await context.new_page()
        try:
            # Check if we should switch proxy for this job
            if self.should_switch_proxy() and SCRAPING_CONFIG['proxy_enabled']:
                new_proxy = self.get_next_proxy()
                logger.info(f"Switching proxy from {current_proxy} to {new_proxy.split('@')[1] if new_proxy else 'None'}")
            
            # Add random delay before navigation
            await asyncio.sleep(random.uniform(3, 7))
            
            # Set additional headers
            await page.set_extra_http_headers({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin'
            })
            
            # Navigate with realistic timeout
            await page.goto(job_url, wait_until='domcontentloaded', timeout=90000)
            
            # Check for Cloudflare challenge
            if await self.detect_and_handle_cloudflare(page):
                logger.warning(f"Cloudflare detected on {job_url}, attempting to handle...")
                await asyncio.sleep(random.uniform(15, 25))
            
            # Simulate human behavior on job detail pages
            await self.simulate_job_page_behavior(page)
            
            html = await page.content()
            soup = BeautifulSoup(html, 'lxml')
            
            details = {}
            
            # ===== NEW: Extract Company Indeed URL and Rating =====
            # Company Indeed URL from the job detail page
            company_link = soup.select_one('div[data-testid="inlineHeader-companyName"] a[href]')
            if company_link and company_link.get('href'):
                company_url = company_link.get('href')
                # Make absolute URL if relative
                if company_url and not company_url.startswith('http'):
                    details['company_url_indeed'] = urljoin(self.base_url, company_url)
                else:
                    details['company_url_indeed'] = company_url
                logger.info(f"Found company Indeed URL: {details['company_url_indeed']}")
            
            # Company Rating
            rating_elem = soup.select_one('span.css-10jzft1')
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                details['company_rating'] = rating_text
                logger.info(f"Found company rating: {rating_text}")
            
            # ===== NEW: Extract Location and Work Type =====
            # Location
            location_elem = soup.select_one('div[data-testid="inlineHeader-companyLocation"]')
            if location_elem:
                location_text = location_elem.get_text(strip=True)
                details['location'] = location_text
                logger.info(f"Found location: {location_text}")
            
            # Work Type (Remote/Hybrid/Office)
            work_type_elem = soup.select_one('div.css-1fajx0z')
            if work_type_elem:
                work_type_text = work_type_elem.get_text(strip=True).lower()
                
                # Map Italian terms to standardized values
                if 'remoto' in work_type_text or 'lavoro da casa' in work_type_text:
                    details['remote'] = True
                    details['work_type'] = 'remote'
                elif 'ibrido' in work_type_text or 'hybrid' in work_type_text:
                    details['remote'] = False
                    details['work_type'] = 'hybrid'
                else:
                    details['remote'] = False
                    details['work_type'] = 'office'
                
                logger.info(f"Found work type: {details.get('work_type')}")
            
            # ===== EXISTING: Full job description =====
            desc_elem = soup.select_one(
                'div#jobDescriptionText, div.jobsearch-jobDescriptionText, div[data-testid="jobDescriptionText"]'
            )
            if desc_elem:
                details['full_description'] = desc_elem.get_text(separator=' ', strip=True)
            
            # ===== EXISTING: Additional job details =====
            for label in soup.select('div.jobsearch-JobDescriptionSection-sectionItem span.jobsearch-JobDescriptionSection-label'):
                text = label.get_text(strip=True).lower()
                value = label.find_next_sibling('span')
                if not value:
                    continue
                
                value_text = value.get_text(strip=True)
                
                if 'job type' in text or 'employment type' in text or 'tipo di contratto' in text:
                    details['job_type'] = value_text
                elif 'salary' in text or 'pay' in text or 'stipendio' in text:
                    details['salary'] = value_text
            
            # ===== EXISTING: Extract company website from job description =====
            if details.get('full_description'):
                url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*)?'
                urls = re.findall(url_pattern, details['full_description'])
                
                # Filter for likely company websites (not Indeed URLs)
                company_urls = [url for url in urls if 'indeed.com' not in url.lower() 
                            and not url.endswith(('.pdf', '.jpg', '.png', '.gif'))]
                
                if company_urls:
                    details['company_website'] = company_urls[0]
            
            return details
            
        except Exception as e:
            logger.warning(f"Error fetching job details for {job_url}: {e}")
            return {}
        finally:
            await page.close()
    
    def parse_search_results(self, html_content: str) -> List[Dict]:
        """Parse job listings from search results page"""
        soup = BeautifulSoup(html_content, 'lxml')
        jobs = []
        
        # Multiple selectors for different Indeed layouts
        job_containers = soup.select('li.css-1ac2h1w, div[data-jk], .jobsearch-SerpJobCard, .job_seen_beacon, li[data-jk]')
        
        for container in job_containers:
            job = {}
            
            # Title
            title_elem = container.select_one(
                'span[title], span[id*="jobTitle"], h2.jobTitle a, .jobTitle a, h2 a, a[data-testid="job-title"]'
            )
            if title_elem:
                job['title'] = title_elem.get('title') or title_elem.get_text(strip=True)
            else:
                continue  # Skip if no title found
            
            # URL
            url_elem = container.select_one('a[data-jk], h2.jobTitle a, a[data-testid="job-title"]')
            if url_elem:
                href = url_elem.get('href', '')
                job['job_url_indeed'] = urljoin(self.base_url, href) if href and not href.startswith('http') else href
            else:
                job['job_url_indeed'] = None
            
            # Company
            company_elem = container.select_one(
                '[data-testid="company-name"], span.companyName, .companyName, a[data-testid="company-name"]'
            )
            job['company_name'] = company_elem.get_text(strip=True) if company_elem else 'Unknown Company'
            
            # Location
            location_elem = container.select_one(
                '[data-testid="text-location"], div.companyLocation, .companyLocation'
            )
            job['location'] = location_elem.get_text(strip=True) if location_elem else 'Location not specified'
            
            # Description snippet
            desc_elem = container.select_one(
                '[data-testid="belowJobSnippet"], .job-snippet, [data-testid="job-snippet"], .summary'
            )
            job['description'] = desc_elem.get_text(separator=' ', strip=True) if desc_elem else ''
            
            # Salary
            salary_elem = container.select_one('.salary-snippet, [data-testid="salary-snippet"]')
            job['salary'] = salary_elem.get_text(strip=True) if salary_elem else None
            
            # Date posted
            date_elem = container.select_one('.date, [data-testid*="date"]')
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                try:
                    parsed_date = dateparser.parse(date_text)
                    if parsed_date:
                        job['date_posted'] = parsed_date.strftime('%Y-%m-%d')
                except:
                    job['date_posted'] = date_text
            else:
                job['date_posted'] = None
            
            # Remote work detection
            full_text = container.get_text(separator=' ', strip=True).lower()
            remote_keywords = ['remote', 'work from home', 'wfh', 'telecommute', 'hybrid', 'work remotely']
            job['remote'] = any(keyword in full_text for keyword in remote_keywords)
            
            # Skills extraction
            skill_keywords = [
                'python', 'django', 'flask', 'fastapi', 'pandas', 'numpy', 'tensorflow', 
                'pytorch', 'scikit-learn', 'sql', 'postgresql', 'mysql', 'mongodb',
                'redis', 'elasticsearch', 'aws', 'azure', 'gcp', 'docker', 'kubernetes',
                'git', 'jenkins', 'ci/cd', 'linux', 'rest api', 'graphql', 'microservices',
                'javascript', 'react', 'node.js', 'angular', 'vue.js', 'java', 'spring',
                'php', 'laravel', 'c++', 'c#', '.net', 'ruby', 'rails', 'go', 'rust'
            ]
            job['skills'] = [kw for kw in skill_keywords if kw in full_text]
            
            # Experience level
            exp_match = re.search(r'(\d+)[+\s]*years?|senior|junior|lead|principal|entry.level', full_text)
            job['experience_level'] = exp_match.group(0) if exp_match else None
            
            # Employment type
            employment_keywords = {
                'full-time': ['full time', 'full-time', 'permanent'],
                'part-time': ['part time', 'part-time'],
                'contract': ['contract', 'contractor', 'freelance'],
                'internship': ['intern', 'internship', 'trainee']
            }
            for emp_type, keywords in employment_keywords.items():
                if any(keyword in full_text for keyword in keywords):
                    job['employment_type'] = emp_type
                    break
            else:
                job['employment_type'] = None
            
            # Company rating
            rating_elem = container.select_one('.ratingNumber, [data-testid*="rating"]')
            job['company_rating'] = rating_elem.get_text(strip=True) if rating_elem else None
            
            jobs.append(job)
        
        return jobs
    
    async def detect_and_handle_cloudflare(self, page) -> bool:
        """Detect and attempt to handle Cloudflare challenges"""
        try:
            # Wait a moment for page to fully load
            await asyncio.sleep(2)
            
            # Check for common Cloudflare indicators
            cloudflare_indicators = [
                'Checking your browser',
                'DDoS protection by Cloudflare',
                'Ray ID',
                'Additional Verification Required',
                'cf-browser-verification',
                'cf-wrapper',
                'cf-challenge',
                'Verify you are human'
            ]
            
            page_content = await page.content()
            page_text = await page.evaluate('() => document.body ? document.body.innerText : ""')
            page_title = await page.title()
            
            # Check if any Cloudflare indicators are present
            is_cloudflare = (any(indicator.lower() in page_content.lower() for indicator in cloudflare_indicators) or
                           any(indicator.lower() in page_text.lower() for indicator in cloudflare_indicators) or
                           'cloudflare' in page_title.lower())
            
            if is_cloudflare:
                logger.warning("Cloudflare challenge detected, attempting advanced handling...")
                
                # Strategy 1: Wait for automatic resolution (most common)
                logger.info("Waiting for automatic Cloudflare resolution...")
                for attempt in range(3):
                    await asyncio.sleep(8 + (attempt * 3))
                    current_content = await page.content()
                    if not any(indicator.lower() in current_content.lower() for indicator in cloudflare_indicators):
                        logger.info("Cloudflare automatically resolved!")
                        return True
                
                # Strategy 2: Look for and handle interactive elements
                await self.handle_cloudflare_interactions(page)
                
                # Strategy 3: Final wait and verification
                await asyncio.sleep(random.uniform(10, 15))
                
                # Check if we've bypassed Cloudflare
                final_content = await page.content()
                final_text = await page.evaluate('() => document.body ? document.body.innerText : ""')
                still_blocked = any(indicator.lower() in final_content.lower() or 
                                  indicator.lower() in final_text.lower() 
                                  for indicator in cloudflare_indicators)
                
                if still_blocked:
                    logger.warning("Cloudflare challenge persists, skipping this page")
                    return False
                else:
                    logger.info("Successfully bypassed Cloudflare challenge!")
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error handling Cloudflare challenge: {e}")
            return False
    
    async def handle_cloudflare_interactions(self, page):
        """Handle interactive Cloudflare elements"""
        try:
            # Look for checkbox
            checkbox_selectors = [
                'input[type="checkbox"]',
                '.cf-turnstile input',
                '[data-callback] input',
                '.challenge-form input[type="checkbox"]'
            ]
            
            for selector in checkbox_selectors:
                checkbox = await page.query_selector(selector)
                if checkbox:
                    logger.info(f"Found checkbox with selector: {selector}")
                    await asyncio.sleep(random.uniform(1, 3))
                    await checkbox.click()
                    logger.info("Clicked Cloudflare checkbox")
                    await asyncio.sleep(random.uniform(3, 6))
                    break
            
            # Look for verify buttons
            button_selectors = [
                'button:has-text("Verify")',
                'button:has-text("Continue")',
                'button:has-text("Proceed")',
                'input[type="submit"]',
                '[role="button"]:has-text("Verify")',
                '.cf-button'
            ]
            
            for selector in button_selectors:
                try:
                    button = await page.query_selector(selector)
                    if button:
                        button_text = await button.inner_text()
                        if any(text in button_text.lower() for text in ['verify', 'continue', 'proceed']):
                            logger.info(f"Clicking verification button: {button_text}")
                            await asyncio.sleep(random.uniform(1, 2))
                            await button.click()
                            await asyncio.sleep(random.uniform(5, 8))
                            break
                except:
                    continue
            
            # Handle iframe challenges (like Turnstile)
            frames = await page.frames
            for frame in frames:
                try:
                    if 'turnstile' in frame.url or 'challenge' in frame.url:
                        logger.info("Found Cloudflare iframe challenge")
                        iframe_checkbox = await frame.query_selector('input[type="checkbox"]')
                        if iframe_checkbox:
                            await asyncio.sleep(random.uniform(2, 4))
                            await iframe_checkbox.click()
                            logger.info("Clicked iframe checkbox")
                            await asyncio.sleep(random.uniform(5, 10))
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error in Cloudflare interaction handling: {e}")
    
    async def create_new_context_with_proxy(self, browser):
        """Create a new browser context with a different proxy"""
        new_proxy = self.get_next_proxy()
        
        # Parse new proxy
        proxy_config = None
        if new_proxy:
            try:
                proxy_parts = new_proxy.replace('http://', '').split('@')
                if len(proxy_parts) == 2:
                    credentials, server = proxy_parts
                    username, password = credentials.split(':')
                    ip, port = server.split(':')
                    
                    proxy_config = {
                        'server': f'http://{ip}:{port}',
                        'username': username,
                        'password': password
                    }
                    logger.info(f"Using new proxy: {ip}:{port}")
            except Exception as e:
                logger.warning(f"Failed to parse new proxy {new_proxy}: {e}")
                proxy_config = None
        
        # Create new context with new proxy
        new_context = await browser.new_context(
            viewport={'width': 1366, 'height': 768},
            locale='it-IT',
            timezone_id='Europe/Rome',
            user_agent=self.ua.random,
            proxy=proxy_config
        )
        
        # Add stealth scripts to new context
        await new_context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'languages', {get: () => ['it-IT', 'it', 'en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {
                get: () => Array.from({length: 5}, (_, i) => ({name: `Plugin ${i}`}))
            });
            Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
            Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 4});
            window.chrome = {runtime: {}};
            delete window.navigator.webdriver;
            
            // Override canvas fingerprinting
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {
                const shift = Math.floor(Math.random() * 10);
                this.getContext('2d').fillStyle = `rgb(${100 + shift}, ${100 + shift}, ${100 + shift})`;
                return originalToDataURL.apply(this, arguments);
            };
            
            // Override WebGL fingerprinting
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Intel Inc.';
                if (parameter === 37446) return 'Intel(R) HD Graphics';
                return getParameter.apply(this, arguments);
            };
        """)
        
        return new_context
    
    async def simulate_job_page_behavior(self, page):
        """Simulate realistic human behavior on job detail pages"""
        try:
            # Random mouse movements
            for _ in range(random.randint(2, 4)):
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                await page.mouse.move(x, y, steps=random.randint(8, 15))
                await asyncio.sleep(random.uniform(0.3, 1.0))
            
            # Slow, realistic scrolling to read the job description
            viewport_height = await page.evaluate('window.innerHeight')
            total_height = await page.evaluate('document.body.scrollHeight')
            
            # Scroll down in small increments
            current_position = 0
            scroll_increment = random.randint(150, 300)
            
            while current_position < total_height - viewport_height:
                scroll_amount = min(scroll_increment, total_height - viewport_height - current_position)
                await page.evaluate(f'window.scrollBy(0, {scroll_amount})')
                current_position += scroll_amount
                
                # Random pause while "reading"
                reading_time = random.uniform(1.5, 4.0)
                await asyncio.sleep(reading_time)
                
                # Sometimes scroll back up slightly (as if re-reading)
                if random.random() < 0.3:
                    back_scroll = random.randint(50, 150)
                    await page.evaluate(f'window.scrollBy(0, -{back_scroll})')
                    await asyncio.sleep(random.uniform(0.8, 2.0))
                    current_position -= back_scroll
            
            # Sometimes scroll back to top
            if random.random() < 0.4:
                await page.evaluate('window.scrollTo(0, 0)')
                await asyncio.sleep(random.uniform(1, 3))
            
            # Final random mouse movements
            for _ in range(random.randint(1, 3)):
                x = random.randint(200, 700)
                y = random.randint(200, 500)
                await page.mouse.move(x, y, steps=random.randint(5, 12))
                await asyncio.sleep(random.uniform(0.2, 0.8))
                
        except Exception as e:
            logger.warning(f"Error simulating human behavior: {e}")
    
    async def simulate_human_behavior(self, page):
        """Simulate human-like behavior on the page"""
        # Random mouse movements
        for _ in range(random.randint(2, 5)):
            x = random.randint(50, 1300)
            y = random.randint(50, 700)
            await page.mouse.move(x, y, steps=random.randint(5, 15))
            await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Random scrolling
        scroll_amount = random.randint(100, 300)
        for _ in range(random.randint(3, 7)):
            await page.evaluate(f'window.scrollBy(0, {scroll_amount})')
            await asyncio.sleep(random.uniform(0.5, 2))
            
            # Sometimes scroll back up
            if random.random() < 0.3:
                await page.evaluate(f'window.scrollBy(0, -{scroll_amount//2})')
                await asyncio.sleep(random.uniform(0.5, 1))