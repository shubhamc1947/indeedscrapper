import asyncio
import logging
import sys
import argparse
import random  
from datetime import datetime, date
from typing import List, Dict, Any

# Import modules
from config import (
    LOG_LEVEL, SCRAPING_CONFIG, INDEED_CONFIG, 
    ITALY_LOCATIONS, JOB_SEARCH_QUERIES, MULTI_LOCATION_CONFIG
)
from utils.db_utils import db_manager
from adapters.indeed_adapter import IndeedAdapter
from services.company_matcher import company_matcher
from models.job_model import job_model, JobListing

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'indeed_scraper_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class IndeedScraperPipeline:
    def __init__(self):
        self.indeed_adapter = IndeedAdapter()
        self.stats = {
            'start_time': None,
            'end_time': None,
            'total_scraped': 0,
            'total_stored': 0,
            'total_processed': 0,
            'duplicates_found': 0,
            'errors': 0,
            'locations_scraped': 0,
            'locations_failed': 0,
            'queries_completed': 0,
        }
    
    async def initialize(self):
        """Initialize the pipeline"""
        logger.info("Initializing Indeed Scraper Pipeline...")
        
        try:
            # Initialize database
            await db_manager.initialize()
            logger.info("Database initialized successfully")
            
            # Load companies cache
            await company_matcher._load_companies_cache()
            logger.info("Companies cache loaded successfully")
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise
    
    async def scrape_single_location(self, query: str, location: str, 
                                    max_pages: int = None, date_filter: str = "1") -> List[JobListing]:
        """Scrape jobs from a single location"""
        logger.info(f"Scraping: '{query}' in '{location}'")
        
        try:
            if max_pages is None:
                max_pages = MULTI_LOCATION_CONFIG.get('max_pages_per_location', 5)
            
            jobs = await self.indeed_adapter.scrape_jobs(
                query=query,
                location=location,
                max_pages=max_pages,
                date_filter=date_filter
            )
            
            logger.info(f"Successfully scraped {len(jobs)} jobs from {location}")
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to scrape {location}: {e}")
            self.stats['errors'] += 1
            self.stats['locations_failed'] += 1
            
            if not MULTI_LOCATION_CONFIG.get('continue_on_error', True):
                raise
            
            return []
    
    async def scrape_multi_location(self, query: str, tiers: List[str] = None,
                                   max_pages: int = None, date_filter: str = "1") -> int:
        """Scrape jobs from multiple locations across Italy"""
        logger.info(f"Starting multi-location scrape for query: '{query}'")
        
        if tiers is None:
            tiers = MULTI_LOCATION_CONFIG.get('enabled_tiers', ['tier_1', 'tier_2', 'remote'])
        
        total_jobs_scraped = 0
        
        for tier in tiers:
            if tier not in ITALY_LOCATIONS:
                logger.warning(f"Tier '{tier}' not found in ITALY_LOCATIONS, skipping")
                continue
            
            locations = ITALY_LOCATIONS[tier]
            logger.info(f"Processing {len(locations)} locations in tier '{tier}'")
            
            for idx, location in enumerate(locations, 1):
                logger.info(f"[{tier}] Location {idx}/{len(locations)}: {location}")
                
                retry_count = 0
                max_retries = MULTI_LOCATION_CONFIG.get('max_retries_per_location', 2)
                
                while retry_count <= max_retries:
                    try:
                        # Scrape this location
                        jobs = await self.scrape_single_location(
                            query=query,
                            location=location,
                            max_pages=max_pages,
                            date_filter=date_filter
                        )
                        
                        if jobs:
                            # Store jobs immediately
                            try:
                                stored_count, duplicate_count = await job_model.store_raw_jobs_batch(jobs)
                                
                                self.stats['total_scraped'] += len(jobs)
                                self.stats['total_stored'] += stored_count
                                self.stats['duplicates_found'] += duplicate_count
                                total_jobs_scraped += len(jobs)
                                
                                logger.info(
                                    f"Stored {stored_count} new jobs, {duplicate_count} duplicates from {location}"
                                )
                            except Exception as e:
                                logger.error(f"Failed to store jobs batch from {location}: {e}")
                                self.stats['errors'] += 1
                        
                        self.stats['locations_scraped'] += 1
                        break  # Success, move to next location
                        
                    except Exception as e:
                        retry_count += 1
                        logger.error(f"Attempt {retry_count} failed for {location}: {e}")
                        
                        if retry_count <= max_retries:
                            wait_time = retry_count * 60  # Exponential backoff
                            logger.info(f"Retrying {location} in {wait_time} seconds...")
                            await asyncio.sleep(wait_time)
                        else:
                            logger.error(f"Max retries reached for {location}, skipping")
                            self.stats['locations_failed'] += 1
                            break
                
                # Delay between locations (unless it's the last one)
                if idx < len(locations):
                    delay = random.uniform(
                        MULTI_LOCATION_CONFIG['delay_between_locations_min'],
                        MULTI_LOCATION_CONFIG['delay_between_locations_max']
                    )
                    logger.info(f"Waiting {delay:.0f} seconds before next location...")
                    await asyncio.sleep(delay)
        
        logger.info(f"Multi-location scrape completed. Total jobs scraped: {total_jobs_scraped}")
        return total_jobs_scraped
    
    async def scrape_multi_query(self, queries: List[str] = None, tiers: List[str] = None,
                                max_pages: int = None, date_filter: str = "1") -> int:
        """Scrape multiple job queries across multiple locations"""
        logger.info("Starting multi-query, multi-location scrape")
        
        if queries is None:
            queries = JOB_SEARCH_QUERIES[:5]  # Default to first 5 queries
            logger.info(f"Using default queries: {queries}")
        
        total_jobs = 0
        
        for query_idx, query in enumerate(queries, 1):
            logger.info(f"Query {query_idx}/{len(queries)}: '{query}'")
            
            try:
                jobs_count = await self.scrape_multi_location(
                    query=query,
                    tiers=tiers,
                    max_pages=max_pages,
                    date_filter=date_filter
                )
                
                total_jobs += jobs_count
                self.stats['queries_completed'] += 1
                
                # Delay between queries (unless it's the last one)
                if query_idx < len(queries):
                    delay = random.uniform(
                        MULTI_LOCATION_CONFIG['delay_between_queries_min'],
                        MULTI_LOCATION_CONFIG['delay_between_queries_max']
                    )
                    logger.info(f"Waiting {delay:.0f} seconds before next query...")
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Failed to process query '{query}': {e}")
                self.stats['errors'] += 1
                
                if not MULTI_LOCATION_CONFIG.get('continue_on_error', True):
                    raise
        
        logger.info(f"Multi-query scrape completed. Total jobs: {total_jobs}")
        return total_jobs
    
    async def run_processing_phase(self, limit: int = None) -> int:
        """Phase 3: Process jobs and match with companies"""
        logger.info("Starting job processing and company matching...")
        
        try:
            # Get unprocessed jobs
            unprocessed_jobs = await job_model.get_unprocessed_jobs(limit=limit)
            
            if not unprocessed_jobs:
                logger.info("No unprocessed jobs found")
                return 0
            
            logger.info(f"Found {len(unprocessed_jobs)} unprocessed jobs")
            
            processed_count = 0
            
            # Process jobs in batches
            batch_size = 50
            for i in range(0, len(unprocessed_jobs), batch_size):
                batch = unprocessed_jobs[i:i + batch_size]
                
                logger.info(f"Processing batch {i//batch_size + 1}/{(len(unprocessed_jobs) + batch_size - 1)//batch_size}")
                
                for job_data in batch:
                    try:
                        # Process job and match company
                        processed_job = await company_matcher.process_job(job_data)
                        
                        if processed_job:
                            # Store processed job
                            result_id = await job_model.store_processed_job(
                                processed_job, 
                                job_data['id']
                            )
                            
                            if result_id:
                                processed_count += 1
                        else:
                            # Mark as failed
                            await job_model.mark_job_failed(job_data['id'], "Processing failed")
                            
                    except Exception as e:
                        logger.error(f"Failed to process job {job_data['id']}: {e}")
                        await job_model.mark_job_failed(job_data['id'], str(e))
                        self.stats['errors'] += 1
                
                # Small delay between batches
                await asyncio.sleep(1)
            
            self.stats['total_processed'] = processed_count
            logger.info(f"Processing completed: {processed_count} jobs processed")
            
            return processed_count
            
        except Exception as e:
            logger.error(f"Processing phase failed: {e}")
            self.stats['errors'] += 1
            raise
    
    async def run_full_pipeline(self, queries: List[str] = None, tiers: List[str] = None,
                               max_pages: int = None, date_filter: str = "1", 
                               process_limit: int = None) -> Dict[str, Any]:
        """Run the complete multi-location pipeline"""
        self.stats['start_time'] = datetime.now()
        
        try:
            # Phase 1 & 2: Scraping and Storage (combined)
            await self.scrape_multi_query(
                queries=queries,
                tiers=tiers,
                max_pages=max_pages,
                date_filter=date_filter
            )
            
            # Phase 3: Processing
            await self.run_processing_phase(limit=process_limit)
            
            # Generate final statistics
            self.stats['end_time'] = datetime.now()
            await self.generate_final_report()
            
            return self.stats
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            self.stats['end_time'] = datetime.now()
            self.stats['errors'] += 1
            raise
    
    async def generate_final_report(self):
        """Generate final execution report"""
        logger.info("Generating execution report...")
        
        # Get database statistics
        db_stats = await job_model.get_processing_stats()
        match_stats = await job_model.get_company_match_stats()
        
        # Calculate execution time
        if self.stats['start_time'] and self.stats['end_time']:
            execution_time = self.stats['end_time'] - self.stats['start_time']
            execution_minutes = execution_time.total_seconds() / 60
        else:
            execution_minutes = 0
        
        # Print comprehensive report
        print("\n" + "="*80)
        print("INDEED SCRAPER EXECUTION REPORT - MULTI-LOCATION")
        print("="*80)
        print(f"Date: {date.today()}")
        print(f"Execution Time: {execution_minutes:.2f} minutes")
        print(f"\nScraping Statistics:")
        print(f"   Queries Completed: {self.stats['queries_completed']}")
        print(f"   Locations Scraped: {self.stats['locations_scraped']}")
        print(f"   Locations Failed: {self.stats['locations_failed']}")
        print(f"   Total Jobs Scraped: {self.stats['total_scraped']}")
        print(f"   New Jobs Stored: {self.stats['total_stored']}")
        print(f"   Duplicates Found: {self.stats['duplicates_found']}")
        print(f"\nProcessing Statistics:")
        print(f"   Jobs Processed: {self.stats['total_processed']}")
        print(f"   Errors: {self.stats['errors']}")
        print(f"\nDatabase Statistics:")
        print(f"   Total in DB Today: {db_stats['total_scraped']}")
        print(f"   Pending Processing: {db_stats['pending']}")
        print(f"   Successfully Processed: {db_stats['processed']}")
        print(f"   Failed: {db_stats['failed']}")
        print(f"   Final Results: {db_stats['processed_results']}")
        
        if match_stats:
            print("\nCompany Matching Statistics:")
            for match_type, count in match_stats.items():
                print(f"   {match_type.title()} Matches: {count}")
        
        print("="*80)
        
        logger.info("Report generation completed")


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Indeed Job Scraper - Multi-Location Support')
    
    # Query options
    parser.add_argument('--query', '-q', help='Single job search query')
    parser.add_argument('--queries', '-Q', nargs='+', help='Multiple job search queries')
    parser.add_argument('--all-queries', action='store_true', help='Use all predefined queries')
    
    # Location options
    parser.add_argument('--location', '-l', help='Single location for job search')
    parser.add_argument('--tiers', '-t', nargs='+', 
                       choices=['tier_1', 'tier_2', 'tier_3', 'remote'],
                       help='Location tiers to scrape')
    parser.add_argument('--all-tiers', action='store_true', help='Scrape all location tiers')
    
    # Scraping options
    parser.add_argument('--max-pages', '-p', type=int, help='Maximum pages to scrape per location')
    parser.add_argument('--date-filter', '-d', default="1", 
                       help='Date filter: "1"=last 24h, "3"=last 3 days, "7"=last week')
    
    # Processing options
    parser.add_argument('--process-only', action='store_true', 
                       help='Only run processing phase (skip scraping)')
    parser.add_argument('--process-limit', type=int, help='Limit number of jobs to process')
    
    args = parser.parse_args()
    
    pipeline = IndeedScraperPipeline()
    
    try:
        # Initialize pipeline
        await pipeline.initialize()
        
        if args.process_only:
            # Only run processing phase
            logger.info("Running processing phase only...")
            await pipeline.run_processing_phase(limit=args.process_limit)
        else:
            # Determine queries
            if args.query:
                queries = [args.query]
            elif args.queries:
                queries = args.queries
            elif args.all_queries:
                queries = JOB_SEARCH_QUERIES
            else:
                # Default to single query for backwards compatibility
                queries = ['']
            
            # Determine tiers
            if args.location:
                # Single location mode (backwards compatibility)
                logger.info(f"Single location mode: {args.location}")
                jobs = await pipeline.scrape_single_location(
                    query=queries[0],
                    location=args.location,
                    max_pages=args.max_pages,
                    date_filter=args.date_filter
                )
                if jobs:
                    await job_model.store_raw_jobs_batch(jobs)
            else:
                # Multi-location mode
                if args.all_tiers:
                    tiers = list(ITALY_LOCATIONS.keys())
                elif args.tiers:
                    tiers = args.tiers
                else:
                    tiers = MULTI_LOCATION_CONFIG.get('enabled_tiers', ['tier_1', 'remote'])
                
                logger.info(f"Multi-location mode with tiers: {tiers}")
                
                # Run full pipeline
                await pipeline.run_full_pipeline(
                    queries=queries,
                    tiers=tiers,
                    max_pages=args.max_pages,
                    date_filter=args.date_filter,
                    process_limit=args.process_limit
                )
        
        logger.info("Pipeline execution completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        await db_manager.close()


if __name__ == "__main__":
    asyncio.run(main())