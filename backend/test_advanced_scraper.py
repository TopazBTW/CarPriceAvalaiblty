"""
Test script for the advanced Morocco car scraper
Tests both new and used car sections
"""

import asyncio
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_morocco_scraper import get_advanced_morocco_prices
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_new_cars():
    """Test scraping for new cars (Voitures Neuves)"""
    print("🚗 Testing NEW CARS (Voitures Neuves) scraping...")
    print("=" * 60)
    
    test_cases = [
        {"brand": "Toyota", "model": "Yaris", "year": 2024},
        {"brand": "Peugeot", "model": "208", "year": 2024},
        {"brand": "Renault", "model": "Clio", "year": 2024}
    ]
    
    for case in test_cases:
        try:
            print(f"\nTesting: {case['brand']} {case['model']} {case['year']} (NEUF)")
            result = await get_advanced_morocco_prices(
                case["brand"], case["model"], case["year"], "Neuf"
            )
            
            print(f"✅ Found {result['data_points']} listings")
            if result['market_price']:
                print(f"💰 Average price: {result['market_price']:,} MAD")
                print(f"📊 Price range: {result.get('price_range', [0, 0])[0]:,} - {result.get('price_range', [0, 0])[1]:,} MAD")
            print(f"🎯 Confidence: {result['confidence']}")
            print(f"🌐 Sites scraped: {list(result['sites_data'].keys())}")
            
            # Show sample listings
            if result['sample_listings']:
                print("📋 Sample listings:")
                for i, listing in enumerate(result['sample_listings'][:3]):
                    print(f"   {i+1}. {listing['title']} - {listing['price']:,} MAD ({listing['site']})")
            
        except Exception as e:
            print(f"❌ Error testing {case['brand']} {case['model']}: {str(e)}")

async def test_used_cars():
    """Test scraping for used cars (Voitures d'Occasion)"""
    print("\n🚙 Testing USED CARS (Voitures d'Occasion) scraping...")
    print("=" * 60)
    
    test_cases = [
        {"brand": "Toyota", "model": "Yaris", "year": 2020},
        {"brand": "Peugeot", "model": "208", "year": 2019},
        {"brand": "Renault", "model": "Clio", "year": 2021}
    ]
    
    for case in test_cases:
        try:
            print(f"\nTesting: {case['brand']} {case['model']} {case['year']} (OCCASION)")
            result = await get_advanced_morocco_prices(
                case["brand"], case["model"], case["year"], "Occasion"
            )
            
            print(f"✅ Found {result['data_points']} listings")
            if result['market_price']:
                print(f"💰 Average price: {result['market_price']:,} MAD")
                print(f"📊 Price range: {result.get('price_range', [0, 0])[0]:,} - {result.get('price_range', [0, 0])[1]:,} MAD")
            print(f"🎯 Confidence: {result['confidence']}")
            print(f"🌐 Sites scraped: {list(result['sites_data'].keys())}")
            
            # Show sample listings  
            if result['sample_listings']:
                print("📋 Sample listings:")
                for i, listing in enumerate(result['sample_listings'][:3]):
                    print(f"   {i+1}. {listing['title']} - {listing['price']:,} MAD ({listing['site']})")
            
        except Exception as e:
            print(f"❌ Error testing {case['brand']} {case['model']}: {str(e)}")

async def test_comparison():
    """Compare new vs used pricing for the same model"""
    print("\n⚖️ Testing NEW vs USED comparison...")
    print("=" * 60)
    
    brand, model, year = "Toyota", "Yaris", 2022
    
    try:
        print(f"Comparing {brand} {model} {year}: NEW vs USED")
        
        # Test new
        new_result = await get_advanced_morocco_prices(brand, model, year, "Neuf")
        
        # Test used  
        used_result = await get_advanced_morocco_prices(brand, model, year, "Occasion")
        
        print(f"\n🆕 NEW Cars:")
        print(f"   Listings: {new_result['data_points']}")
        print(f"   Avg Price: {new_result['market_price']:,} MAD" if new_result['market_price'] else "   Avg Price: No data")
        print(f"   Confidence: {new_result['confidence']}")
        
        print(f"\n🔄 USED Cars:")
        print(f"   Listings: {used_result['data_points']}")
        print(f"   Avg Price: {used_result['market_price']:,} MAD" if used_result['market_price'] else "   Avg Price: No data")
        print(f"   Confidence: {used_result['confidence']}")
        
        if new_result['market_price'] and used_result['market_price']:
            diff = new_result['market_price'] - used_result['market_price']
            percentage = (diff / used_result['market_price']) * 100
            print(f"\n📈 Price Difference: {diff:,} MAD ({percentage:.1f}% more for new)")
            
    except Exception as e:
        print(f"❌ Error in comparison test: {str(e)}")

async def main():
    """Run all tests"""
    print("🇲🇦 ADVANCED MOROCCO CAR SCRAPER TESTS")
    print("Testing dedicated sections for 'Voitures Neuves' and 'Voitures d'Occasion'")
    print("=" * 80)
    
    try:
        await test_new_cars()
        await test_used_cars() 
        await test_comparison()
        
        print("\n✅ All tests completed!")
        print("The advanced scraper targets specific sections like the AutoValue tabs shown.")
        
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())