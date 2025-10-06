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
        
        print(f"[STATE] URL: {url}")
        print(f"[STATE] Title: {title}")
        
        if 'auth' in url or 'login' in url.lower() or 'bot-detection' in url:
            print("[STATE] ❌ Bot detection/auth page")
            return 'blocked'
        
        await asyncio.sleep(2)
        job_cards = await page.query_selector_all('li.css-1ac2h1w > div[class*="cardOutline"]')
        print(f"[STATE] ✓ Found {len(job_cards)} job cards")
        
        if len(job_cards) == 0:
            return 'no_jobs'
        
        return 'normal'
        
    except Exception as e:
        print(f"[STATE] Error: {e}")
        return 'error'

async def scrape_single_page(page_config):
    """
    Scrape a single page in a completely fresh browser session.
    Each call creates and destroys a new browser instance.
    """
    page_num = page_config['page_num']
    start_offset = page_config['start_offset']
    location = page_config['location']
    
    results = []
    
    async with async_playwright() as p:
        # Launch fresh browser
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
        )
        
        # Random viewport dimensions
        width = random.choice([1920, 1366, 1440, 1536])
        height = random.choice([1080, 768, 900, 864])
        
        # Create context with realistic settings
        context = await browser.new_context(
            viewport={'width': width, 'height': height},
            locale='it-IT',
            timezone_id='Europe/Rome',
            geolocation={'longitude': 9.1900, 'latitude': 45.4642},
            permissions=['geolocation'],
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            device_scale_factor=random.choice([1.0, 1.25]),
            has_touch=False,
            is_mobile=False,
            color_scheme=random.choice(['light', 'dark'])
        )
        
        # Stealth scripts
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5].map(i => ({
                    name: `Plugin ${i}`,
                    filename: `plugin${i}.so`,
                    description: `Description ${i}`
                }))
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['it-IT', 'it', 'en-US', 'en']
            });
            
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
        """)
        
        page = await context.new_page()
        
        # Set headers
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
        
        try:
            search_url = f"https://it.indeed.com/jobs?q=&l={location}&sort=date&fromage=1&start={start_offset}"
            
            print(f"\n{'='*80}")
            print(f"SESSION {page_num} - Location: {location} - Offset: {start_offset}")
            print(f"{'='*80}")
            
            # Navigate
            print(f"[NAV] Opening Indeed...")
            await page.goto(search_url, wait_until='domcontentloaded', timeout=120000)
            await asyncio.sleep(random.uniform(4, 7))
            
            # Check state
            state = await check_page_state(page)
            if state == 'blocked':
                print("\n[BLOCKED] Cloudflare/bot detection triggered!")
                screenshot = f"blocked_{datetime.now().strftime('%H%M%S')}.png"
                await page.screenshot(path=screenshot)
                print(f"Screenshot: {screenshot}")
                await browser.close()
                return results
            elif state != 'normal':
                print(f"\n[ERROR] Unexpected state: {state}")
                await browser.close()
                return results
            
            # Act like human
            print("\n[HUMAN] Browsing search results...")
            await human_like_mouse_movement(page)
            await asyncio.sleep(random.uniform(2, 4))
            await human_like_scroll(page)
            await asyncio.sleep(random.uniform(3, 5))
            await human_like_mouse_movement(page)
            
            # Get jobs
            job_cards = await page.query_selector_all('li.css-1ac2h1w > div[class*="cardOutline"]')
            print(f"\n[JOBS] Found {len(job_cards)} jobs")
            
            # Only process 5-8 random jobs
            jobs_to_process = random.randint(5, min(8, len(job_cards)))
            selected_indices = random.sample(range(len(job_cards)), jobs_to_process)
            
            for idx in selected_indices:
                card = job_cards[idx]
                try:
                    print(f"\n--- Job {idx + 1} ---")
                    await asyncio.sleep(random.uniform(2, 5))
                    
                    job_link = await card.query_selector('a.jcs-JobTitle')
                    if not job_link:
                        continue
                    
                    job_url = await job_link.get_attribute('href')
                    if job_url and not job_url.startswith('http'):
                        job_url = f"https://it.indeed.com{job_url}"
                    
                    title_elem = await card.query_selector('span[id^="jobTitle-"]')
                    title = await title_elem.inner_text() if title_elem else "Unknown"
                    print(f"Title: {title[:60]}...")
                    
                    # Hover and click
                    box = await job_link.bounding_box()
                    if box:
                        await page.mouse.move(
                            box['x'] + box['width'] / 2,
                            box['y'] + box['height'] / 2,
                            steps=random.randint(10, 20)
                        )
                        await asyncio.sleep(random.uniform(0.5, 1.5))
                    
                    await job_link.click()
                    await asyncio.sleep(random.uniform(3, 5))
                    
                    # Wait for details
                    try:
                        await page.wait_for_selector('#jobDescriptionText', state='visible', timeout=10000)
                        await asyncio.sleep(random.uniform(2, 4))
                    except:
                        print("[WARN] Details timeout")
                        continue
                    
                    # Read job (scroll)
                    print("[READ] Reading job details...")
                    for _ in range(random.randint(2, 4)):
                        await page.mouse.wheel(0, random.randint(100, 300))
                        await asyncio.sleep(random.uniform(1, 2.5))
                    
                    # Extract data
                    job_data = {
                        'session': page_num,
                        'location': location,
                        'position': idx + 1,
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
                            job_data['location_detail'] = (await elem.inner_text()).strip()
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
                    
                    results.append(job_data)
                    print("✓ Scraped")
                    
                except Exception as e:
                    print(f"❌ Error: {e}")
                    continue
            
        except Exception as e:
            print(f"❌ Session error: {e}")
        
        finally:
            # Always close browser
            print(f"\n[CLOSE] Closing browser session {page_num}")
            await browser.close()
    
    return results

async def scrape_multiple_sessions():
    """
    Main function: scrape multiple pages using separate browser sessions.
    Each session starts fresh with new location/offset.
    """
    
    # Configuration: define your searches
    # You can vary location, search terms, or just pagination offsets
    sessions = [
        {'page_num': 1, 'start_offset': 0, 'location': 'Milano%2C+Lombardia'},
        {'page_num': 2, 'start_offset': 10, 'location': 'Milano%2C+Lombardia'},
        {'page_num': 3, 'start_offset': 20, 'location': 'Milano%2C+Lombardia'},
        # You can also change locations to make it even more natural:
        # {'page_num': 4, 'start_offset': 0, 'location': 'Roma%2C+Lazio'},
        # {'page_num': 5, 'start_offset': 0, 'location': 'Torino%2C+Piemonte'},
    ]
    
    all_results = []
    
    for i, config in enumerate(sessions):
        print(f"\n\n🚀 Starting session {i+1}/{len(sessions)}")
        
        # Scrape this session
        results = await scrape_single_page(config)
        all_results.extend(results)
        
        # Long delay between sessions (very important!)
        if i < len(sessions) - 1:
            delay = random.uniform(60, 120)  # 1-2 minutes between sessions
            print(f"\n⏳ Waiting {delay:.1f}s before next session...")
            print("   (This makes it look like a real user coming back later)")
            await asyncio.sleep(delay)
    
    # Save all results
    output = f'sessions_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print(f"✅ COMPLETE: Scraped {len(all_results)} jobs across {len(sessions)} sessions")
    print(f"📁 Saved: {output}")
    print(f"{'='*80}")
    
    return all_results

if __name__ == "__main__":
    results = asyncio.run(scrape_multiple_sessions())