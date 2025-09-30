import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from urllib.parse import quote, urljoin
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

async def scrape_real_morocco_prices(brand: str, model: str, year: int) -> Dict[str, any]:
    """
    Scraper avancé pour obtenir les vrais prix du marché marocain
    """
    
    # Sites marocains pour le scraping de prix
    sites_config = [
        {
            'name': 'Avito.ma',
            'base_url': 'https://www.avito.ma',
            'search_url': 'https://www.avito.ma/fr/maroc/voitures-à_vendre?q={brand}%20{model}&year_from={year}&year_to={year_max}',
            'selectors': {
                'listings': '.ads__list .ads__list__item, .listing-card',
                'price': '.ads__list__item__price, .price',
                'title': '.ads__list__item__title, .listing-title',
                'year': '.ads__list__item__properties, .listing-properties'
            }
        },
        {
            'name': 'Moteur.ma',
            'base_url': 'https://www.moteur.ma',
            'search_url': 'https://www.moteur.ma/neuf/{brand}/{model}/',
            'selectors': {
                'listings': '.car-list .car-item, .vehicle-listing',
                'price': '.car-price, .vehicle-price',
                'title': '.car-title, .vehicle-title',
            }
        },
        {
            'name': 'Automobile.tn (Maroc)',
            'base_url': 'https://www.automobile.tn',
            'search_url': 'https://www.automobile.tn/neuf/{brand}-{model}',
            'selectors': {
                'listings': '.car-item, .vehicle-card',
                'price': '.price, .car-price',
                'title': '.title, .car-title',
            }
        }
    ]
    
    all_prices = []
    new_car_prices = []
    used_car_prices = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,ar-MA;q=0.8,ar;q=0.7,en;q=0.6',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        
        for site in sites_config:
            try:
                logger.info(f"Scraping prices from {site['name']} for {brand} {model} {year}")
                
                # Construire l'URL de recherche
                search_url = site['search_url'].format(
                    brand=brand.lower(),
                    model=model.lower().replace(' ', '-'),
                    year=year,
                    year_max=year + 1
                )
                
                await asyncio.sleep(2)  # Délai respectueux
                
                async with session.get(urljoin(site['base_url'], search_url)) as response:
                    if response.status != 200:
                        logger.warning(f"{site['name']} returned status {response.status}")
                        continue
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Trouver les listings
                    listings = soup.select(site['selectors']['listings'])
                    
                    for listing in listings[:10]:  # Limiter à 10 résultats par site
                        try:
                            # Extraire le prix
                            price_elem = listing.select_one(site['selectors']['price'])
                            if not price_elem:
                                continue
                                
                            price_text = price_elem.get_text(strip=True)
                            price = extract_price_from_text(price_text)
                            
                            if not price or price < 10000 or price > 2000000:
                                continue
                            
                            # Extraire le titre pour vérification
                            title_elem = listing.select_one(site['selectors']['title'])
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                                
                                # Vérifier que c'est le bon modèle
                                if not fuzzy_match_model(model, title):
                                    continue
                                
                                all_prices.append({
                                    'price': price,
                                    'title': title,
                                    'source': site['name'],
                                    'condition': determine_condition(title, price, year)
                                })
                                
                                # Classifier nouveau vs occasion
                                if is_likely_new_car(title, price, year):
                                    new_car_prices.append(price)
                                else:
                                    used_car_prices.append(price)
                                    
                        except Exception as e:
                            logger.debug(f"Error parsing listing from {site['name']}: {e}")
                            continue
                            
            except Exception as e:
                logger.warning(f"Error scraping {site['name']}: {e}")
                continue
    
    # Analyse des prix
    result = {
        'total_listings': len(all_prices),
        'new_car_avg': calculate_average(new_car_prices) if new_car_prices else None,
        'used_car_avg': calculate_average(used_car_prices) if used_car_prices else None,
        'overall_avg': calculate_average([p['price'] for p in all_prices]) if all_prices else None,
        'price_range': [min([p['price'] for p in all_prices]), max([p['price'] for p in all_prices])] if all_prices else None,
        'listings_sample': all_prices[:5],  # Échantillon des 5 premiers
        'new_count': len(new_car_prices),
        'used_count': len(used_car_prices)
    }
    
    logger.info(f"Scraping summary: {result['total_listings']} listings found, {result['new_count']} new, {result['used_count']} used")
    
    return result


def extract_price_from_text(text: str) -> Optional[int]:
    """Extrait le prix d'un texte en dirhams marocains"""
    if not text:
        return None
    
    # Nettoyer le texte
    text = text.replace(',', '').replace(' ', '').replace('.', '')
    
    # Patterns pour les prix en MAD/DH
    patterns = [
        r'(\d+)(?:\s*(?:dh|mad|dirham))',  # 150000 DH
        r'(\d+)',  # Juste le nombre si c'est le seul
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            try:
                price = int(match.group(1))
                # Valider la plage de prix raisonnable
                if 10000 <= price <= 2000000:
                    return price
            except ValueError:
                continue
    
    return None


def fuzzy_match_model(target_model: str, title: str) -> bool:
    """Vérification floue pour voir si le titre correspond au modèle recherché"""
    target_lower = target_model.lower()
    title_lower = title.lower()
    
    # Correspondance exacte
    if target_lower in title_lower:
        return True
    
    # Correspondance avec variations
    variations = {
        'yaris': ['yaris', 'yaris cross'],
        'corolla': ['corolla', 'corolla cross'],
        'rav4': ['rav4', 'rav 4', 'rav-4'],
        'land cruiser': ['land cruiser', 'landcruiser', 'lc'],
        'camry': ['camry'],
        '208': ['208', 'deux cent huit'],
        '308': ['308', 'trois cent huit'],
        '2008': ['2008', 'deux mille huit'],
        '3008': ['3008', 'trois mille huit'],
    }
    
    model_variations = variations.get(target_lower, [target_lower])
    
    for variation in model_variations:
        if variation in title_lower:
            return True
    
    return False


def is_likely_new_car(title: str, price: int, target_year: int) -> bool:
    """Détermine si c'est probablement une voiture neuve"""
    title_lower = title.lower()
    
    # Indicateurs de voiture neuve
    new_indicators = ['neuf', 'neuve', '0 km', 'livraison', 'concessionnaire', 'garantie constructeur']
    used_indicators = ['occasion', 'km', 'propriétaire', 'bon état']
    
    new_score = sum(1 for indicator in new_indicators if indicator in title_lower)
    used_score = sum(1 for indicator in used_indicators if indicator in title_lower)
    
    # Si c'est l'année courante ou précédente avec un prix élevé
    current_year = 2024
    if target_year >= current_year - 1 and price > 150000:
        new_score += 2
    
    return new_score > used_score


def determine_condition(title: str, price: int, year: int) -> str:
    """Détermine l'état du véhicule"""
    if is_likely_new_car(title, price, year):
        return 'Neuf'
    else:
        return 'Occasion'


def calculate_average(prices: List[int]) -> int:
    """Calcule la moyenne en excluant les valeurs aberrantes"""
    if not prices:
        return 0
    
    if len(prices) < 3:
        return sum(prices) // len(prices)
    
    # Exclure les 10% des valeurs les plus hautes et les plus basses
    sorted_prices = sorted(prices)
    trim_count = max(1, len(sorted_prices) // 10)
    
    trimmed_prices = sorted_prices[trim_count:-trim_count] if trim_count < len(sorted_prices)//2 else sorted_prices
    
    return sum(trimmed_prices) // len(trimmed_prices)


async def get_enhanced_market_data(brand: str, model: str, year: int, condition: str = 'Occasion') -> Dict:
    """
    Interface principale pour obtenir les données de marché améliorées
    """
    try:
        market_data = await scrape_real_morocco_prices(brand, model, year)
        
        # Sélectionner le prix approprié selon la condition
        if condition == 'Neuf' and market_data['new_car_avg']:
            estimated_price = market_data['new_car_avg']
            confidence = 'high' if market_data['new_count'] >= 3 else 'medium'
        elif condition == 'Occasion' and market_data['used_car_avg']:
            estimated_price = market_data['used_car_avg']
            confidence = 'high' if market_data['used_count'] >= 3 else 'medium'
        else:
            estimated_price = market_data['overall_avg']
            confidence = 'medium' if market_data['total_listings'] >= 2 else 'low'
        
        return {
            'market_price': estimated_price,
            'confidence': confidence,
            'data_points': market_data['total_listings'],
            'price_range': market_data['price_range'],
            'sample_listings': market_data['listings_sample']
        }
        
    except Exception as e:
        logger.error(f"Error getting enhanced market data: {e}")
        return {
            'market_price': None,
            'confidence': 'none',
            'data_points': 0,
            'price_range': None,
            'sample_listings': []
        }