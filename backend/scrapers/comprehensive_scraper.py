import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from urllib.parse import quote, urljoin, urlparse
from typing import List, Dict, Optional, Tuple
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class MoroccanCarScraper:
    """
    Scraper complet pour tous les sites automobiles marocains
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,ar-MA;q=0.8,ar;q=0.7,en-US;q=0.6,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        
        # Configuration complète des sites marocains
        self.sites_config = [
            {
                'name': 'Avito.ma',
                'base_url': 'https://www.avito.ma',
                'search_urls': [
                    '/fr/maroc/voitures-à_vendre?q={brand}%20{model}&year_from={year_min}&year_to={year_max}',
                    '/fr/maroc/voitures-à_vendre?q={brand}%20{model}',
                    '/fr/marrakech/voitures-à_vendre?q={brand}%20{model}',
                    '/fr/casablanca/voitures-à_vendre?q={brand}%20{model}',
                    '/fr/rabat/voitures-à_vendre?q={brand}%20{model}'
                ],
                'selectors': {
                    'listings': [
                        'div[data-testid="aditem"]',
                        '.ads__list__item',
                        'div.listing-card',
                        'article[data-test-id]',
                        '.ad-item'
                    ],
                    'price': [
                        'span[aria-label*="Prix"]',
                        '.ads__list__item__price',
                        'p[data-testid*="price"]',
                        '.price',
                        'span[class*="price"]',
                        'div[class*="price"]'
                    ],
                    'title': [
                        'p[data-testid="ad-title"]',
                        '.ads__list__item__title',
                        'h3',
                        'h2',
                        '.listing-title',
                        'a[title]'
                    ],
                    'details': [
                        'div[data-testid="ad-description"]',
                        '.ads__list__item__description',
                        '.listing-details'
                    ]
                },
                'new_car_indicators': ['neuf', 'neuve', '0 km', 'garantie constructeur', 'livraison'],
                'used_car_indicators': ['occasion', 'km', 'bon état', 'très bon état']
            },
            
            {
                'name': 'Moteur.ma',
                'base_url': 'https://www.moteur.ma',
                'search_urls': [
                    '/neuf/{brand}/{model}/',
                    '/occasion/{brand}/{model}/',
                    '/voiture/{brand}-{model}',
                    '/recherche/{brand}%20{model}'
                ],
                'selectors': {
                    'listings': [
                        '.car-list .car-item',
                        '.vehicle-listing',
                        '.product-item',
                        'div[class*="car"]',
                        'article[class*="vehicle"]'
                    ],
                    'price': [
                        '.car-price',
                        '.vehicle-price',
                        '.price',
                        'span[class*="price"]',
                        '.montant'
                    ],
                    'title': [
                        '.car-title',
                        '.vehicle-title',
                        '.title',
                        'h3',
                        'h2'
                    ]
                },
                'new_car_indicators': ['neuf', 'neuve', '0 km', 'concessionnaire'],
                'used_car_indicators': ['occasion', 'km', 'particulier']
            },
            
            {
                'name': 'WafaSalaf.ma',
                'base_url': 'https://www.wafasalaf.ma',
                'search_urls': [
                    '/occasions?brand={brand}&model={model}',
                    '/neuf/{brand}/{model}',
                    '/voiture/{brand}-{model}'
                ],
                'selectors': {
                    'listings': [
                        '.car-item',
                        '.vehicle-card',
                        '.occasion-item'
                    ],
                    'price': [
                        '.price',
                        '.car-price',
                        'span[class*="prix"]'
                    ],
                    'title': [
                        '.car-title',
                        'h3',
                        '.title'
                    ]
                },
                'new_car_indicators': ['neuf', 'crédit auto'],
                'used_car_indicators': ['occasion', 'financement']
            },
            
            {
                'name': 'AutoScout24.ma',
                'base_url': 'https://www.autoscout24.ma',
                'search_urls': [
                    '/lst/{brand}/{model}',
                    '/cars/{brand}-{model}'
                ],
                'selectors': {
                    'listings': ['.listing-item', '.car-card'],
                    'price': ['.price-primary', '.price'],
                    'title': ['.listing-title', 'h3']
                },
                'new_car_indicators': ['neuf'],
                'used_car_indicators': ['occasion', 'used']
            },
            
            {
                'name': 'Tayara.tn (Maroc)',
                'base_url': 'https://www.tayara.tn',
                'search_urls': [
                    '/ads/c/Voitures?q={brand}%20{model}',
                    '/voitures/{brand}-{model}'
                ],
                'selectors': {
                    'listings': ['.announcement-card', '.ad-card'],
                    'price': ['.price', '.announcement-price'],
                    'title': ['.announcement-title', '.title']
                },
                'new_car_indicators': ['neuf', 'jamais utilisé'],
                'used_car_indicators': ['occasion', 'utilisé']
            },
            
            {
                'name': 'AutoDeal.ma',
                'base_url': 'https://autodeal.ma',
                'search_urls': [
                    '/voitures/{brand}/{model}',
                    '/search?q={brand}+{model}'
                ],
                'selectors': {
                    'listings': ['.car-listing', '.vehicle-item'],
                    'price': ['.listing-price', '.price'],
                    'title': ['.listing-title', 'h2']
                },
                'new_car_indicators': ['neuf', 'dealer'],
                'used_car_indicators': ['occasion', 'pre-owned']
            }
        ]
    
    async def scrape_all_sites(self, brand: str, model: str, year: int, condition: str = "all") -> Dict:
        """
        Scrape tous les sites marocains pour un modèle donné
        """
        all_listings = []
        new_car_listings = []
        used_car_listings = []
        site_results = {}
        
        timeout = aiohttp.ClientTimeout(total=45)
        
        async with aiohttp.ClientSession(timeout=timeout, headers=self.headers) as session:
            
            tasks = []
            for site_config in self.sites_config:
                task = self._scrape_single_site(session, site_config, brand, model, year)
                tasks.append(task)
            
            # Exécuter tous les scraping en parallèle
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                site_name = self.sites_config[i]['name']
                
                if isinstance(result, Exception):
                    logger.error(f"Error scraping {site_name}: {result}")
                    site_results[site_name] = {'count': 0, 'listings': []}
                    continue
                
                site_listings = result
                site_results[site_name] = {
                    'count': len(site_listings),
                    'listings': site_listings[:3]  # Garder les 3 meilleurs
                }
                
                for listing in site_listings:
                    all_listings.append(listing)
                    
                    if listing['condition'] == 'Neuf':
                        new_car_listings.append(listing)
                    else:
                        used_car_listings.append(listing)
        
        # Analyse des résultats
        analysis = self._analyze_listings(all_listings, new_car_listings, used_car_listings)
        
        result = {
            'total_listings': len(all_listings),
            'new_car_count': len(new_car_listings),
            'used_car_count': len(used_car_listings),
            'sites_scraped': len([s for s in site_results.values() if s['count'] > 0]),
            'site_breakdown': site_results,
            **analysis,
            'timestamp': datetime.now().isoformat(),
            'search_params': {
                'brand': brand,
                'model': model,
                'year': year,
                'condition': condition
            }
        }
        
        logger.info(f"Scraping complete: {result['total_listings']} total listings "
                   f"({result['new_car_count']} new, {result['used_car_count']} used) "
                   f"from {result['sites_scraped']} sites")
        
        return result
    
    async def _scrape_single_site(self, session: aiohttp.ClientSession, site_config: Dict, 
                                 brand: str, model: str, year: int) -> List[Dict]:
        """
        Scrape un seul site
        """
        listings = []
        site_name = site_config['name']
        
        try:
            for search_url_template in site_config['search_urls']:
                try:
                    # Construire l'URL de recherche
                    search_url = search_url_template.format(
                        brand=self._clean_brand(brand),
                        model=self._clean_model(model),
                        year_min=max(2010, year - 3),
                        year_max=year + 1
                    )
                    
                    full_url = urljoin(site_config['base_url'], search_url)
                    
                    await asyncio.sleep(1)  # Délai respectueux
                    
                    async with session.get(full_url) as response:
                        if response.status != 200:
                            logger.debug(f"{site_name} returned {response.status} for {search_url}")
                            continue
                        
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Trouver les listings avec plusieurs sélecteurs
                        listing_containers = []
                        for selector in site_config['selectors']['listings']:
                            containers = soup.select(selector)
                            if containers:
                                listing_containers.extend(containers)
                                break
                        
                        if not listing_containers:
                            logger.debug(f"No listings found on {site_name} with URL {search_url}")
                            continue
                        
                        logger.info(f"Found {len(listing_containers)} potential listings on {site_name}")
                        
                        # Parser chaque listing
                        for container in listing_containers[:15]:  # Limiter à 15 par URL
                            listing = self._parse_listing(container, site_config, site_name)
                            if listing and self._validate_listing(listing, brand, model, year):
                                listings.append(listing)
                        
                        if listings:
                            break  # Arrêter si on a trouvé des listings
                            
                except Exception as e:
                    logger.debug(f"Error with search URL {search_url} on {site_name}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Critical error scraping {site_name}: {e}")
        
        return listings[:10]  # Retourner max 10 listings par site
    
    def _parse_listing(self, container, site_config: Dict, site_name: str) -> Optional[Dict]:
        """
        Parser un listing individuel
        """
        try:
            # Extraire le titre
            title = None
            for selector in site_config['selectors']['title']:
                title_elem = container.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if not title:
                        title = title_elem.get('title', '').strip()
                    if title:
                        break
            
            if not title:
                return None
            
            # Extraire le prix
            price = None
            for selector in site_config['selectors']['price']:
                price_elem = container.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price = self._extract_price(price_text)
                    if price:
                        break
            
            if not price:
                # Chercher le prix dans tout le texte du container
                all_text = container.get_text()
                price = self._extract_price(all_text)
            
            if not price or price < 20000 or price > 3000000:
                return None
            
            # Déterminer la condition
            condition = self._determine_condition(
                title, price, site_config['new_car_indicators'], 
                site_config['used_car_indicators']
            )
            
            # Extraire l'URL si possible
            link_elem = container.find('a', href=True)
            url = None
            if link_elem:
                url = link_elem.get('href')
                if url and not url.startswith('http'):
                    url = urljoin(site_config['base_url'], url)
            
            if not url:
                url = f"{site_config['base_url']}/search?q={title.replace(' ', '+')}"
            
            return {
                'title': title,
                'price': price,
                'condition': condition,
                'source': site_name,
                'url': url,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.debug(f"Error parsing listing from {site_name}: {e}")
            return None
    
    def _extract_price(self, text: str) -> Optional[int]:
        """
        Extraire le prix du texte
        """
        if not text:
            return None
        
        # Nettoyer le texte
        text = re.sub(r'[^\d\s]', ' ', text)  # Garder seulement chiffres et espaces
        
        # Patterns pour différents formats de prix
        patterns = [
            r'(\d{6,7})',  # 6-7 chiffres (ex: 150000, 1500000)
            r'(\d{2,3})\s*(\d{3})',  # Format avec espace (ex: 150 000)
            r'(\d+)',  # Tout nombre
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    if isinstance(match, tuple):
                        # Recombiner les parties
                        price_str = ''.join(match)
                    else:
                        price_str = match
                    
                    price = int(price_str)
                    
                    # Valider la plage de prix
                    if 20000 <= price <= 3000000:
                        return price
                        
                except ValueError:
                    continue
        
        return None
    
    def _determine_condition(self, title: str, price: int, new_indicators: List[str], 
                           used_indicators: List[str]) -> str:
        """
        Déterminer si c'est neuf ou occasion
        """
        title_lower = title.lower()
        
        # Score pour nouveau
        new_score = sum(1 for indicator in new_indicators if indicator in title_lower)
        used_score = sum(1 for indicator in used_indicators if indicator in title_lower)
        
        # Facteurs de prix (les voitures neuves sont généralement plus chères)
        if price > 200000:
            new_score += 1
        if price < 100000:
            used_score += 1
        
        return 'Neuf' if new_score > used_score else 'Occasion'
    
    def _validate_listing(self, listing: Dict, target_brand: str, target_model: str, target_year: int) -> bool:
        """
        Valider qu'un listing correspond aux critères de recherche
        """
        title = listing['title'].lower()
        target_brand_lower = target_brand.lower()
        target_model_lower = target_model.lower()
        
        # Vérifier que la marque est mentionnée
        brand_variations = {
            'toyota': ['toyota', 'toyta'],
            'peugeot': ['peugeot', 'peugot'],
            'renault': ['renault', 'renaul'],
            'dacia': ['dacia', 'dasia'],
            'hyundai': ['hyundai', 'hundai'],
            'kia': ['kia'],
            'volkswagen': ['volkswagen', 'vw', 'volks'],
            'ford': ['ford']
        }
        
        brand_found = False
        for variation in brand_variations.get(target_brand_lower, [target_brand_lower]):
            if variation in title:
                brand_found = True
                break
        
        if not brand_found:
            return False
        
        # Vérifier le modèle avec variations
        model_variations = {
            'yaris': ['yaris'],
            'corolla': ['corolla'],
            'rav4': ['rav4', 'rav 4', 'rav-4'],
            'camry': ['camry'],
            'land cruiser': ['land cruiser', 'landcruiser', 'lc'],
            '208': ['208'],
            '308': ['308'],
            '2008': ['2008'],
            '3008': ['3008'],
            'clio': ['clio'],
            'megane': ['megane', 'mégane'],
            'captur': ['captur'],
            'sandero': ['sandero'],
            'logan': ['logan'],
            'duster': ['duster']
        }
        
        model_found = False
        for variation in model_variations.get(target_model_lower, [target_model_lower]):
            if variation in title:
                model_found = True
                break
        
        return model_found
    
    def _analyze_listings(self, all_listings: List[Dict], new_listings: List[Dict], 
                         used_listings: List[Dict]) -> Dict:
        """
        Analyser les listings récupérés
        """
        if not all_listings:
            return {
                'new_avg_price': None,
                'used_avg_price': None,
                'overall_avg_price': None,
                'price_range': None,
                'best_listings': []
            }
        
        # Calculer les moyennes
        new_avg = self._calculate_trimmed_average([l['price'] for l in new_listings]) if new_listings else None
        used_avg = self._calculate_trimmed_average([l['price'] for l in used_listings]) if used_listings else None
        overall_avg = self._calculate_trimmed_average([l['price'] for l in all_listings])
        
        # Fourchette de prix
        prices = [l['price'] for l in all_listings]
        price_range = [min(prices), max(prices)]
        
        # Meilleurs listings (triés par pertinence)
        best_listings = sorted(all_listings, key=lambda x: x['price'])[:6]
        
        return {
            'new_avg_price': new_avg,
            'used_avg_price': used_avg,
            'overall_avg_price': overall_avg,
            'price_range': price_range,
            'best_listings': best_listings
        }
    
    def _calculate_trimmed_average(self, prices: List[int]) -> int:
        """
        Calculer la moyenne en excluant les valeurs aberrantes
        """
        if not prices:
            return 0
        
        if len(prices) <= 2:
            return sum(prices) // len(prices)
        
        # Trier et exclure 20% des extrêmes
        sorted_prices = sorted(prices)
        trim_count = max(1, len(sorted_prices) // 5)
        
        if trim_count * 2 >= len(sorted_prices):
            return sum(sorted_prices) // len(sorted_prices)
        
        trimmed = sorted_prices[trim_count:-trim_count]
        return sum(trimmed) // len(trimmed)
    
    def _clean_brand(self, brand: str) -> str:
        """Nettoyer le nom de marque pour les URLs"""
        return brand.lower().replace(' ', '-')
    
    def _clean_model(self, model: str) -> str:
        """Nettoyer le nom de modèle pour les URLs"""
        return model.lower().replace(' ', '-')


# Interface principale
async def get_comprehensive_morocco_prices(brand: str, model: str, year: int, condition: str = "all") -> Dict:
    """
    Interface principale pour obtenir tous les prix du marché marocain
    """
    scraper = MoroccanCarScraper()
    
    try:
        results = await scraper.scrape_all_sites(brand, model, year, condition)
        
        # Sélectionner le prix approprié selon la condition demandée
        if condition.lower() == "neuf" and results['new_avg_price']:
            market_price = results['new_avg_price']
            confidence = 'high' if results['new_car_count'] >= 5 else 'medium'
        elif condition.lower() == "occasion" and results['used_avg_price']:
            market_price = results['used_avg_price']
            confidence = 'high' if results['used_car_count'] >= 5 else 'medium'
        else:
            market_price = results['overall_avg_price']
            confidence = 'medium' if results['total_listings'] >= 3 else 'low'
        
        return {
            'market_price': market_price,
            'confidence': confidence,
            'data_points': results['total_listings'],
            'price_range': results['price_range'],
            'sample_listings': results['best_listings'][:5],
            'breakdown': {
                'new_count': results['new_car_count'],
                'used_count': results['used_car_count'],
                'new_avg': results['new_avg_price'],
                'used_avg': results['used_avg_price']
            },
            'sites_data': results['site_breakdown']
        }
        
    except Exception as e:
        logger.error(f"Comprehensive scraping failed: {e}")
        return {
            'market_price': None,
            'confidence': 'none',
            'data_points': 0,
            'price_range': None,
            'sample_listings': [],
            'breakdown': {'new_count': 0, 'used_count': 0, 'new_avg': None, 'used_avg': None},
            'sites_data': {}
        }