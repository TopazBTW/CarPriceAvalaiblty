#!/usr/bin/env python3
"""
Generate comprehensive Morocco used cars dataset
Creates realistic used car data with proper depreciation and market conditions
"""
import json
import csv
import random
from datetime import datetime

def load_new_cars_data():
    """Load the clean new cars data as reference"""
    try:
        with open('data/json/morocco_cars_clean.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ New cars data not found. Using fallback data.")
        return []

def calculate_used_price(original_price, year, km_driven, condition):
    """Calculate realistic used car price based on depreciation factors"""
    current_year = 2025
    age = current_year - year
    
    # Base depreciation: 15-20% per year for first 5 years, then 8-12% per year
    if age <= 5:
        yearly_depreciation = random.uniform(0.15, 0.20)
    else:
        yearly_depreciation = random.uniform(0.08, 0.12)
    
    # Calculate age depreciation
    age_depreciation = 1 - (yearly_depreciation * age)
    age_depreciation = max(age_depreciation, 0.15)  # Minimum 15% of original value
    
    # KM depreciation: 0.5-1.5 MAD per km depending on car type
    if original_price > 500000:  # Luxury cars
        km_cost = random.uniform(1.0, 1.5)
    elif original_price > 250000:  # Mid-range
        km_cost = random.uniform(0.7, 1.2)
    else:  # Budget cars
        km_cost = random.uniform(0.3, 0.8)
    
    km_depreciation = km_driven * km_cost
    
    # Condition multiplier
    condition_multipliers = {
        'Excellent': random.uniform(0.95, 1.0),
        'Very Good': random.uniform(0.85, 0.95),
        'Good': random.uniform(0.75, 0.85),
        'Fair': random.uniform(0.65, 0.75),
        'Poor': random.uniform(0.45, 0.65)
    }
    
    condition_multiplier = condition_multipliers.get(condition, 0.8)
    
    # Calculate final price
    depreciated_price = original_price * age_depreciation * condition_multiplier
    final_price = max(depreciated_price - km_depreciation, original_price * 0.1)
    
    return int(final_price)

def generate_realistic_km(year, brand):
    """Generate realistic KM driven based on car age and type"""
    current_year = 2025
    age = current_year - year
    
    # Average KM per year by brand category
    luxury_brands = ['Mercedes', 'BMW', 'Audi', 'Porsche', 'Jaguar', 'Lexus']
    city_brands = ['Smart', 'Mini', 'Fiat']
    
    if brand in luxury_brands:
        avg_km_per_year = random.uniform(8000, 15000)
    elif brand in city_brands:
        avg_km_per_year = random.uniform(6000, 12000)
    else:
        avg_km_per_year = random.uniform(10000, 20000)
    
    # Add some randomness
    variation = random.uniform(0.7, 1.4)
    total_km = int(age * avg_km_per_year * variation)
    
    # Ensure reasonable bounds
    min_km = max(1000, age * 2000)
    max_km = age * 30000
    
    return max(min_km, min(total_km, max_km))

def generate_location():
    """Generate realistic Morocco locations with proper distribution"""
    locations = [
        ('Casablanca', 0.25),
        ('Rabat', 0.15),
        ('Marrakech', 0.12),
        ('Fès', 0.08),
        ('Tangier', 0.08),
        ('Agadir', 0.06),
        ('Meknès', 0.05),
        ('Oujda', 0.04),
        ('Kenitra', 0.04),
        ('Tetouan', 0.03),
        ('Safi', 0.03),
        ('Mohammedia', 0.03),
        ('Khouribga', 0.02),
        ('Beni Mellal', 0.02)
    ]
    
    # Weighted random selection
    rand = random.random()
    cumulative = 0
    for location, weight in locations:
        cumulative += weight
        if rand <= cumulative:
            return location
    return locations[0][0]

def generate_seller_info():
    """Generate seller information"""
    seller_types = ['Dealer', 'Private', 'Showroom']
    weights = [0.4, 0.45, 0.15]
    
    seller_type = random.choices(seller_types, weights=weights)[0]
    
    if seller_type == 'Dealer':
        return {
            'seller_type': seller_type,
            'phone': f"+212{random.randint(600000000, 699999999)}",
            'verified': random.choice([True, False])
        }
    elif seller_type == 'Private':
        return {
            'seller_type': seller_type,
            'phone': f"+212{random.randint(600000000, 699999999)}",
            'verified': random.choice([True, False])
        }
    else:  # Showroom
        return {
            'seller_type': seller_type,
            'phone': f"+212{random.randint(520000000, 529999999)}",
            'verified': True
        }

def create_used_cars_dataset():
    """Create comprehensive used cars dataset"""
    print("🚗 Creating Morocco Used Cars Dataset")
    print("=" * 50)
    
    # Load new cars data for reference
    new_cars = load_new_cars_data()
    used_cars = []
    
    conditions = ['Excellent', 'Very Good', 'Good', 'Fair', 'Poor']
    condition_weights = [0.15, 0.25, 0.35, 0.20, 0.05]
    
    fuel_types = ['Gasoline', 'Diesel', 'Hybrid', 'Electric']
    fuel_weights = [0.65, 0.25, 0.08, 0.02]
    
    transmissions = ['Manual', 'Automatic', 'CVT']
    transmission_weights = [0.70, 0.25, 0.05]
    
    # Generate used cars from new cars data
    cars_generated = 0
    target_cars = 2500  # Generate 2500 used cars
    
    for _ in range(target_cars):
        if new_cars:
            # Use existing car as base
            base_car = random.choice(new_cars)
            brand = base_car['Brand']
            model = base_car['Model']
            original_price = base_car['Price']
        else:
            # Fallback if no data
            brand = random.choice(['Toyota', 'Dacia', 'Hyundai', 'Ford'])
            model = random.choice(['Corolla', 'Logan', 'i10', 'Fiesta'])
            original_price = random.randint(150000, 400000)
        
        # Generate car details
        year = random.randint(2010, 2024)  # Used cars from 2010-2024
        km_driven = generate_realistic_km(year, brand)
        condition = random.choices(conditions, weights=condition_weights)[0]
        fuel_type = random.choices(fuel_types, weights=fuel_weights)[0]
        transmission = random.choices(transmissions, weights=transmission_weights)[0]
        location = generate_location()
        seller_info = generate_seller_info()
        
        # Calculate used price
        used_price = calculate_used_price(original_price, year, km_driven, condition)
        
        # Create used car entry
        used_car = {
            'Brand': brand,
            'Model': model,
            'Year': year,
            'Price': used_price,
            'KM_Driven': km_driven,
            'Fuel_Type': fuel_type,
            'Transmission': transmission,
            'Condition': condition,
            'Location': location,
            'Seller_Type': seller_info['seller_type'],
            'Phone': seller_info['phone'],
            'Verified_Seller': seller_info['verified'],
            'Days_Listed': random.randint(1, 180),
            'Views': random.randint(10, 500),
            'Source': random.choice(['Avito', 'Facebook Marketplace', 'Moteur.ma', 'Sarouty'])
        }
        
        used_cars.append(used_car)
        cars_generated += 1
        
        if cars_generated % 250 == 0:
            print(f"✅ Generated {cars_generated} used cars...")
    
    return used_cars

def save_to_csv(used_cars):
    """Save used cars data to CSV"""
    csv_path = 'data/csv/morocco_used_cars.csv'
    
    # Define CSV columns
    columns = [
        'Brand', 'Model', 'Year', 'Price', 'KM_Driven', 'Fuel_Type',
        'Transmission', 'Condition', 'Location', 'Seller_Type',
        'Phone', 'Verified_Seller', 'Days_Listed', 'Views', 'Source'
    ]
    
    print(f"\n💾 Saving to {csv_path}...")
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        writer.writerows(used_cars)
    
    print(f"✅ Successfully saved {len(used_cars)} used cars to CSV")
    
    # Show sample data
    print(f"\n📊 Sample data:")
    print("-" * 80)
    for i, car in enumerate(used_cars[:5]):
        print(f"{i+1}. {car['Brand']} {car['Model']} {car['Year']} - {car['Price']:,} MAD")
        print(f"   📍 {car['Location']} | 🛣️ {car['KM_Driven']:,} KM | 🏷️ {car['Condition']}")
        print(f"   📱 {car['Phone']} | 🏪 {car['Seller_Type']} | 🌐 {car['Source']}")
        print()

def generate_statistics(used_cars):
    """Generate and display dataset statistics"""
    print("\n📈 Dataset Statistics:")
    print("=" * 50)
    
    total_cars = len(used_cars)
    print(f"Total used cars: {total_cars:,}")
    
    # Price statistics
    prices = [car['Price'] for car in used_cars]
    print(f"Price range: {min(prices):,} - {max(prices):,} MAD")
    print(f"Average price: {sum(prices) // len(prices):,} MAD")
    
    # Brand distribution (top 10)
    brands = {}
    for car in used_cars:
        brand = car['Brand']
        brands[brand] = brands.get(brand, 0) + 1
    
    print(f"\nTop 10 brands:")
    for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True)[:10]:
        percentage = (count / total_cars) * 100
        print(f"  {brand}: {count} cars ({percentage:.1f}%)")
    
    # Location distribution
    locations = {}
    for car in used_cars:
        location = car['Location']
        locations[location] = locations.get(location, 0) + 1
    
    print(f"\nTop 5 locations:")
    for location, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]:
        percentage = (count / total_cars) * 100
        print(f"  {location}: {count} cars ({percentage:.1f}%)")

def main():
    """Main function to generate used cars dataset"""
    try:
        # Generate the dataset
        used_cars = create_used_cars_dataset()
        
        # Save to CSV
        save_to_csv(used_cars)
        
        # Generate statistics
        generate_statistics(used_cars)
        
        print("\n🎉 Used Cars Dataset Generation Complete!")
        print("📁 File saved: data/csv/morocco_used_cars.csv")
        print("🔗 Ready for ML training and API integration")
        
    except Exception as e:
        print(f"❌ Error generating dataset: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()