#!/usr/bin/env python3
"""
🎯 FINAL JSON DATA CLEANUP
Creates perfectly clean car model data by extracting only actual car listings
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any

def extract_car_models_from_listings(data: Dict[str, Any]) -> Dict[str, Dict[str, List[Any]]]:
    """
    Extract actual car models from listings, ignoring navigation categories
    """
    
    # Known car model patterns
    known_models = {
        'Audi': ['A1', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'Q2', 'Q3', 'Q4', 'Q5', 'Q7', 'Q8', 'TT', 'R8', 'e-tron'],
        'BMW': ['X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'X7', 'Z4', 'i3', 'i4', 'i7', 'iX', 'M2', 'M3', 'M4', 'M5', 'M8'],
        'Toyota': ['Yaris', 'Corolla', 'Camry', 'RAV4', 'Highlander', 'Land Cruiser', 'Prius', 'C-HR', 'Aygo'],
        'Renault': ['Clio', 'Megane', 'Scenic', 'Captur', 'Kadjar', 'Koleos', 'Talisman', 'Twingo', 'Zoe'],
        'Peugeot': ['208', '308', '3008', '5008', '2008', '408', '508', 'Partner', 'Expert', 'Boxer'],
        'Dacia': ['Sandero', 'Logan', 'Duster', 'Lodgy', 'Dokker', 'Spring', 'Jogger'],
        'Mercedes-Benz': ['Classe A', 'Classe B', 'Classe C', 'Classe E', 'Classe S', 'GLA', 'GLB', 'GLC', 'GLE', 'GLS', 'CLA', 'CLS'],
        'Volkswagen': ['Polo', 'Golf', 'Passat', 'Tiguan', 'Touareg', 'T-Cross', 'T-Roc', 'Arteon', 'ID.3', 'ID.4'],
        'Ford': ['Fiesta', 'Focus', 'Mondeo', 'Kuga', 'Edge', 'Explorer', 'Mustang', 'Ranger', 'Transit'],
        'Hyundai': ['i10', 'i20', 'i30', 'Tucson', 'Santa Fe', 'Kona', 'Ioniq', 'Elantra'],
        'Kia': ['Picanto', 'Rio', 'Ceed', 'Sportage', 'Sorento', 'Stonic', 'XCeed', 'EV6'],
        'Nissan': ['Micra', 'Juke', 'Qashqai', 'X-Trail', 'Leaf', 'Note', '370Z', 'GT-R']
    }
    
    def extract_model_from_title(title: str) -> str:
        """Extract car model from listing title"""
        if not title:
            return None
            
        title_clean = title.strip().upper()
        
        # Look for known model patterns
        for brand, models in known_models.items():
            if brand.upper() in title_clean:
                for model in models:
                    if model.upper() in title_clean:
                        return model
        
        # Extract model using patterns
        # Pattern: "BRAND MODEL ..."
        words = title_clean.split()
        if len(words) >= 2:
            potential_model = words[1]
            # Filter out common non-model words
            if potential_model not in ['NEUF', 'OCCASION', 'PRIX', 'MAROC', 'AUTO', 'VOITURE']:
                return potential_model
        
        return None
    
    cleaned_data = {}
    
    for brand, categories in data.items():
        if not isinstance(categories, dict):
            continue
            
        # Collect all listings from all categories for this brand
        all_listings = []
        
        for category, listings in categories.items():
            if isinstance(listings, list):
                all_listings.extend(listings)
        
        # Group listings by actual car model
        model_groups = {}
        
        for listing in all_listings:
            if not isinstance(listing, dict):
                continue
                
            title = listing.get('title', '')
            price = listing.get('price')
            url = listing.get('url', '')
            
            # Validate listing
            if not title or not price or not url:
                continue
                
            # Validate price range
            try:
                price_num = float(price)
                if not (50000 <= price_num <= 5000000):
                    continue
            except:
                continue
            
            # Extract model from title
            model = extract_model_from_title(title)
            if not model:
                continue
            
            # Add to model group
            if model not in model_groups:
                model_groups[model] = []
            
            model_groups[model].append(listing)
        
        # Only keep models with multiple listings (more reliable)
        filtered_models = {}
        for model, model_listings in model_groups.items():
            if len(model_listings) >= 1:  # Keep all for now
                filtered_models[model] = model_listings
        
        if filtered_models:
            cleaned_data[brand] = filtered_models
    
    return cleaned_data

def main():
    """Main cleanup function"""
    print("🎯 CREATING PERFECTLY CLEAN CAR DATA")
    print("=" * 50)
    
    # Load the cleaned data
    input_file = Path("scraped_wandaloo_followed_clean.json")
    output_file = Path("car_data_clean_final.json")
    
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 Processing data from: {input_file}")
    
    # Extract clean car models
    clean_data = extract_car_models_from_listings(data)
    
    # Save clean data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clean_data, f, indent=2, ensure_ascii=False)
    
    # Generate stats
    total_brands = len(clean_data)
    total_models = sum(len(models) for models in clean_data.values())
    total_listings = sum(len(listings) for brand_models in clean_data.values() 
                        for listings in brand_models.values())
    
    print(f"✅ FINAL CLEAN DATA CREATED!")
    print(f"📊 Brands: {total_brands}")
    print(f"🚗 Models: {total_models}")
    print(f"📋 Listings: {total_listings}")
    print(f"💾 Saved to: {output_file}")
    
    # Show sample data
    print(f"\n📝 SAMPLE CLEAN DATA:")
    print("-" * 30)
    for brand, models in list(clean_data.items())[:3]:
        print(f"🏷️  {brand}:")
        for model, listings in list(models.items())[:3]:
            print(f"   🚗 {model}: {len(listings)} listings")
    
    print(f"\n🎉 PERFECT CLEAN CAR DATA READY!")

if __name__ == "__main__":
    main()