#!/usr/bin/env python3
"""
Usage examples for the Indeed Job Scraper
"""

from indeed_scraper import IndeedJobScraper
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def basic_job_search():
    """Basic job search example"""
    scraper = IndeedJobScraper()
    
    # Search for jobs
    jobs = scraper.search_jobs(
        query="data scientist",
        location="San Francisco, CA",
        max_pages=3
    )
    
    print(f"Found {len(jobs)} jobs")
    
    # Export results
    csv_file = scraper.export_results('csv')
    print(f"Results exported to: {csv_file}")

def advanced_job_search():
    """Advanced job search with filters"""
    scraper = IndeedJobScraper()
    
    # Search with multiple filters
    jobs = scraper.search_jobs(
        query="software engineer",
        location="Austin, TX",
        max_pages=5,
        job_type="fulltime",
        salary_min="80000",
        date_posted="3"  # Last 3 days
    )
    
    print(f"Found {len(jobs)} full-time software engineer jobs")
    
    # Get detailed statistics
    stats = scraper.get_stats()
    print(f"Database contains {stats['total_jobs']} total jobs from {stats['unique_companies']} companies")

def continuous_monitoring():
    """Example of continuous job monitoring with health checks"""
    scraper = IndeedJobScraper()
    
    search_queries = [
        {"query": "python developer", "location": "New York, NY"},
        {"query": "machine learning", "location": "Seattle, WA"},
        {"query": "DevOps engineer", "location": "Chicago, IL"}
    ]
    
    while True:
        try:
            # Health check before scraping
            health = scraper.health_check()
            if health['status'] != 'healthy':
                logger.warning(f"Scraper unhealthy: {health}")
                time.sleep(300)  # Wait 5 minutes
                continue
            
            # Scrape jobs for each query
            for search in search_queries:
                logger.info(f"Searching for: {search}")
                jobs = scraper.search_jobs(
                    query=search["query"],
                    location=search["location"],
                    max_pages=2,
                    date_posted="1"  # Only today's jobs
                )
                logger.info(f"Found {len(jobs)} new jobs for {search['query']}")
                
            # Export daily results
            csv_file = scraper.export_results('csv', f'daily_jobs_{time.strftime("%Y%m%d")}.csv')
            logger.info(f"Daily results exported to: {csv_file}")
            
            # Wait 24 hours before next run
            time.sleep(86400)
            
        except KeyboardInterrupt:
            logger.info("Stopping continuous monitoring...")
            break
        except Exception as e:
            logger.error(f"Error in continuous monitoring: {e}")
            time.sleep(1800)  # Wait 30 minutes before retry

def custom_company_tracking():
    """Track specific companies for job openings"""
    scraper = IndeedJobScraper()
    
    target_companies = ["Google", "Apple", "Microsoft", "Amazon", "Meta"]
    
    all_jobs = []
    for company in target_companies:
        jobs = scraper.search_jobs(
            query=f"company:{company}",
            location="",  # All locations
            max_pages=3
        )
        all_jobs.extend(jobs)
        print(f"Found {len(jobs)} jobs at {company}")
    
    # Filter and export results for target companies
    company_jobs = [job for job in all_jobs if job.company in target_companies]
    
    # Export with custom filename
    filename = f"target_companies_{time.strftime('%Y%m%d')}.csv"
    csv_file = scraper.export_results('csv', filename)
    print(f"Target company jobs exported to: {csv_file}")

def salary_analysis():
    """Analyze salary trends across different roles and locations"""
    scraper = IndeedJobScraper()
    
    roles = ["data scientist", "software engineer", "product manager", "UX designer"]
    locations = ["San Francisco, CA", "New York, NY", "Austin, TX", "Seattle, WA"]
    
    for role in roles:
        for location in locations:
            try:
                jobs = scraper.search_jobs(
                    query=role,
                    location=location,
                    max_pages=2,
                    salary_min="60000"  # Jobs with salary info
                )
                
                # Count jobs with salary information
                salary_jobs = [job for job in jobs if job.salary]
                print(f"{role} in {location}: {len(salary_jobs)}/{len(jobs)} jobs with salary info")
                
            except Exception as e:
                logger.error(f"Error searching {role} in {location}: {e}")
                continue
    
    # Export comprehensive results
    csv_file = scraper.export_results('csv', 'salary_analysis.csv')
    json_file = scraper.export_results('json', 'salary_analysis.json')
    print(f"Analysis exported to: {csv_file}, {json_file}")

def health_monitoring_daemon():
    """Run as a daemon with health monitoring"""
    scraper = IndeedJobScraper()
    
    while True:
        try:
            # Perform health check
            health = scraper.health_check()
            logger.info(f"Health Status: {health['status']}")
            
            if health['status'] == 'unhealthy':
                logger.warning("Attempting auto-heal...")
                if scraper.auto_heal():
                    logger.info("Auto-heal successful")
                else:
                    logger.error("Auto-heal failed, waiting before retry")
                    time.sleep(1800)  # Wait 30 minutes
                    continue
            
            # Get current statistics
            stats = scraper.get_stats()
            logger.info(f"Stats: {stats['total_jobs']} jobs, {stats['consecutive_failures']} failures")
            
            # Sleep for 1 hour
            time.sleep(3600)
            
        except KeyboardInterrupt:
            logger.info("Health monitoring stopped")
            break
        except Exception as e:
            logger.error(f"Health monitoring error: {e}")
            time.sleep(300)

if __name__ == "__main__":
    import sys
    
    examples = {
        "basic": basic_job_search,
        "advanced": advanced_job_search,
        "continuous": continuous_monitoring,
        "companies": custom_company_tracking,
        "salary": salary_analysis,
        "health": health_monitoring_daemon
    }
    
    if len(sys.argv) > 1 and sys.argv[1] in examples:
        examples[sys.argv[1]]()
    else:
        print(f"Usage: python {sys.argv[0]} [{'/'.join(examples.keys())}]")
        print("\nAvailable examples:")
        for name, func in examples.items():
            print(f"  {name}: {func.__doc__}")