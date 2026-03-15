#!/usr/bin/env python3
"""
Simple test script to verify Kick.com API endpoints work correctly.
Run this script to test the API functionality before using the main kick.py script.
"""

import requests
import json
from typing import Dict, Any, List

def test_kick_api():
    """Test various Kick.com API endpoints."""
    print("Testing Kick.com API endpoints...")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    
    # Test different possible API endpoints
    endpoints_to_test = [
        "https://kick.com/api/v2/channels/live",
        "https://kick.com/api/v1/channels/live", 
        "https://kick.com/api/channels/live",
        "https://kick.com/stream/livestreams",
        "https://kick.com/api/v2/categories",
        "https://kick.com/api/v1/categories"
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\nTesting: {endpoint}")
        try:
            response = session.get(endpoint, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        print(f"Response Type: dict with keys: {list(data.keys())}")
                        if "data" in data:
                            print(f"Data contains {len(data['data'])} items")
                    elif isinstance(data, list):
                        print(f"Response Type: list with {len(data)} items")
                    else:
                        print(f"Response Type: {type(data)}")
                except json.JSONDecodeError:
                    print("Response is not valid JSON")
                    print(f"Content preview: {response.text[:200]}...")
            else:
                print(f"Error response: {response.text[:200]}")
                
        except requests.RequestException as e:
            print(f"Request failed: {e}")
    
    print("\n" + "=" * 50)
    print("API endpoint testing complete.")

def test_specific_channel():
    """Test accessing a specific channel."""
    print("\nTesting specific channel access...")
    
    # Test well-known Kick channels
    test_channels = ["trainwreckstv", "xqc", "amouranth"]  # Popular streamers who might be on Kick
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    
    for channel in test_channels:
        endpoint = f"https://kick.com/api/v2/channels/{channel}"
        print(f"Testing channel: {channel}")
        
        try:
            response = session.get(endpoint, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    username = data.get("username", data.get("slug", "Unknown"))
                    is_live = data.get("livestream") is not None
                    print(f"  Username: {username}")
                    print(f"  Is Live: {is_live}")
            
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    try:
        test_kick_api()
        test_specific_channel()
        
        print("\n" + "=" * 50)
        print("Test complete! Check the results above to see which endpoints work.")
        print("If most endpoints return 404 or other errors, the API structure may have changed.")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error during testing: {e}")
