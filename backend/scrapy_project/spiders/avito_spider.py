import scrapy
import re
import json
from datetime import datetime
from scrapy_project.items import UsedCarItem

class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ma']
    
    def __init__(self, brand=None, model=None, max_price=None, city=None, *args, **kwargs):
        super(AvitoSpider, self).__init__(*args, **kwargs)
        self.brand = brand
        self.model = model
        self.max_price = max_price
        self.city = city
        
    def start_requests(self):
        """Generate search URLs based on parameters"""
        base_url = "https://www.avito.ma/fr/maroc/voitures"
        
        # Build search parameters
        params = []
        if self.brand:
            params.append(f"q={self.brand}")
        if self.model and self.brand:
            params.append(f"q={self.brand}+{self.model}")
        if self.max_price:
            params.append(f"price_max={self.max_price}")
        if self.city:
            params.append(f"city={self.city}")
            
        search_url = base_url
        if params:
            search_url += "?" + "&".join(params)
            
        yield scrapy.Request(url=search_url, callback=self.parse)
    
    def parse(self, response):
        """Parse search results page"""
        # Extract car listing URLs
        car_links = response.css('a[href*="/voitures/"]::attr(href)').getall()
        
        for link in car_links[:20]:  # Limit to first 20 results
            if link.startswith('/'):
                link = 'https://www.avito.ma' + link
            yield scrapy.Request(url=link, callback=self.parse_car_detail)
        
        # Handle pagination
        next_page = response.css('a.pagination-next::attr(href)').get()
        if next_page and len(car_links) > 0:
            if next_page.startswith('/'):
                next_page = 'https://www.avito.ma' + next_page
            yield scrapy.Request(url=next_page, callback=self.parse)
    
    def parse_car_detail(self, response):
        """Parse individual car listing"""
        item = UsedCarItem()
        
        # Extract basic info
        title = response.css('h1.fs22.fw6.lh1-4.dark::text').get()
        if not title:
            title = response.css('h1::text').get()
            
        # Parse title for brand and model
        if title:
            title_parts = title.strip().split()
            item['brand'] = title_parts[0] if title_parts else ''
            item['model'] = ' '.join(title_parts[1:3]) if len(title_parts) > 1 else ''
        
        # Extract price
        price_text = response.css('.amount::text').get()
        if not price_text:
            price_text = response.css('[class*="price"]::text').get()
        
        if price_text:
            price_clean = re.sub(r'[^\d]', '', price_text)
            item['price'] = int(price_clean) if price_clean else 0
        else:
            item['price'] = 0
            
        # Extract specifications from description or details
        specs_section = response.css('.spec-container, .features-container')
        
        # Year
        year_text = response.css('*:contains("Année")::text').get()
        if year_text:
            year_match = re.search(r'(\d{4})', year_text)
            item['year'] = int(year_match.group(1)) if year_match else None
        else:
            # Try to extract from title or description
            year_match = re.search(r'(\d{4})', title or '')
            item['year'] = int(year_match.group(1)) if year_match else None
            
        # Mileage
        mileage_text = response.css('*:contains("Kilométrage")::text').get()
        if mileage_text:
            mileage_match = re.search(r'([\d\s]+)', mileage_text)
            if mileage_match:
                mileage_clean = re.sub(r'[^\d]', '', mileage_match.group(1))
                item['mileage'] = int(mileage_clean) if mileage_clean else 0
        else:
            item['mileage'] = 0
            
        # Fuel type
        fuel_keywords = {
            'essence': 'ESSENCE',
            'diesel': 'DIESEL', 
            'électrique': 'ELECTRIQUE',
            'hybride': 'HYBRID',
            'gpl': 'GPL'
        }
        
        description = response.css('.description::text, .ad-description::text').get() or ''
        item['fuel_type'] = 'ESSENCE'  # default
        
        for keyword, fuel_type in fuel_keywords.items():
            if keyword.lower() in description.lower() or keyword.lower() in (title or '').lower():
                item['fuel_type'] = fuel_type
                break
                
        # Transmission
        if any(word in description.lower() for word in ['automatique', 'automatic']):
            item['transmission'] = 'AUTOMATIQUE'
        elif any(word in description.lower() for word in ['manuelle', 'manual']):
            item['transmission'] = 'MANUELLE'
        else:
            item['transmission'] = 'MANUELLE'  # default
            
        # Location
        location = response.css('.location-info::text, .breadcrumb a::text').getall()
        item['city'] = location[-1] if location else 'Morocco'
        
        # Contact and images
        item['url'] = response.url
        item['images'] = response.css('img[src*="avito"]::attr(src)').getall()[:3]  # First 3 images
        
        phone_element = response.css('[class*="phone"], [data-phone]')
        item['phone'] = phone_element.css('::text').get() or phone_element.css('::attr(data-phone)').get()
        
        item['description'] = description.strip() if description else ''
        item['source'] = 'avito.ma'
        item['scraped_at'] = datetime.now().isoformat()
        
        # Filter by criteria if provided
        if self.should_include_item(item):
            yield item
    
    def should_include_item(self, item):
        """Filter items based on search criteria"""
        # Brand filtering
        if self.brand and self.brand.lower() not in (item.get('brand', '') or '').lower():
            return False
            
        # Model filtering  
        if self.model and self.model.lower() not in (item.get('model', '') or '').lower():
            return False
            
        # Price filtering
        if self.max_price and item.get('price', 0) > int(self.max_price):
            return False
            
        # Basic validation
        if not item.get('price') or item.get('price') < 10000:  # Minimum realistic price
            return False
            
        return True