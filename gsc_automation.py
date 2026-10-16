import asyncio
from playwright.async_api import async_playwright

async def gsc_setup():
    async with async_playwright() as p:
        # Connect to existing Chrome via CDP
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        pages = context.pages
        
        print(f"Found {len(pages)} open tabs")
        
        gsc_page = None
        for page in pages:
            url = page.url
            print(f"Tab: {url}")
            if "search.google.com" in url and "search-console" in url and "autotradenexus" in url:
                gsc_page = page
                break
        
        if not gsc_page:
            print("GSC tab with autotradenexus not found!")
            return
        
        print(f"\n[OK] Using GSC tab: {gsc_page.url}")
        await gsc_page.bring_to_front()
        await gsc_page.wait_for_load_state("networkidle", timeout=15000)
        
        content = await gsc_page.content()
        
        # Check if already verified
        if "Verified" in content or "verified" in content.lower():
            print("[OK] Property appears to be already verified!")
        else:
            print("⚠️  Property not verified yet. Checking verification methods...")
        
        # Look for verification methods / HTML tag
        # Navigate to settings if needed
        try:
            # Try to find "Settings" or gear icon
            settings_selectors = [
                '[aria-label="Settings"]',
                'a[href*="settings"]',
                'button[aria-label="Settings"]',
                'text="Settings"',
            ]
            
            for sel in settings_selectors:
                try:
                    await gsc_page.click(sel, timeout=3000)
                    print(f"Clicked Settings with: {sel}")
                    await gsc_page.wait_for_load_state("networkidle", timeout=10000)
                    break
                except:
                    continue
            
            # Look for "Ownership verification" or "Verification methods"
            verify_selectors = [
                'text="Ownership verification"',
                'text="Verification methods"',
                'a[href*="verification"]',
                'text="Verify"',
            ]
            
            for sel in verify_selectors:
                try:
                    await gsc_page.click(sel, timeout=3000)
                    print(f"Clicked verification with: {sel}")
                    await gsc_page.wait_for_load_state("networkidle", timeout=10000)
                    break
                except:
                    continue
            
            # Now look for HTML tag option
            await gsc_page.wait_for_timeout(2000)
            
            html_tag_selectors = [
                'text="HTML tag"',
                '[value="html-tag"]',
                'text="HTML file"',  # sometimes labeled differently
            ]
            
            for sel in html_tag_selectors:
                try:
                    await gsc_page.click(sel, timeout=3000)
                    print(f"Selected HTML tag with: {sel}")
                    await gsc_page.wait_for_timeout(2000)
                    break
                except:
                    continue
            
            # Extract the meta tag
            meta_tag = await gsc_page.evaluate("""
                () => {
                    // Look for the meta tag in various places
                    const codeElements = document.querySelectorAll('code, pre, textarea, input[readonly], .code-snippet, [data-test-id="verification-code"]');
                    for (const el of codeElements) {
                        const text = el.innerText || el.value || el.textContent || '';
                        if (text.includes('google-site-verification')) {
                            return text.trim();
                        }
                    }
                    // Also check for any element containing the verification code
                    const allText = document.body.innerText;
                    const match = allText.match(/<meta name="google-site-verification" content="[^"]*"[^>]*>/);
                    if (match) return match[0];
                    return null;
                }
            """)
            
            if meta_tag:
                print("[OK] FOUND META TAG:")
                print(meta_tag)
                
                # Save to file for user
                with open("gsc_meta_tag.txt", "w") as f:
                    f.write(meta_tag)
                print("[OK] Saved to gsc_meta_tag.txt")
            else:
                print("[WARN] Could not auto-extract meta tag. Taking screenshot...")
                await gsc_page.screenshot(path="gsc_verification.png", full_page=True)
                print("[OK] Screenshot saved: gsc_verification.png")
                
                # Also dump page text for manual extraction
                text = await gsc_page.evaluate("() => document.body.innerText")
                with open("gsc_page_text.txt", "w", encoding="utf-8") as f:
                    f.write(text)
                print("[OK] Full page text saved to gsc_page_text.txt - search for 'google-site-verification'")
        
        except Exception as e:
            print(f"Error during GSC automation: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback: screenshot
            await gsc_page.screenshot(path="gsc_error.png", full_page=True)
            print("[OK] Error screenshot saved: gsc_error.png")
        
        await browser.close()

asyncio.run(gsc_setup())