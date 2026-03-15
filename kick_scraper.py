#!/usr/bin/env python3
"""
Alternative Kick.com data scraper using Selenium WebDriver.
This approach uses browser automation to bypass bot protection.
"""

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

import json
import time
import re
from typing import Dict, Any, List, Optional

def test_selenium_approach():
    """Test if we can access Kick.com using Selenium WebDriver."""
    if not SELENIUM_AVAILABLE:
        print("Selenium is not installed. Install with: pip install selenium")
        print("You'll also need ChromeDriver: https://chromedriver.chromium.org/")
        return False
    
    print("Testing Selenium WebDriver approach...")
    print("=" * 50)
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    # For headless browsing (uncomment if needed)
    # chrome_options.add_argument("--headless")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("Attempting to load Kick.com main page...")
        driver.get("https://kick.com")
        
        # Wait for page to load
        time.sleep(5)
        
        # Check if we got blocked
        page_title = driver.title
        page_source = driver.page_source
        
        print(f"Page title: {page_title}")
        print(f"Page source length: {len(page_source)} characters")
        
        # Look for common blocking indicators
        blocked_indicators = [
            "403 Forbidden",
            "Access Denied",
            "security policy",
            "Cloudflare",
            "DDoS protection"
        ]
        
        blocked = any(indicator.lower() in page_source.lower() for indicator in blocked_indicators)
        
        if blocked:
            print("❌ Still blocked by security policy")
            # Save page source for debugging
            with open("kick_blocked_page.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            print("Saved blocked page to kick_blocked_page.html for analysis")
        else:
            print("✅ Successfully loaded Kick.com!")
            
            # Try to find live streams data
            try:
                # Wait for content to load
                WebDriverWait(driver, 10).wait(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Look for stream data in the page
                scripts = driver.find_elements(By.TAG_NAME, "script")
                
                for script in scripts:
                    script_content = script.get_attribute("innerHTML") or ""
                    
                    # Look for JSON data containing stream information
                    if any(keyword in script_content.lower() for keyword in ["livestream", "channels", "viewer", "category"]):
                        print("Found potential stream data in script tag")
                        
                        # Try to extract JSON
                        json_matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', script_content)
                        
                        for match in json_matches[:3]:  # Check first 3 matches
                            try:
                                data = json.loads(match)
                                if isinstance(data, dict) and any(key in data for key in ["livestream", "channels", "data"]):
                                    print(f"Found JSON stream data with keys: {list(data.keys())}")
                                    return True
                            except json.JSONDecodeError:
                                continue
                
                # Alternative: Look for specific elements that contain stream info
                stream_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid*='stream'], [class*='stream'], [class*='channel']")
                
                if stream_elements:
                    print(f"Found {len(stream_elements)} potential stream elements")
                    return True
                else:
                    print("No obvious stream elements found")
                    
            except TimeoutException:
                print("Timeout waiting for page content")
        
        return not blocked
        
    except WebDriverException as e:
        print(f"WebDriver error: {e}")
        print("Make sure ChromeDriver is installed and in PATH")
        return False
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    
    finally:
        try:
            driver.quit()
        except:
            pass

def test_manual_browser_instructions():
    """Provide instructions for manual data extraction."""
    print("\nMANUAL BROWSER EXTRACTION METHOD")
    print("=" * 50)
    print("Since automated access is blocked, here's how to manually extract data:")
    print()
    print("1. Open your browser and go to https://kick.com")
    print("2. Open Developer Tools (F12)")
    print("3. Go to the Network tab")
    print("4. Reload the page")
    print("5. Look for XHR/API calls that contain stream data")
    print("6. Common endpoints to look for:")
    print("   - /api/v*/channels/live")
    print("   - /api/v*/streams")  
    print("   - GraphQL queries")
    print("7. Copy the working request as cURL and convert to Python")
    print()
    print("Alternative: Check page source for embedded JSON data")
    print("1. View page source (Ctrl+U)")
    print("2. Search for keywords like 'livestream', 'channels', 'viewers'")
    print("3. Look for JSON objects containing stream data")

def create_proxy_test_script():
    """Create a script to test different proxy configurations."""
    proxy_script = '''#!/usr/bin/env python3
"""
Test Kick.com access through different proxy servers.
Install required packages: pip install requests[socks] selenium
"""

import requests
import time
from itertools import cycle

# Free proxy lists (update these with current working proxies)
HTTP_PROXIES = [
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:3128",
    # Add more HTTP proxies
]

SOCKS_PROXIES = [
    "socks5://proxy1.example.com:1080",
    "socks5://proxy2.example.com:1080", 
    # Add more SOCKS proxies
]

def test_with_proxy(proxy_url):
    """Test Kick.com access through a specific proxy."""
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    
    session = requests.Session()
    session.proxies.update(proxies)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    })
    
    try:
        response = session.get("https://kick.com/api/v2/channels/live", timeout=10)
        return response.status_code, response.text[:200]
    except Exception as e:
        return None, str(e)

def main():
    print("Testing Kick.com access through proxies...")
    
    all_proxies = HTTP_PROXIES + SOCKS_PROXIES
    
    for proxy in all_proxies:
        print(f"\\nTesting proxy: {proxy}")
        status, response = test_with_proxy(proxy)
        
        if status == 200:
            print("✅ SUCCESS! Proxy works")
            print(f"Response preview: {response}")
            break
        elif status:
            print(f"❌ Got status {status}")
            print(f"Response: {response}")
        else:
            print(f"❌ Connection failed: {response}")
        
        time.sleep(1)  # Be respectful

if __name__ == "__main__":
    main()
'''
    
    with open("kick_proxy_test.py", "w") as f:
        f.write(proxy_script)
    
    print("Created kick_proxy_test.py - Update with working proxy servers")

def analyze_current_situation():
    """Analyze the current blocking situation and provide recommendations."""
    print("\nKICK.COM API ACCESS ANALYSIS")
    print("=" * 60)
    
    print("🔒 CURRENT STATUS: COMPLETELY BLOCKED")
    print("   - All API endpoints return 403")
    print("   - Even main website access is blocked")
    print("   - Cloudflare Bot Management is active")
    print("   - Reference ID '9e4db7e3' suggests IP-based blocking")
    
    print("\n🧭 ROOT CAUSES:")
    print("   1. Kick.com has implemented aggressive bot protection")
    print("   2. Your IP might be flagged for automated requests")
    print("   3. API may have been discontinued for public use")
    print("   4. Strong anti-scraping measures are in place")
    
    print("\n💡 POTENTIAL SOLUTIONS (in order of likelihood):")
    print("   1. Use a VPN/proxy to change your IP address")
    print("   2. Use Selenium WebDriver with browser automation")
    print("   3. Find official API documentation with authentication")
    print("   4. Use a residential proxy service")
    print("   5. Manual data extraction from browser network tools")
    
    print("\n⚠️  IMPORTANT CONSIDERATIONS:")
    print("   - Respect Kick.com's terms of service")
    print("   - Bot protection is intentional - don't abuse it")
    print("   - Consider reaching out to Kick.com for official API access")
    print("   - Rate limiting and responsible scraping are essential")

def main():
    """Main function to run all tests and provide recommendations."""
    print("KICK.COM 403 ERROR INVESTIGATION")
    print("=" * 60)
    
    # Test selenium approach
    selenium_works = test_selenium_approach()
    
    print("\n" + "=" * 60)
    
    # Analyze situation
    analyze_current_situation()
    
    print("\n" + "=" * 60)
    
    # Provide manual instructions
    test_manual_browser_instructions()
    
    print("\n" + "=" * 60)
    
    # Create proxy test script
    create_proxy_test_script()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    
    if selenium_works:
        print("✅ Selenium WebDriver approach worked!")
        print("   You can now build a scraper using browser automation")
    else:
        print("❌ All automated approaches failed")
        print("   Recommended actions:")
        print("   1. Try the proxy test script with different IPs")
        print("   2. Use manual browser extraction method")
        print("   3. Consider contacting Kick.com for API access")
        print("   4. Look for alternative data sources")

if __name__ == "__main__":
    main()
