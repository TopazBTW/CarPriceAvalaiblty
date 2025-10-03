import scrapy
import re
import json
from datetime import datetime
from scrapy_project.items import UsedCarItem

class FacebookMarketplaceSpider(scrapy.Spider):
    name = 'facebook_marketplace'
    allowed_domains = ['facebook.com']
    
    def __init__(self, brand=None, model=None, max_price=None, city=None, *args, **kwargs):
        super(FacebookMarketplaceSpider, self).__init__(*args, **kwargs)
        self.brand = brand
        self.model = model
        self.max_price = max_price
        self.city = city or 'casablanca'
        
    def start_requests(self):
        """Generate Facebook Marketplace search URLs"""
        # Facebook Marketplace Morocco cars URL
        base_url = "https://www.facebook.com/marketplace/casablanca/vehicles"
        
        # Build search query
        search_query = ""
        if self.brand:
            search_query = self.brand
        if self.model and self.brand:
            search_query = f"{self.brand} {self.model}"
            
        if search_query:
            search_url = f"{base_url}?query={search_query}"
        else:
            search_url = base_url
            
        # Add price filter if provided
        if self.max_price:
            search_url += f"&maxPrice={self.max_price}"
            
        yield scrapy.Request(
            url=search_url,
            callback=self.parse,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
    
    def parse(self, response):
        """Parse Facebook Marketplace search results"""
        # Facebook uses dynamic loading, so we'll look for static elements first
        
        # Try to extract car listings from the page
        listing_links = response.css('a[href*="/marketplace/item/"]::attr(href)').getall()
        
        for link in listing_links[:15]:  # Limit results
            full_url = response.urljoin(link)
            yield scrapy.Request(url=full_url, callback=self.parse_listing_detail)
    
    def parse_listing_detail(self, response):
        """Parse individual Facebook listing"""
        item = UsedCarItem()
        
        # Extract title
        title = response.css('h1[data-testid="marketplace-listing-title"]::text').get()
        if not title:
            title = response.css('span[dir="auto"]:contains("voiture")::text, span[dir="auto"]:contains("car")::text').get()
            
        # Parse brand and model from title
        if title:
            title_clean = title.strip().lower()
            
            # Common car brands in Morocco
            brands = ['toyota', 'renault', 'peugeot', 'dacia', 'ford', 'volkswagen', 'audi', 'bmw', 'mercedes', 
                     'nissan', 'hyundai', 'kia', 'citroen', 'fiat', 'seat', 'skoda', 'honda', 'mazda']
            
            found_brand = None
            for brand in brands:
                if brand in title_clean:
                    found_brand = brand.upper()
                    break
                    
            item['brand'] = found_brand or 'UNKNOWN'
            
            # Extract model (words after brand)
            if found_brand:
                title_parts = title_clean.split()
                try:
                    brand_index = title_parts.index(found_brand.lower())
                    model_parts = title_parts[brand_index + 1:brand_index + 3]
                    item['model'] = ' '.join(model_parts).upper()
                except ValueError:
                    item['model'] = 'UNKNOWN'
            else:
                item['model'] = title[:20] if title else 'UNKNOWN'
        
        # Extract price
        price_element = response.css('[data-testid="marketplace-listing-price"]::text').get()
        if not price_element:
            price_element = response.css('span:contains("DH")::text, span:contains("MAD")::text').get()
            
        if price_element:
            price_clean = re.sub(r'[^\d]', '', price_element)
            item['price'] = int(price_clean) if price_clean and len(price_clean) > 3 else 0
        else:
            item['price'] = 0
        
        # Extract description and details
        description = response.css('[data-testid="marketplace-listing-description"] span::text').get()
        if not description:
            description = response.css('div[dir="auto"]:contains("Description") + div span::text').get()
        
        item['description'] = description or ''
        
        # Extract year from description or title
        year_match = re.search(r'(19|20)\d{2}', (title or '') + ' ' + (description or ''))
        item['year'] = int(year_match.group()) if year_match else None
        
        # Extract mileage
        mileage_match = re.search(r'(\d+[\s,]*\d*)\s*km', (description or '').lower())
        if mileage_match:
            mileage_str = re.sub(r'[^\d]', '', mileage_match.group(1))
            item['mileage'] = int(mileage_str) if mileage_str else 0
        else:
            item['mileage'] = 0
        
        # Extract fuel type
        fuel_keywords = {
            'essence': 'ESSENCE',
            'diesel': 'DIESEL',
            'électrique': 'ELECTRIQUE', 
            'electric': 'ELECTRIQUE',
            'hybride': 'HYBRID',
            'hybrid': 'HYBRID'
        }
        
        item['fuel_type'] = 'ESSENCE'  # default
        desc_lower = (description or '').lower() + ' ' + (title or '').lower()
        
        for keyword, fuel_type in fuel_keywords.items():
            if keyword in desc_lower:
                item['fuel_type'] = fuel_type
                break
        
        # Extract transmission
        if any(word in desc_lower for word in ['automatique', 'automatic', 'auto']):
            item['transmission'] = 'AUTOMATIQUE'
        elif any(word in desc_lower for word in ['manuelle', 'manual']):
            item['transmission'] = 'MANUELLE'  
        else:
            item['transmission'] = 'MANUELLE'  # default
        
        # Extract location
        location_element = response.css('[aria-label*="location"], .location::text').get()
        item['city'] = location_element or self.city or 'Morocco'
        
        # Extract images
        images = response.css('img[src*="scontent"]::attr(src)').getall()
        item['images'] = images[:3] if images else []
        
        # Other fields
        item['url'] = response.url
        item['phone'] = None  # Facebook doesn't usually show phone directly
        item['source'] = 'facebook.com'
        item['scraped_at'] = datetime.now().isoformat()
        
        # Validate and filter
        if self.should_include_item(item):
            yield item
    
    def should_include_item(self, item):
        """Validate item meets criteria"""
        # Brand filter
        if self.brand and self.brand.lower() not in (item.get('brand', '') or '').lower():
            return False
            
        # Model filter
        if self.model and self.model.lower() not in (item.get('model', '') or '').lower():
            return False
            
        # Price validation
        price = item.get('price', 0)
        if not price or price < 15000:  # Minimum reasonable price
            return False
            
        if self.max_price and price > int(self.max_price):
            return False
            
        return True