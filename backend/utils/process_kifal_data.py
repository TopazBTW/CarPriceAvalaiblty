#!/usr/bin/env python3
"""
📊 KIFAL DATA PROCESSOR
Process scraped Kifal.ma data into clean, structured formats
"""

import json
import csv
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class KifalDataProcessor:
    """Process and clean scraped Kifal.ma data"""
    
    def __init__(self, input_file: str = "data/json/kifal_scraped_data.json"):
        self.input_file = input_file
        self.clean_data = {
            "brands": {},
            "models": {},
            "cars": [],
            "metadata": {}
        }
        
    def load_scraped_data(self) -> Dict[str, Any]:
        """Load scraped data from JSON file"""
        print(f"📂 Loading scraped data from {self.input_file}...")
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Loaded data: {len(data.get('brands', {}))} brands, "
              f"{sum(len(models) for models in data.get('models', {}).values())} models")
        
        return data
    
    def clean_brand_name(self, brand_name: str) -> str:
        """Clean and standardize brand name"""
        # Remove extra spaces and normalize
        cleaned = re.sub(r'\s+', ' ', brand_name.strip().upper())
        
        # Handle special cases
        replacements = {
            'MERCEDES-BENZ': 'MERCEDES',
            'MERCEDES BENZ': 'MERCEDES',
            'VOLKSWAGEN': 'VW',
        }
        
        return replacements.get(cleaned, cleaned)
    
    def clean_model_name(self, model_name: str) -> str:
        """Clean and standardize model name"""
        # Remove extra spaces and normalize
        cleaned = re.sub(r'\s+', ' ', model_name.strip())
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = ['NOUVELLE', 'NOUVEAU', 'NEW', 'ALL-NEW']
        for prefix in prefixes_to_remove:
            cleaned = re.sub(f'^{prefix}\\s+', '', cleaned, flags=re.IGNORECASE)
        
        # Handle special characters
        cleaned = cleaned.replace('é', 'e').replace('è', 'e').replace('à', 'a')
        
        return cleaned.title()
    
    def extract_car_details(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract detailed car information from model data"""
        raw_text = model_data.get('raw_text', '')
        
        # Extract year
        year_match = re.search(r'20\d{2}', raw_text)
        year = int(year_match.group()) if year_match else None
        
        # Extract engine info
        engine_match = re.search(r'(\d+\.\d+|\d+)\s*(L|l|TSI|TDI|HDI|DCI)', raw_text, re.IGNORECASE)
        engine = engine_match.group().upper() if engine_match else None
        
        # Extract fuel type
        fuel_types = ['ESSENCE', 'DIESEL', 'HYBRID', 'ELECTRIQUE', 'GPL']
        fuel_type = None
        for fuel in fuel_types:
            if fuel.lower() in raw_text.lower():
                fuel_type = fuel
                break
        
        # Extract transmission
        if any(term in raw_text.upper() for term in ['AUTO', 'AUTOMATIQUE', 'CVT', 'DSG']):
            transmission = 'AUTOMATIQUE'
        elif any(term in raw_text.upper() for term in ['MANUEL', 'MANUELLE', 'MT']):
            transmission = 'MANUELLE'
        else:
            transmission = None
        
        return {
            'year': year,
            'engine': engine,
            'fuel_type': fuel_type,
            'transmission': transmission,
            'raw_text': raw_text
        }
    
    def categorize_price_range(self, price: Optional[int]) -> str:
        """Categorize price into ranges"""
        if not price:
            return 'Non spécifié'
        
        if price < 200000:
            return 'Moins de 200k'
        elif price < 300000:
            return '200k - 300k'
        elif price < 500000:
            return '300k - 500k'
        elif price < 800000:
            return '500k - 800k'
        elif price < 1500000:
            return '800k - 1.5M'
        else:
            return 'Plus de 1.5M'
    
    def process_data(self) -> Dict[str, Any]:
        """Process and clean the scraped data"""
        print("🔄 Processing scraped Kifal.ma data...")
        
        raw_data = self.load_scraped_data()
        
        # Process brands
        for brand_name, brand_info in raw_data.get('brands', {}).items():
            clean_name = self.clean_brand_name(brand_name)
            self.clean_data['brands'][clean_name] = {
                'name': clean_name,
                'original_name': brand_name,
                'category': brand_info.get('category', 'generaliste'),
                'image': brand_info.get('image'),
                'url': brand_info.get('url')
            }
        
        # Process models and cars
        car_id = 1
        for brand_name, brand_models in raw_data.get('models', {}).items():
            clean_brand_name = self.clean_brand_name(brand_name)
            
            if clean_brand_name not in self.clean_data['models']:
                self.clean_data['models'][clean_brand_name] = {}
            
            for model_name, model_variations in brand_models.items():
                clean_model_name = self.clean_model_name(model_name)
                
                if clean_model_name not in self.clean_data['models'][clean_brand_name]:
                    self.clean_data['models'][clean_brand_name][clean_model_name] = []
                
                for variation in model_variations:
                    # Extract car details
                    details = self.extract_car_details(variation)
                    
                    # Create clean car entry
                    car_entry = {
                        'id': car_id,
                        'brand': clean_brand_name,
                        'model': clean_model_name,
                        'price': variation.get('price'),
                        'price_range': self.categorize_price_range(variation.get('price')),
                        'year': details['year'],
                        'engine': details['engine'],
                        'fuel_type': details['fuel_type'],
                        'transmission': details['transmission'],
                        'url': variation.get('url'),
                        'image': variation.get('image'),
                        'source': 'kifal.ma',
                        'scraped_at': raw_data.get('metadata', {}).get('scraped_at')
                    }
                    
                    self.clean_data['cars'].append(car_entry)
                    self.clean_data['models'][clean_brand_name][clean_model_name].append(car_entry)
                    
                    car_id += 1
        
        # Update metadata
        self.clean_data['metadata'] = {
            'processed_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'source': 'kifal.ma',
            'original_scrape_time': raw_data.get('metadata', {}).get('scraped_at'),
            'total_brands': len(self.clean_data['brands']),
            'total_models': sum(len(models) for models in self.clean_data['models'].values()),
            'total_cars': len(self.clean_data['cars']),
            'price_ranges': {
                'Moins de 200k': len([c for c in self.clean_data['cars'] if c['price_range'] == 'Moins de 200k']),
                '200k - 300k': len([c for c in self.clean_data['cars'] if c['price_range'] == '200k - 300k']),
                '300k - 500k': len([c for c in self.clean_data['cars'] if c['price_range'] == '300k - 500k']),
                '500k - 800k': len([c for c in self.clean_data['cars'] if c['price_range'] == '500k - 800k']),
                '800k - 1.5M': len([c for c in self.clean_data['cars'] if c['price_range'] == '800k - 1.5M']),
                'Plus de 1.5M': len([c for c in self.clean_data['cars'] if c['price_range'] == 'Plus de 1.5M']),
            }
        }
        
        print(f"✅ Processing completed!")
        print(f"📊 Results:")
        print(f"   🏷️ Brands: {self.clean_data['metadata']['total_brands']}")
        print(f"   🚗 Models: {self.clean_data['metadata']['total_models']}")
        print(f"   📋 Cars: {self.clean_data['metadata']['total_cars']}")
        
        return self.clean_data
    
    def save_json(self, filename: str = "data/json/morocco_cars_clean.json"):
        """Save processed data to JSON"""
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.clean_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Clean JSON data saved to {filename}")
    
    def save_csv(self, filename: str = "data/csv/morocco_cars_clean.csv"):
        """Save car data to CSV"""
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        fieldnames = [
            'id', 'brand', 'model', 'price', 'price_range', 'year', 
            'engine', 'fuel_type', 'transmission', 'url', 'source'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for car in self.clean_data['cars']:
                # Only write relevant fields to CSV
                csv_row = {field: car.get(field, '') for field in fieldnames}
                writer.writerow(csv_row)
        
        print(f"📊 Clean CSV data saved to {filename}")
    
    def save_brands_json(self, filename: str = "data/json/morocco_brands_clean.json"):
        """Save brands data to separate JSON"""
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        brands_data = {
            'brands': list(self.clean_data['brands'].values()),
            'categories': {
                'premium': [b for b in self.clean_data['brands'].values() if b['category'] == 'premium'],
                'generaliste': [b for b in self.clean_data['brands'].values() if b['category'] == 'generaliste'],
                'chinese': [b for b in self.clean_data['brands'].values() if b['category'] == 'chinese'],
                'electric': [b for b in self.clean_data['brands'].values() if b['category'] == 'electric'],
            },
            'metadata': {
                'total_brands': len(self.clean_data['brands']),
                'processed_at': self.clean_data['metadata']['processed_at']
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(brands_data, f, indent=2, ensure_ascii=False)
        
        print(f"🏷️ Clean brands data saved to {filename}")

def main():
    """Main processing function"""
    print("📊 KIFAL DATA PROCESSOR")
    print("=" * 30)
    print()
    
    processor = KifalDataProcessor()
    
    try:
        # Process the data
        clean_data = processor.process_data()
        
        # Save in multiple formats
        processor.save_json()
        processor.save_csv()
        processor.save_brands_json()
        
        print()
        print("🎉 DATA PROCESSING COMPLETED!")
        print("📁 Files created:")
        print("   📄 data/json/morocco_cars_clean.json - Complete dataset")
        print("   📊 data/csv/morocco_cars_clean.csv - Car listings CSV")
        print("   🏷️ data/json/morocco_brands_clean.json - Brands data")
        
        # Show some statistics
        print()
        print("📈 Price Distribution:")
        for range_name, count in clean_data['metadata']['price_ranges'].items():
            print(f"   💰 {range_name}: {count} cars")
        
        return clean_data
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        raise

if __name__ == "__main__":
    main()