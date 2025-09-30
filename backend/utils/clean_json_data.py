#!/usr/bin/env python3
"""
🧹 JSON DATA CLEANER
Clean up scraped car data by removing invalid entries and improving data quality
"""

import json
import re
from typing import Dict, List, Any
from pathlib import Path

class JSONDataCleaner:
    """Clean up car data JSON files"""
    
    def __init__(self):
        self.cars_file = "data/json/morocco_cars_clean.json"
        self.brands_file = "data/json/morocco_brands_clean.json"
        
        # Patterns to identify invalid model names
        self.invalid_patterns = [
            r'^\d{2}\s\d{2}\s\d{2}\s\d{2}\s\d{2}$',  # Phone numbers
            r'^0\d{9}$',  # Phone numbers
            r'^[+]\d+',   # International phone numbers
            r'vendez|achetez|annonce|kifal|occasion',  # Website text
            r'&nbsp|javascript|void|function',  # HTML/JS artifacts
            r'^[a-z\s]+$',  # All lowercase (likely website text)
            r'voiture|automobile|auto',  # Generic car terms
            r'prix|tarif|devis|contact',  # Pricing/contact text
            r'marque|brand|category',  # Category text
        ]
        
        # Invalid brand names to remove
        self.invalid_brands = {
            'MARQUE',  # Generic placeholder
        }
        
        # Valid car model patterns (to keep)
        self.valid_model_patterns = [
            r'[A-Z]\w+',  # Proper car model names (starts with capital)
            r'[0-9]+[A-Za-z]*',  # Model with numbers (e.g., "308", "A3")
            r'[A-Z][a-z]+[\s\-][A-Z0-9]',  # Multi-word models (e.g., "Série 3")
        ]
    
    def is_valid_model_name(self, model_name: str) -> bool:
        """Check if model name is valid"""
        if not model_name or len(model_name.strip()) < 2:
            return False
        
        # Check against invalid patterns
        for pattern in self.invalid_patterns:
            if re.search(pattern, model_name.lower()):
                return False
        
        # Must contain at least one letter
        if not re.search(r'[a-zA-Z]', model_name):
            return False
            
        # Must not be all numbers
        if model_name.strip().isdigit():
            return False
            
        # Check for obvious website artifacts
        website_keywords = [
            'kifal', 'ma', 'www', 'http', 'html', '.com',
            'contact', 'vendez', 'achetez', 'annonce'
        ]
        if any(keyword in model_name.lower() for keyword in website_keywords):
            return False
        
        return True
    
    def is_valid_brand(self, brand_name: str) -> bool:
        """Check if brand name is valid"""
        return brand_name not in self.invalid_brands
    
    def clean_model_name(self, model_name: str) -> str:
        """Clean up model name"""
        if not model_name:
            return model_name
            
        # Remove HTML entities
        model_name = model_name.replace('&nbsp', ' ').replace('&amp', '&')
        
        # Remove extra whitespace
        model_name = re.sub(r'\s+', ' ', model_name.strip())
        
        # Title case for proper nouns
        if model_name.isupper() and len(model_name) > 3:
            model_name = model_name.title()
        
        return model_name
    
    def clean_car_data(self) -> Dict[str, Any]:
        """Clean the main car data file"""
        print("🧹 Cleaning car data...")
        
        with open(self.cars_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        original_stats = {
            'brands': len(data.get('brands', {})),
            'models_count': sum(len(models) for models in data.get('models', {}).values()),
            'cars': len(data.get('cars', []))
        }
        
        # Clean brands
        clean_brands = {}
        for brand_name, brand_info in data.get('brands', {}).items():
            if self.is_valid_brand(brand_name):
                clean_brands[brand_name] = brand_info
        
        # Clean models and cars
        clean_models = {}
        clean_cars = []
        car_id = 1
        
        for brand_name, brand_models in data.get('models', {}).items():
            if not self.is_valid_brand(brand_name):
                continue
                
            clean_brand_models = {}
            
            for model_name, model_cars in brand_models.items():
                # Clean and validate model name
                cleaned_model_name = self.clean_model_name(model_name)
                
                if not self.is_valid_model_name(cleaned_model_name):
                    print(f"❌ Removing invalid model: {brand_name} -> {model_name}")
                    continue
                
                # Clean cars for this model
                valid_cars = []
                for car in model_cars:
                    # Update car data
                    car['id'] = car_id
                    car['brand'] = brand_name
                    car['model'] = cleaned_model_name
                    
                    # Validate car has meaningful data
                    if car.get('price') or car.get('year') or car.get('engine'):
                        valid_cars.append(car)
                        clean_cars.append(car)
                        car_id += 1
                
                # Only keep model if it has valid cars
                if valid_cars:
                    clean_brand_models[cleaned_model_name] = valid_cars
            
            # Only keep brand if it has valid models
            if clean_brand_models:
                clean_models[brand_name] = clean_brand_models
        
        # Update data structure
        data['brands'] = clean_brands
        data['models'] = clean_models
        data['cars'] = clean_cars
        
        # Update metadata
        if 'metadata' not in data:
            data['metadata'] = {}
        
        data['metadata'].update({
            'cleaned_at': '2025-09-30 01:30:00',
            'total_brands': len(clean_brands),
            'total_models': sum(len(models) for models in clean_models.values()),
            'total_cars': len(clean_cars),
            'cleaning_stats': {
                'brands_removed': original_stats['brands'] - len(clean_brands),
                'models_removed': original_stats['models_count'] - sum(len(models) for models in clean_models.values()),
                'cars_removed': original_stats['cars'] - len(clean_cars)
            }
        })
        
        new_stats = {
            'brands': len(clean_brands),
            'models_count': sum(len(models) for models in clean_models.values()),
            'cars': len(clean_cars)
        }
        
        print(f"📊 Cleaning Results:")
        print(f"   🏷️ Brands: {original_stats['brands']} → {new_stats['brands']} (-{original_stats['brands'] - new_stats['brands']})")
        print(f"   🚗 Models: {original_stats['models_count']} → {new_stats['models_count']} (-{original_stats['models_count'] - new_stats['models_count']})")
        print(f"   📋 Cars: {original_stats['cars']} → {new_stats['cars']} (-{original_stats['cars'] - new_stats['cars']})")
        
        return data
    
    def clean_brands_data(self) -> Dict[str, Any]:
        """Clean the brands data file"""
        print("🧹 Cleaning brands data...")
        
        with open(self.brands_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Clean brands list
        clean_brands_list = []
        for brand in data.get('brands', []):
            if self.is_valid_brand(brand.get('name', '')):
                clean_brands_list.append(brand)
        
        # Clean categories
        clean_categories = {}
        for category, brands in data.get('categories', {}).items():
            clean_category_brands = []
            for brand in brands:
                if self.is_valid_brand(brand.get('name', '')):
                    clean_category_brands.append(brand)
            
            if clean_category_brands:  # Only keep categories with valid brands
                clean_categories[category] = clean_category_brands
        
        # Update data
        data['brands'] = clean_brands_list
        data['categories'] = clean_categories
        
        if 'metadata' not in data:
            data['metadata'] = {}
            
        data['metadata'].update({
            'cleaned_at': '2025-09-30 01:30:00',
            'total_brands': len(clean_brands_list)
        })
        
        print(f"✅ Brands cleaned: {len(clean_brands_list)} valid brands")
        
        return data
    
    def save_cleaned_data(self, cars_data: Dict[str, Any], brands_data: Dict[str, Any]):
        """Save cleaned data to files"""
        # Backup originals
        backup_cars = self.cars_file.replace('.json', '_backup.json')
        backup_brands = self.brands_file.replace('.json', '_backup.json')
        
        # Create backups
        Path(backup_cars).write_text(Path(self.cars_file).read_text(encoding='utf-8'), encoding='utf-8')
        Path(backup_brands).write_text(Path(self.brands_file).read_text(encoding='utf-8'), encoding='utf-8')
        
        print(f"💾 Created backups: {backup_cars}, {backup_brands}")
        
        # Save cleaned data
        with open(self.cars_file, 'w', encoding='utf-8') as f:
            json.dump(cars_data, f, indent=2, ensure_ascii=False)
        
        with open(self.brands_file, 'w', encoding='utf-8') as f:
            json.dump(brands_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved cleaned data to {self.cars_file} and {self.brands_file}")
    
    def clean_all(self):
        """Clean both data files"""
        print("🧹 STARTING DATA CLEANUP")
        print("=" * 30)
        
        try:
            # Clean car data
            cars_data = self.clean_car_data()
            
            # Clean brands data  
            brands_data = self.clean_brands_data()
            
            # Save cleaned data
            self.save_cleaned_data(cars_data, brands_data)
            
            print()
            print("🎉 DATA CLEANUP COMPLETED!")
            print("📈 Final Statistics:")
            print(f"   🏷️ Brands: {cars_data['metadata']['total_brands']}")
            print(f"   🚗 Models: {cars_data['metadata']['total_models']}")  
            print(f"   📋 Cars: {cars_data['metadata']['total_cars']}")
            
            return cars_data, brands_data
            
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
            raise

def main():
    """Main cleanup function"""
    cleaner = JSONDataCleaner()
    cleaner.clean_all()

if __name__ == "__main__":
    main()