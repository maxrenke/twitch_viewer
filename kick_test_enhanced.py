#!/usr/bin/env python3
"""
Enhanced test script to investigate and bypass Kick.com API 403 errors.
This script tries multiple approaches to access the Kick.com API.
"""

import requests
import json
import time
import random
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

# Different User-Agent strings to test
USER_AGENTS = [
    # Standard browser user agents
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    # Mobile user agents
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
]

# Different header configurations to test
HEADER_CONFIGS = [
    {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Ch-Ua": '"Not A(Brand";v="99", "Google Chrome";v="122", "Chromium";v="122"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"'
    },
    {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    },
    {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
    },
    # Minimal headers
    {
        "Accept": "application/json",
    },
    # No additional headers (just User-Agent)
    {}
]

# API endpoints to test
ENDPOINTS_TO_TEST = [
    # Original API endpoints
    "https://kick.com/api/v2/channels/live",
    "https://kick.com/api/v1/channels/live", 
    "https://kick.com/api/channels/live",
    "https://kick.com/api/v2/categories",
    "https://kick.com/api/v1/categories",
    
    # Alternative endpoints to try
    "https://kick.com/api/channels",
    "https://kick.com/api/v2/streams",
    "https://kick.com/api/v1/streams",
    "https://kick.com/api/livestreams",
    "https://kick.com/api/channels/featured",
    "https://kick.com/api/v2/channels/featured",
    
    # GraphQL endpoint (common in modern apps)
    "https://kick.com/graphql",
    
    # Public endpoints that might not be protected
    "https://kick.com/api/health",
    "https://kick.com/api/status",
    "https://kick.com/api/ping",
]

def test_endpoint_with_config(endpoint: str, user_agent: str, headers: Dict[str, str], delay: float = 0) -> Dict[str, Any]:
    """Test a single endpoint with specific configuration."""
    if delay > 0:
        time.sleep(delay)
    
    session = requests.Session()
    
    # Set user agent
    session.headers.update({"User-Agent": user_agent})
    
    # Set additional headers
    session.headers.update(headers)
    
    try:
        response = session.get(endpoint, timeout=15)
        
        result = {
            "endpoint": endpoint,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "success": response.status_code == 200
        }
        
        if response.status_code == 200:
            try:
                result["json_data"] = response.json()
                result["data_type"] = type(response.json()).__name__
                if isinstance(response.json(), dict):
                    result["json_keys"] = list(response.json().keys())
                elif isinstance(response.json(), list):
                    result["data_length"] = len(response.json())
            except json.JSONDecodeError:
                result["text_preview"] = response.text[:200]
        else:
            result["error_text"] = response.text[:500]
        
        return result
        
    except requests.RequestException as e:
        return {
            "endpoint": endpoint,
            "status_code": None,
            "error": str(e),
            "success": False
        }
    finally:
        session.close()

def test_with_browser_simulation():
    """Test with browser-like behavior simulation."""
    print("Testing with browser simulation (cookies, referrer, etc.)...")
    print("=" * 70)
    
    # Create a session that maintains cookies
    session = requests.Session()
    
    # First, visit the main page to get cookies
    try:
        print("Step 1: Visiting main page to establish session...")
        main_response = session.get("https://kick.com", headers={
            "User-Agent": USER_AGENTS[0],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }, timeout=15)
        
        print(f"Main page status: {main_response.status_code}")
        print(f"Cookies received: {len(session.cookies)}")
        
        if session.cookies:
            print("Cookie names:", [cookie.name for cookie in session.cookies])
        
        # Wait a bit to simulate human behavior
        time.sleep(2)
        
        # Now try API calls with established session
        print("\nStep 2: Testing API endpoints with established session...")
        
        api_headers = {
            "User-Agent": USER_AGENTS[0],
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://kick.com/",
            "Origin": "https://kick.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        
        test_endpoints = [
            "https://kick.com/api/v2/channels/live",
            "https://kick.com/api/v1/channels/live",
            "https://kick.com/api/v2/categories"
        ]
        
        for endpoint in test_endpoints:
            try:
                response = session.get(endpoint, headers=api_headers, timeout=15)
                print(f"\n{endpoint}")
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"Success! Data type: {type(data)}")
                        if isinstance(data, dict):
                            print(f"Keys: {list(data.keys())}")
                        elif isinstance(data, list):
                            print(f"List length: {len(data)}")
                    except json.JSONDecodeError:
                        print("Response is not JSON")
                else:
                    error_text = response.text[:200]
                    print(f"Error: {error_text}")
                    
            except Exception as e:
                print(f"Request failed: {e}")
        
    except Exception as e:
        print(f"Browser simulation failed: {e}")
    finally:
        session.close()

def test_rate_limiting():
    """Test if rate limiting is causing issues."""
    print("\nTesting rate limiting behavior...")
    print("=" * 50)
    
    endpoint = "https://kick.com/api/v2/channels/live"
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENTS[0]})
    
    delays = [0, 1, 3, 5, 10]  # Different delays between requests
    
    for delay in delays:
        print(f"\nTesting with {delay}s delay between requests:")
        
        for i in range(3):  # Make 3 requests
            if i > 0:
                time.sleep(delay)
            
            try:
                response = session.get(endpoint, timeout=10)
                print(f"  Request {i+1}: {response.status_code}")
                if response.status_code != 200:
                    print(f"    Error: {response.text[:100]}")
            except Exception as e:
                print(f"  Request {i+1}: Failed - {e}")
    
    session.close()

def test_alternative_approaches():
    """Test alternative ways to access Kick data."""
    print("\nTesting alternative approaches...")
    print("=" * 50)
    
    # Test direct channel pages (might have JSON data)
    channels_to_test = ["trainwreckstv", "xqc", "amouranth"]
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENTS[0],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    })
    
    for channel in channels_to_test:
        print(f"\nTesting channel page: {channel}")
        
        try:
            # Test channel page
            url = f"https://kick.com/{channel}"
            response = session.get(url, timeout=15)
            print(f"  Page status: {response.status_code}")
            
            if response.status_code == 200:
                # Look for JSON data in the page
                content = response.text
                if '"livestream"' in content or '"user"' in content:
                    print(f"  ✓ Channel page contains stream data")
                else:
                    print(f"  ✗ No obvious stream data found")
            
            # Also test the API endpoint for this specific channel
            api_url = f"https://kick.com/api/v2/channels/{channel}"
            api_response = session.get(api_url, timeout=10)
            print(f"  API status: {api_response.status_code}")
            
            if api_response.status_code != 200:
                print(f"    API Error: {api_response.text[:100]}")
            
        except Exception as e:
            print(f"  Error testing {channel}: {e}")
        
        time.sleep(1)  # Be respectful
    
    session.close()

def run_comprehensive_test():
    """Run comprehensive tests with different configurations."""
    print("COMPREHENSIVE KICK.COM API ACCESS TEST")
    print("=" * 70)
    print("Testing multiple user agents, headers, and endpoints...")
    
    successful_configs = []
    
    # Test a subset of combinations (to avoid too many requests)
    test_combinations = []
    
    # Create test combinations
    for i, user_agent in enumerate(USER_AGENTS[:3]):  # Test first 3 user agents
        for j, headers in enumerate(HEADER_CONFIGS[:2]):  # Test first 2 header configs
            for endpoint in ENDPOINTS_TO_TEST[:3]:  # Test first 3 endpoints
                test_combinations.append((endpoint, user_agent, headers, f"UA{i+1}_H{j+1}"))
    
    print(f"\nRunning {len(test_combinations)} test combinations...\n")
    
    for i, (endpoint, user_agent, headers, config_name) in enumerate(test_combinations):
        print(f"Test {i+1}/{len(test_combinations)}: {config_name} -> {endpoint.split('/')[-1]}")
        
        result = test_endpoint_with_config(endpoint, user_agent, headers, delay=0.5)
        
        if result["success"]:
            print(f"  ✓ SUCCESS!")
            successful_configs.append((config_name, endpoint, result))
        else:
            status = result.get("status_code", "Error")
            print(f"  ✗ Failed: {status}")
        
        # Small delay between tests
        time.sleep(0.5)
    
    # Report results
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    
    if successful_configs:
        print(f"✓ Found {len(successful_configs)} working configurations!")
        for config_name, endpoint, result in successful_configs:
            print(f"  {config_name}: {endpoint}")
            if "json_data" in result:
                print(f"    Data type: {result['data_type']}")
                if "json_keys" in result:
                    print(f"    Keys: {result['json_keys']}")
                elif "data_length" in result:
                    print(f"    Items: {result['data_length']}")
    else:
        print("✗ No working configurations found.")
        print("\nThis suggests that:")
        print("  1. Kick.com has implemented strong bot protection")
        print("  2. API access may require authentication")
        print("  3. The API structure may have changed significantly")
        print("  4. IP-based blocking may be in effect")

def main():
    """Main test function."""
    print("Starting enhanced Kick.com API investigation...\n")
    
    # Run different test approaches
    test_with_browser_simulation()
    print("\n" + "="*70 + "\n")
    
    test_rate_limiting()
    print("\n" + "="*70 + "\n")
    
    test_alternative_approaches()
    print("\n" + "="*70 + "\n")
    
    run_comprehensive_test()
    
    print("\n" + "="*70)
    print("RECOMMENDATIONS:")
    print("="*70)
    print("1. Check if any configurations worked above")
    print("2. If none worked, consider web scraping the channel pages")
    print("3. Look into using a browser automation tool (Selenium)")
    print("4. Check if Kick.com has published official API documentation")
    print("5. Consider using a proxy or VPN to test IP-based blocking")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error during testing: {e}")
