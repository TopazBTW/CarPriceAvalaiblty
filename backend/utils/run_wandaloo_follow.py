import asyncio
import json
import re
from collections import OrderedDict
from urllib.parse import urljoin
import aiohttp
from bs4 import BeautifulSoup
from wandaloo_scraper import fetch_wandaloo_brands, fetch_wandaloo_models, fetch_wandaloo_model_listings

# Quick normalization map
BRAND_ALIASES = {'Vw': 'Volkswagen', 'Bmw': 'BMW', 'Citro N': 'Citroën'}

def normalize_name(s: str) -> str:
    if not s:
        return s
    s = s.strip()
    s = re.sub(r"[^\w\s\-]", ' ', s)
    s = re.sub(r"\s+", ' ', s).strip()
    parts = s.split()
    parts = [p.upper() if len(p) <= 3 and p.isalpha() else p.title() for p in parts]
    res = ' '.join(parts)
    return BRAND_ALIASES.get(res, res)


async def extract_price_from_page(session: aiohttp.ClientSession, url: str) -> int | None:
    try:
        async with session.get(url, timeout=15) as resp:
            if resp.status != 200:
                return None
            html = await resp.text()
    except Exception:
        return None

    # Try meta tags
    try:
        soup = BeautifulSoup(html, 'html.parser')
        # JSON-LD schema price
        scripts = soup.find_all('script', type='application/ld+json')
        for s in scripts:
            try:
                j = json.loads(s.string or '{}')
                # Possible structures
                if isinstance(j, dict):
                    # Offer.price or offers.price
                    offer = j.get('offers') or j.get('offer')
                    if isinstance(offer, dict):
                        p = offer.get('price') or offer.get('priceSpecification', {}).get('price')
                        if p:
                            pnum = re.sub(r'[^0-9]', '', str(p))
                            if pnum:
                                return int(pnum)
                elif isinstance(j, list):
                    for item in j:
                        if isinstance(item, dict):
                            offer = item.get('offers')
                            if isinstance(offer, dict):
                                p = offer.get('price')
                                if p:
                                    pnum = re.sub(r'[^0-9]', '', str(p))
                                    if pnum:
                                        return int(pnum)
            except Exception:
                continue

        # Open Graph or meta tags
        metas = soup.find_all('meta')
        for m in metas:
            for attr in ['property', 'name', 'itemprop']:
                key = m.get(attr, '').lower()
                if key in ['product:price:amount', 'og:price:amount', 'price']:
                    v = m.get('content')
                    if v:
                        pnum = re.sub(r'[^0-9]', '', v)
                        if pnum:
                            return int(pnum)

        # Common selectors that may show price
        selectors = ['.price', '.prix', '.car-price', '.voiture-price', '.listing-price', '.price-amount']
        for sel in selectors:
            el = soup.select_one(sel)
            if el and el.get_text():
                txt = el.get_text()
                m = re.search(r"([0-9\s\.,]{3,})\s*(?:MAD|DH|Dh|dh)?", txt)
                if m:
                    pnum = re.sub(r'[^0-9]', '', m.group(1))
                    if pnum:
                        return int(pnum)

        # Fallback: regex on whole page for MAD/DH
        m = re.search(r"([0-9\s\.,]{3,})\s*(?:MAD|DH|Dh|dh)", html)
        if m:
            pnum = re.sub(r'[^0-9]', '', m.group(1))
            if pnum:
                return int(pnum)

        # Final fallback: first number > 10000
        nums = re.findall(r"\b([0-9]{5,})\b", html)
        if nums:
            return int(nums[0])

    except Exception:
        return None

    return None


async def main(limit_brands: int = 10, max_listings_per_model: int = 40):
    out = OrderedDict()
    brands = await fetch_wandaloo_brands()
    if not brands:
        print('No brands found on Wandaloo')
        return

    normalized_brands = []
    seen = set()
    for b in brands:
        nb = normalize_name(b)
        if nb and nb not in seen:
            seen.add(nb)
            normalized_brands.append(nb)
    if limit_brands and limit_brands > 0:
        normalized_brands = normalized_brands[:limit_brands]

    timeout = aiohttp.ClientTimeout(total=25)
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; PriceBot/1.0)'}

    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        for brand in normalized_brands:
            brand_entry = OrderedDict()
            try:
                models = await fetch_wandaloo_models(brand)
            except Exception as e:
                out[brand] = {'error': f'failed to fetch models: {e}'}
                continue

            # normalize + dedupe models
            norm_models = []
            seen_m = set()
            for m in models:
                nm = normalize_name(m)
                if nm and nm not in seen_m:
                    seen_m.add(nm)
                    norm_models.append(nm)

            for model in norm_models:
                try:
                    listings = await fetch_wandaloo_model_listings(brand, model, max_results=max_listings_per_model)
                except Exception as e:
                    brand_entry[model] = {'error': f'failed to fetch listings: {e}'}
                    continue

                # For each listing, if price present keep it; else follow the listing URL and try to extract
                filtered = []
                seen_urls = set()
                for l in listings:
                    price = l.get('price')
                    url = l.get('url') or ''
                    # normalize relative urls
                    if url and url.startswith('/'):
                        url = urljoin('https://www.wandaloo.com', url)

                    if price and isinstance(price, int):
                        key = url or (l.get('title') or '')
                        if key not in seen_urls:
                            seen_urls.add(key)
                            filtered.append({'title': (l.get('title') or '').strip(), 'price': price, 'year': l.get('year'), 'url': url})
                    else:
                        # follow and try to extract
                        if not url:
                            continue
                        # polite fetch
                        p = await extract_price_from_page(session, url)
                        if p:
                            key = url
                            if key not in seen_urls:
                                seen_urls.add(key)
                                filtered.append({'title': (l.get('title') or '').strip(), 'price': p, 'year': l.get('year'), 'url': url})

                if filtered:
                    brand_entry[model] = filtered

            out[brand] = brand_entry

    path = 'scraped_wandaloo_followed.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    total_brands = len(out)
    total_models = sum(len(v) if isinstance(v, dict) else 0 for v in out.values())
    print(json.dumps({'file': path, 'brands': total_brands, 'models_found': total_models}, ensure_ascii=False))


if __name__ == '__main__':
    asyncio.run(main(limit_brands=10, max_listings_per_model=40))
