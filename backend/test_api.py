#!/usr/bin/env python3
"""
Test script for the Used Cars API
"""
import requests
import json
import time

API_BASE_URL = "http://localhost:8001"

def test_scrapers():
    """Test the scrapers endpoint"""
    try:
        print("🔄 Testing scrapers endpoint...")
        response = requests.get(f"{API_BASE_URL}/test-scrapers")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error testing scrapers: {e}")
        return False

def test_search_cars():
    """Test the search cars endpoint"""
    try:
        print("\n🔍 Testing car search endpoint...")
        search_data = {
            "brand": "Toyota",
            "model": "Corolla",
            "year_min": 2015,
            "year_max": 2023,
            "price_min": 50000,
            "price_max": 200000
        }
        
        response = requests.post(
            f"{API_BASE_URL}/search-cars", 
            json=search_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code == 202:
            task_id = result.get("task_id")
            print(f"✅ Search started with task ID: {task_id}")
            
            # Check status a few times
            for i in range(3):
                time.sleep(2)
                status_response = requests.get(f"{API_BASE_URL}/scraping-status/{task_id}")
                status_data = status_response.json()
                print(f"Status check {i+1}: {status_data}")
                
                if status_data.get("status") == "completed":
                    # Get results
                    results_response = requests.get(f"{API_BASE_URL}/scraped-results/{task_id}")
                    results = results_response.json()
                    print(f"🎉 Results: {results}")
                    break
            
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error testing search: {e}")
        return False

def main():
    """Run all tests"""
    print("🚗 Testing Used Cars API")
    print("=" * 50)
    
    # Test 1: Scrapers endpoint
    test1_passed = test_scrapers()
    
    # Test 2: Search cars endpoint
    test2_passed = test_search_cars()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Scrapers test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Search test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Your API is ready for frontend integration.")
    else:
        print("\n⚠️ Some tests failed. Check the server logs for details.")

if __name__ == "__main__":
    main()