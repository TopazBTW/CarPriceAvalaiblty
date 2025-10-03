import re
import csv
from datetime import datetime
from itemadapter import ItemAdapter

class DataCleanupPipeline:
    """Pipeline to clean and validate scraped data"""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Clean brand and model
        if adapter.get('brand'):
            adapter['brand'] = self.clean_text(adapter['brand']).upper()
        
        if adapter.get('model'):
            adapter['model'] = self.clean_text(adapter['model']).upper()
            
        # Validate and clean price
        price = adapter.get('price', 0)
        if isinstance(price, str):
            price_clean = re.sub(r'[^\d]', '', price)
            adapter['price'] = int(price_clean) if price_clean else 0
        
        # Ensure price is reasonable
        if adapter.get('price', 0) < 10000:
            adapter['price'] = 0
            
        # Clean mileage
        mileage = adapter.get('mileage', 0)
        if isinstance(mileage, str):
            mileage_clean = re.sub(r'[^\d]', '', mileage)
            adapter['mileage'] = int(mileage_clean) if mileage_clean else 0
            
        # Validate year
        year = adapter.get('year')
        if year and (year < 1990 or year > 2025):
            adapter['year'] = None
            
        # Clean description
        if adapter.get('description'):
            adapter['description'] = self.clean_text(adapter['description'])
            
        # Validate fuel type
        valid_fuels = ['ESSENCE', 'DIESEL', 'ELECTRIQUE', 'HYBRID', 'GPL']
        if adapter.get('fuel_type') not in valid_fuels:
            adapter['fuel_type'] = 'ESSENCE'
            
        # Validate transmission
        valid_transmissions = ['AUTOMATIQUE', 'MANUELLE']
        if adapter.get('transmission') not in valid_transmissions:
            adapter['transmission'] = 'MANUELLE'
            
        return item
    
    def clean_text(self, text):
        """Clean text by removing extra spaces and special characters"""
        if not text:
            return ''
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\-\.,]', '', text)
        
        return text.strip()


class CsvExportPipeline:
    """Pipeline to export data to CSV"""
    
    def __init__(self):
        self.files = {}
        self.writers = {}
        
    def open_spider(self, spider):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'used_cars_{spider.name}_{timestamp}.csv'
        
        self.files[spider] = open(filename, 'w', newline='', encoding='utf-8')
        
        fieldnames = [
            'brand', 'model', 'year', 'price', 'mileage', 
            'fuel_type', 'transmission', 'city', 'url', 
            'phone', 'description', 'source', 'scraped_at'
        ]
        
        self.writers[spider] = csv.DictWriter(self.files[spider], fieldnames=fieldnames)
        self.writers[spider].writeheader()
        
    def close_spider(self, spider):
        if spider in self.files:
            self.files[spider].close()
            
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Convert to dict and write to CSV
        item_dict = dict(adapter)
        
        # Handle list fields (like images)
        if 'images' in item_dict and isinstance(item_dict['images'], list):
            item_dict['images'] = '; '.join(item_dict['images'][:3])  # First 3 images
            
        self.writers[spider].writerow(item_dict)
        
        return item


class DatabasePipeline:
    """Pipeline to save data to database (optional)"""
    
    def __init__(self):
        self.items = []
        
    def process_item(self, item, spider):
        # Store items in memory for API access
        self.items.append(dict(ItemAdapter(item)))
        
        # Keep only last 1000 items to prevent memory issues
        if len(self.items) > 1000:
            self.items = self.items[-1000:]
            
        return item
    
    def get_items(self):
        """Return stored items for API access"""
        return self.items