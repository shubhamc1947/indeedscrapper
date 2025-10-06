import asyncio
import json
import random
from datetime import datetime
from playwright.async_api import async_playwright

async def human_like_mouse_movement(page):
    """Simulate realistic mouse movements"""
    for _ in range(random.randint(3, 6)):
        x = random.randint(100, 1500)
        y = random.randint(100, 800)
        steps = random.randint(20, 40)
        await page.mouse.move(x, y, steps=steps)
        await asyncio.sleep(random.uniform(0.1, 0.3))

async def human_like_scroll(page):
    """Simulate human scrolling behavior"""
    viewport_height = await page.evaluate('window.innerHeight')
    total_height = await page.evaluate('document.body.scrollHeight')
    
    current_pos = 0
    scroll_count = random.randint(3, 7)
    
    for _ in range(scroll_count):
        scroll_amount = random.randint(150, 400)
        
        if current_pos + scroll_amount < total_height - viewport_height:
            await page.evaluate(f'window.scrollBy(0, {scroll_amount})')
            current_pos += scroll_amount
            await asyncio.sleep(random.uniform(0.8, 2.5))
            
            # Sometimes scroll back up a bit (like humans do)
            if random.random() < 0.3:
                back_scroll = random.randint(50, 150)
                await page.evaluate(f'window.scrollBy(0, -{back_scroll})')
                current_pos -= back_scroll
                await asyncio.sleep(random.uniform(0.5, 1.2))

async def check_page_state(page):
    """Check for blocks, login walls, etc"""
    try:
        url = page.url
        title = await page.title()
        
        print(f"\n[STATE] URL: {url}")
        print(f"[STATE] Title: {title}")
        
        # Check for auth/login
        if 'auth' in url or 'login' in url.lower() or 'bot-detection' in url:
            print("[STATE] ❌ Bot detection/auth page")
            return 'blocked'
        
        # Check for job cards
        await asyncio.sleep(2)
        job_cards = await page.query_selector_all('li.css-1ac2h1w > div[class*="cardOutline"]')
        print(f"[STATE] ✓ Found {len(job_cards)} job cards")
        
        if len(job_cards) == 0:
            return 'no_jobs'
        
        return 'normal'
        
    except Exception as e:
        print(f"[STATE] Error: {e}")
        return 'error'

async def scrape_with_maximum_stealth(max_pages=2):
    """Scrape with extreme human-like behavior"""
    
    all_results = []
    
    async with async_playwright() as p:
        # Launch with maximum stealth
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-features=IsolateOrigins,site-per-process',
                '--flag-switches-begin --disable-site-isolation-trials --flag-switches-end'
            ]
        )
        
        # Create context with realistic settings
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='it-IT',
            timezone_id='Europe/Rome',
            geolocation={'longitude': 9.1900, 'latitude': 45.4642},  # Milan coordinates
            permissions=['geolocation'],
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            device_scale_factor=1,
            has_touch=False,
            is_mobile=False,
            color_scheme='light'
        )
        
        # Comprehensive stealth scripts
        await context.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Add plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5].map(i => ({
                    name: `Plugin ${i}`,
                    filename: `plugin${i}.so`,
                    description: `Description ${i}`
                }))
            });
            
            // Languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['it-IT', 'it', 'en-US', 'en']
            });
            
            // Chrome object
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            // Modernizr test results
            window.Modernizr = {
                webgl: true,
                canvas: true
            };
        """)
        
        page = await context.new_page()
        
        # Set extra headers
        await page.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        for page_num in range(max_pages):
            try:
                start = page_num * 10
                search_url = f"https://it.indeed.com/jobs?q=&l=Milano%2C+Lombardia&sort=date&fromage=1&start={start}"
                
                print(f"\n{'='*80}")
                print(f"PAGE {page_num + 1}/{max_pages}")
                print(f"{'='*80}")
                
                # Navigate
                print(f"[NAV] Going to page...")
                await page.goto(search_url, wait_until='domcontentloaded', timeout=120000)
                await asyncio.sleep(random.uniform(3, 5))
                
                # Check state
                state = await check_page_state(page)
                if state == 'blocked':
                    print("\n[BLOCKED] Indeed detected automation. Stopping.")
                    screenshot = f"blocked_{datetime.now().strftime('%H%M%S')}.png"
                    await page.screenshot(path=screenshot)
                    print(f"Screenshot: {screenshot}")
                    break
                elif state != 'normal':
                    print(f"\n[ERROR] Unexpected state: {state}")
                    break
                
                # Act like human browsing search results
                print("\n[HUMAN] Simulating human behavior on search page...")
                
                # Random mouse movements
                await human_like_mouse_movement(page)
                await asyncio.sleep(random.uniform(1, 2))
                
                # Scroll through results
                await human_like_scroll(page)
                await asyncio.sleep(random.uniform(2, 4))
                
                # More mouse movements
                await human_like_mouse_movement(page)
                await asyncio.sleep(random.uniform(1, 2))
                
                # Get job cards
                job_cards = await page.query_selector_all('li.css-1ac2h1w > div[class*="cardOutline"]')
                print(f"\n[JOBS] Processing {len(job_cards)} jobs...")
                
                # Only scrape 5-8 jobs per page (humans don't check every job)
                jobs_to_process = random.randint(5, min(8, len(job_cards)))
                selected_indices = random.sample(range(len(job_cards)), jobs_to_process)
                
                for idx in selected_indices:
                    card = job_cards[idx]
                    try:
                        global_idx = (page_num * 10) + idx + 1
                        print(f"\n--- Job {global_idx} ---")
                        
                        # Random delay before clicking (humans pause)
                        await asyncio.sleep(random.uniform(2, 5))
                        
                        # Find link
                        job_link = await card.query_selector('a.jcs-JobTitle')
                        if not job_link:
                            continue
                        
                        # Get basic info
                        job_url = await job_link.get_attribute('href')
                        if job_url and not job_url.startswith('http'):
                            job_url = f"https://it.indeed.com{job_url}"
                        
                        title_elem = await card.query_selector('span[id^="jobTitle-"]')
                        title = await title_elem.inner_text() if title_elem else "Unknown"
                        print(f"Title: {title[:60]}...")
                        
                        # Hover before clicking (very human-like)
                        box = await job_link.bounding_box()
                        if box:
                            await page.mouse.move(
                                box['x'] + box['width'] / 2,
                                box['y'] + box['height'] / 2,
                                steps=random.randint(10, 20)
                            )
                            await asyncio.sleep(random.uniform(0.5, 1.5))
                        
                        # Click
                        await job_link.click()
                        await asyncio.sleep(random.uniform(2, 4))
                        
                        # Wait for details
                        try:
                            await page.wait_for_selector('#jobDescriptionText', state='visible', timeout=10000)
                            await asyncio.sleep(random.uniform(1.5, 3))
                        except:
                            print("[WARN] Details timeout")
                            continue
                        
                        # Read the job (scroll in right pane)
                        print("[READ] Simulating reading...")
                        for _ in range(random.randint(2, 4)):
                            await page.mouse.wheel(0, random.randint(100, 300))
                            await asyncio.sleep(random.uniform(1, 2.5))
                        
                        # Extract data
                        job_data = {
                            'page': page_num + 1,
                            'position': idx + 1,
                            'global_id': global_idx,
                            'title': title,
                            'url': job_url,
                            'scraped': datetime.now().isoformat()
                        }
                        
                        # Company
                        try:
                            elem = await page.query_selector('[data-testid="inlineHeader-companyName"]')
                            if elem:
                                job_data['company'] = (await elem.inner_text()).strip()
                                print(f"Company: {job_data['company']}")
                        except:
                            pass
                        
                        # Location
                        try:
                            elem = await page.query_selector('[data-testid="inlineHeader-companyLocation"]')
                            if elem:
                                job_data['location'] = (await elem.inner_text()).strip()
                        except:
                            pass
                        
                        # Salary
                        try:
                            sections = await page.query_selector_all('#jobDetailsSection div[role="group"]')
                            for section in sections:
                                text = await section.inner_text()
                                if 'Retribuzione' in text:
                                    items = await section.query_selector_all('li[data-testid="list-item"]')
                                    if items:
                                        job_data['salary'] = (await items[0].inner_text()).strip()
                                        print(f"Salary: {job_data['salary']}")
                                    break
                        except:
                            pass
                        
                        # Contract
                        try:
                            sections = await page.query_selector_all('#jobDetailsSection div[role="group"]')
                            for section in sections:
                                text = await section.inner_text()
                                if 'Tipo di contratto' in text:
                                    items = await section.query_selector_all('li[data-testid="list-item"]')
                                    contracts = []
                                    for item in items:
                                        contracts.append((await item.inner_text()).strip())
                                    if contracts:
                                        job_data['contract'] = contracts
                                        print(f"Contract: {contracts}")
                                    break
                        except:
                            pass
                        
                        # Description
                        try:
                            elem = await page.query_selector('#jobDescriptionText')
                            if elem:
                                job_data['description'] = (await elem.inner_text()).strip()
                                print(f"Description: {len(job_data['description'])} chars")
                        except:
                            pass
                        
                        all_results.append(job_data)
                        print("✓ Scraped")
                        
                    except Exception as e:
                        print(f"❌ Error: {e}")
                        continue
                
                # Long delay between pages
                if page_num < max_pages - 1:
                    delay = random.uniform(45, 75)
                    print(f"\n[DELAY] Waiting {delay:.1f}s before next page (acting human)...")
                    await asyncio.sleep(delay)
                
            except Exception as e:
                print(f"❌ Page error: {e}")
                continue
        
        await browser.close()
    
    # Save
    output = f'stealth_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print(f"Scraped {len(all_results)} jobs")
    print(f"Saved: {output}")
    print(f"{'='*80}")
    
    return all_results

if __name__ == "__main__":
    # Only scrape 2 pages to minimize detection risk
    results = asyncio.run(scrape_with_maximum_stealth(max_pages=2))