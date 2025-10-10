"""
Enhanced Indeed Job Scraper with Full Job Details - main7.py
Scrapes job listings from Indeed and, for each job, visits the job detail page to extract the full description and additional fields.
"""

import asyncio
import random
import time
import json
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Union
from urllib.parse import urlencode, urljoin, urlparse
import pandas as pd
from datetime import datetime, timedelta
import logging

# Core scraping libraries
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# Enhanced utilities
from fake_useragent import UserAgent
import dateparser
from fuzzywuzzy import fuzz
import unicodedata

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class JobListing:
    title: str
    company: str
    location: str
    description: str
    url: str
    salary: Optional[str] = None
    date_posted: Optional[str] = None
    job_type: Optional[str] = None
    remote: bool = False
    skills: Optional[List[str]] = None
    experience_level: Optional[str] = None
    employment_type: Optional[str] = None
    company_rating: Optional[str] = None
    full_description: Optional[str] = None

class EnhancedIndeedScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.base_url = "https://in.indeed.com"
        self.session_cookies = None

    def get_rotating_headers(self):
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

    def build_search_url(self, query: str, location: str, start: int = 0):
        formatted_query = query.replace(' ', '+')
        formatted_location = location.replace(', ', '%2C+').replace(' ', '+')
        search_url = f"{self.base_url}/jobs?q={formatted_query}&l={formatted_location}&start={start}&sort=date"
        return search_url

    async def scrape_with_playwright(self, query: str, location: str = "Mumbai, Maharashtra", max_pages: int = 3):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-default-apps',
                    '--window-size=1366,768'
                ]
            )
            context = await browser.new_context(
                viewport={'width': 1366, 'height': 768},
                locale='en-IN',
                timezone_id='Asia/Kolkata',
                user_agent=self.ua.random
            )
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-IN', 'en', 'hi']});
                Object.defineProperty(navigator, 'plugins', {
                    get: () => Array.from({length: 5}, (_, i) => ({name: `Plugin ${i}`}))
                });
                window.chrome = {runtime: {}};
                delete window.navigator.webdriver;
            """)
            page = await context.new_page()
            await page.set_extra_http_headers(self.get_rotating_headers())
            all_jobs = []
            for page_num in range(max_pages):
                try:
                    start = page_num * 10
                    search_url = self.build_search_url(query, location, start)
                    logger.info(f"Scraping page {page_num + 1}: {search_url}")
                    await page.goto(search_url, wait_until='networkidle', timeout=60000)
                    await page.wait_for_load_state('domcontentloaded')
                    await self.simulate_human_behavior(page)
                    html_content = await page.content()
                    jobs = self.parse_search_results(html_content)
                    logger.info(f"Found {len(jobs)} jobs on page {page_num + 1}")
                    # For each job, visit the detail page and get full description
                    for job in jobs:
                        if job['url']:
                            full_details = await self.fetch_job_details(job['url'], context)
                            job['full_description'] = full_details.get('full_description')
                            if full_details.get('job_type'):
                                job['job_type'] = full_details['job_type']
                            if full_details.get('salary'):
                                job['salary'] = full_details['salary']
                        all_jobs.append(job)
                        await asyncio.sleep(random.uniform(1, 3))
                    delay = random.uniform(8, 15) + (page_num * 2)
                    await asyncio.sleep(delay)
                except Exception as e:
                    logger.error(f"Error on page {page_num + 1}: {e}")
                    await asyncio.sleep(random.uniform(20, 30))
                    continue
            await browser.close()
            return [JobListing(**job) for job in all_jobs]

    async def fetch_job_details(self, job_url: str, context) -> Dict:
        page = await context.new_page()
        try:
            await page.goto(job_url, timeout=60000)
            await page.wait_for_load_state('domcontentloaded')
            html = await page.content()
            soup = BeautifulSoup(html, 'lxml')
            desc_elem = soup.select_one('div#jobDescriptionText, div.jobsearch-jobDescriptionText, div[data-testid="jobDescriptionText"]')
            full_description = desc_elem.get_text(separator=' ', strip=True) if desc_elem else None
            job_type = None
            salary = None
            for label in soup.select('div.jobsearch-JobDescriptionSection-sectionItem span.jobsearch-JobDescriptionSection-label'):
                text = label.get_text(strip=True).lower()
                value = label.find_next_sibling('span')
                if not value:
                    continue
                value_text = value.get_text(strip=True)
                if 'job type' in text:
                    job_type = value_text
                if 'salary' in text:
                    salary = value_text
            return {
                'full_description': full_description,
                'job_type': job_type,
                'salary': salary
            }
        except Exception as e:
            logger.warning(f"Error fetching job details for {job_url}: {e}")
            return {}
        finally:
            await page.close()

    def parse_search_results(self, html_content: str) -> List[Dict]:
        soup = BeautifulSoup(html_content, 'lxml')
        jobs = []
        for container in soup.select('li.css-1ac2h1w, div[data-jk], .jobsearch-SerpJobCard, .job_seen_beacon'):
            job = {}
            # Title
            title_elem = container.select_one('span[title], span[id*="jobTitle"], h2.jobTitle a, .jobTitle a, h2 a')
            if title_elem:
                job['title'] = title_elem.get('title') or title_elem.get_text(strip=True)
            else:
                continue
            # URL
            url_elem = container.select_one('a[data-jk], h2.jobTitle a')
            if url_elem:
                href = url_elem.get('href', '')
                job['url'] = urljoin(self.base_url, href) if href and not href.startswith('http') else href
            else:
                job['url'] = None
            # Company
            company_elem = container.select_one('[data-testid="company-name"], span.companyName, .companyName, a[data-testid="company-name"]')
            job['company'] = company_elem.get_text(strip=True) if company_elem else 'Unknown Company'
            # Location
            location_elem = container.select_one('[data-testid="text-location"], div.companyLocation, .companyLocation')
            job['location'] = location_elem.get_text(strip=True) if location_elem else 'Location not specified'
            # Description snippet
            desc_elem = container.select_one('[data-testid="belowJobSnippet"], .job-snippet, [data-testid="job-snippet"], .summary')
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
            # Remote
            full_text = container.get_text(separator=' ', strip=True)
            remote_keywords = ['remote', 'work from home', 'wfh', 'telecommute', 'hybrid', 'work remotely']
            job['remote'] = any(keyword in full_text.lower() for keyword in remote_keywords)
            # Skills (simple keyword search)
            skill_keywords = [
                'python', 'django', 'flask', 'fastapi', 'pandas', 'numpy', 'tensorflow', 
                'pytorch', 'scikit-learn', 'sql', 'postgresql', 'mysql', 'mongodb',
                'redis', 'elasticsearch', 'aws', 'azure', 'gcp', 'docker', 'kubernetes',
                'git', 'jenkins', 'ci/cd', 'linux', 'rest api', 'graphql', 'microservices'
            ]
            job['skills'] = [kw for kw in skill_keywords if kw in full_text.lower()]
            # Experience level (simple regex)
            exp_match = re.search(r'(\d+)[+\s]*years?|senior|junior|lead|principal', full_text.lower())
            job['experience_level'] = exp_match.group(0) if exp_match else None
            # Employment type (simple keyword search)
            employment_keywords = {
                'full-time': ['full time', 'full-time', 'permanent'],
                'part-time': ['part time', 'part-time'],
                'contract': ['contract', 'contractor', 'freelance'],
                'internship': ['intern', 'internship', 'trainee']
            }
            for emp_type, keywords in employment_keywords.items():
                if any(keyword in full_text.lower() for keyword in keywords):
                    job['employment_type'] = emp_type
                    break
            else:
                job['employment_type'] = None
            # Company rating
            rating_elem = container.select_one('.ratingNumber, [data-testid*="rating"]')
            job['company_rating'] = rating_elem.get_text(strip=True) if rating_elem else None
            jobs.append(job)
        return jobs

    async def simulate_human_behavior(self, page):
        for _ in range(random.randint(2, 5)):
            x = random.randint(50, 1300)
            y = random.randint(50, 700)
            await page.mouse.move(x, y, steps=random.randint(5, 15))
            await asyncio.sleep(random.uniform(0.1, 0.5))
        viewport_height = await page.evaluate('window.innerHeight')
        scroll_amount = random.randint(100, 300)
        for _ in range(random.randint(3, 7)):
            await page.evaluate(f'window.scrollBy(0, {scroll_amount})')
            await asyncio.sleep(random.uniform(0.5, 2))
            if random.random() < 0.3:
                await page.evaluate(f'window.scrollBy(0, -{scroll_amount//2})')
                await asyncio.sleep(random.uniform(0.5, 1))

    def save_results(self, jobs: List[JobListing], filename_prefix: str = None):
        if not jobs:
            logger.warning("No jobs to save")
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = filename_prefix or "enhanced_indeed_jobs"
        json_filename = f"{prefix}_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump([asdict(job) for job in jobs], f, indent=2, ensure_ascii=False)
        csv_filename = f"{prefix}_{timestamp}.csv"
        df = pd.DataFrame([asdict(job) for job in jobs])
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        logger.info(f"Results saved: JSON: {json_filename}, CSV: {csv_filename}")
        return {'json': json_filename, 'csv': csv_filename}

async def main():
    scraper = EnhancedIndeedScraper()
    query = "python developer"
    location = "Mumbai, Maharashtra"
    max_pages = 1
    print(f"🚀 Enhanced Indeed Scraper with Full Details Starting...")
    print(f"Query: {query}")
    print(f"Location: {location}")
    print(f"Max Pages: {max_pages}")
    print("-" * 60)
    jobs = await scraper.scrape_with_playwright(query, location, max_pages)
    if jobs:
        files = scraper.save_results(jobs, "enhanced_indeed_jobs_full_details")
        print(f"\n🎉 SUCCESS! Found {len(jobs)} jobs with full details.")
        print(f"Files saved: {files}")
    else:
        print("❌ No jobs found.")

if __name__ == "__main__":
    asyncio.run(main())
