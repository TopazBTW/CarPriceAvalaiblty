import asyncio
import json
import re
from collections import OrderedDict
from wandaloo_scraper import fetch_wandaloo_brands, fetch_wandaloo_models, fetch_wandaloo_model_listings

# Simple normalization maps
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
    # replace multiple spaces and non-letter/digit with space
    s = re.sub(r"[^\w\s\-]", ' ', s)
    s = re.sub(r"\s+", ' ', s).strip()
    # Title case but keep common acronyms uppercase
    parts = s.split()
    parts = [p.upper() if len(p) <= 3 and p.isalpha() else p.title() for p in parts]
    res = ' '.join(parts)
    return BRAND_ALIASES.get(res, res)


async def main(limit_brands: int = 10, max_listings_per_model: int = 40):
    out = OrderedDict()
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

            # filter listings with parsed numeric price
            filtered = []
            seen_urls = set()
            for l in listings:
                price = l.get('price')
                url = l.get('url') or ''
                if price and isinstance(price, int):
                    key = url or (l.get('title') or '')
                    if key in seen_urls:
                        continue
                    seen_urls.add(key)
                    filtered.append({'title': (l.get('title') or '').strip(), 'price': price, 'year': l.get('year'), 'url': url})

            if filtered:
                brand_entry[model] = filtered

        out[brand] = brand_entry

    # Write to file
    path = 'scraped_wandaloo_clean.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # Print summary
    total_brands = len(out)
    total_models = sum(len(v) if isinstance(v, dict) else 0 for v in out.values())
    total_listings = sum(len(listings) for listings in out.values() if isinstance(listings, dict) for listings in [listings])
    print(json.dumps({'file': path, 'brands': total_brands, 'models_found': total_models}, ensure_ascii=False))


if __name__ == '__main__':
    asyncio.run(main(limit_brands=10, max_listings_per_model=40))
