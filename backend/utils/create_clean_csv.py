#!/usr/bin/env python3
"""
Generate a clean CSV from the improved morocco_cars_clean.json
"""
import json
import csv
from pathlib import Path

def create_clean_csv():
    json_path = Path('data/json/morocco_cars_clean.json')
    csv_path = Path('data/csv/morocco_cars_clean.csv')
    
    if not json_path.exists():
        print("❌ JSON file not found")
        return
    
    # Load JSON data
    data = json.loads(json_path.read_text(encoding='utf-8'))
    cars = data.get('cars', [])
    
    # Ensure CSV directory exists
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Define CSV fields for ML training
    fieldnames = [
        'Brand', 'Model', 'Year', 'KM_Driven', 'Fuel', 
        'Seller_Type', 'Transmission', 'Owner', 'Selling_Price'
    ]
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        valid_entries = 0
        for car in cars:
            # Map JSON fields to CSV fields for ML model
            csv_row = {
                'Brand': car.get('brand', ''),
                'Model': car.get('model', ''),
                'Year': car.get('year'),
                'KM_Driven': car.get('mileage', 0),  # Use scraped mileage
                'Fuel': car.get('fuel_type', 'Petrol'),  # Default to Petrol
                'Seller_Type': 'Dealer',  # All from Kifal are dealers
                'Transmission': car.get('transmission', 'Manual'),  # Default to Manual
                'Owner': 'First Owner',  # New cars are first owner
                'Selling_Price': car.get('price')
            }
            
            # Only include entries with valid data
            if (csv_row['Brand'] and csv_row['Model'] and 
                csv_row['Model'] not in ['Unknown', ''] and
                csv_row['Selling_Price'] and csv_row['Selling_Price'] > 0):
                writer.writerow(csv_row)
                valid_entries += 1
    
    print(f"✅ Clean CSV created: {csv_path}")
    print(f"📊 Valid entries: {valid_entries}/{len(cars)}")
    
    # Show sample entries
    print("\n📋 Sample entries:")
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            if i < 5:  # Show first 5 entries
                print(f"   {i+1}. {row['Brand']} {row['Model']} ({row['Year']}) - {row['Selling_Price']} MAD")

if __name__ == "__main__":
    create_clean_csv()