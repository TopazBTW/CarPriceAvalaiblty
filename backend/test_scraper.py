import asyncio
from comprehensive_scraper import get_comprehensive_morocco_prices

async def test_scraper():
    print("Testing comprehensive Morocco scraper...")
    
    try:
        results = await get_comprehensive_morocco_prices(
            brand="Toyota",
            model="Yaris", 
            year=2023,
            condition="Neuf"
        )
        
        print(f"\n=== RESULTS ===")
        print(f"Total listings: {results['data_points']}")
        print(f"Market price: {results['market_price']} MAD")
        print(f"Confidence: {results['confidence']}")
        print(f"Price range: {results['price_range']}")
        print(f"New cars: {results['breakdown']['new_count']}")
        print(f"Used cars: {results['breakdown']['used_count']}")
        print(f"Sites scraped: {len(results['sites_data'])}")
        
        if results['sample_listings']:
            print(f"\nSample listings:")
            for i, listing in enumerate(results['sample_listings'][:3]):
                print(f"{i+1}. {listing['title']} - {listing['price']} MAD ({listing['condition']})")
        
        print(f"\nSites breakdown:")
        for site, data in results['sites_data'].items():
            print(f"- {site}: {data['count']} listings")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scraper())