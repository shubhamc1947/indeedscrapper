import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

async def test_indeed_click_approach():
    """Test scraping Indeed by clicking jobs in the list view"""
    
    results = []
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(
            headless=False,  # Set to True for production
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='it-IT',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        
        # Navigate to search results
        search_url = "https://it.indeed.com/jobs?q=&l=Milano%2C+Lombardia&sort=date&fromage=1"
        print(f"Loading: {search_url}")
        await page.goto(search_url, wait_until='networkidle', timeout=60000)
        await asyncio.sleep(3)
        
        # Find all job cards in the left pane
        job_cards = await page.query_selector_all('li.css-1ac2h1w > div[class*="cardOutline"]')
        print(f"Found {len(job_cards)} job cards")
        
        # Process first 5 jobs only for testing
        for idx, card in enumerate(job_cards[:5], 1):
            try:
                print(f"\n--- Processing Job {idx}/{min(5, len(job_cards))} ---")
                
                # Click the job card to load details in right pane
                job_link = await card.query_selector('a.jcs-JobTitle')
                if not job_link:
                    print("No job link found, skipping")
                    continue
                
                # Get job URL before clicking
                job_url = await job_link.get_attribute('href')
                if job_url and not job_url.startswith('http'):
                    job_url = f"https://it.indeed.com{job_url}"
                
                # Get job title from the card
                title_elem = await card.query_selector('span[id^="jobTitle-"]')
                title = await title_elem.inner_text() if title_elem else "Unknown"
                print(f"Title: {title}")
                
                # Click to load full details in right pane
                await job_link.click()
                print("Clicked job, waiting for details to load...")
                
                # Wait for the right pane to update with new content
                await page.wait_for_selector('#jobDescriptionText', timeout=10000)
                await asyncio.sleep(2)  # Additional wait for full content load
                
                # Extract details from the RIGHT PANE
                job_data = {
                    'title': title,
                    'job_url_indeed': job_url,
                    'scraped_at': datetime.now().isoformat()
                }
                
                # Company name
                company_elem = await page.query_selector('[data-testid="inlineHeader-companyName"]')
                if company_elem:
                    company_text = await company_elem.inner_text()
                    job_data['company_name'] = company_text.strip()
                    print(f"Company: {job_data['company_name']}")
                
                # Location
                location_elem = await page.query_selector('[data-testid="inlineHeader-companyLocation"]')
                if location_elem:
                    job_data['location'] = (await location_elem.inner_text()).strip()
                    print(f"Location: {job_data['location']}")
                
                # Salary
                salary_elem = await page.query_selector('#salaryInfoAndJobType span')
                if salary_elem:
                    job_data['salary'] = (await salary_elem.inner_text()).strip()
                    print(f"Salary: {job_data['salary']}")
                
                # Company rating
                rating_elem = await page.query_selector('span.css-10jzft1')
                if rating_elem:
                    job_data['company_rating'] = (await rating_elem.inner_text()).strip()
                
                # Full job description - THE KEY BENEFIT
                desc_elem = await page.query_selector('#jobDescriptionText')
                if desc_elem:
                    job_data['full_description'] = (await desc_elem.inner_text()).strip()
                    desc_preview = job_data['full_description'][:200]
                    print(f"Description preview: {desc_preview}...")
                
                # Company Indeed URL
                company_link_elem = await page.query_selector('[data-testid="inlineHeader-companyName"] a')
                if company_link_elem:
                    company_url = await company_link_elem.get_attribute('href')
                    if company_url:
                        job_data['company_url_indeed'] = f"https://it.indeed.com{company_url}" if not company_url.startswith('http') else company_url
                
                results.append(job_data)
                print(f"✓ Successfully scraped job {idx}")
                
                # Small delay between jobs
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"✗ Error processing job {idx}: {e}")
                continue
        
        await browser.close()
    
    # Save results to file
    output_file = f'indeed_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"Test complete! Scraped {len(results)} jobs")
    print(f"Results saved to: {output_file}")
    print(f"{'='*60}")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_indeed_click_approach())