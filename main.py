#!/usr/bin/env python3
"""
Indeed Job Scraper - Main Application
Automated daily extraction of job postings from Indeed with intelligent company matching
"""

import asyncio
import logging
import sys
import argparse
from datetime import datetime, date
from typing import List, Dict, Any

# Import modules
from config import LOG_LEVEL, SCRAPING_CONFIG, INDEED_CONFIG
from utils.db_utils import db_manager
from adapters.indeed_adapter import IndeedAdapter
from services.company_matcher import company_matcher
from models.job_model import job_model, JobListing

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'indeed_scraper_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8'),
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
            'errors': 0
        }
    
    async def initialize(self):
        """Initialize the pipeline"""
        logger.info(">>> Initializing Indeed Scraper Pipeline...")
        
        try:
            # Initialize database
            await db_manager.initialize()
            logger.info("[OK] Database initialized successfully")
            
            # Load companies cache
            await company_matcher._load_companies_cache()
            logger.info("[OK] Companies cache loaded successfully")
            logger.info(">>> Initialization completed successfully")
        except Exception as e:
            logger.error(f"[ERROR] Initialization failed: {e}")
            raise
    
    async def run_scraping_phase(self, query: str, location: str = None, max_pages: int = None, date_filter: str = "1") -> List[JobListing]:
        """Phase 1: Scrape jobs from Indeed"""
        logger.info("[INFO] Phase 1: Starting job scraping from Indeed...")
        
        self.stats['start_time'] = datetime.now()
        
        try:
            # Set defaults
            if location is None:
                location = INDEED_CONFIG['default_location']
            if max_pages is None:
                max_pages = SCRAPING_CONFIG['max_pages']
            
            logger.info(f"Search parameters: '{query}' in '{location}', {max_pages} pages, date_filter: {date_filter}")
            
            # Scrape jobs
            scraped_jobs = await self.indeed_adapter.scrape_jobs(
                query=query,
                location=location,
                max_pages=max_pages,
                date_filter=date_filter
            )
            
            self.stats['total_scraped'] = len(scraped_jobs)
            logger.info(f"[OK] Scraping completed: {len(scraped_jobs)} jobs found")
            
            return scraped_jobs
            
        except Exception as e:
            logger.error(f"[ERROR] Scraping phase failed: {e}")
            self.stats['errors'] += 1
            raise
    
    async def run_storage_phase(self, jobs: List[JobListing]) -> int:
        """Phase 2: Store raw jobs in database"""
        logger.info("[INFO] Phase 2: Storing raw jobs in database...")
        
        try:
            stored_count, duplicate_count = await job_model.store_raw_jobs_batch(jobs)
            
            self.stats['total_stored'] = stored_count
            self.stats['duplicates_found'] = duplicate_count
            
            logger.info(f"[OK] Storage completed: {stored_count} new jobs stored, {duplicate_count} duplicates skipped")
            
            return stored_count
            
        except Exception as e:
            logger.error(f"[ERROR] Storage phase failed: {e}")
            self.stats['errors'] += 1
            raise
    
    async def run_processing_phase(self, limit: int = None) -> int:
        """Phase 3: Process jobs and match with companies"""
        logger.info("[INFO] Phase 3: Processing jobs and matching companies...")
        
        try:
            # Get unprocessed jobs
            unprocessed_jobs = await job_model.get_unprocessed_jobs(limit=limit)
            
            if not unprocessed_jobs:
                logger.info("[INFO] No unprocessed jobs found")
                return 0

            logger.info(f"[INFO] Found {len(unprocessed_jobs)} unprocessed jobs")

            processed_count = 0
            
            # Process jobs in batches
            batch_size = 50
            for i in range(0, len(unprocessed_jobs), batch_size):
                batch = unprocessed_jobs[i:i + batch_size]
                
                logger.info(f"Processing batch {i//batch_size + 1}/{(len(unprocessed_jobs) + batch_size - 1)//batch_size}")
                
                # Process each job in the batch
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
            logger.info(f"[OK] Processing completed: {processed_count} jobs processed")
            
            return processed_count
            
        except Exception as e:
            logger.error(f"[ERROR] Processing phase failed: {e}")
            self.stats['errors'] += 1
            raise
    
    async def run_full_pipeline(self, query: str, location: str = None, max_pages: int = None, 
                               date_filter: str = "1", process_limit: int = None) -> Dict[str, Any]:
        """Run the complete pipeline"""
        try:
            # Phase 1: Scraping
            scraped_jobs = await self.run_scraping_phase(query, location, max_pages, date_filter)
            
            # Phase 2: Storage
            if scraped_jobs:
                await self.run_storage_phase(scraped_jobs)
            
            # Phase 3: Processing
            await self.run_processing_phase(limit=process_limit)
            
            # Generate final statistics
            self.stats['end_time'] = datetime.now()
            await self.generate_final_report()
            
            return self.stats
            
        except Exception as e:
            logger.error(f"[ERROR] Pipeline failed: {e}")
            self.stats['end_time'] = datetime.now()
            self.stats['errors'] += 1
            raise
    
    async def generate_final_report(self):
        """Generate final execution report"""
        logger.info("[INFO] Generating execution report...")
        
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
        print("🎉 INDEED SCRAPER EXECUTION REPORT")
        print("="*80)
        print(f"[INFO] Date: {date.today()}")
        print(f"[INFO] Execution Time: {execution_minutes:.2f} minutes")
        print(f"[INFO] Jobs Scraped: {self.stats['total_scraped']}")
        print(f"[INFO] Jobs Stored: {self.stats['total_stored']}")
        print(f"[INFO] Jobs Processed: {self.stats['total_processed']}")
        print(f"[INFO] Duplicates Found: {self.stats['duplicates_found']}")
        print(f"[ERROR] Errors: {self.stats['errors']}")
        print("\n[INFO] Database Statistics:")
        print(f"   Total in DB Today: {db_stats['total_scraped']}")
        print(f"   Pending Processing: {db_stats['pending']}")
        print(f"   Successfully Processed: {db_stats['processed']}")
        print(f"   Failed: {db_stats['failed']}")
        print(f"   Final Results: {db_stats['processed_results']}")
        
        if match_stats:
            print("\n[INFO] Company Matching Statistics:")
            for match_type, count in match_stats.items():
                print(f"   {match_type.title()} Matches: {count}")
        
        print("="*80)

        logger.info("[INFO] Report generation completed")

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Indeed Job Scraper')
    parser.add_argument('query', help='Job search query (e.g., "python developer")')
    parser.add_argument('--location', '-l', default=None, help='Location for job search')
    parser.add_argument('--max-pages', '-p', type=int, default=None, help='Maximum pages to scrape')
    parser.add_argument('--date-filter', '-d', default="1", 
                       help='Date filter: "1"=last 24h, "3"=last 3 days, "7"=last week')
    parser.add_argument('--process-only', action='store_true', 
                       help='Only run processing phase (skip scraping)')
    parser.add_argument('--process-limit', type=int, default=None,
                       help='Limit number of jobs to process')
    
    args = parser.parse_args()
    
    pipeline = IndeedScraperPipeline()
    
    try:
        # Initialize pipeline
        await pipeline.initialize()
        
        if args.process_only:
            # Only run processing phase
            logger.info("🔄 Running processing phase only...")
            await pipeline.run_processing_phase(limit=args.process_limit)
        else:
            # Run full pipeline
            logger.info("🚀 Running full pipeline...")
            await pipeline.run_full_pipeline(
                query=args.query,
                location=args.location,
                max_pages=args.max_pages,
                date_filter=args.date_filter,
                process_limit=args.process_limit
            )

        logger.info("[INFO] Pipeline execution completed successfully!")

    except KeyboardInterrupt:
        logger.info("[WARNING] Pipeline interrupted by user")
    except Exception as e:
        logger.error(f"[ERROR] Pipeline execution failed: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        await db_manager.close()

if __name__ == "__main__":
    asyncio.run(main())