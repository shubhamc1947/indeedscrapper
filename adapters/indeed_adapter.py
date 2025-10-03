import asyncio
import random
import logging
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from config import SCRAPING_CONFIG, INDEED_CONFIG, PROXY_LIST
from models.job_model import JobListing
from indeed_selectors_config import INDEED_SELECTORS, SKILL_KEYWORDS

logger = logging.getLogger(__name__)

class IndeedAdapter:
    def __init__(self):
        self.ua = UserAgent()
        self.base_url = INDEED_CONFIG['base_url']
        self.current_proxy_index = 0
        self.retry_attempts = INDEED_CONFIG['retry_attempts']
        self.retry_delay = INDEED_CONFIG['retry_delay']
        self.scraped_urls = set()  # Track scraped URLs to avoid duplicates

    def get_rotating_headers(self):
        """Get rotating headers for requests"""
        headers_list = [
            {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
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
    
    def build_search_url(self, query: str, location: str, start: int = 0, date_filter: str = "1") -> str:
        """Build Indeed search URL with date filtering"""
        formatted_query = query.replace(' ', '+')
        formatted_location = location.replace(', ', '%2C+').replace(' ', '+')
        
        params = {
            'q': formatted_query,
            'l': formatted_location,
            'start': start,
            'sort': 'date',
            'fromage': date_filter
        }
        
        if start > 0:
            params['from'] = 'searchOnDesktopSerp'
        
        search_url = f"{self.base_url}/jobs?" + "&".join([f"{k}={v}" for k, v in params.items()])
        return search_url
    
    async def scrape_jobs(self, query: str, location: str = None, max_pages: int = None, date_filter: str = "1") -> List[JobListing]:
        """
        Main method to scrape jobs from Indeed.
        Now uses NEW SESSION approach - each location gets a fresh browser session.
        NO PAGINATION - only scrapes first page (start=0)
        """
        if location is None:
            location = INDEED_CONFIG['default_location']
        
        logger.info(f"Starting Indeed scraping (new session, no pagination): {query} in {location}")
        
        retry_count = 0
        
        while retry_count < self.retry_attempts:
            try:
                logger.info(f"\n{'='*80}")
                logger.info(f"NEW BROWSER SESSION - {query} in {location}")
                logger.info(f"{'='*80}")
                
                # Scrape ONLY the first page (start=0) in a fresh browser session
                jobs = await self.scrape_single_page_session(
                    query=query,
                    location=location,
                    date_filter=date_filter
                )
                
                logger.info(f"Session complete: {len(jobs)} jobs scraped from search results")
                return jobs
                
            except Exception as e:
                retry_count += 1
                logger.error(f"Scraping attempt {retry_count} failed: {e}")
                
                if retry_count < self.retry_attempts:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error("All retry attempts failed")
                    raise
        
        return []
    
    async def scrape_single_page_session(self, query: str, location: str, date_filter: str) -> List[JobListing]:
        """
        Scrape search results and click each job to get full details.
        Browser is closed after scraping this single page.
        """
        proxy = self.get_next_proxy()
        
        # Parse proxy if available
        proxy_config = None
        if proxy:
            try:
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
                '--window-size=1920,1080',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-dev-shm-usage',
                '--no-first-run',
                '--disable-gpu',
            ]
            
            # Launch browser
            browser = await p.chromium.launch(
                headless=True,  
                args=browser_args,
                proxy=proxy_config
            )
            
            # Random viewport dimensions for variety
            width = random.choice([1920, 1366, 1440, 1536])
            height = random.choice([1080, 768, 900, 864])
            
            context = await browser.new_context(
                viewport={'width': width, 'height': height},
                locale='it-IT',
                timezone_id='Europe/Rome',
                user_agent=self.ua.random,
                device_scale_factor=random.choice([1.0, 1.25]),
                color_scheme=random.choice(['light', 'dark'])
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
                
                // Override canvas fingerprinting
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(type) {
                    const shift = Math.floor(Math.random() * 10);
                    this.getContext('2d').fillStyle = `rgb(${100 + shift}, ${100 + shift}, ${100 + shift})`;
                    return originalToDataURL.apply(this, arguments);
                };
            """)
            
            page = await context.new_page()
            await page.set_extra_http_headers(self.get_rotating_headers())
            
            try:
                # Build URL for FIRST page only (start=0)
                search_url = self.build_search_url(query, location, start=0, date_filter=date_filter)
                
                logger.info(f"Navigating to: {search_url}")
                
                # Navigate to search page
                await page.goto(search_url, wait_until='domcontentloaded', timeout=90000)
                await page.wait_for_load_state('domcontentloaded')
                
                # Wait a bit for dynamic content
                await asyncio.sleep(random.uniform(3, 6))
                
                # Check for Cloudflare
                if await self.detect_cloudflare(page):
                    logger.warning("Cloudflare detected, attempting to handle...")
                    await asyncio.sleep(random.uniform(15, 25))
                
                # Simulate human behavior on search page
                await self.simulate_human_behavior(page)
                
                # Get job cards - try multiple selectors
                job_cards = None
                for selector in INDEED_SELECTORS['job_cards']:
                    try:
                        cards = await page.query_selector_all(selector)
                        if cards and len(cards) > 0:
                            job_cards = cards
                            logger.info(f"Found {len(job_cards)} job cards using selector: {selector}")
                            break
                    except:
                        continue
                
                if not job_cards:
                    logger.warning("No job cards found with any selector")
                    return []
                
                # Process each job card by clicking it
                filtered_jobs = []
                jobs_to_process = min(len(job_cards), 15)  # Limit to 15 jobs per page
                
                for idx in range(jobs_to_process):
                    try:
                        card = job_cards[idx]
                        logger.info(f"\n--- Processing job {idx + 1}/{jobs_to_process} ---")
                        
                        # Random delay before clicking (human behavior)
                        await asyncio.sleep(random.uniform(2, 5))
                        
                        # Find the job link - try multiple selectors
                        job_link = None
                        for selector in INDEED_SELECTORS['job_title_link']:
                            try:
                                link = await card.query_selector(selector)
                                if link:
                                    job_link = link
                                    break
                            except:
                                continue
                        
                        if not job_link:
                            logger.warning(f"No job link found for card {idx + 1}")
                            continue
                        
                        # Get job URL
                        job_url = await job_link.get_attribute('href')
                        if job_url and not job_url.startswith('http'):
                            job_url = f"{self.base_url}{job_url}"
                        
                        # Skip if duplicate
                        if job_url and job_url in self.scraped_urls:
                            logger.info(f"Skipping duplicate: {job_url[:50]}...")
                            continue
                        
                        # Get title from card - try multiple selectors
                        title = "Unknown"
                        for selector in INDEED_SELECTORS['job_title_text']:
                            try:
                                title_elem = await card.query_selector(selector)
                                if title_elem:
                                    title = await title_elem.inner_text()
                                    break
                            except:
                                continue
                        
                        logger.info(f"Title: {title[:60]}...")
                        
                        # Hover before clicking (very human-like)
                        box = await job_link.bounding_box()
                        if box:
                            await page.mouse.move(
                                box['x'] + box['width'] / 2,
                                box['y'] + box['height'] / 2,
                                steps=random.randint(10, 20)
                            )
                            await asyncio.sleep(random.uniform(0.5, 1.5))
                        
                        # Click the job card
                        await job_link.click()
                        await asyncio.sleep(random.uniform(2, 4))
                        
                        # Wait for details panel to load
                        try:
                            await page.wait_for_selector('#jobDescriptionText', state='visible', timeout=10000)
                            await asyncio.sleep(random.uniform(1.5, 3))
                        except:
                            logger.warning(f"Details panel timeout for job {idx + 1}")
                            continue
                        
                        # Simulate reading the job description (scroll in details panel)
                        logger.info("Reading job details...")
                        for _ in range(random.randint(2, 4)):
                            await page.mouse.wheel(0, random.randint(100, 300))
                            await asyncio.sleep(random.uniform(1, 2.5))
                        
                        # Extract full job details
                        job_data = await self.extract_job_details(page, job_url, title)
                        
                        if job_data and job_data.get('job_url_indeed'):
                            self.scraped_urls.add(job_data['job_url_indeed'])
                            
                            # Create JobListing object
                            try:
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
                                filtered_jobs.append(job)
                                logger.info(f"Successfully scraped job {idx + 1}")
                            except ValueError as e:
                                logger.error(f"Job validation failed: {e}")
                                continue
                    
                    except Exception as e:
                        logger.error(f"Error processing job card {idx + 1}: {e}")
                        continue
                
                logger.info(f"Returning {len(filtered_jobs)} jobs with full details")
                return filtered_jobs
                
            except Exception as e:
                logger.error(f"Error during scraping: {e}")
                raise
                
            finally:
                # ALWAYS close browser to complete the session
                logger.info("Closing browser session")
                await browser.close()
    
    async def extract_job_details(self, page, job_url: str, title: str) -> Dict:
        """Extract full job details from the details panel using configurable selectors"""
        job_data = {
            'title': title,
            'job_url_indeed': job_url
        }
        
        try:
            # Company name
            for selector in INDEED_SELECTORS['company_name']:
                try:
                    elem = await page.query_selector(selector)
                    if elem:
                        job_data['company_name'] = (await elem.inner_text()).strip()
                        logger.info(f"Company: {job_data['company_name']}")
                        break
                except:
                    continue
            
            # Company Indeed URL
            for selector in INDEED_SELECTORS['company_link']:
                try:
                    company_link = await page.query_selector(selector)
                    if company_link:
                        href = await company_link.get_attribute('href')
                        if href:
                            job_data['company_url_indeed'] = urljoin(self.base_url, href) if not href.startswith('http') else href
                            logger.info(f"Company URL: {job_data['company_url_indeed']}")
                        break
                except:
                    continue
            
            # Location
            for selector in INDEED_SELECTORS['company_location']:
                try:
                    elem = await page.query_selector(selector)
                    if elem:
                        job_data['location'] = (await elem.inner_text()).strip()
                        logger.info(f"Location: {job_data['location']}")
                        break
                except:
                    continue
            
            # Company Rating
            for selector in INDEED_SELECTORS['company_rating']:
                try:
                    elem = await page.query_selector(selector)
                    if elem:
                        job_data['company_rating'] = (await elem.inner_text()).strip()
                        logger.info(f"Rating: {job_data['company_rating']}")
                        break
                except:
                    continue
            
            # Full description - try multiple selectors
            full_desc_parts = []
            
            # Method 1: Try the main description div
            for selector in INDEED_SELECTORS['full_description']:
                try:
                    elem = await page.query_selector(selector)
                    if elem:
                        desc_text = (await elem.inner_text()).strip()
                        if desc_text:
                            full_desc_parts.append(desc_text)
                            logger.info(f"Found description: {len(desc_text)} characters")
                        break
                except:
                    continue
            
            # Method 2: Try job details section
            try:
                details_section = await page.query_selector(INDEED_SELECTORS['job_details_section'])
                if details_section:
                    details_text = (await details_section.inner_text()).strip()
                    if details_text and details_text not in full_desc_parts:
                        full_desc_parts.append(details_text)
                        logger.info(f"Found job details section: {len(details_text)} characters")
            except Exception as e:
                logger.warning(f"Error extracting job details section: {e}")
            
            # Method 3: Try benefits section
            try:
                benefits_section = await page.query_selector(INDEED_SELECTORS['benefits_section'])
                if benefits_section:
                    benefits_text = (await benefits_section.inner_text()).strip()
                    if benefits_text and benefits_text not in full_desc_parts:
                        full_desc_parts.append(f"Benefits: {benefits_text}")
                        logger.info(f"Found benefits section: {len(benefits_text)} characters")
            except Exception as e:
                logger.warning(f"Error extracting benefits: {e}")
            
            # Combine all description parts
            if full_desc_parts:
                job_data['full_description'] = '\n\n'.join(full_desc_parts)
                job_data['description'] = job_data['full_description'][:500]  # Short snippet
                logger.info(f"Total description: {len(job_data['full_description'])} characters")
            
            # Extract structured job details (Tipo di contratto, Turni, etc.)
            try:
                groups = await page.query_selector_all(INDEED_SELECTORS['job_details_groups'])
                job_details_extracted = []
                
                for group in groups:
                    try:
                        group_text = await group.inner_text()
                        
                        # Contract type
                        if 'tipo di contratto' in group_text.lower():
                            items = await group.query_selector_all(INDEED_SELECTORS['job_details_items'])
                            contracts = []
                            for item in items:
                                contracts.append((await item.inner_text()).strip())
                            if contracts:
                                job_data['employment_type'] = ', '.join(contracts)
                                job_data['job_type'] = contracts[0]
                                job_details_extracted.append(f"Tipo di contratto: {', '.join(contracts)}")
                                logger.info(f"Contract: {contracts}")
                        
                        # Shifts and hours (Turni e orari)
                        elif 'turni' in group_text.lower() or 'orari' in group_text.lower():
                            items = await group.query_selector_all(INDEED_SELECTORS['job_details_items'])
                            shifts = []
                            for item in items:
                                shifts.append((await item.inner_text()).strip())
                            if shifts:
                                job_details_extracted.append(f"Turni e orari: {', '.join(shifts)}")
                                logger.info(f"Shifts: {shifts}")
                        
                        # Salary
                        elif 'retribuzione' in group_text.lower() or 'stipendio' in group_text.lower():
                            items = await group.query_selector_all(INDEED_SELECTORS['job_details_items'])
                            if items and len(items) > 0:
                                job_data['salary'] = (await items[0].inner_text()).strip()
                                job_details_extracted.append(f"Retribuzione: {job_data['salary']}")
                                logger.info(f"Salary: {job_data['salary']}")
                    
                    except Exception as e:
                        logger.warning(f"Error processing job details group: {e}")
                        continue
                
                # Add structured details to description if found
                if job_details_extracted and job_data.get('full_description'):
                    job_data['full_description'] += '\n\n' + '\n'.join(job_details_extracted)
                
            except Exception as e:
                logger.warning(f"Error extracting structured job details: {e}")
            
            # Remote work detection
            try:
                full_text = job_data.get('full_description', '').lower()
                remote_keywords = ['remoto', 'remote', 'lavoro da casa', 'work from home', 'ibrido', 'hybrid', 'smartworking', 'smart working']
                job_data['remote'] = any(keyword in full_text for keyword in remote_keywords)
            except Exception as e:
                logger.warning(f"Error detecting remote work: {e}")
            
            # Extract skills from description using IMPORTED skill list from config
            try:
                if job_data.get('full_description'):
                    full_text = job_data['full_description'].lower()
                    job_data['skills'] = [skill for skill in SKILL_KEYWORDS if skill in full_text]
                    if job_data['skills']:
                        logger.info(f"Found {len(job_data['skills'])} skills: {job_data['skills'][:10]}")
            except Exception as e:
                logger.warning(f"Error extracting skills: {e}")
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error extracting job details: {e}")
            return job_data
    
    async def detect_cloudflare(self, page) -> bool:
        """Detect Cloudflare challenges"""
        try:
            await asyncio.sleep(2)
            
            cloudflare_indicators = [
                'Checking your browser',
                'DDoS protection by Cloudflare',
                'Ray ID',
                'cf-browser-verification',
                'Verify you are human'
            ]
            
            page_content = await page.content()
            page_text = await page.evaluate('() => document.body ? document.body.innerText : ""')
            
            is_cloudflare = any(indicator.lower() in page_content.lower() or 
                               indicator.lower() in page_text.lower() 
                               for indicator in cloudflare_indicators)
            
            if is_cloudflare:
                logger.warning("Cloudflare challenge detected")
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error detecting Cloudflare: {e}")
            return False
    
    async def simulate_human_behavior(self, page):
        """Simulate human-like behavior on the search page"""
        try:
            # Random mouse movements
            for _ in range(random.randint(3, 6)):
                x = random.randint(100, 1500)
                y = random.randint(100, 800)
                await page.mouse.move(x, y, steps=random.randint(10, 20))
                await asyncio.sleep(random.uniform(0.2, 0.6))
            
            # Scroll through search results
            viewport_height = await page.evaluate('window.innerHeight')
            total_height = await page.evaluate('document.body.scrollHeight')
            
            current_pos = 0
            scroll_count = random.randint(3, 6)
            
            for _ in range(scroll_count):
                scroll_amount = random.randint(200, 400)
                
                if current_pos + scroll_amount < total_height - viewport_height:
                    await page.evaluate(f'window.scrollBy(0, {scroll_amount})')
                    current_pos += scroll_amount
                    await asyncio.sleep(random.uniform(1.0, 3.0))
                    
                    # Sometimes scroll back up
                    if random.random() < 0.3:
                        back_scroll = random.randint(50, 150)
                        await page.evaluate(f'window.scrollBy(0, -{back_scroll})')
                        current_pos -= back_scroll
                        await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # More mouse movements
            for _ in range(random.randint(2, 4)):
                x = random.randint(100, 1500)
                y = random.randint(100, 800)
                await page.mouse.move(x, y, steps=random.randint(8, 15))
                await asyncio.sleep(random.uniform(0.3, 0.8))
                
        except Exception as e:
            logger.warning(f"Error simulating human behavior: {e}")
    
    def parse_search_results(self, html_content: str) -> List[Dict]:
        """Parse job listings from search results page - NOT USED in current implementation"""
        soup = BeautifulSoup(html_content, 'lxml')
        jobs = []
        
        job_containers = soup.select('li.css-1ac2h1w, div[data-jk], .jobsearch-SerpJobCard')
        
        for container in job_containers:
            job = {}
            
            title_elem = container.select_one('span[title], h2.jobTitle a')
            if title_elem:
                job['title'] = title_elem.get('title') or title_elem.get_text(strip=True)
            else:
                continue
            
            url_elem = container.select_one('a[data-jk], h2.jobTitle a')
            if url_elem:
                href = url_elem.get('href', '')
                job['job_url_indeed'] = urljoin(self.base_url, href) if href and not href.startswith('http') else href
            
            jobs.append(job)
        
        return jobs