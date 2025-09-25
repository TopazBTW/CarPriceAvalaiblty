import json
from collections import Counter, OrderedDict

inp = 'scraped_wandaloo_followed.json'
out_sample = 'scraped_wandaloo_followed_sample.json'

def main():
    with open(inp, 'r', encoding='utf-8') as f:
        data = json.load(f)

    brands = list(data.keys())
    brands_count = len(brands)

    models_with_listings = 0
    total_models = 0
    total_listings = 0
    brand_listing_counts = {}

    for b, models in data.items():
        if not isinstance(models, dict):
            continue
        total_models += len(models)
        b_count = 0
        for m, listings in models.items():
            if isinstance(listings, list) and listings:
                models_with_listings += 1
                total_listings += len(listings)
                b_count += len(listings)
        brand_listing_counts[b] = b_count

    top_brands = Counter(brand_listing_counts).most_common(10)

    # build sample: top brand -> first 5 models -> first 3 listings
    sample = OrderedDict()
    if top_brands:
        top_brand = top_brands[0][0]
        sample[top_brand] = OrderedDict()
        models = data.get(top_brand, {})
        for i, (m, listings) in enumerate(models.items()):
            if i >= 5:
                break
            sample[top_brand][m] = listings[:3] if isinstance(listings, list) else listings

    summary = {
        'file': inp,
        'brands_scanned': brands_count,
        'total_models': total_models,
        'models_with_listings': models_with_listings,
        'total_listings': total_listings,
        'top_brands_by_listings': top_brands,
        'sample_file': out_sample
    }

    with open(out_sample, 'w', encoding='utf-8') as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)

    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
