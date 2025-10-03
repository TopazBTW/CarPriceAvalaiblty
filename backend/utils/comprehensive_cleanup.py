#!/usr/bin/env python3
"""
Comprehensive cleanup of morocco_cars_clean.json:
1. Remove all "Unknown" model entries
2. Improve model name extraction from URLs and text
3. Re-scrape all links for complete data
4. Clean up brand names and categorization
"""
import asyncio
import aiohttp
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime

class ComprehensiveDataCleaner:
    def __init__(self):
        self.session = None
        self.updated_count = 0
        self.removed_count = 0
        
    async def create_session(self):
        """Create async HTTP session with proper headers"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=45)
        self.session = aiohttp.ClientSession(
            headers=headers,
            connector=connector,
            timeout=timeout
        )
    
    async def close_session(self):
        if self.session:
            await self.session.close()
    
    def extract_model_from_url(self, url: str) -> str:
        """Extract model name from URL path"""
        if not url:
            return None
            
        try:
            # Parse URL and get the path segments
            parsed = urlparse(url)
            path_segments = [seg for seg in parsed.path.split('/') if seg]
            
            # Look for model-like segments (after brand)
            for i, segment in enumerate(path_segments):
                # Decode URL encoding
                segment = segment.replace('%20', ' ').replace('-', ' ').replace('_', ' ')
                
                # Skip common non-model segments
                skip_segments = ['search', 'neuf', 'www', 'fr', 'en', 'voiture', 'car']
                if segment.lower() in skip_segments:
                    continue
                
                # If it looks like a model (contains letters and maybe numbers)
                if re.match(r'^[A-Za-z][A-Za-z0-9\s-]*$', segment) and len(segment) > 1:
                    # Clean up the segment
                    model = re.sub(r'\s+', ' ', segment.strip().title())
                    if len(model) > 2 and not self.is_location_string(model):
                        return model
            
            return None
        except Exception:
            return None
    
    def is_location_string(self, s: str) -> bool:
        """Check if string looks like an address/location"""
        if not s:
            return False
        s_upper = s.upper()
        location_indicators = [
            'BOULEVARD', 'RUE', 'ROUTE', 'RTE', 'CASABLANCA', 'RABAT', 
            'BUSINESS CENTER', 'AVENUE', 'PLACE', 'IMM', 'Z.I', 'ZONE',
            'YASMINA', 'CHEFCHAOUNI', 'MOROCCO', 'MAROC', 'MA'
        ]
        
        # Check for location indicators
        if any(indicator in s_upper for indicator in location_indicators):
            return True
        
        # Check for comma-separated addresses
        if ',' in s and len(s) > 30:
            return True
            
        # Very long strings are likely addresses
        if len(s) > 60:
            return True
            
        return False
    
    def clean_brand_name(self, brand: str) -> str:
        """Standardize brand names"""
        if not brand:
            return brand
            
        brand = brand.upper().strip()
        
        # Brand name mappings
        brand_mappings = {
            'MERCEDES-BENZ': 'MERCEDES',
            'MERCEDES BENZ': 'MERCEDES',
            'VOLKSWAGEN': 'VW',
            'LAND-ROVER': 'LAND ROVER',
            'ALFA-ROMEO': 'ALFA ROMEO',
        }
        
        return brand_mappings.get(brand, brand)
    
    async def scrape_listing_details(self, url: str) -> dict:
        """Scrape detailed information from a listing URL"""
        if not url or not self.session:
            return {}
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {}
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract all text for analysis
                text = soup.get_text(separator=' ', strip=True)
                
                details = {}
                
                # Extract price - multiple patterns
                price_patterns = [
                    r'Prix\s*:?\s*(\d{1,3}(?:[\s,]\d{3})*)\s*(?:DH|MAD|Dh)',
                    r'(\d{1,3}(?:[\s,]\d{3})*)\s*(?:DH|MAD|Dh)',
                    r'Price\s*:?\s*(\d{1,3}(?:[\s,]\d{3})*)',
                    r'(\d{3,})\s*MAD',
                ]
                
                for pattern in price_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        price_str = match.group(1).replace(' ', '').replace(',', '')
                        try:
                            price = int(price_str)
                            if 50000 <= price <= 5000000:  # Reasonable price range
                                details['price'] = price
                                break
                        except ValueError:
                            continue
                
                # Extract year
                year_match = re.search(r'\b(20[0-2][0-9])\b', text)
                if year_match:
                    year = int(year_match.group(1))
                    if 2000 <= year <= 2025:
                        details['year'] = year
                
                # Extract engine
                engine_patterns = [
                    r'(\d+\.?\d*)\s*[Ll](?:itre)?s?',
                    r'Moteur\s*:?\s*(\d+\.?\d*)\s*[Ll]',
                    r'Engine\s*:?\s*(\d+\.?\d*)\s*[Ll]',
                ]
                
                for pattern in engine_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        details['engine'] = f"{match.group(1)}L"
                        break
                
                # Extract fuel type
                fuel_keywords = {
                    'ESSENCE': ['essence', 'petrol', 'gasoline'],
                    'DIESEL': ['diesel', 'gasoil'],
                    'HYBRID': ['hybrid', 'hybride'],
                    'ELECTRIQUE': ['electrique', 'electric', 'électrique'],
                    'GPL': ['gpl', 'lpg']
                }
                
                text_lower = text.lower()
                for fuel_type, keywords in fuel_keywords.items():
                    if any(keyword in text_lower for keyword in keywords):
                        details['fuel_type'] = fuel_type
                        break
                
                # Extract transmission
                if any(word in text_lower for word in ['automatique', 'automatic', 'auto', 'cvt', 'dsg']):
                    details['transmission'] = 'AUTOMATIQUE'
                elif any(word in text_lower for word in ['manuelle', 'manual', 'manuel']):
                    details['transmission'] = 'MANUELLE'
                
                # Extract mileage/kilometers
                km_patterns = [
                    r'(\d{1,3}(?:[\s,]\d{3})*)\s*(?:km|KM|kilomètre)',
                    r'Kilométrage\s*:?\s*(\d{1,3}(?:[\s,]\d{3})*)',
                    r'Mileage\s*:?\s*(\d{1,3}(?:[\s,]\d{3})*)',
                ]
                
                for pattern in km_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        km_str = match.group(1).replace(' ', '').replace(',', '')
                        try:
                            km = int(km_str)
                            if 0 <= km <= 500000:  # Reasonable mileage
                                details['mileage'] = km
                                break
                        except ValueError:
                            continue
                
                # Extract better images
                image_selectors = [
                    'meta[property="og:image"]',
                    'img.main-image',
                    'img.car-image',
                    'img[alt*="car"]',
                    'img[src*="car"]'
                ]
                
                for selector in image_selectors:
                    img = soup.select_one(selector)
                    if img:
                        src = img.get('content') or img.get('src')
                        if src:
                            details['image'] = urljoin(url, src)
                            break
                
                # Try to extract actual model name from the page
                model_selectors = [
                    'h1', '.model-name', '.car-title', '.product-title',
                    'title', '.breadcrumb a:last-child'
                ]
                
                for selector in model_selectors:
                    element = soup.select_one(selector)
                    if element:
                        model_text = element.get_text(strip=True)
                        # Clean and validate model name
                        model_clean = re.sub(r'\s+', ' ', model_text).strip()
                        if (len(model_clean) > 2 and len(model_clean) < 50 and 
                            not self.is_location_string(model_clean)):
                            # Remove year and price from model name
                            model_clean = re.sub(r'\b20[0-2][0-9]\b', '', model_clean)
                            model_clean = re.sub(r'\d+\s*(?:DH|MAD)', '', model_clean, flags=re.IGNORECASE)
                            model_clean = re.sub(r'\s+', ' ', model_clean).strip()
                            if len(model_clean) > 2:
                                details['extracted_model'] = model_clean.title()
                                break
                
                return details
                
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {}
    
    def improve_model_name(self, car_entry: dict) -> str:
        """Try to get a better model name using multiple strategies"""
        current_model = car_entry.get('model', '')
        
        # If current model is "Unknown" or looks like address, try to improve
        if (current_model == 'Unknown' or 
            self.is_location_string(current_model) or 
            len(current_model) < 2):
            
            # Try URL-based extraction
            url_model = self.extract_model_from_url(car_entry.get('url', ''))
            if url_model:
                return url_model
            
            # Try to extract from any available text fields
            raw_text = car_entry.get('raw_text', '')
            if raw_text:
                # Look for model-like tokens
                tokens = re.findall(r'[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9\s-]*', raw_text)
                for token in tokens[:5]:  # Check first few tokens
                    token = token.strip().title()
                    if (len(token) > 2 and len(token) < 30 and 
                        not self.is_location_string(token) and
                        not re.match(r'^\d+$', token)):  # Not just numbers
                        return token
        
        return current_model if current_model != 'Unknown' else None
    
    async def process_data(self):
        """Main data processing function"""
        json_path = Path('data/json/morocco_cars_clean.json')
        if not json_path.exists():
            print("❌ morocco_cars_clean.json not found")
            return
        
        print("📂 Loading data...")
        data = json.loads(json_path.read_text(encoding='utf-8'))
        
        await self.create_session()
        
        try:
            cars = data.get('cars', [])
            print(f"🔄 Processing {len(cars)} cars...")
            
            # Process each car
            updated_cars = []
            tasks = []
            
            # Create scraping tasks for all URLs
            for car in cars:
                url = car.get('url')
                if url:
                    tasks.append(asyncio.create_task(self.scrape_listing_details(url)))
                else:
                    tasks.append(asyncio.create_task(asyncio.sleep(0)))  # Dummy task
            
            # Wait for all scraping to complete
            if tasks:
                print(f"🌐 Scraping {len([t for t in tasks if not t.done()])} URLs...")
                scraped_results = await asyncio.gather(*tasks)
            else:
                scraped_results = []
            
            # Process results
            for i, car in enumerate(cars):
                updated_car = car.copy()
                scraped_data = scraped_results[i] if i < len(scraped_results) else {}
                
                # Clean brand name
                if 'brand' in updated_car:
                    updated_car['brand'] = self.clean_brand_name(updated_car['brand'])
                
                # Improve model name
                better_model = None
                
                # First try scraped model
                if 'extracted_model' in scraped_data:
                    better_model = scraped_data['extracted_model']
                else:
                    # Try our improvement function
                    better_model = self.improve_model_name(updated_car)
                
                # If we still don't have a good model, skip this entry
                if not better_model or better_model == 'Unknown' or self.is_location_string(better_model):
                    self.removed_count += 1
                    continue  # Skip this car
                
                updated_car['model'] = better_model
                
                # Update with scraped data
                changed = False
                for key, value in scraped_data.items():
                    if key != 'extracted_model' and value is not None:
                        if updated_car.get(key) != value:
                            updated_car[key] = value
                            changed = True
                
                if changed:
                    self.updated_count += 1
                
                updated_cars.append(updated_car)
            
            # Rebuild models structure
            new_models = {}
            for car in updated_cars:
                brand = car['brand']
                model = car['model']
                
                if brand not in new_models:
                    new_models[brand] = {}
                
                if model not in new_models[brand]:
                    new_models[brand][model] = []
                
                new_models[brand][model].append(car)
            
            # Update data structure
            data['cars'] = updated_cars
            data['models'] = new_models
            
            # Update metadata
            metadata = data.get('metadata', {})
            metadata.update({
                'cleaned_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_brands': len(new_models),
                'total_models': sum(len(brand_models) for brand_models in new_models.values()),
                'total_cars': len(updated_cars),
                'removed_unknown_entries': self.removed_count,
                'updated_entries': self.updated_count
            })
            data['metadata'] = metadata
            
            # Save cleaned data
            json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            
            print("✅ Cleanup completed!")
            print(f"📊 Results:")
            print(f"   🏷️ Brands: {metadata['total_brands']}")
            print(f"   🚗 Models: {metadata['total_models']}")
            print(f"   📋 Cars: {metadata['total_cars']}")
            print(f"   🔄 Updated: {self.updated_count}")
            print(f"   🗑️ Removed: {self.removed_count}")
        
        finally:
            await self.close_session()

async def main():
    print("🧹 COMPREHENSIVE DATA CLEANUP")
    print("=" * 40)
    print("🎯 Cleaning up model names and scraping all links")
    print()
    
    cleaner = ComprehensiveDataCleaner()
    await cleaner.process_data()

if __name__ == "__main__":
    asyncio.run(main())