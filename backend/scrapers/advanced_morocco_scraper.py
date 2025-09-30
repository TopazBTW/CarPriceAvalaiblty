"""
Advanced Morocco Car Scraper
Scrapes specific sections for new and used cars from Moroccan automotive websites
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
import logging
from typing import Dict, List, Optional, Any
import random
from urllib.parse import urlencode, urljoin
import json
import time

logger = logging.getLogger(__name__)

class AdvancedMoroccoCarScraper:
    def __init__(self):
        self.session = None
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
        ]
        
        # Sites spécialisés avec sections dédiées neuves/occasion
        self.sites_config = {
            'avito': {
                'new_cars_url': 'https://www.avito.ma/fr/maroc/voitures_neuves',
                'used_cars_url': 'https://www.avito.ma/fr/maroc/voitures',
                'search_params': {
                    'new': {'o': '1', 'ca': '2', 'w': '3'},  # Voitures neuves
                    'used': {'o': '1', 'ca': '2'}           # Voitures d'occasion
                }
            },
            'moteur': {
                'new_cars_url': 'https://www.moteur.ma/neuf',
                'used_cars_url': 'https://www.moteur.ma/occasion',
                'search_params': {
                    'new': {'type': 'neuf'},
                    'used': {'type': 'occasion'}
                }
            },
            'autoscout24': {
                'new_cars_url': 'https://www.autoscout24.ma/lst/new',
                'used_cars_url': 'https://www.autoscout24.ma/lst/used',
                'search_params': {
                    'new': {'condition': 'new'},
                    'used': {'condition': 'used'}
                }
            },
            'wafasalaf': {
                'new_cars_url': 'https://www.wafasalaf.ma/particuliers/credit-auto/voitures-neuves',
                'used_cars_url': 'https://www.wafasalaf.ma/particuliers/credit-auto/voitures-occasion',
                'search_params': {
                    'new': {'category': 'neuf'},
                    'used': {'category': 'occasion'}
                }
            },
            'wandaloo': {
                'new_cars_url': 'https://www.wandaloo.com/voiture-neuve',
                'used_cars_url': 'https://www.wandaloo.com/voiture-occasion',
                'search_params': {
                    'new': {'type': 'neuf'},
                    'used': {'type': 'occasion'}
                }
            },
            'autodeal': {
                'new_cars_url': 'https://www.autodeal.ma/new-cars',
                'used_cars_url': 'https://www.autodeal.ma/used-cars',
                'search_params': {
                    'new': {'type': 'new'},
                    'used': {'type': 'used'}
                }
            }
        }

    async def create_session(self):
        """Create aiohttp session with proper headers"""
        if not self.session:
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=3)
            timeout = aiohttp.ClientTimeout(total=20, connect=10)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'fr,fr-FR;q=0.9,en;q=0.8,ar;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
            )

    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None

    def get_random_headers(self):
        """Get randomized headers to avoid detection"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Referer': 'https://www.google.com/',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

    async def safe_request(self, url: str, params: Dict = None) -> Optional[str]:
        """Make a safe HTTP request with error handling"""
        try:
            headers = self.get_random_headers()
            
            # Add random delay to avoid rate limiting
            await asyncio.sleep(random.uniform(1, 3))
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    content = await response.text()
                    logger.info(f"Successfully scraped {url[:50]}...")
                    return content
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
                    
        except Exception as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            return None

    def extract_price_from_text(self, text: str) -> Optional[int]:
        """Extract price from text with multiple patterns"""
        if not text:
            return None
            
        # Remove common text and normalize
        text = re.sub(r'[^\d\s,.]', ' ', text)
        text = ' '.join(text.split())
        
        # Patterns for different price formats
        patterns = [
            r'(\d{2,3})[,\s]*(\d{3})[,\s]*(\d{3})',  # 250,000 or 250 000
            r'(\d{2,3})[,\s]*(\d{3})',                # 25,000 or 25 000
            r'(\d{4,7})',                             # 250000
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    price_str = ''.join(match)
                else:
                    price_str = match
                
                try:
                    price = int(price_str)
                    # Validate price range for Moroccan market
                    if 20000 <= price <= 3000000:
                        return price
                except:
                    continue
        
        return None

    async def scrape_avito_section(self, brand: str, model: str, year: int, condition: str) -> List[Dict]:
        """Scrape Avito with dedicated new/used sections"""
        listings = []
        
        try:
            base_url = self.sites_config['avito']['new_cars_url'] if condition == "Neuf" else self.sites_config['avito']['used_cars_url']
            search_params = self.sites_config['avito']['search_params']['new' if condition == "Neuf" else 'used'].copy()
            
            # Add car-specific search parameters
            search_params.update({
                'q': f"{brand} {model}",
                'ano': year if condition == "Neuf" else None
            })
            
            # Remove None values
            search_params = {k: v for k, v in search_params.items() if v is not None}
            
            content = await self.safe_request(base_url, search_params)
            if not content:
                return listings
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Avito listing selectors
            listing_selectors = [
                '.listing-item',
                '.ads-item',
                '.classified-item',
                '[data-testid="listing-item"]'
            ]
            
            items = []
            for selector in listing_selectors:
                items = soup.select(selector)
                if items:
                    break
            
            for item in items[:10]:  # Limit to first 10 results
                try:
                    # Extract title
                    title_elem = item.select_one('h3, .title, .listing-title, [data-testid="ad-title"]')
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    
                    # Skip if not relevant
                    if not any(word.lower() in title.lower() for word in [brand.lower(), model.lower()]):
                        continue
                    
                    # Extract price
                    price_elem = item.select_one('.price, .listing-price, [data-testid="ad-price"]')
                    price_text = price_elem.get_text(strip=True) if price_elem else ""
                    price = self.extract_price_from_text(price_text)
                    
                    if price:
                        # Extract URL
                        link_elem = item.select_one('a[href]')
                        url = urljoin('https://www.avito.ma', link_elem['href']) if link_elem else ""
                        
                        listings.append({
                            'title': title,
                            'price': price,
                            'url': url,
                            'site': 'avito',
                            'condition': condition,
                            'location': 'Morocco'
                        })
                        
                except Exception as e:
                    logger.debug(f"Error parsing Avito item: {e}")
                    continue
            
            logger.info(f"Avito {condition}: Found {len(listings)} listings for {brand} {model}")
            
        except Exception as e:
            logger.error(f"Avito scraping failed: {e}")
        
        return listings

    async def scrape_moteur_section(self, brand: str, model: str, year: int, condition: str) -> List[Dict]:
        """Scrape Moteur.ma with dedicated sections"""
        listings = []
        
        try:
            base_url = self.sites_config['moteur']['new_cars_url'] if condition == "Neuf" else self.sites_config['moteur']['used_cars_url']
            search_params = self.sites_config['moteur']['search_params']['new' if condition == "Neuf" else 'used'].copy()
            
            search_params.update({
                'marque': brand.lower(),
                'modele': model.lower(),
                'annee': year if condition == "Neuf" else None
            })
            
            search_params = {k: v for k, v in search_params.items() if v is not None}
            
            content = await self.safe_request(base_url, search_params)
            if not content:
                return listings
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Moteur.ma selectors
            items = soup.select('.car-item, .vehicle-card, .listing-card, .annonce-item')
            
            for item in items[:8]:
                try:
                    title_elem = item.select_one('h3, h4, .title, .car-title')
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    
                    if not any(word.lower() in title.lower() for word in [brand.lower(), model.lower()]):
                        continue
                    
                    price_elem = item.select_one('.price, .prix, .car-price')
                    price_text = price_elem.get_text(strip=True) if price_elem else ""
                    price = self.extract_price_from_text(price_text)
                    
                    if price:
                        link_elem = item.select_one('a[href]')
                        url = urljoin('https://www.moteur.ma', link_elem['href']) if link_elem else ""
                        
                        listings.append({
                            'title': title,
                            'price': price,
                            'url': url,
                            'site': 'moteur',
                            'condition': condition,
                            'location': 'Morocco'
                        })
                        
                except Exception as e:
                    logger.debug(f"Error parsing Moteur item: {e}")
                    continue
            
            logger.info(f"Moteur {condition}: Found {len(listings)} listings for {brand} {model}")
            
        except Exception as e:
            logger.error(f"Moteur scraping failed: {e}")
        
        return listings

    async def scrape_wafasalaf_section(self, brand: str, model: str, year: int, condition: str) -> List[Dict]:
        """Scrape WafaSalaf credit auto sections"""
        listings = []
        
        try:
            base_url = self.sites_config['wafasalaf']['new_cars_url'] if condition == "Neuf" else self.sites_config['wafasalaf']['used_cars_url']
            
            content = await self.safe_request(base_url)
            if not content:
                return listings
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Look for car listings and pricing info
            items = soup.select('.car-offer, .vehicle-info, .credit-offer, .auto-card')
            
            for item in items[:5]:
                try:
                    text_content = item.get_text()
                    if brand.lower() in text_content.lower() and model.lower() in text_content.lower():
                        
                        title = f"{brand} {model} {year} ({condition})"
                        price = self.extract_price_from_text(text_content)
                        
                        if price:
                            listings.append({
                                'title': title,
                                'price': price,
                                'url': base_url,
                                'site': 'wafasalaf',
                                'condition': condition,
                                'location': 'Morocco'
                            })
                            
                except Exception as e:
                    logger.debug(f"Error parsing WafaSalaf item: {e}")
                    continue
            
            logger.info(f"WafaSalaf {condition}: Found {len(listings)} listings for {brand} {model}")
            
        except Exception as e:
            logger.error(f"WafaSalaf scraping failed: {e}")
        
        return listings

    async def get_advanced_market_data(self, brand: str, model: str, year: int, condition: str) -> Dict[str, Any]:
        """Get comprehensive market data from dedicated sections"""
        
        await self.create_session()
        
        try:
            # Run all scrapers in parallel
            tasks = [
                self.scrape_avito_section(brand, model, year, condition),
                self.scrape_moteur_section(brand, model, year, condition),
                self.scrape_wafasalaf_section(brand, model, year, condition),
                # Wandaloo doesn't have a standardized card selector, we include generic fetch
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine all listings
            all_listings = []
            sites_data = {}
            
            site_names = ['avito', 'moteur', 'wafasalaf']
            
            for i, result in enumerate(results):
                if isinstance(result, list):
                    all_listings.extend(result)
                    sites_data[site_names[i]] = {
                        'count': len(result),
                        'condition': condition
                    }
                else:
                    logger.warning(f"Scraper {site_names[i]} failed: {result}")
                    sites_data[site_names[i]] = {'count': 0, 'error': str(result)}
            
            # Calculate market statistics
            if all_listings:
                prices = [listing['price'] for listing in all_listings]
                
                new_listings = [l for l in all_listings if l['condition'] == 'Neuf']
                used_listings = [l for l in all_listings if l['condition'] == 'Occasion']
                
                market_price = int(sum(prices) / len(prices))
                
                confidence = 'high' if len(all_listings) >= 5 else 'medium' if len(all_listings) >= 2 else 'low'
                
                breakdown = {
                    'new_count': len(new_listings),
                    'used_count': len(used_listings),
                    'new_avg': int(sum(l['price'] for l in new_listings) / len(new_listings)) if new_listings else None,
                    'used_avg': int(sum(l['price'] for l in used_listings) / len(used_listings)) if used_listings else None
                }
                
                return {
                    'market_price': market_price,
                    'confidence': confidence,
                    'data_points': len(all_listings),
                    'sample_listings': sorted(all_listings, key=lambda x: x['price'])[:5],
                    'breakdown': breakdown,
                    'sites_data': sites_data,
                    'price_range': [min(prices), max(prices)],
                    'condition_specific': condition
                }
            
            else:
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

# Convenience function
async def get_advanced_morocco_prices(brand: str, model: str, year: int, condition: str) -> Dict[str, Any]:
    """
    Get advanced market data for Morocco car prices with dedicated new/used sections
    
    Args:
        brand: Car brand (e.g., 'Toyota')
        model: Car model (e.g., 'Yaris')  
        year: Car year (e.g., 2020)
        condition: Car condition ('Neuf' or 'Occasion')
    
    Returns:
        Dictionary with market data including prices, confidence, and listings
    """
    scraper = AdvancedMoroccoCarScraper()
    return await scraper.get_advanced_market_data(brand, model, year, condition)


if __name__ == "__main__":
    async def test_scraper():
        # Test the advanced scraper
        result = await get_advanced_morocco_prices("Toyota", "Yaris", 2022, "Neuf")
        print(f"New Toyota Yaris results: {result}")
        
        result2 = await get_advanced_morocco_prices("Toyota", "Yaris", 2020, "Occasion")
        print(f"Used Toyota Yaris results: {result2}")
    
    asyncio.run(test_scraper())