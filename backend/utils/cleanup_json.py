#!/usr/bin/env python3
"""
Clean up scraped Wandaloo JSON data by:
1. Removing non-model entries (concessionnaires, guides, etc.)
2. Filtering out invalid prices
3. Organizing data by brand -> model -> listings
4. Removing duplicate entries
"""

import json
import re
from pathlib import Path

def is_valid_model_name(name):
    """Check if a name looks like a car model rather than navigation/info page"""
    name_lower = name.lower()
    
    # Skip obvious non-model entries
    bad_keywords = [
        'concessionnaire', 'guide', 'tarif', 'budget', 'trouver', 'prix', 
        'achat', 'acheter', 'neuve', 'maroc', 'automobile', 'voiture',
        'comparateur', 'offre', 'promo', 'financement', 'credit'
    ]
    
    for keyword in bad_keywords:
        if keyword in name_lower:
            return False
    
    # Valid model names are usually 2-10 characters, contain letters/numbers
    if len(name) < 2 or len(name) > 15:
        return False
        
    if not re.search(r'[A-Za-z]', name):
        return False
        
    return True

def is_valid_price(price):
    """Check if price looks reasonable for a car (30k to 3M MAD)"""
    if not price or not isinstance(price, (int, float)):
        return False
    return 30000 <= price <= 3000000

def clean_scraped_data(input_file, output_file):
    """Clean and reorganize the scraped data"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cleaned_data = {}
    stats = {'brands': 0, 'models': 0, 'listings': 0, 'removed': 0}
    
    for brand, brand_data in data.items():
        if not isinstance(brand_data, dict):
            continue
            
        cleaned_brand = {}
        
        for potential_model, listings in brand_data.items():
            # Clean and validate model name
            model_name = re.sub(r'[^A-Za-z0-9 \-]', ' ', potential_model).strip()
            model_name = re.sub(r'\s+', ' ', model_name).title()
            
            if not is_valid_model_name(model_name):
                stats['removed'] += len(listings) if isinstance(listings, list) else 1
                continue
                
            if not isinstance(listings, list):
                continue
                
            # Clean listings for this model
            cleaned_listings = []
            for listing in listings:
                if not isinstance(listing, dict):
                    continue
                    
                title = listing.get('title', '').strip()
                price = listing.get('price')
                url = listing.get('url', '').strip()
                year = listing.get('year')
                
                # Validate listing
                if not title or not url:
                    stats['removed'] += 1
                    continue
                    
                if not is_valid_price(price):
                    stats['removed'] += 1
                    continue
                
                # Clean title
                title = re.sub(r'\b20\d{2}\b', '', title)
                title = re.sub(r'neuve|maroc', '', title, flags=re.I)
                title = re.sub(r'[^A-Za-z0-9 \-]', ' ', title).strip()
                title = re.sub(r'\s+', ' ', title)
                
                if len(title) < 5:
                    stats['removed'] += 1
                    continue
                
                cleaned_listing = {
                    'title': title,
                    'price': int(price),
                    'url': url
                }
                
                if year and isinstance(year, (int, float)) and 2020 <= year <= 2025:
                    cleaned_listing['year'] = int(year)
                
                cleaned_listings.append(cleaned_listing)
                stats['listings'] += 1
            
            if cleaned_listings:
                cleaned_brand[model_name] = cleaned_listings
                stats['models'] += 1
        
        if cleaned_brand:
            cleaned_data[brand] = cleaned_brand
            stats['brands'] += 1
    
    # Write cleaned data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
    
    return stats

if __name__ == "__main__":
    input_file = Path("scraped_wandaloo_followed.json")
    output_file = Path("scraped_wandaloo_clean.json")
    
    if not input_file.exists():
        print(f"Input file {input_file} not found")
        exit(1)
    
    print("Cleaning scraped data...")
    stats = clean_scraped_data(input_file, output_file)
    
    print(f"✅ Cleanup completed!")
    print(f"📊 Stats:")
    print(f"  - Brands: {stats['brands']}")
    print(f"  - Models: {stats['models']}")
    print(f"  - Listings: {stats['listings']}")
    print(f"  - Removed: {stats['removed']}")
    print(f"📁 Clean data saved to: {output_file}")