#!/usr/bin/env python3
"""
Create separate CSV files for new cars and used cars with appropriate fields
"""

import json
import csv
import os
from pathlib import Path

def load_cars_data():
    """Load the cleaned cars data from JSON"""
    json_path = Path(__file__).parent.parent / "data" / "json" / "morocco_cars_clean.json"
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data

def create_new_cars_csv(cars_data):
    """Create CSV for new cars with minimal fields"""
    new_cars = []
    
    # Extract cars from the models section
    models = cars_data.get('models', {})
    
    for brand_name, brand_models in models.items():
        for model_name, model_cars in brand_models.items():
            for car in model_cars:
                # Skip entries without valid prices or with placeholder models
                if not car.get('price') or model_name in ['Kifalauto', 'Accueil']:
                    continue
                
                # All cars with valid prices are considered new cars for now
                # (since most of the data appears to be new car listings)
                
                new_cars.append({
                    'Brand': car.get('brand', brand_name),
                    'Model': car.get('model', model_name),
                    'Fuel': car.get('fuel_type', ''),
                    'Transmission': car.get('transmission', ''),
                    'Selling_Price': car.get('price')
                })
    
    return new_cars

def create_used_cars_csv(cars_data):
    """Create CSV for used cars with all fields"""
    used_cars = []
    
    # For now, create a sample used cars CSV with some example data
    # Since most of our current data appears to be new cars
    # This can be expanded when we have more used car data
    
    return used_cars  # Return empty for now, focus on new cars

def save_csv(data, filename, fieldnames):
    """Save data to CSV file"""
    csv_path = Path(__file__).parent.parent / "data" / "csv" / filename
    
    # Ensure the csv directory exists
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✅ Created {filename} with {len(data)} entries")
    return csv_path

def main():
    """Main function to create both CSV files"""
    print("🔄 Loading cars data...")
    cars_data = load_cars_data()
    
    # Create new cars CSV (simplified fields)
    print("\n🔄 Processing new cars...")
    new_cars = create_new_cars_csv(cars_data)
    new_cars_fieldnames = ['Brand', 'Model', 'Fuel', 'Transmission', 'Selling_Price']
    new_cars_path = save_csv(new_cars, 'morocco_new_cars.csv', new_cars_fieldnames)
    
    # Create used cars CSV (full fields)  
    print("\n🔄 Processing used cars...")
    used_cars = create_used_cars_csv(cars_data)
    used_cars_fieldnames = ['Brand', 'Model', 'Year', 'KM_Driven', 'Fuel', 'Seller_Type', 'Transmission', 'Owner', 'Selling_Price']
    used_cars_path = save_csv(used_cars, 'morocco_used_cars.csv', used_cars_fieldnames)
    
    # Show sample data
    if new_cars:
        print(f"\n📋 Sample new cars:")
        for car in new_cars[:5]:
            print(f"  • {car['Brand']} {car['Model']} ({car['Fuel']}) - {car['Selling_Price']:,} MAD")
    
    if used_cars:
        print(f"\n📋 Sample used cars:")
        for car in used_cars[:5]:
            print(f"  • {car['Brand']} {car['Model']} ({car['Year']}, {car['KM_Driven']}km) - {car['Selling_Price']:,} MAD")
    
    print(f"\n✅ CSV files created successfully!")
    print(f"   📁 New cars: {new_cars_path}")
    print(f"   📁 Used cars: {used_cars_path}")

if __name__ == "__main__":
    main()