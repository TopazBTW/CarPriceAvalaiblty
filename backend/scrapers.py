import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional
import re
from difflib import SequenceMatcher
from urllib.parse import urljoin, quote
import time

logger = logging.getLogger(__name__)

class ScrapingError(Exception):
    """Custom exception for scraping errors"""
    pass

def similarity(a: str, b: str) -> float:
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def fuzzy_match_model(target_model: str, listing_title: str, threshold: float = 0.6) -> bool:
    """Check if the listing title contains a similar model name"""
    target_model = target_model.lower()
    listing_title = listing_title.lower()
    
    # Direct substring match
    if target_model in listing_title:
        return True
    
    # Fuzzy matching for model variations
    words = listing_title.split()
    for word in words:
        if similarity(target_model, word) >= threshold:
            return True
    
    return False

def extract_price_from_text(price_text: str) -> Optional[int]:
    """Extract numeric price from text (handles various formats)"""
    if not price_text:
        return None
    
    # Remove common currency symbols and text
    price_text = re.sub(r'[^\d\s]', '', price_text)
    price_text = re.sub(r'\s+', '', price_text)
    
    # Extract numbers
    numbers = re.findall(r'\d+', price_text)
    if numbers:
        # Join numbers and convert to int
        price_str = ''.join(numbers)
        try:
            price = int(price_str)
            # Filter reasonable car prices (10,000 to 2,000,000 MAD)
            if 10000 <= price <= 2000000:
                return price
        except ValueError:
            pass
    
    return None

async def fetch_avito_listings(brand: str, model: str, year: int, limit: int = 15) -> List[Dict]:
    """
    Scrape car listings from Avito.ma
    """
    listings = []
    
    try:
        # Construct search URL for Avito
        search_query = f"{brand} {model}"
        encoded_query = quote(search_query)
        
        # Avito search URL with filters for cars
        base_url = "https://www.avito.ma"
        search_url = f"{base_url}/fr/maroc/voitures-à_vendre?q={encoded_query}&o=1"
        
        logger.info(f"Scraping Avito: {search_url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            async with session.get(search_url) as response:
                if response.status != 200:
                    raise ScrapingError(f"Avito returned status {response.status}")
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find listing containers (Avito's structure may change)
                listing_containers = soup.find_all('div', class_=re.compile(r'listing|item|card'))
                
                if not listing_containers:
                    # Try alternative selectors
                    listing_containers = soup.find_all('a', href=re.compile(r'/\d+'))
                
                logger.info(f"Found {len(listing_containers)} potential listings")
                
                for container in listing_containers[:limit]:
                    try:
                        # Extract title
                        title_elem = container.find(['h3', 'h4', 'span'], class_=re.compile(r'title|name'))
                        if not title_elem:
                            title_elem = container.find('a', href=re.compile(r'/\d+'))
                        
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        
                        # Check if the listing matches our search criteria
                        if not fuzzy_match_model(model, title):
                            continue
                        
                        # Extract price
                        price_elem = container.find(['span', 'div'], class_=re.compile(r'price|amount'))
                        if not price_elem:
                            price_elem = container.find(string=re.compile(r'\d+.*dh|MAD', re.I))
                            if price_elem:
                                price_text = str(price_elem)
                            else:
                                continue
                        else:
                            price_text = price_elem.get_text(strip=True)
                        
                        price = extract_price_from_text(price_text)
                        if not price:
                            continue
                        
                        # Extract URL
                        link_elem = container.find('a', href=True)
                        if not link_elem:
                            if container.name == 'a' and container.get('href'):
                                link_elem = container
                            else:
                                continue
                        
                        url = link_elem.get('href')
                        if url and not url.startswith('http'):
                            url = urljoin(base_url, url)
                        
                        if not url:
                            continue
                        
                        listing = {
                            'title': title,
                            'price': price,
                            'url': url
                        }
                        
                        listings.append(listing)
                        logger.debug(f"Added listing: {title} - {price} MAD")
                        
                    except Exception as e:
                        logger.debug(f"Error parsing listing container: {e}")
                        continue
                
    except asyncio.TimeoutError:
        raise ScrapingError("Timeout while scraping Avito")
    except Exception as e:
        raise ScrapingError(f"Error scraping Avito: {str(e)}")
    
    logger.info(f"Successfully scraped {len(listings)} listings from Avito")
    return listings

async def fetch_moteur_listings(brand: str, model: str, year: int, limit: int = 15) -> List[Dict]:
    """
    Scrape car listings from Moteur.ma
    """
    listings = []
    
    try:
        # Construct search URL for Moteur.ma
        search_query = f"{brand} {model}"
        encoded_query = quote(search_query)
        
        base_url = "https://www.moteur.ma"
        search_url = f"{base_url}/fr/voiture/recherche.html?q={encoded_query}"
        
        logger.info(f"Scraping Moteur.ma: {search_url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            async with session.get(search_url) as response:
                if response.status != 200:
                    raise ScrapingError(f"Moteur.ma returned status {response.status}")
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find listing containers
                listing_containers = soup.find_all(['div', 'article'], class_=re.compile(r'car|vehicle|listing|item'))
                
                if not listing_containers:
                    # Try alternative approach
                    listing_containers = soup.find_all('a', href=re.compile(r'voiture|car'))
                
                logger.info(f"Found {len(listing_containers)} potential listings")
                
                for container in listing_containers[:limit]:
                    try:
                        # Extract title
                        title_elem = container.find(['h2', 'h3', 'h4', 'span'], class_=re.compile(r'title|name'))
                        if not title_elem:
                            title_elem = container.find('a')
                        
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        
                        # Check if the listing matches our search criteria
                        if not fuzzy_match_model(model, title):
                            continue
                        
                        # Extract price
                        price_elem = container.find(['span', 'div', 'strong'], class_=re.compile(r'price|prix|montant'))
                        if not price_elem:
                            price_text = container.get_text()
                            price_match = re.search(r'(\d+[\s\d]*)\s*(?:dh|mad|dirham)', price_text, re.I)
                            if price_match:
                                price_text = price_match.group(1)
                            else:
                                continue
                        else:
                            price_text = price_elem.get_text(strip=True)
                        
                        price = extract_price_from_text(price_text)
                        if not price:
                            continue
                        
                        # Extract URL
                        link_elem = container.find('a', href=True)
                        if not link_elem:
                            if container.name == 'a' and container.get('href'):
                                link_elem = container
                            else:
                                continue
                        
                        url = link_elem.get('href')
                        if url and not url.startswith('http'):
                            url = urljoin(base_url, url)
                        
                        if not url:
                            continue
                        
                        listing = {
                            'title': title,
                            'price': price,
                            'url': url
                        }
                        
                        listings.append(listing)
                        logger.debug(f"Added listing: {title} - {price} MAD")
                        
                    except Exception as e:
                        logger.debug(f"Error parsing listing container: {e}")
                        continue
                
    except asyncio.TimeoutError:
        raise ScrapingError("Timeout while scraping Moteur.ma")
    except Exception as e:
        raise ScrapingError(f"Error scraping Moteur.ma: {str(e)}")
    
    logger.info(f"Successfully scraped {len(listings)} listings from Moteur.ma")
    return listings

def compute_average_price(listings: List[Dict]) -> Optional[int]:
    """
    Compute average price from listings
    """
    if not listings:
        return None
    
    prices = [listing['price'] for listing in listings if listing.get('price')]
    
    if not prices:
        return None
    
    # Remove outliers (prices that are too far from median)
    prices.sort()
    n = len(prices)
    
    if n >= 3:
        # Remove extreme outliers (bottom and top 10%)
        start_idx = max(0, int(n * 0.1))
        end_idx = min(n, int(n * 0.9))
        prices = prices[start_idx:end_idx]
    
    if prices:
        average = sum(prices) / len(prices)
        return int(average)
    
    return None

# Test functions (for development/debugging)
async def test_scraping():
    """Test the scraping functions"""
    try:
        print("Testing Avito scraping...")
        avito_results = await fetch_avito_listings("Toyota", "Yaris", 2018)
        print(f"Avito results: {len(avito_results)}")
        for result in avito_results[:3]:
            print(f"  - {result}")
        
        print("\nTesting Moteur.ma scraping...")
        moteur_results = await fetch_moteur_listings("Toyota", "Yaris", 2018)
        print(f"Moteur results: {len(moteur_results)}")
        for result in moteur_results[:3]:
            print(f"  - {result}")
        
        # Test average calculation
        all_results = avito_results + moteur_results
        avg_price = compute_average_price(all_results)
        print(f"\nAverage price: {avg_price} MAD")
        
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    asyncio.run(test_scraping())