#!/usr/bin/env python3
"""
Test script to verify the cleaned backend endpoints work correctly
"""

import requests
import json
import sys

def test_endpoint(url, description):
    """Test an endpoint and show results"""
    print(f"\n🧪 Testing: {description}")
    print(f"📍 URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Status: {response.status_code}")
            
            if isinstance(data, dict):
                if 'brands' in data:
                    brands = data['brands']
                    print(f"📊 Found {len(brands)} brands")
                    print(f"🏷️  Sample brands: {brands[:5]}")
                    # Check for "Occasion" entries
                    occasion_brands = [b for b in brands if 'occasion' in b.lower()]
                    if occasion_brands:
                        print(f"⚠️  WARNING: Found Occasion entries: {occasion_brands}")
                    else:
                        print(f"✅ No Occasion entries found!")
                else:
                    print(f"📊 Response keys: {list(data.keys())}")
            else:
                print(f"📊 Response type: {type(data)}")
                
        else:
            print(f"❌ Failed! Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    base_url = "http://127.0.0.1:8001"
    
    # Test if server is running
    print("🚀 Testing Backend Endpoints")
    
    endpoints_to_test = [
        (f"{base_url}/health", "Health Check"),
        (f"{base_url}/brands", "All Brands"),
        (f"{base_url}/brands?condition=neuf", "Neuf Brands Only"),
        (f"{base_url}/brands?condition=occasion", "Occasion Brands"),
        (f"{base_url}/scrape/wandaloo/brands_with_prices", "Original Brands with Prices"),
    ]
    
    for url, desc in endpoints_to_test:
        test_endpoint(url, desc)
    
    print(f"\n🏁 Testing completed!")

if __name__ == "__main__":
    main()