import asyncio
import json
from playwright.async_api import async_playwright

async def run_lighthouse_audits():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        
        urls = [
            "https://autotradenexus.netlify.app/",
            "https://autotradenexus.netlify.app/features",
            "https://autotradenexus.netlify.app/pricing",
            "https://autotradenexus.netlify.app/brokers",
            "https://autotradenexus.netlify.app/faq",
            "https://autotradenexus.netlify.app/blog"
        ]
        
        results = {}
        
        for url in urls:
            print(f"\n--- Auditing {url} ---")
            page = await context.new_page()
            try:
                # Navigate to the page
                response = await page.goto(url, wait_until="networkidle", timeout=30000)
                print(f"Status: {response.status}")
                
                # Run Lighthouse via CDP
                # We'll use the Lighthouse API through Chrome DevTools Protocol
                cdp_session = await page.context.new_cdp_session(page)
                
                # Enable necessary domains
                await cdp_session.send("Lighthouse.enable")
                await cdp_session.send("Page.enable")
                await cdp_session.send("Network.enable")
                await cdp_session.send("Runtime.enable")
                
                # Start Lighthouse audit
                # Using the lighthouse.audit command (available in newer Chrome versions)
                try:
                    audit_result = await cdp_session.send("Lighthouse.audit", {
                        "url": url,
                        "config": {
                            "categories": ["performance", "accessibility", "best-practices", "seo"],
                            "formFactor": "desktop"
                        }
                    })
                    
                    categories = audit_result.get("categories", {})
                    for cat_name, cat_data in categories.items():
                        score = cat_data.get("score", 0) * 100
                        print(f"  {cat_name}: {score:.0f}/100")
                    
                    results[url] = {
                        "status": response.status,
                        "categories": {k: v.get("score", 0) * 100 for k, v in categories.items()}
                    }
                except Exception as e:
                    print(f"  Lighthouse error: {e}")
                    # Fallback: basic checks
                    results[url] = {"status": response.status, "error": str(e)}
                
                await cdp_session.detach()
                
            except Exception as e:
                print(f"  Error: {e}")
                results[url] = {"error": str(e)}
            finally:
                await page.close()
        
        # Save results
        with open("lighthouse_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print("\n\n=== LIGHTHOUSE SUMMARY ===")
        for url, data in results.items():
            if "categories" in data:
                print(f"\n{url}")
                for cat, score in data["categories"].items():
                    print(f"  {cat}: {score:.0f}/100")
            else:
                print(f"\n{url}: {data}")
        
        await browser.close()

asyncio.run(run_lighthouse_audits())