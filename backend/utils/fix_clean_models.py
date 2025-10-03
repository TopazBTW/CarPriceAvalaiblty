#!/usr/bin/env python3
"""
Post-process morocco_cars_clean.json to fix model keys that are actually addresses/locations.
This script will:
- load data/json/morocco_cars_clean.json
- detect model keys that look like addresses
- for each variation under such keys, derive a model name from variation['model'], variation['url'], or variation['raw_text']
- rebuild the `models` mapping and `cars` list, and update metadata
"""
import json
import re
from pathlib import Path


def is_location_string(s: str) -> bool:
    if not s or not isinstance(s, str):
        return False
    s_u = s.upper()
    indicators = ['BOULEVARD', 'RUE', 'ROUTE', 'RTE', 'CASABLANCA', 'RABAT', 'BUSINESS CENTER', ',', 'AVENUE', 'PLACE', 'IMM', 'Z.I', 'ZONE']
    if any(tok in s_u for tok in indicators):
        return True
    if len(s) > 60 and ' ' in s:
        return True
    return False


def derive_model(variation: dict) -> str:
    # Try variation['model'] first
    m = variation.get('model') or variation.get('title') or ''
    if m and not is_location_string(m):
        return clean_model(m)

    # Try URL last segment
    url = variation.get('url') or ''
    if url:
        parts = url.rstrip('/').split('/')
        if parts:
            candidate = parts[-1]
            # decode percent and remove query
            candidate = re.sub(r"\%[0-9A-Fa-f]{2}", '', candidate)
            candidate = re.split(r'[\?_#]', candidate)[0]
            if candidate and not is_location_string(candidate):
                return clean_model(candidate.replace('-', ' '))

    # Try raw_text tokens
    raw = variation.get('raw_text') or variation.get('description') or ''
    if raw:
        tokens = re.findall(r"[A-Za-zÀ-ÿ0-9'-]+", raw)
        tokens = [t for t in tokens if not re.match(r'^\d{4}$', t) and not re.match(r'^\d+(\.\d+)?L$', t, flags=re.IGNORECASE)]
        if tokens:
            candidate = ' '.join(tokens[:3])
            if not is_location_string(candidate):
                return clean_model(candidate)

    return 'Unknown'


def clean_model(s: str) -> str:
    s = re.sub(r'\s+', ' ', str(s).strip())
    s = s.replace("\u00e9", 'e').replace("\u00e8", 'e').replace("\u00e0", 'a')
    # Remove obvious prefixes
    s = re.sub(r'^(NOUVELLE|NOUVEAU|NEW|PROMO)\s+', '', s, flags=re.IGNORECASE)
    return s.title()


def main():
    path = Path('data/json/morocco_cars_clean.json')
    if not path.exists():
        print(f"File not found: {path}")
        return

    data = json.loads(path.read_text(encoding='utf-8'))

    new_models = {}
    new_cars = []
    car_id = 1

    for brand, models in data.get('models', {}).items():
        new_models.setdefault(brand, {})
        for model_key, variations in models.items():
            if is_location_string(model_key):
                for v in variations:
                    real_model = derive_model(v)
                    if real_model not in new_models[brand]:
                        new_models[brand][real_model] = []

                    entry = {
                        'id': car_id,
                        'brand': brand,
                        'model': real_model,
                        'price': v.get('price'),
                        'price_range': v.get('price_range', 'Non spécifié'),
                        'year': v.get('year'),
                        'engine': v.get('engine'),
                        'fuel_type': v.get('fuel_type'),
                        'transmission': v.get('transmission'),
                        'url': v.get('url'),
                        'image': v.get('image'),
                        'source': v.get('source', 'kifal.ma'),
                        'scraped_at': v.get('scraped_at')
                    }
                    new_models[brand][real_model].append(entry)
                    new_cars.append(entry)
                    car_id += 1
            else:
                clean_m = clean_model(model_key)
                if clean_m not in new_models[brand]:
                    new_models[brand][clean_m] = []
                for v in variations:
                    entry = {
                        'id': car_id,
                        'brand': brand,
                        'model': clean_m,
                        'price': v.get('price'),
                        'price_range': v.get('price_range', 'Non spécifié'),
                        'year': v.get('year'),
                        'engine': v.get('engine'),
                        'fuel_type': v.get('fuel_type'),
                        'transmission': v.get('transmission'),
                        'url': v.get('url'),
                        'image': v.get('image'),
                        'source': v.get('source', 'kifal.ma'),
                        'scraped_at': v.get('scraped_at')
                    }
                    new_models[brand][clean_m].append(entry)
                    new_cars.append(entry)
                    car_id += 1

    # Build final structure
    data['models'] = new_models
    data['cars'] = new_cars
    data['metadata'] = data.get('metadata', {})
    data['metadata']['total_brands'] = len(data.get('brands', {}))
    data['metadata']['total_models'] = sum(len(m) for m in new_models.values())
    data['metadata']['total_cars'] = len(new_cars)

    # Update price_ranges counts
    ranges = ['Moins de 200k', '200k - 300k', '300k - 500k', '500k - 800k', '800k - 1.5M', 'Plus de 1.5M']
    price_counts = {r: 0 for r in ranges}
    for c in new_cars:
        pr = c.get('price_range', 'Non spécifié')
        if pr in price_counts:
            price_counts[pr] += 1

    data['metadata']['price_ranges'] = price_counts

    # Save back
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Fixed models.json saved. Brands: {len(data.get('brands', {}))}, Models: {data['metadata']['total_models']}, Cars: {data['metadata']['total_cars']}")


if __name__ == '__main__':
    main()
