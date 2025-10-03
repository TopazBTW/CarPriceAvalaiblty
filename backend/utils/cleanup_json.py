#!/usr/bin/env python3
"""
Clean up the JSON data by removing placeholder entries and invalid data
"""

import json
import os
from pathlib import Path

def clean_json_data():
    """Clean the JSON data by removing placeholders and invalid entries"""
    
    # Load the current JSON
    json_path = Path(__file__).parent.parent / "data" / "json" / "morocco_cars_clean.json"
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("🔄 Cleaning JSON data...")
    
    original_models = data.get('models', {})
    cleaned_models = {}
    cleaned_brands = {}
    
    removed_entries = 0
    kept_entries = 0
    
    # Clean the models section
    for brand_name, brand_models in original_models.items():
        cleaned_brand_models = {}
        
        for model_name, model_cars in brand_models.items():
            # Skip placeholder models entirely
            if model_name in ['Kifalauto', 'Accueil']:
                removed_entries += len(model_cars)
                print(f"❌ Removed placeholder model: {brand_name} - {model_name} ({len(model_cars)} entries)")
                continue
            
            # Filter valid cars within the model
            valid_cars = []
            for car in model_cars:
                # Keep only cars with valid prices
                if car.get('price') and 50000 <= car.get('price') <= 2000000:
                    valid_cars.append(car)
                    kept_entries += 1
                else:
                    removed_entries += 1
            
            # Only keep the model if it has valid cars
            if valid_cars:
                cleaned_brand_models[model_name] = valid_cars
        
        # Only keep the brand if it has valid models
        if cleaned_brand_models:
            cleaned_models[brand_name] = cleaned_brand_models
            
            # Update brands section to match
            if brand_name in data.get('brands', {}):
                cleaned_brands[brand_name] = data['brands'][brand_name]
    
    # Update the data structure
    cleaned_data = {
        'brands': cleaned_brands,
        'models': cleaned_models,
        'metadata': {
            'total_brands': len(cleaned_brands),
            'total_models': sum(len(models) for models in cleaned_models.values()),
            'total_cars': kept_entries,
            'last_updated': '2025-09-30 01:17:03',
            'source': 'kifal.ma',
            'cleaned': True
        }
    }
    
    # Save the cleaned JSON
    backup_path = json_path.with_suffix('.backup.json')
    
    # Create backup of original
    print(f"📋 Creating backup: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Save cleaned data
    print(f"💾 Saving cleaned JSON: {json_path}")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
    
    # Report results
    print(f"\n✅ JSON cleanup complete!")
    print(f"   📊 Original entries: {removed_entries + kept_entries}")
    print(f"   ❌ Removed entries: {removed_entries}")
    print(f"   ✅ Valid entries kept: {kept_entries}")
    print(f"   🏷️  Valid brands: {len(cleaned_brands)}")
    print(f"   🚗 Valid models: {sum(len(models) for models in cleaned_models.values())}")
    
    return cleaned_data

def verify_cleanup():
    """Verify the cleaned data"""
    json_path = Path(__file__).parent.parent / "data" / "json" / "morocco_cars_clean.json"
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\n🔍 Verification:")
    print(f"   📈 Structure: {list(data.keys())}")
    
    models = data.get('models', {})
    total_cars = 0
    
    for brand_name, brand_models in models.items():
        brand_car_count = sum(len(cars) for cars in brand_models.values())
        total_cars += brand_car_count
        print(f"   🏷️  {brand_name}: {len(brand_models)} models, {brand_car_count} cars")
    
    print(f"   📊 Total cars: {total_cars}")
    
    # Check for any remaining issues
    issues = 0
    for brand_name, brand_models in models.items():
        for model_name, model_cars in brand_models.items():
            if model_name in ['Kifalauto', 'Accueil']:
                print(f"   ⚠️  Still has placeholder: {brand_name} - {model_name}")
                issues += 1
            for car in model_cars:
                if not car.get('price'):
                    print(f"   ⚠️  Missing price: {brand_name} - {model_name}")
                    issues += 1
    
    if issues == 0:
        print(f"   ✅ No issues found!")
    else:
        print(f"   ⚠️  {issues} issues still present")

def main():
    """Main cleanup function"""
    print("🧹 Starting JSON data cleanup...\n")
    
    cleaned_data = clean_json_data()
    verify_cleanup()
    
    print(f"\n🎉 Cleanup completed successfully!")

if __name__ == "__main__":
    main()