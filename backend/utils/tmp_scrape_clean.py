import asyncio
import json
from wandaloo_scraper import fetch_wandaloo_brands, fetch_wandaloo_models, fetch_wandaloo_model_listings

async def main(limit=2, max_listings_per_model=40):
    out = {}
    brands = await fetch_wandaloo_brands()
    if not brands:
        print(json.dumps({'error':'no brands found'}, ensure_ascii=False))
        return
    brands = brands[:limit]
    for brand in brands:
        try:
            models = await fetch_wandaloo_models(brand)
            brand_entry = {}
            for model in models:
                try:
                    listings = await fetch_wandaloo_model_listings(brand, model, max_results=max_listings_per_model)
                    # Keep only listings that have a parsed price (number)
                    filtered = [l for l in listings if l.get('price')]
                    if filtered:
                        brand_entry[model] = filtered
                except Exception as e:
                    brand_entry[model] = {'error': str(e)}
            out[brand] = brand_entry
        except Exception as e:
            out[brand] = {'error': str(e)}
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    asyncio.run(main(limit=2, max_listings_per_model=40))
