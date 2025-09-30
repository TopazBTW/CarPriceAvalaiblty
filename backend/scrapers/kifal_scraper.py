#!/usr/bin/env python3
"""
🚗 KIFAL.MA COMPREHENSIVE DATA SCRAPER
Extract real, accurate car data directly from neuf.kifal.ma
"""

import asyncio
import aiohttp
import json
import re
import time
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KifalDataScraper:
    """Comprehensive scraper for Kifal.ma car data"""
    
    def __init__(self):
        self.base_url = "https://neuf.kifal.ma"
        self.session = None
        self.scraped_data = {
            "brands": {},
            "models": {},
            "cars": {},
            "prices": {},
            "metadata": {
                "scraped_at": None,
                "total_brands": 0,
                "total_models": 0,
                "total_cars": 0,
                "source": "neuf.kifal.ma"
            }
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    async def create_session(self):
        """Create async HTTP session"""
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            connector=connector,
            timeout=timeout
        )
    
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    async def fetch_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page"""
        for attempt in range(retries):
            try:
                logger.info(f"Fetching: {url} (attempt {attempt + 1})")
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        return BeautifulSoup(content, 'html.parser')
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
        return None
    
    async def extract_brands_from_homepage(self) -> List[Dict[str, str]]:
        """Extract brand information from homepage and search pages"""
        logger.info("🏷️ Extracting ALL brands from Kifal.ma...")
        
        brands = []
        
        # Method 1: Extract from homepage
        soup = await self.fetch_page(self.base_url)
        if soup:
            brands.extend(self.extract_brands_from_page(soup))
        
        # Method 2: Try to find brand selector/dropdown
        # Many car sites have a brand selector dropdown
        search_page = await self.fetch_page(f"{self.base_url}/search")
        if search_page:
            brands.extend(self.extract_brands_from_search_page(search_page))
        
        # Method 3: Common brand list - ensure we don't miss major brands
        common_brands = [
            'ABARTH', 'ACURA', 'AIWAYS', 'ALFA ROMEO', 'ALPINE', 'ASTON MARTIN',
            'AUDI', 'BAIC', 'BENTLEY', 'BMW', 'BORGWARD', 'BYD', 
            'CADILLAC', 'CHANGAN', 'CHERY', 'CHEVROLET', 'CHRYSLER', 'CITROEN',
            'CUPRA', 'DACIA', 'DAEWOO', 'DAIHATSU', 'DFSK', 'DODGE', 'DS',
            'FERRARI', 'FIAT', 'FORD', 'GEELY', 'GENESIS', 'GMC', 'GWM',
            'HAVAL', 'HONDA', 'HUMMER', 'HYUNDAI', 'INFINITI', 'ISUZU', 'IVECO',
            'JAECOO', 'JAGUAR', 'JEEP', 'KIA', 'LADA', 'LAMBORGHINI', 'LANCIA',
            'LAND ROVER', 'LEXUS', 'LINCOLN', 'LOTUS', 'MAHINDRA', 'MASERATI',
            'MAYBACH', 'MAZDA', 'MCLAREN', 'MERCEDES', 'MERCEDES-BENZ', 'MG', 'MINI',
            'MITSUBISHI', 'NISSAN', 'OMODA', 'OPEL', 'PEUGEOT', 'PORSCHE',
            'PROTON', 'RENAULT', 'ROLLS-ROYCE', 'SAAB', 'SEAT', 'SKODA', 'SMART',
            'SSANGYONG', 'SUBARU', 'SUZUKI', 'TATA', 'TESLA', 'TOYOTA', 'VOLVO',
            'VOLKSWAGEN', 'VW', 'ZEEKR'
        ]
        
        # Check each common brand
        for brand_name in common_brands:
            brand_url = f"{self.base_url}/search?marque={brand_name}"
            test_page = await self.fetch_page(brand_url)
            
            if test_page and not self.is_empty_results_page(test_page):
                brands.append({
                    'name': brand_name,
                    'url': brand_url,
                    'image': f"https://referentiel.kifal.ma/imgs/brands/{brand_name}.webp",
                    'category': self.categorize_brand(brand_name)
                })
                logger.info(f"✅ Found brand: {brand_name}")
        
        # Remove duplicates
        unique_brands = {}
        for brand in brands:
            if brand['name'] not in unique_brands:
                unique_brands[brand['name']] = brand
        
        brands_list = list(unique_brands.values())
        logger.info(f"🎉 Total brands found: {len(brands_list)}")
        
        return brands_list
    
    def extract_brands_from_page(self, soup) -> List[Dict[str, str]]:
        """Extract brands from a page"""
        brands = []
        
        # Look for brand links and images
        brand_links = soup.find_all('a', href=True)
        
        for link in brand_links:
            href = link.get('href', '')
            
            # Check if it's a brand page URL
            if '/search' in href and 'marque=' in href:
                match = re.search(r'marque=([^&]+)', href)
                if match:
                    brand_name = match.group(1).replace('%20', ' ').upper()
                    
                    img = link.find('img')
                    brand_image = None
                    if img and img.get('src'):
                        brand_image = urljoin(self.base_url, img.get('src'))
                    
                    brands.append({
                        'name': brand_name,
                        'url': urljoin(self.base_url, href),
                        'image': brand_image,
                        'category': self.categorize_brand(brand_name)
                    })
        
        return brands
    
    def extract_brands_from_search_page(self, soup) -> List[Dict[str, str]]:
        """Extract brands from search page dropdowns/selectors"""
        brands = []
        
        # Look for select elements with brand options
        selects = soup.find_all('select')
        for select in selects:
            if 'marque' in str(select).lower() or 'brand' in str(select).lower():
                options = select.find_all('option')
                for option in options:
                    brand_name = option.get_text(strip=True).upper()
                    if brand_name and len(brand_name) > 1 and brand_name != 'TOUS':
                        brands.append({
                            'name': brand_name,
                            'url': f"{self.base_url}/search?marque={brand_name}",
                            'image': f"https://referentiel.kifal.ma/imgs/brands/{brand_name}.webp",
                            'category': self.categorize_brand(brand_name)
                        })
        
        return brands
    
    def is_empty_results_page(self, soup) -> bool:
        """Check if the page shows empty results"""
        text = soup.get_text().lower()
        empty_indicators = [
            'aucun résultat', 'no results', '0 result', 'pas de résultats',
            'aucune annonce', 'no listings', 'empty', 'vide'
        ]
        return any(indicator in text for indicator in empty_indicators)
    
    def categorize_brand(self, brand_name: str) -> str:
        """Categorize brand as premium, generaliste, etc."""
        premium_brands = [
            'AUDI', 'BMW', 'MERCEDES', 'MERCEDES-BENZ', 'PORSCHE', 'LEXUS', 'INFINITI',
            'JAGUAR', 'LAND ROVER', 'VOLVO', 'ALFA ROMEO', 'MASERATI', 'BENTLEY',
            'ASTON MARTIN', 'FERRARI', 'LAMBORGHINI', 'MCLAREN', 'ROLLS-ROYCE',
            'MAYBACH', 'LOTUS', 'GENESIS', 'CADILLAC', 'LINCOLN', 'ACURA'
        ]
        
        luxury_brands = [
            'MINI', 'CUPRA', 'DS', 'ALPINE', 'LANCIA'
        ]
        
        electric_brands = ['TESLA', 'BYD', 'ZEEKR', 'AIWAYS']
        
        chinese_brands = [
            'CHANGAN', 'CHERY', 'BAIC', 'DFSK', 'GEELY', 'GWM', 
            'JAECOO', 'OMODA', 'HAVAL', 'MG', 'BORGWARD'
        ]
        
        korean_brands = ['HYUNDAI', 'KIA', 'GENESIS', 'SSANGYONG']
        
        japanese_brands = [
            'TOYOTA', 'HONDA', 'NISSAN', 'MAZDA', 'SUBARU', 'SUZUKI',
            'MITSUBISHI', 'LEXUS', 'INFINITI', 'ACURA', 'ISUZU', 'DAIHATSU'
        ]
        
        if brand_name in premium_brands:
            return 'premium'
        elif brand_name in luxury_brands:
            return 'luxury'
        elif brand_name in electric_brands:
            return 'electric'
        elif brand_name in chinese_brands:
            return 'chinese'
        elif brand_name in korean_brands:
            return 'korean'
        elif brand_name in japanese_brands:
            return 'japanese'
        else:
            return 'generaliste'
    
    async def scrape_brand_models(self, brand: Dict[str, str]) -> List[Dict[str, Any]]:
        """Scrape all models for a specific brand"""
        logger.info(f"🚗 Scraping models for {brand['name']}...")
        
        models = []
        
        # Try brand page URL
        brand_url = f"{self.base_url}/search?marque={brand['name']}"
        soup = await self.fetch_page(brand_url)
        
        if not soup:
            return models
        
        # Look for model listings
        model_elements = soup.find_all(['a', 'div'], href=True) or soup.find_all(['a', 'div'])
        
        for element in model_elements:
            model_info = self.extract_model_info(element, brand['name'])
            if model_info:
                models.append(model_info)
        
        # Also try to find models in search results
        search_url = f"{self.base_url}/search?marque={brand['name']}"
        soup = await self.fetch_page(search_url)
        
        if soup:
            # Look for car cards/listings
            car_cards = soup.find_all(['div', 'article'], class_=re.compile(r'card|item|listing|car'))
            
            for card in car_cards:
                model_info = self.extract_model_from_card(card, brand['name'])
                if model_info:
                    models.append(model_info)
        
        # Remove duplicates based on model name
        unique_models = {}
        for model in models:
            key = f"{brand['name']}_{model.get('model', '')}"
            if key not in unique_models:
                unique_models[key] = model
        
        models_list = list(unique_models.values())
        logger.info(f"✅ Found {len(models_list)} models for {brand['name']}")
        
        return models_list
    
    def extract_model_info(self, element, brand_name: str) -> Optional[Dict[str, Any]]:
        """Extract model information from HTML element"""
        try:
            # Try to get model name from text
            text = element.get_text(strip=True) if hasattr(element, 'get_text') else str(element)
            
            # Skip if it's just the brand name or too generic
            if not text or text.upper() == brand_name or len(text) < 2:
                return None
            
            # Try to get URL
            url = element.get('href') if element.get('href') else None
            if url and not url.startswith('http'):
                url = urljoin(self.base_url, url)
            
            # Try to extract price
            price_text = text
            price = self.extract_price(price_text)
            
            # Try to get image
            img = element.find('img') if hasattr(element, 'find') else None
            image_url = None
            if img and img.get('src'):
                image_url = urljoin(self.base_url, img.get('src'))
            
            # Extract model name (remove brand name if present)
            model_name = text.replace(brand_name, '').strip()
            if not model_name:
                return None
            
            return {
                'brand': brand_name,
                'model': model_name,
                'price': price,
                'url': url,
                'image': image_url,
                'raw_text': text
            }
            
        except Exception as e:
            logger.debug(f"Error extracting model info: {e}")
            return None
    
    def extract_model_from_card(self, card_element, brand_name: str) -> Optional[Dict[str, Any]]:
        """Extract model info from car card element"""
        try:
            # Get all text content
            text_content = card_element.get_text(separator=' ', strip=True)
            
            # Try to extract model name
            model_match = re.search(f'{brand_name}\\s+([^\\d]+)', text_content, re.IGNORECASE)
            model_name = model_match.group(1).strip() if model_match else None
            
            if not model_name or len(model_name) < 2:
                return None
            
            # Extract price
            price = self.extract_price(text_content)
            
            # Get URL
            link = card_element.find('a', href=True)
            url = urljoin(self.base_url, link.get('href')) if link else None
            
            # Get image
            img = card_element.find('img')
            image_url = urljoin(self.base_url, img.get('src')) if img and img.get('src') else None
            
            return {
                'brand': brand_name,
                'model': model_name,
                'price': price,
                'url': url,
                'image': image_url,
                'raw_text': text_content
            }
            
        except Exception as e:
            logger.debug(f"Error extracting from card: {e}")
            return None
    
    def extract_price(self, text: str) -> Optional[int]:
        """Extract price from text"""
        try:
            # Look for price patterns
            price_patterns = [
                r'(\d{1,3}(?:\s?\d{3})*)\s*(?:DH|MAD|Dh)',  # 123 456 DH
                r'(\d{1,3}(?:,\d{3})*)\s*(?:DH|MAD|Dh)',    # 123,456 DH
                r'(\d{3,})\s*(?:DH|MAD|Dh)',                # 123456 DH
                r'Prix\s*:?\s*(\d{1,3}(?:\s?\d{3})*)',      # Prix: 123 456
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    price_str = matches[0].replace(' ', '').replace(',', '')
                    price = int(price_str)
                    # Validate price range (50K to 5M MAD)
                    if 50000 <= price <= 5000000:
                        return price
            
        except (ValueError, AttributeError):
            pass
        
        return None
    
    async def scrape_complete_data(self) -> Dict[str, Any]:
        """Scrape complete car data from Kifal.ma"""
        logger.info("🚀 Starting comprehensive Kifal.ma data scraping...")
        
        await self.create_session()
        
        try:
            # 1. Extract brands
            brands = await self.extract_brands_from_homepage()
            self.scraped_data["brands"] = {brand["name"]: brand for brand in brands}
            
            # 2. Scrape models for each brand
            all_models = []
            
            # Scrape ALL brands - no limits!
            for brand in brands:
                models = await self.scrape_brand_models(brand)
                all_models.extend(models)
                
                # Add delay to be respectful
                await asyncio.sleep(2)
            
            # Organize models data
            self.scraped_data["models"] = {}
            self.scraped_data["cars"] = {}
            
            for model in all_models:
                brand_name = model["brand"]
                model_name = model["model"]
                
                if brand_name not in self.scraped_data["models"]:
                    self.scraped_data["models"][brand_name] = {}
                
                if model_name not in self.scraped_data["models"][brand_name]:
                    self.scraped_data["models"][brand_name][model_name] = []
                
                self.scraped_data["models"][brand_name][model_name].append(model)
            
            # Update metadata
            self.scraped_data["metadata"].update({
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_brands": len(self.scraped_data["brands"]),
                "total_models": len(all_models),
                "total_cars": sum(len(models) for brand_models in self.scraped_data["models"].values() 
                                for models in brand_models.values())
            })
            
            logger.info("✅ Scraping completed successfully!")
            logger.info(f"📊 Results: {self.scraped_data['metadata']['total_brands']} brands, "
                       f"{self.scraped_data['metadata']['total_models']} models, "
                       f"{self.scraped_data['metadata']['total_cars']} cars")
            
        finally:
            await self.close_session()
        
        return self.scraped_data
    
    def save_data(self, filename: str = "data/json/kifal_scraped_data.json"):
        """Save scraped data to JSON file"""
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Data saved to {filename}")

async def main():
    """Main scraping function"""
    scraper = KifalDataScraper()
    
    print("🚗 KIFAL.MA COMPREHENSIVE DATA SCRAPER")
    print("=" * 45)
    print("🎯 Target: https://neuf.kifal.ma/")
    print("📊 Extracting: Brands, Models, Prices, URLs")
    print()
    
    try:
        data = await scraper.scrape_complete_data()
        scraper.save_data()
        
        print(f"✅ SCRAPING COMPLETED SUCCESSFULLY!")
        print(f"📈 Statistics:")
        print(f"   🏷️  Brands: {data['metadata']['total_brands']}")
        print(f"   🚗 Models: {data['metadata']['total_models']}")
        print(f"   📋 Cars: {data['metadata']['total_cars']}")
        print(f"   💾 Saved to: data/json/kifal_scraped_data.json")
        
        return data
        
    except Exception as e:
        logger.error(f"❌ Scraping failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())