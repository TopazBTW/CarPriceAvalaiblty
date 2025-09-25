import asyncio
import json
import re
from collections import OrderedDict
from urllib.parse import urlparse, urljoin
import aiohttp
from bs4 import BeautifulSoup
from wandaloo_scraper import fetch_wandaloo_brands, fetch_wandaloo_models, fetch_wandaloo_model_listings

# Simple normalization map
BRAND_ALIASES = {
    'Vw': 'Volkswagen',
    'Volkswagen': 'Volkswagen',
    'Bmw': 'BMW',
    'Bmw ': 'BMW',
    'Ds Automobiles': 'DS Automobiles',
    'Citro N': 'Citroën'
}


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


async def fetch_price_from_url(session: aiohttp.ClientSession, url: str) -> int | None:
    try:
        async with session.get(url, timeout=15) as resp:
            if resp.status != 200:
                return None
            html = await resp.text()
    except Exception:
        return None

    # Try meta tags first
    try:
        soup = BeautifulSoup(html, 'html.parser')
    except Exception:
        return None

    # Common meta tags
    meta_selectors = [
        ('meta', {'property': 'og:price:amount'}),
        ('meta', {'itemprop': 'price'}),
        ('meta', {'name': 'price'})
    ]
    for tag, attrs in meta_selectors:
        m = soup.find(tag, attrs=attrs)
        if m:
            content = m.get('content') or m.get('value')
            if content:
                num = re.sub(r'[^0-9]', '', content)
                if num:
                    try:
                        return int(num)
                    except:
                        pass

    # Look for elements with class or id containing price-like words
    candidates = soup.find_all(True, attrs={'class': re.compile(r'price|prix|tarif|cost', re.I)})
    candidates += soup.find_all(True, attrs={'id': re.compile(r'price|prix|tarif|cost', re.I)})

    for c in candidates:
        txt = c.get_text(separator=' ', strip=True)
        if not txt:
            continue
        m = re.search(r"([0-9][0-9\s\.,]{2,})\s*(?:MAD|DH|Dh|dh|MAD\b)", txt, flags=re.I)
        if not m:
            m = re.search(r"([0-9][0-9\s\.,]{2,})", txt)
        if m:
            num = re.sub(r'[^0-9]', '', m.group(1))
            if num:
                try:
                    return int(num)
                except:
                    continue

    # Fallback: look for any price-like token in the page
    all_text = soup.get_text(separator=' ', strip=True)
    m = re.search(r"([0-9][0-9\s\.,]{2,})\s*(?:MAD|DH|Dh|dh|MAD\b)", all_text, flags=re.I)
    if m:
        num = re.sub(r'[^0-9]', '', m.group(1))
        if num:
            try:
                return int(num)
            except:
                pass

    return None


async def main(limit_brands: int = 10, max_listings_per_model: int = 40):
    out = OrderedDict()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8'
    }

    brands = await fetch_wandaloo_brands()
    if not brands:
        print('No brands found on Wandaloo')
        return

    # Normalize + dedupe brands preserving order
    normalized_brands = []
    seen = set()
    for b in brands:
        nb = normalize_name(b)
        if nb and nb not in seen:
            seen.add(nb)
            normalized_brands.append(nb)
    if limit_brands and limit_brands > 0:
        normalized_brands = normalized_brands[:limit_brands]

    timeout = aiohttp.ClientTimeout(total=20)
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

                filtered = []
                seen_urls = set()
                for l in listings:
                    price = l.get('price')
                    url = l.get('url') or ''
                    title = (l.get('title') or '').strip()
                    # If price already parsed, keep it
                    if price and isinstance(price, int):
                        key = url or title
                        if key in seen_urls:
                            continue
                        seen_urls.add(key)
                        filtered.append({'title': title, 'price': price, 'year': l.get('year'), 'url': url})
                        continue

                    # Otherwise, try to follow the url and extract price from the target page
                    if url and url.startswith('http'):
                        # polite delay
                        await asyncio.sleep(0.6)
                        p = await fetch_price_from_url(session, url)
                        if p:
                            key = url
                            if key in seen_urls:
                                continue
                            seen_urls.add(key)
                            filtered.append({'title': title, 'price': p, 'year': l.get('year'), 'url': url})

                if filtered:
                    brand_entry[model] = filtered

            out[brand] = brand_entry

    # Write to file
    path = 'scraped_wandaloo_followed.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # Print summary
    total_brands = len(out)
    total_models = sum(len(v) if isinstance(v, dict) else 0 for v in out.values())
    total_listings = sum(len(listings) for listings in out.values() if isinstance(listings, dict) for listings in [listings])
    print(json.dumps({'file': path, 'brands': total_brands, 'models_found': total_models}, ensure_ascii=False))


if __name__ == '__main__':
    asyncio.run(main(limit_brands=10, max_listings_per_model=40))
