import asyncio
from playwright.async_api import async_playwright

async def check_netlify():
    async with async_playwright() as p:
        # Connect to existing Chrome via CDP
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        pages = context.pages
        
        print(f"Found {len(pages)} open tabs")
        
        netlify_page = None
        for page in pages:
            url = page.url
            print(f"Tab: {url}")
            if "netlify" in url.lower() and "app.netlify.com" in url:
                netlify_page = page
                break
        
        if not netlify_page:
            print("\n❌ Netlify tab not found. Opening Netlify...")
            netlify_page = await context.new_page()
            await netlify_page.goto("https://app.netlify.com", wait_until="networkidle")
        
        print(f"\n[OK] Using Netlify tab: {netlify_page.url}")
        
        # Check if logged in
        try:
            await netlify_page.wait_for_load_state("networkidle", timeout=10000)
        except:
            pass
        
        # Check for login indicators
        content = await netlify_page.content()
        
        if "Sign up" in content or "Log in" in content or "login" in content.lower():
            print("[FAIL] NOT LOGGED IN - Need to login first")
        else:
            print("[OK] LOGGED IN to Netlify")
            
            # Check for team/project selection
            if "AutoTrade Nexus" in content or "autotradenexus" in content:
                print("[OK] AutoTrade Nexus project found in dashboard")
            else:
                print("[WARN] AutoTrade Nexus project not visible - may need to select team/project")
        
        # Check for deploy status
        if "Published" in content or "Deployed" in content or "Live" in content:
            print("[OK] Site appears to be deployed/published")
        elif "Drag and drop" in content or "deploy" in content.lower():
            print("[WARN] Deploy area visible - site may not be deployed yet")
        
        # Screenshot for verification
        await netlify_page.screenshot(path="netlify_check.png", full_page=True)
        print("\n[INFO] Screenshot saved: netlify_check.png")
        
        # Check the actual site
        print("\n--- Checking live site ---")
        site_page = await context.new_page()
        try:
            response = await site_page.goto("https://autotradenexus.netlify.app/", wait_until="networkidle", timeout=15000)
            print(f"Homepage status: {response.status}")
            
            # Check robots.txt
            robots_response = await site_page.goto("https://autotradenexus.netlify.app/robots.txt", wait_until="networkidle")
            print(f"robots.txt status: {robots_response.status}")
            if robots_response.status == 200:
                robots_content = await site_page.content()
                print(f"robots.txt preview: {robots_content[:200]}")
            
            # Check sitemap.xml
            sitemap_response = await site_page.goto("https://autotradenexus.netlify.app/sitemap.xml", wait_until="networkidle")
            print(f"sitemap.xml status: {sitemap_response.status}")
            
            # Check features page
            features_response = await site_page.goto("https://autotradenexus.netlify.app/features", wait_until="networkidle")
            print(f"/features status: {features_response.status}")
            
            # Check pricing page
            pricing_response = await site_page.goto("https://autotradenexus.netlify.app/pricing", wait_until="networkidle")
            print(f"/pricing status: {pricing_response.status}")
            
        except Exception as e:
            print(f"Error checking live site: {e}")
        
        await site_page.close()
        await browser.close()

asyncio.run(check_netlify())