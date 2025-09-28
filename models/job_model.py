import json
import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict

from utils.db_utils import db_manager

logger = logging.getLogger(__name__)

@dataclass
class JobListing:
    title: str
    company_name: str
    location: str
    description: str
    job_url_indeed: str
    salary: Optional[str] = None
    date_posted: Optional[str] = None
    job_type: Optional[str] = None
    remote: bool = False
    skills: Optional[List[str]] = None
    experience_level: Optional[str] = None
    employment_type: Optional[str] = None
    company_rating: Optional[str] = None
    full_description: Optional[str] = None
    company_url_indeed: Optional[str] = None

@dataclass
class ProcessedJob:
    job_url_indeed: str
    company_url_indeed: Optional[str]
    job_offer_text: str
    company_id: Optional[int]
    extraction_date: date
    company_website_url: Optional[str]
    match_type: Optional[str] = None
    match_confidence: Optional[float] = None

class JobModel:
    
    async def store_raw_job(self, job: JobListing) -> Optional[int]:
        """Store a single raw job in the database"""
        try:
            # Check if job already exists
            existing_job = await db_manager.execute_query_one(
                "SELECT id FROM it_indeed_scrapped_data WHERE job_url_indeed = $1",
                job.job_url_indeed
            )
            
            if existing_job:
                logger.info(f"Job already exists: {job.job_url_indeed}")
                return existing_job['id']
            
            # Insert new job
            query = """
            INSERT INTO it_indeed_scrapped_data (
                job_url_indeed, title, company_name, location, description, salary,
                date_posted, job_type, remote, skills, experience_level, employment_type,
                company_rating, full_description, company_url_indeed, extraction_date,
                status, created_at, updated_at
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19
            ) RETURNING id
            """
            
            current_time = datetime.now()
            skills_json = json.dumps(job.skills) if job.skills else None
            date_posted = None
            
            if job.date_posted:
                try:
                    if isinstance(job.date_posted, str):
                        date_posted = datetime.strptime(job.date_posted, '%Y-%m-%d').date()
                    elif isinstance(job.date_posted, date):
                        date_posted = job.date_posted
                except ValueError:
                    logger.warning(f"Invalid date format: {job.date_posted}")
            
            result = await db_manager.execute_insert(
                query,
                job.job_url_indeed,
                job.title,
                job.company_name,
                job.location,
                job.description,
                job.salary,
                date_posted,
                job.job_type,
                job.remote,
                skills_json,
                job.experience_level,
                job.employment_type,
                job.company_rating,
                job.full_description,
                job.company_url_indeed,
                date.today(),
                'extracted',
                current_time,
                current_time
            )
            
            logger.info(f"Raw job stored with ID: {result['id']}")
            return result['id']
            
        except Exception as e:
            logger.error(f"Failed to store raw job {job.job_url_indeed}: {e}")
            return None
    
    async def store_raw_jobs_batch(self, jobs: List[JobListing]) -> Tuple[int, int]:
        """Store multiple raw jobs in batch"""
        stored_count = 0
        duplicate_count = 0
        
        for job in jobs:
            job_id = await self.store_raw_job(job)
            if job_id:
                # Check if this was a new insertion or existing job
                existing_job = await db_manager.execute_query_one(
                    "SELECT created_at FROM it_indeed_scrapped_data WHERE id = $1",
                    job_id
                )
                
                if existing_job and existing_job['created_at'].date() == date.today():
                    stored_count += 1
                else:
                    duplicate_count += 1
        
        logger.info(f"Batch storage completed: {stored_count} new jobs, {duplicate_count} duplicates")
        return stored_count, duplicate_count
    
    async def get_unprocessed_jobs(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get jobs that haven't been processed yet"""
        query = """
        SELECT s.* FROM it_indeed_scrapped_data s
        LEFT JOIN it_indeed_result_data r ON s.job_url_indeed = r.job_url_indeed
        WHERE r.id IS NULL AND s.status = 'extracted'
        ORDER BY s.created_at ASC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        results = await db_manager.execute_query(query)
        return [dict(row) for row in results]
    
    async def store_processed_job(self, processed_job: ProcessedJob, scrapped_job_id: int) -> Optional[int]:
        """Store processed job result"""
        try:
            # Check if already processed
            existing_result = await db_manager.execute_query_one(
                "SELECT id FROM it_indeed_result_data WHERE job_url_indeed = $1",
                processed_job.job_url_indeed
            )
            
            if existing_result:
                logger.info(f"Job already processed: {processed_job.job_url_indeed}")
                return existing_result['id']
            
            query = """
            INSERT INTO it_indeed_result_data (
                scrapped_job_id, job_url_indeed, company_url_indeed, job_offer_text,
                company_id, extraction_date, company_website_url, match_type, match_confidence,
                created_at
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10
            ) RETURNING id
            """
            
            result = await db_manager.execute_insert(
                query,
                scrapped_job_id,
                processed_job.job_url_indeed,
                processed_job.company_url_indeed,
                processed_job.job_offer_text,
                processed_job.company_id,
                processed_job.extraction_date,
                processed_job.company_website_url,
                processed_job.match_type,
                processed_job.match_confidence,
                datetime.now()
            )
            
            # Update raw job status
            await db_manager.execute_insert(
                "UPDATE it_indeed_scrapped_data SET status = 'processed', updated_at = $1 WHERE id = $2",
                datetime.now(),
                scrapped_job_id
            )
            
            logger.info(f"Processed job stored with ID: {result['id']}")
            return result['id']
            
        except Exception as e:
            logger.error(f"Failed to store processed job {processed_job.job_url_indeed}: {e}")
            # Mark as failed
            await db_manager.execute_insert(
                "UPDATE it_indeed_scrapped_data SET status = 'failed', updated_at = $1 WHERE id = $2",
                datetime.now(),
                scrapped_job_id
            )
            return None
    
    async def get_jobs_by_date(self, extraction_date: date) -> List[Dict[str, Any]]:
        """Get jobs extracted on a specific date"""
        query = """
        SELECT * FROM it_indeed_scrapped_data 
        WHERE extraction_date = $1
        ORDER BY created_at DESC
        """
        
        results = await db_manager.execute_query(query, extraction_date)
        return [dict(row) for row in results]
    
    async def get_processing_stats(self) -> Dict[str, int]:
        """Get processing statistics"""
        stats_query = """
        SELECT 
            COUNT(*) as total_scraped,
            COUNT(CASE WHEN status = 'extracted' THEN 1 END) as pending,
            COUNT(CASE WHEN status = 'processed' THEN 1 END) as processed,
            COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed
        FROM it_indeed_scrapped_data
        WHERE extraction_date = CURRENT_DATE
        """
        
        result = await db_manager.execute_query_one(stats_query)
        
        # Get processed results count
        processed_results_query = """
        SELECT COUNT(*) as processed_results
        FROM it_indeed_result_data
        WHERE extraction_date = CURRENT_DATE
        """
        
        processed_result = await db_manager.execute_query_one(processed_results_query)
        
        return {
            'total_scraped': result['total_scraped'] if result else 0,
            'pending': result['pending'] if result else 0,
            'processed': result['processed'] if result else 0,
            'failed': result['failed'] if result else 0,
            'processed_results': processed_result['processed_results'] if processed_result else 0
        }
    
    async def get_company_match_stats(self) -> Dict[str, int]:
        """Get company matching statistics"""
        query = """
        SELECT 
            match_type,
            COUNT(*) as count
        FROM it_indeed_result_data
        WHERE extraction_date = CURRENT_DATE
        GROUP BY match_type
        """
        
        results = await db_manager.execute_query(query)
        stats = {}
        
        for row in results:
            stats[row['match_type'] or 'none'] = row['count']
        
        return stats
    
    async def mark_job_failed(self, job_id: int, error_message: str = None) -> None:
        """Mark a job as failed"""
        try:
            await db_manager.execute_insert(
                "UPDATE it_indeed_scrapped_data SET status = 'failed', updated_at = $1 WHERE id = $2",
                datetime.now(),
                job_id
            )
            logger.warning(f"Job {job_id} marked as failed: {error_message}")
        except Exception as e:
            logger.error(f"Failed to mark job as failed: {e}")

# Global job model instance
job_model = JobModel()