import asyncio
import json
from wandaloo_scraper import fetch_wandaloo_brands, fetch_wandaloo_models, fetch_wandaloo_model_listings

async def main(limit=2):
    result = {}
    brands = await fetch_wandaloo_brands()
    if not brands:
        print(json.dumps({'error':'no brands found'}, ensure_ascii=False))
        return
    brands = brands[:limit]
    for brand in brands:
        try:
            models = await fetch_wandaloo_models(brand)
            entries = {}
            for model in models:
                try:
                    listings = await fetch_wandaloo_model_listings(brand, model, max_results=20)
                    entries[model] = listings
                except Exception as e:
                    entries[model] = {'error': str(e)}
            result[brand] = entries
        except Exception as e:
            result[brand] = {'error': str(e)}
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    asyncio.run(main(limit=2))
