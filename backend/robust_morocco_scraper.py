"""
Enhanced Morocco Car Scraper with better anti-scraping protection
Focuses on reliable Moroccan car sites with dedicated new/used sections
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
import logging
from typing import Dict, List, Optional, Any
import random
from urllib.parse import urlencode, urljoin, quote
import json
import ssl
import certifi

logger = logging.getLogger(__name__)

class RobustMoroccoCarScraper:
    def __init__(self):
        self.session = None
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        # Focus on more reliable Moroccan car sites
        self.sites_config = {
            'sarouty': {
                'new_cars_url': 'https://sarouty.ma/cars/new',
                'used_cars_url': 'https://sarouty.ma/cars/used',
                'enabled': True
            },
            'automobile': {
                'new_cars_url': 'https://www.automobile.ma/voiture-neuve',
                'used_cars_url': 'https://www.automobile.ma/voiture-occasion', 
                'enabled': True
            },
            'tayara': {
                'new_cars_url': 'https://www.tayara.tn/sc/Voitures-neuves/c/Voitures',
                'used_cars_url': 'https://www.tayara.tn/sc/Voitures/c/Voitures',
                'enabled': True
            },
            'wandaloo': {
                'new_cars_url': 'https://www.wandaloo.com/voiture-neuve',
                'used_cars_url': 'https://www.wandaloo.com/voiture-occasion',
                'enabled': True
            },
            'openroads': {
                'new_cars_url': 'https://openroads.ma/new-cars',
                'used_cars_url': 'https://openroads.ma/used-cars',
                'enabled': True
            }
        }

    async def create_robust_session(self):
        """Create a robust aiohttp session that handles various encoding issues"""
        if not self.session:
            # Create SSL context that's more permissive
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Create connector with proper settings
            connector = aiohttp.TCPConnector(
                limit=5,
                limit_per_host=2,
                ssl=ssl_context,
                force_close=True,
                enable_cleanup_closed=True
            )
            
            timeout = aiohttp.ClientTimeout(total=15, connect=8)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'fr,fr-FR;q=0.9,en;q=0.8,ar;q=0.7',
                    'Accept-Encoding': 'gzip, deflate',  # Avoid brotli
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none'
                }
            )

    async def close_session(self):
        """Close aiohttp session safely"""
        if self.session:
            await self.session.close()
            await asyncio.sleep(0.1)  # Give time for cleanup
            self.session = None

    def get_enhanced_headers(self):
        """Get enhanced headers to bypass detection"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Referer': random.choice([
                'https://www.google.co.ma/',
                'https://www.google.com/',
                'https://www.facebook.com/',
                ''
            ]),
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }

    def extract_price_patterns(self, text: str) -> Optional[int]:
        """Enhanced price extraction with Morocco-specific patterns"""
        if not text:
            return None
            
        # Clean and normalize text
        text = re.sub(r'[^\d\s,.\-dh mad]', ' ', text.lower())
        text = ' '.join(text.split())
        
        # Morocco-specific price patterns
        patterns = [
            r'(\d{2,3})[,\s]*(\d{3})[,\s]*(\d{3})',  # 250,000 format
            r'(\d{2,3})[,\s\.]*(\d{3})',             # 25,000 format  
            r'(\d{4,7})(?:\s*(?:dh|mad|dirham))?',   # 250000 MAD
            r'(?:prix|price)[:\s]*(\d{4,7})',        # Prix: 250000
            r'(\d{2,3})\s*k(?:\s*(?:dh|mad))?',      # 250K format
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    if isinstance(match, tuple):
                        if len(match) == 3:
                            price_str = ''.join(match)
                        elif len(match) == 2:
                            price_str = ''.join(match)
                        else:
                            price_str = match[0]
                    else:
                        price_str = match
                    
                    price = int(price_str)
                    
                    # Handle K format (multiply by 1000)
                    if 'k' in text.lower() and price < 1000:
                        price *= 1000
                    
                    # Validate for Moroccan market (20K to 3M MAD)
                    if 20000 <= price <= 3000000:
                        return price
                        
                except (ValueError, TypeError):
                    continue
        
        return None

    async def safe_fetch(self, url: str, params: Dict = None, max_retries: int = 2) -> Optional[str]:
        """Robust HTTP request with retries and error handling"""
        for attempt in range(max_retries + 1):
            try:
                headers = self.get_enhanced_headers()
                
                # Add random delay to avoid rate limiting
                await asyncio.sleep(random.uniform(1.5, 4))
                
                async with self.session.get(url, params=params, headers=headers, allow_redirects=True) as response:
                    if response.status == 200:
                        try:
                            content = await response.text(encoding='utf-8')
                        except UnicodeDecodeError:
                            # Fallback to latin-1 if UTF-8 fails
                            content = await response.text(encoding='latin-1')
                        
                        logger.info(f"Successfully fetched {url[:60]}... (attempt {attempt + 1})")
                        return content
                    
                    elif response.status in [403, 429]:
                        logger.warning(f"Rate limited {url} (status {response.status}), attempt {attempt + 1}")
                        if attempt < max_retries:
                            await asyncio.sleep(random.uniform(5, 10))
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout for {url}, attempt {attempt + 1}")
                if attempt < max_retries:
                    await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Request failed for {url}: {str(e)[:100]}")
                if attempt < max_retries:
                    await asyncio.sleep(1)
        
        return None

    async def scrape_generic_site(self, base_url: str, brand: str, model: str, year: int, condition: str, site_name: str) -> List[Dict]:
        """Generic scraper for Moroccan car sites"""
        listings = []
        
        try:
            # Build search URL with parameters
            search_terms = f"{brand} {model}".strip()
            params = {
                'q': search_terms,
                'search': search_terms,
                'keyword': search_terms,
                'marque': brand.lower(),
                'model': model.lower(),
                'brand': brand.lower(),
                'year': year if condition == "Neuf" else None,
                'annee': year if condition == "Neuf" else None,
                'condition': 'new' if condition == "Neuf" else 'used',
                'type': 'neuf' if condition == "Neuf" else 'occasion'
            }
            
            # Filter out None values
            params = {k: v for k, v in params.items() if v is not None}
            
            content = await self.safe_fetch(base_url, params)
            if not content:
                return listings
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Generic selectors for car listings
            listing_selectors = [
                '.car-item', '.vehicle-item', '.listing-item', '.ad-item', '.product-item',
                '.car-card', '.vehicle-card', '.listing-card', '.ad-card', '.product-card',
                '.annonce', '.classified', '.offer', '.deal',
                '[data-testid*="listing"]', '[data-testid*="car"]', '[data-testid*="ad"]'
            ]
            
            items = []
            for selector in listing_selectors:
                items = soup.select(selector)
                if items:
                    logger.info(f"Found {len(items)} items with selector '{selector}' on {site_name}")
                    break
            
            # If no items found with specific selectors, try broader search
            if not items:
                items = soup.select('div[class*="car"], div[class*="vehicle"], div[class*="listing"], div[class*="ad"]')[:20]
                if items:
                    logger.info(f"Found {len(items)} items with broad selectors on {site_name}")
            
            for item in items[:12]:  # Limit results
                try:
                    item_text = item.get_text(separator=' ', strip=True).lower()
                    
                    # Check if item is relevant
                    brand_match = brand.lower() in item_text
                    model_match = model.lower() in item_text
                    
                    if not (brand_match or model_match):
                        continue
                    
                    # Extract title
                    title_selectors = [
                        'h1', 'h2', 'h3', 'h4', '.title', '.heading', '.name', '.car-title',
                        '.vehicle-title', '.listing-title', '.ad-title', '.product-title'
                    ]
                    
                    title = ""
                    for sel in title_selectors:
                        title_elem = item.select_one(sel)
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            break
                    
                    if not title:
                        # Fallback: use first line of text
                        lines = item_text.split('\n')
                        title = lines[0][:100] if lines else f"{brand} {model} {year}"
                    
                    # Extract price
                    price_selectors = [
                        '.price', '.prix', '.cost', '.amount', '.value', '.car-price',
                        '.vehicle-price', '.listing-price', '.ad-price', '.product-price',
                        '[class*="price"]', '[class*="prix"]', '[data-testid*="price"]'
                    ]
                    
                    price = None
                    for sel in price_selectors:
                        price_elem = item.select_one(sel)
                        if price_elem:
                            price_text = price_elem.get_text(strip=True)
                            price = self.extract_price_patterns(price_text)
                            if price:
                                break
                    
                    # If no specific price element, search in all text
                    if not price:
                        price = self.extract_price_patterns(item_text)
                    
                    if price:
                        # Extract URL
                        link_elem = item.select_one('a[href]')
                        url = ""
                        if link_elem and link_elem.get('href'):
                            href = link_elem['href']
                            if href.startswith('http'):
                                url = href
                            else:
                                url = urljoin(base_url, href)
                        else:
                            url = base_url
                        
                        listings.append({
                            'title': title,
                            'price': price,
                            'url': url,
                            'site': site_name,
                            'condition': condition,
                            'location': 'Morocco'
                        })
                        
                except Exception as e:
                    logger.debug(f"Error parsing item on {site_name}: {e}")
                    continue
            
            logger.info(f"{site_name} {condition}: Found {len(listings)} relevant listings")
            
        except Exception as e:
            logger.error(f"{site_name} scraping failed: {e}")
        
        return listings

    async def get_robust_market_data(self, brand: str, model: str, year: int, condition: str) -> Dict[str, Any]:
        """Get market data using robust scraping methods"""
        
        await self.create_robust_session()
        
        try:
            tasks = []
            
            # Create scraping tasks for enabled sites
            for site_name, config in self.sites_config.items():
                if not config.get('enabled', True):
                    continue
                
                base_url = config['new_cars_url'] if condition == "Neuf" else config['used_cars_url']
                
                task = self.scrape_generic_site(base_url, brand, model, year, condition, site_name)
                tasks.append(task)
            
            # Execute all scraping tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            all_listings = []
            sites_data = {}
            
            for i, result in enumerate(results):
                site_name = list(self.sites_config.keys())[i]
                
                if isinstance(result, list):
                    all_listings.extend(result)
                    sites_data[site_name] = {
                        'count': len(result),
                        'condition': condition,
                        'status': 'success'
                    }
                else:
                    logger.warning(f"Site {site_name} failed: {result}")
                    sites_data[site_name] = {
                        'count': 0,
                        'error': str(result),
                        'status': 'failed'
                    }
            
            # Calculate market statistics
            if all_listings:
                prices = [listing['price'] for listing in all_listings]
                
                # Remove outliers (prices that are way off)
                sorted_prices = sorted(prices)
                q1 = sorted_prices[len(sorted_prices)//4]
                q3 = sorted_prices[3*len(sorted_prices)//4]
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                filtered_prices = [p for p in prices if lower_bound <= p <= upper_bound]
                
                if filtered_prices:
                    market_price = int(sum(filtered_prices) / len(filtered_prices))
                    
                    confidence = ('high' if len(all_listings) >= 4 
                                else 'medium' if len(all_listings) >= 2 
                                else 'low')
                    
                    return {
                        'market_price': market_price,
                        'confidence': confidence,
                        'data_points': len(all_listings),
                        'sample_listings': sorted(all_listings, key=lambda x: x['price'])[:5],
                        'breakdown': {
                            'new_count': len([l for l in all_listings if l['condition'] == 'Neuf']),
                            'used_count': len([l for l in all_listings if l['condition'] == 'Occasion']),
                            'new_avg': None,
                            'used_avg': None
                        },
                        'sites_data': sites_data,
                        'price_range': [min(filtered_prices), max(filtered_prices)],
                        'condition_specific': condition,
                        'outliers_removed': len(prices) - len(filtered_prices)
                    }
            
            return {
                'market_price': None,
                'confidence': 'none',
                'data_points': 0,
                'sample_listings': [],
                'breakdown': {'new_count': 0, 'used_count': 0, 'new_avg': None, 'used_avg': None},
                'sites_data': sites_data,
                'condition_specific': condition
            }
                
        finally:
            await self.close_session()

# Main function for external use
async def get_robust_morocco_prices(brand: str, model: str, year: int, condition: str) -> Dict[str, Any]:
    """
    Get robust market data for Morocco cars with enhanced anti-scraping protection
    
    Args:
        brand: Car brand (e.g., 'Toyota')
        model: Car model (e.g., 'Yaris')
        year: Car year (e.g., 2020) 
        condition: Car condition ('Neuf' or 'Occasion')
    
    Returns:
        Dictionary with market data, prices, and listings
    """
    scraper = RobustMoroccoCarScraper()
    return await scraper.get_robust_market_data(brand, model, year, condition)


if __name__ == "__main__":
    async def test_robust_scraper():
        print("Testing Robust Morocco Car Scraper...")
        
        # Test new car
        result1 = await get_robust_morocco_prices("Toyota", "Yaris", 2023, "Neuf")
        print(f"New Toyota Yaris: {result1['data_points']} listings, avg: {result1['market_price']}")
        
        # Test used car  
        result2 = await get_robust_morocco_prices("Toyota", "Yaris", 2020, "Occasion")
        print(f"Used Toyota Yaris: {result2['data_points']} listings, avg: {result2['market_price']}")
    
    asyncio.run(test_robust_scraper())