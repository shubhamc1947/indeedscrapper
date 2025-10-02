import asyncio
import asyncpg
import logging
from typing import Optional, Dict, Any, List
from config import DATABASE_CONFIG

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def initialize(self):
        """Initialize database connection pool and run migrations"""
        try:
            # First, try to connect to the database
            self.pool = await asyncpg.create_pool(
                **DATABASE_CONFIG,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool created successfully")
            
            # Run migrations
            await self.run_migrations()
            
        except asyncpg.InvalidCatalogNameError:
            # Database doesn't exist, create it
            await self.create_database()
            self.pool = await asyncpg.create_pool(
                **DATABASE_CONFIG,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            await self.run_migrations()
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def create_database(self):
        """Create the database if it doesn't exist"""
        try:
            # Connect to default postgres database to create our database
            conn_config = DATABASE_CONFIG.copy()
            conn_config['database'] = 'postgres'
            
            conn = await asyncpg.connect(**conn_config)
            
            # Check if database exists
            db_exists = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1",
                DATABASE_CONFIG['database']
            )
            
            if not db_exists:
                await conn.execute(f'CREATE DATABASE "{DATABASE_CONFIG["database"]}"')
                logger.info(f"Database '{DATABASE_CONFIG['database']}' created successfully")
            
            await conn.close()
            
        except Exception as e:
            logger.error(f"Failed to create database: {e}")
            raise
    
    async def run_migrations(self):
        """Run database migrations to create tables"""
        # Only create companies table, job tables should already exist
        migrations = [
            self.create_companies_table(),
            # Skip job table migrations if they already exist
        ]
        
        async with self.pool.acquire() as conn:
            # Check if job tables exist
            job_tables_exist = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'it_indeed_scrapped_data'
                ) AND EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'it_indeed_result_data'
                );
            """)
            
            if not job_tables_exist:
                logger.info("Job tables don't exist. Please create them manually with correct column names.")
                migrations.extend([
                    self.create_indeed_scrapped_data_table(),
                    self.create_indeed_result_data_table(),
                ])
            
            for migration in migrations:
                try:
                    await conn.execute(migration)
                    logger.info("Migration executed successfully")
                except Exception as e:
                    logger.error(f"Migration failed: {e}")
                    raise
    
    def create_companies_table(self) -> str:
        """Create simplified companies table migration"""
        return """
        CREATE TABLE IF NOT EXISTS companies (
            id SERIAL PRIMARY KEY,
            company_id VARCHAR(50) UNIQUE,
            legal_name TEXT,
            vat VARCHAR(20),
            iva VARCHAR(20),
            name VARCHAR(255),
            url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_companies_company_id ON companies(company_id);
        CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
        CREATE INDEX IF NOT EXISTS idx_companies_url ON companies(url);
        CREATE INDEX IF NOT EXISTS idx_companies_iva ON companies(iva);
        """
    
    def create_indeed_scrapped_data_table(self) -> str:
        """Create raw scrapped data table migration"""
        return """
        CREATE TABLE IF NOT EXISTS it_indeed_scrapped_data (
            id SERIAL PRIMARY KEY,
            job_url_indeed TEXT UNIQUE NOT NULL,
            title TEXT,
            company_name TEXT,
            location TEXT,
            description TEXT,
            salary TEXT,
            date_posted DATE,
            job_type TEXT,
            remote BOOLEAN DEFAULT FALSE,
            skills JSONB,
            experience_level TEXT,
            employment_type TEXT,
            company_rating TEXT,
            full_description TEXT,
            company_url_indeed TEXT,
            extraction_date DATE DEFAULT CURRENT_DATE,
            status VARCHAR(20) DEFAULT 'extracted',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_indeed_scrapped_job_url ON it_indeed_scrapped_data(job_url_indeed);
        CREATE INDEX IF NOT EXISTS idx_indeed_scrapped_status ON it_indeed_scrapped_data(status);
        CREATE INDEX IF NOT EXISTS idx_indeed_scrapped_date ON it_indeed_scrapped_data(extraction_date);
        CREATE INDEX IF NOT EXISTS idx_indeed_scrapped_company ON it_indeed_scrapped_data(company_name);
        """
    
    def create_indeed_result_data_table(self) -> str:
        """Create processed results table migration"""
        return """
        CREATE TABLE IF NOT EXISTS it_indeed_result_data (
            id SERIAL PRIMARY KEY,
            scrapped_job_id INTEGER REFERENCES it_indeed_scrapped_data(id),
            job_url_indeed TEXT NOT NULL,
            company_url_indeed TEXT,
            job_offer_text TEXT,
            company_id INTEGER REFERENCES companies(id),
            extraction_date DATE DEFAULT CURRENT_DATE,
            company_website_url TEXT,
            match_type VARCHAR(20), -- 'url', 'name', 'google_api', 'none'
            match_confidence DECIMAL(5,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_indeed_result_job_url ON it_indeed_result_data(job_url_indeed);
        CREATE INDEX IF NOT EXISTS idx_indeed_result_company ON it_indeed_result_data(company_id);
        CREATE INDEX IF NOT EXISTS idx_indeed_result_date ON it_indeed_result_data(extraction_date);
        """
    
    async def execute_query(self, query: str, *args) -> Any:
        """Execute a query and return results"""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def execute_query_one(self, query: str, *args) -> Any:
        """Execute a query and return single result"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def execute_insert(self, query: str, *args) -> Any:
        """Execute insert query and return inserted record"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def execute_many(self, query: str, args_list: List[tuple]) -> None:
        """Execute query with multiple parameter sets"""
        async with self.pool.acquire() as conn:
            await conn.executemany(query, args_list)
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

# Global database manager instance
db_manager = DatabaseManager()