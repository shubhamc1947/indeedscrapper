#!/usr/bin/env python3
"""
Company Data Import Script
Imports company data from JSON file into PostgreSQL database
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_utils import db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompanyImporter:
    def __init__(self):
        self.imported_count = 0
        self.updated_count = 0
        self.failed_count = 0
    
    async def import_companies_from_json(self, json_file_path: str) -> None:
        """Import companies from JSON file"""
        try:
            # Read JSON file
            with open(json_file_path, 'r', encoding='utf-8') as f:
                companies_data = json.load(f)
            
            logger.info(f"Loaded {len(companies_data)} companies from {json_file_path}")
            
            # Process companies in batches
            batch_size = 100
            for i in range(0, len(companies_data), batch_size):
                batch = companies_data[i:i + batch_size]
                await self.process_company_batch(batch)
                logger.info(f"Processed batch {i//batch_size + 1}/{(len(companies_data) + batch_size - 1)//batch_size}")
            
            logger.info(f"Import completed: {self.imported_count} imported, {self.updated_count} updated, {self.failed_count} failed")
            
        except FileNotFoundError:
            logger.error(f"JSON file not found: {json_file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {e}")
            raise
        except Exception as e:
            logger.error(f"Import failed: {e}")
            raise
    
    async def process_company_batch(self, companies: List[Dict[str, Any]]) -> None:
        """Process a batch of companies"""
        for company_data in companies:
            try:
                await self.import_single_company(company_data)
            except Exception as e:
                logger.error(f"Failed to import company {company_data.get('companyID', 'unknown')}: {e}")
                self.failed_count += 1
    
    async def import_single_company(self, company_data: Dict[str, Any]) -> None:
        """Import or update a single company"""
        try:
            # Check if company already exists
            existing_company = await db_manager.execute_query_one(
                "SELECT id FROM companies WHERE company_id = $1",
                company_data.get('companyID')
            )
            
            if existing_company:
                await self.update_company(company_data, existing_company['id'])
                self.updated_count += 1
            else:
                await self.insert_company(company_data)
                self.imported_count += 1
                
        except Exception as e:
            logger.error(f"Error processing company {company_data.get('companyID')}: {e}")
            raise
    
    async def insert_company(self, company_data: Dict[str, Any]) -> None:
        """Insert new company"""
        query = """
        INSERT INTO companies (
            company_id, legal_name, vat, iva, name, url, created_at, updated_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8
        )
        """
        
        current_time = datetime.now()
        
        await db_manager.execute_insert(
            query,
            company_data.get('companyID'),
            company_data.get('ragioneSociale'),
            company_data.get('vat'),
            company_data.get('iva'),
            company_data.get('name'),
            company_data.get('url'),
            current_time,
            current_time
        )
    
    async def update_company(self, company_data: Dict[str, Any], company_id: int) -> None:
        """Update existing company"""
        query = """
        UPDATE companies SET
            legal_name = $2, vat = $3, iva = $4, name = $5, url = $6, updated_at = $7
        WHERE id = $1
        """
        
        await db_manager.execute_insert(
            query,
            company_id,
            company_data.get('ragioneSociale'),
            company_data.get('vat'),
            company_data.get('iva'),
            company_data.get('name'),
            company_data.get('url'),
            datetime.now()
        )

async def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python import_companies.py <path_to_companies.json>")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    
    if not os.path.exists(json_file_path):
        logger.error(f"File not found: {json_file_path}")
        sys.exit(1)
    
    try:
        # Initialize database
        await db_manager.initialize()
        logger.info("Database initialized successfully")
        
        # Import companies
        importer = CompanyImporter()
        await importer.import_companies_from_json(json_file_path)
        
        logger.info("Company import completed successfully")
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        sys.exit(1)
    finally:
        await db_manager.close()

if __name__ == "__main__":
    asyncio.run(main())