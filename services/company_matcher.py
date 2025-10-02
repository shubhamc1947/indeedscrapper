import re
import logging
from typing import Dict, Any, Optional, Tuple, List
from urllib.parse import urlparse
from datetime import date

from fuzzywuzzy import fuzz
import requests

from config import SCRAPING_CONFIG, GOOGLE_API_KEY
from utils.db_utils import db_manager
from models.job_model import ProcessedJob

logger = logging.getLogger(__name__)

class CompanyMatcher:
    def __init__(self):
        self.fuzzy_threshold = SCRAPING_CONFIG['fuzzy_match_threshold']
        self.companies_cache = {'by_url': {}, 'by_name': {}, 'by_iva': {}, 'all': []}
    
    async def _load_companies_cache(self):
        """Load companies into memory cache for faster matching"""
        try:
            companies = await db_manager.execute_query(
                "SELECT id, company_id, name, legal_name, url, iva FROM companies"
            )
            
            self.companies_cache = {
                'by_url': {},
                'by_name': {},
                'by_iva': {},
                'all': []
            }
            
            for company in companies:
                company_dict = dict(company)
                self.companies_cache['all'].append(company_dict)
                
                # Index by normalized URL
                if company_dict.get('url'):
                    normalized_url = self.normalize_url(company_dict['url'])
                    self.companies_cache['by_url'][normalized_url] = company_dict
                
                # Index by normalized name
                if company_dict.get('name'):
                    normalized_name = self.normalize_company_name(company_dict['name'])
                    self.companies_cache['by_name'][normalized_name] = company_dict
                
                # Index by VAT/IVA
                if company_dict.get('iva'):
                    self.companies_cache['by_iva'][company_dict['iva']] = company_dict
            
            logger.info(f"Loaded {len(self.companies_cache['all'])} companies into cache")
            
        except Exception as e:
            logger.error(f"Failed to load companies cache: {e}")
            self.companies_cache = {'by_url': {}, 'by_name': {}, 'by_iva': {}, 'all': []}
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL for comparison with validation"""
        if not url:
            return ""
        
        try:
            # Basic validation - check for common URL patterns
            if not isinstance(url, str):
                logger.warning(f"URL is not a string: {type(url)}")
                return ""
            
            url = url.strip()
            
            # Check minimum length
            if len(url) < 4:
                return ""
            
            # Add http:// if no protocol specified
            if not url.startswith(('http://', 'https://', '//')):
                url = 'https://' + url
            
            # Parse URL
            parsed = urlparse(url.lower())
            
            # Validate domain exists
            domain = parsed.netloc or parsed.path
            if not domain or len(domain) < 3:
                logger.warning(f"Invalid domain in URL: {url}")
                return ""
            
            # Check for valid TLD (basic check)
            if '.' not in domain:
                logger.warning(f"URL missing TLD: {url}")
                return ""
            
            # Remove www prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Remove trailing slash from path
            path = parsed.path.rstrip('/')
            
            # Validate characters (basic check for malformed URLs)
            if any(char in domain for char in ['<', '>', '"', "'", '|', '^', '`', '{', '}']):
                logger.warning(f"URL contains invalid characters: {url}")
                return ""
            
            return f"{domain}{path}"
            
        except Exception as e:
            logger.warning(f"Failed to normalize URL '{url}': {e}")
            return ""
    
    def normalize_company_name(self, name: str) -> str:
        """Normalize company name for comparison"""
        if not name:
            return ""
        
        # Convert to lowercase and remove common company suffixes
        normalized = name.lower().strip()
        
        # Remove common company suffixes
        suffixes = [
            's.p.a.', 'spa', 's.r.l.', 'srl', 's.r.l', 'ltd', 'limited', 'inc', 'corp',
            'corporation', 'company', 'co.', 'llc', 'pte ltd', 'pvt ltd', 'private limited',
            'societa per azioni', 'societa a responsabilita limitata'
        ]
        
        for suffix in suffixes:
            if normalized.endswith(f' {suffix}'):
                normalized = normalized[:-len(f' {suffix}')].strip()
            elif normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)].strip()
        
        # Remove special characters and extra spaces
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """Extract URLs from job description text"""
        if not text:
            return []
        
        # URL pattern
        url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*)?'
        urls = re.findall(url_pattern, text, re.IGNORECASE)
        
        # Filter out non-company URLs
        excluded_domains = [
            'indeed.com', 'linkedin.com', 'google.com', 'facebook.com',
            'twitter.com', 'instagram.com', 'youtube.com', 'stackoverflow.com'
        ]
        
        filtered_urls = []
        for url in urls:
            domain = urlparse(url.lower()).netloc
            if not any(excluded in domain for excluded in excluded_domains):
                filtered_urls.append(url)
        
        return filtered_urls
    
    async def find_company_match(self, job_data: Dict[str, Any]) -> Tuple[Optional[Dict], str, float]:
        """
        Find matching company using 3-tier strategy
        Returns: (company_dict, match_type, confidence)
        """
        
        # Strategy 1: URL Matching (Highest Priority)
        company, confidence = await self.match_by_url(job_data)
        if company:
            return company, 'url', confidence
        
        # Strategy 2: Company Name Fuzzy Matching (Medium Priority)
        company, confidence = await self.match_by_name(job_data)
        if company and confidence >= self.fuzzy_threshold:
            return company, 'name', confidence
        
        # Strategy 3: Google API + VAT Number (Low Priority, Fallback)
        if GOOGLE_API_KEY:
            company, confidence = await self.match_by_google_api(job_data)
            if company:
                return company, 'google_api', confidence
        
        return None, 'none', 0.0
    
    async def match_by_url(self, job_data: Dict[str, Any]) -> Tuple[Optional[Dict], float]:
        """Match company by URL comparison"""
        urls_to_check = []
        
        # Get URLs from various sources
        if job_data.get('url_company_indeed'):
            # Try to extract actual company website from Indeed company page
            company_website = await self.extract_company_website_from_indeed(
                job_data['url_company_indeed']
            )
            if company_website:
                urls_to_check.append(company_website)
        
        # Extract URLs from job description
        if job_data.get('full_description'):
            urls_to_check.extend(self.extract_urls_from_text(job_data['full_description']))
        
        if job_data.get('description'):
            urls_to_check.extend(self.extract_urls_from_text(job_data['description']))
        
        # Try to match each URL
        for url in urls_to_check:
            normalized_url = self.normalize_url(url)
            
            # Direct match
            if normalized_url in self.companies_cache['by_url']:
                return self.companies_cache['by_url'][normalized_url], 100.0
            
            # Partial match (domain level)
            for cached_url, company in self.companies_cache['by_url'].items():
                if self.calculate_url_similarity(normalized_url, cached_url) > 90:
                    return company, 95.0
        
        return None, 0.0
    
    async def match_by_name(self, job_data: Dict[str, Any]) -> Tuple[Optional[Dict], float]:
        """Match company by name using optimized fuzzy matching"""
        job_company_name = job_data.get('company_name', '').strip()
        if not job_company_name:
            return None, 0.0
        
        normalized_job_name = self.normalize_company_name(job_company_name)
        
        # Check direct normalized match first
        if normalized_job_name in self.companies_cache['by_name']:
            return self.companies_cache['by_name'][normalized_job_name], 100.0
        
        # Pre-filter: only check companies that start with the same letter
        first_char = normalized_job_name[0] if normalized_job_name else ''
        filtered_companies = [
            c for c in self.companies_cache['all'] 
            if (c.get('name') and self.normalize_company_name(c['name']).startswith(first_char)) or
            (c.get('legal_name') and self.normalize_company_name(c['legal_name']).startswith(first_char))
        ]
        
        # If no matches with first letter, expand search but limit to companies with similar length
        if not filtered_companies:
            name_len = len(normalized_job_name)
            filtered_companies = [
                c for c in self.companies_cache['all']
                if (c.get('name') and abs(len(self.normalize_company_name(c['name'])) - name_len) <= 5) or
                (c.get('legal_name') and abs(len(self.normalize_company_name(c['legal_name'])) - name_len) <= 5)
            ]
        
        # Limit search to top N candidates if still too many
        MAX_CANDIDATES = 100
        if len(filtered_companies) > MAX_CANDIDATES:
            filtered_companies = filtered_companies[:MAX_CANDIDATES]
        
        best_match = None
        best_score = 0
        
        # Fuzzy matching against filtered companies
        for company in filtered_companies:
            scores = []
            
            # Match against company name
            if company.get('name'):
                normalized_company_name = self.normalize_company_name(company['name'])
                scores.append(fuzz.ratio(normalized_job_name, normalized_company_name))
                scores.append(fuzz.partial_ratio(normalized_job_name, normalized_company_name))
                scores.append(fuzz.token_sort_ratio(normalized_job_name, normalized_company_name))
            
            # Match against legal name
            if company.get('legal_name'):
                normalized_legal_name = self.normalize_company_name(company['legal_name'])
                scores.append(fuzz.ratio(normalized_job_name, normalized_legal_name))
                scores.append(fuzz.partial_ratio(normalized_job_name, normalized_legal_name))
            
            if scores:
                max_score = max(scores)
                if max_score > best_score:
                    best_score = max_score
                    best_match = company
        
        logger.debug(f"Fuzzy match for '{job_company_name}': best score {best_score} from {len(filtered_companies)} candidates")
        return best_match, best_score
    
    async def match_by_google_api(self, job_data: Dict[str, Any]) -> Tuple[Optional[Dict], float]:
        """Match company using Google API to find VAT number"""
        company_name = job_data.get('company_name', '').strip()
        if not company_name or not GOOGLE_API_KEY:
            return None, 0.0
        
        try:
            # Search for company VAT number using Google API
            vat_number = await self.search_company_vat_google(company_name)
            
            if vat_number and vat_number in self.companies_cache['by_iva']:
                return self.companies_cache['by_iva'][vat_number], 90.0
            
        except Exception as e:
            logger.warning(f"Google API search failed for {company_name}: {e}")
        
        return None, 0.0
    
    async def search_company_vat_google(self, company_name: str) -> Optional[str]:
        """Search for company VAT number using Google API"""
        try:
            # This is a placeholder implementation
            # You would need to implement actual Google Custom Search API calls
            # to search for VAT numbers
            
            # Example search query: "company_name VAT number Italy"
            query = f"{company_name} partita IVA VAT number Italy"
            
            # Placeholder for Google API call
            # search_results = google_api_search(query)
            # vat_number = extract_vat_from_results(search_results)
            
            logger.info(f"Google API search not implemented for: {query}")
            return None
            
        except Exception as e:
            logger.error(f"Google API search error: {e}")
            return None
    
    def calculate_url_similarity(self, url1: str, url2: str) -> float:
        """Calculate similarity between two normalized URLs"""
        return fuzz.ratio(url1, url2)
    
    async def extract_company_website_from_indeed(self, indeed_company_url: str) -> Optional[str]:
        """Extract actual company website from Indeed company page"""
        try:
            # This would require scraping the Indeed company page
            # to find the actual company website link
            # For now, return None
            logger.debug(f"Company website extraction not implemented for: {indeed_company_url}")
            return None
            
        except Exception as e:
            logger.warning(f"Failed to extract company website from {indeed_company_url}: {e}")
            return None
    
    async def process_job(self, job_data: Dict[str, Any]) -> Optional[ProcessedJob]:
        """Process a single job and create ProcessedJob object"""
        try:
            # Find company match
            company, match_type, confidence = await self.find_company_match(job_data)
            
            # Create processed job
            processed_job = ProcessedJob(
                job_url_indeed=job_data['job_url_indeed'],
                company_url_indeed=job_data.get('company_url_indeed'),
                job_offer_text=job_data.get('full_description') or job_data.get('description', ''),
                company_id=company['id'] if company else None,
                extraction_date=date.today(),
                company_website_url=company['url'] if company else None,
                match_type=match_type,
                match_confidence=confidence
            )
            
            logger.info(
                f"Job processed: {job_data['job_url_indeed'][:50]}... | "
                f"Match: {match_type} ({confidence:.1f}%) | "
                f"Company: {company['name'] if company else 'None'}"
            )
            
            return processed_job
            
        except Exception as e:
            logger.error(f"Failed to process job {job_data.get('url_job_indeed')}: {e}")
            return None
    
    async def process_jobs_batch(self, jobs_data: List[Dict[str, Any]]) -> List[ProcessedJob]:
        """Process multiple jobs in batch"""
        processed_jobs = []
        
        for job_data in jobs_data:
            processed_job = await self.process_job(job_data)
            if processed_job:
                processed_jobs.append(processed_job)
        
        # Log batch statistics
        total_jobs = len(jobs_data)
        successful_jobs = len(processed_jobs)
        
        if successful_jobs > 0:
            match_stats = {}
            for job in processed_jobs:
                match_type = job.match_type or 'none'
                match_stats[match_type] = match_stats.get(match_type, 0) + 1
            
            logger.info(f"Batch processed: {successful_jobs}/{total_jobs} jobs")
            logger.info(f"Match statistics: {match_stats}")
        
        return processed_jobs
    
    async def refresh_companies_cache(self):
        """Refresh the companies cache from database"""
        logger.info("Refreshing companies cache...")
        await self._load_companies_cache()

# Global company matcher instance
company_matcher = CompanyMatcher()