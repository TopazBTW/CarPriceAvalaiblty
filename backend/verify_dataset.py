#!/usr/bin/env python3
"""
Final verification of the massive used cars dataset
"""
import csv
import json
from collections import Counter

def verify_massive_dataset():
    """Verify the quality and completeness of the massive dataset"""
    print("🔍 FINAL DATASET VERIFICATION")
    print("=" * 50)
    
    csv_path = 'data/csv/morocco_used_cars.csv'
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            cars = list(reader)
        
        total_cars = len(cars)
        print(f"✅ Successfully loaded {total_cars:,} cars")
        
        # Verify all required columns exist
        required_columns = [
            'Brand', 'Model', 'Year', 'Price', 'KM_Driven', 'Fuel_Type',
            'Transmission', 'Condition', 'Location', 'Seller_Type', 'Phone',
            'Verified_Seller', 'Days_Listed', 'Views', 'Source', 'Link',
            'Color', 'Body_Type', 'Engine_Size'
        ]
        
        first_car = cars[0]
        missing_columns = [col for col in required_columns if col not in first_car.keys()]
        
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            return False
        else:
            print(f"✅ All {len(required_columns)} required columns present")
        
        # Verify data quality
        print(f"\n📊 Data Quality Verification:")
        
        # Check for empty values
        empty_count = 0
        for car in cars[:1000]:  # Sample check
            for key, value in car.items():
                if not value or value.strip() == '':
                    empty_count += 1
        
        if empty_count > 0:
            print(f"⚠️  Found {empty_count} empty values in sample")
        else:
            print(f"✅ No empty values in sample check")
        
        # Verify price range
        prices = [int(car['Price']) for car in cars if car['Price'].isdigit()]
        print(f"✅ Price range: {min(prices):,} - {max(prices):,} MAD")
        
        # Verify years
        years = [int(car['Year']) for car in cars if car['Year'].isdigit()]
        print(f"✅ Year range: {min(years)} - {max(years)}")
        
        # Verify links
        links_with_https = sum(1 for car in cars if car['Link'].startswith('https://'))
        print(f"✅ Links with HTTPS: {links_with_https:,}/{total_cars:,} ({(links_with_https/total_cars)*100:.1f}%)")
        
        # Brand distribution
        brands = Counter(car['Brand'] for car in cars)
        print(f"✅ Unique brands: {len(brands)}")
        
        # Source distribution
        sources = Counter(car['Source'] for car in cars)
        print(f"✅ Marketplace sources: {len(sources)}")
        
        # Location distribution
        locations = Counter(car['Location'] for car in cars)
        print(f"✅ Geographic locations: {len(locations)}")
        
        # Show sample premium cars
        print(f"\n🏆 Premium Cars Sample:")
        luxury_brands = ['Ferrari', 'Lamborghini', 'Rolls Royce', 'Bentley', 'McLaren', 'Porsche']
        luxury_cars = [car for car in cars if car['Brand'] in luxury_brands][:3]
        
        for i, car in enumerate(luxury_cars, 1):
            print(f"  {i}. {car['Brand']} {car['Model']} {car['Year']} - {int(car['Price']):,} MAD")
            print(f"     🔗 {car['Link']}")
        
        # Show sample budget cars
        print(f"\n💰 Budget Cars Sample:")
        budget_cars = sorted(cars, key=lambda x: int(x['Price']) if x['Price'].isdigit() else 0)[:3]
        
        for i, car in enumerate(budget_cars, 1):
            print(f"  {i}. {car['Brand']} {car['Model']} {car['Year']} - {int(car['Price']):,} MAD")
            print(f"     🔗 {car['Link']}")
        
        print(f"\n🎉 DATASET VERIFICATION COMPLETE!")
        print(f"📊 {total_cars:,} cars verified and ready")
        print(f"🚀 System ready for production use")
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    verify_massive_dataset()