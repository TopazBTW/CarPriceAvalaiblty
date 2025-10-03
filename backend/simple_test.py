#!/usr/bin/env python3
"""
Simple API test using urllib instead of requests
"""
import urllib.request
import urllib.parse
import json

def test_api():
    """Simple test of the API"""
    try:
        print("🔄 Testing used cars API...")
        
        # Test the test-scrapers endpoint
        url = "http://localhost:8001/test-scrapers"
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            result = json.loads(data)
            print(f"✅ API Response: {result}")
            return True
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    test_api()