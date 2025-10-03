#!/usr/bin/env python3
"""
Enrich morocco_cars_clean.json by scraping each listing URL for updated price and details.
This is asynchronous and uses aiohttp + BeautifulSoup.
"""
import asyncio
import aiohttp
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin


async def fetch(session, url):
    try:
        async with session.get(url, timeout=30) as resp:
            if resp.status == 200:
                return await resp.text()
    except Exception:
        return None


def parse_listing(html, base_url=None):
    if not html:
        return {}
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)

    # Price
    price = None
    m = re.search(r'(\d{1,3}(?:[\s,]?\d{3})*)\s*(?:DH|MAD|Dh)', text)
    if m:
        price = int(m.group(1).replace(' ', '').replace(',', ''))

    # Year
    y = re.search(r'20\d{2}', text)
    year = int(y.group()) if y else None

    # Engine
    eng = re.search(r'(\d+(?:\.\d+)?)\s*(?:L|l)', text)
    engine = eng.group(1) + 'L' if eng else None

    # Fuel
    fuel = None
    for f in ['ESSENCE', 'DIESEL', 'HYBRID', 'ELECTRIQUE', 'GPL']:
        if f.lower() in text.lower():
            fuel = f
            break

    # Transmission
    transmission = None
    if any(t in text.upper() for t in ['AUTOMATIQUE', 'AUTO', 'CVT', 'DSG']):
        transmission = 'AUTOMATIQUE'
    elif any(t in text.upper() for t in ['MANUEL', 'MANUELLE', 'MT']):
        transmission = 'MANUELLE'

    # Image: try og:image
    image = None
    og = soup.find('meta', property='og:image')
    if og and og.get('content'):
        image = urljoin(base_url or '', og.get('content'))

    return {
        'price': price,
        'year': year,
        'engine': engine,
        'fuel_type': fuel,
        'transmission': transmission,
        'image': image
    }


async def enrich_all(concurrency: int = 8):
    path = Path('data/json/morocco_cars_clean.json')
    if not path.exists():
        print('File not found:', path)
        return

    data = json.loads(path.read_text(encoding='utf-8'))
    cars = data.get('cars', [])

    connector = aiohttp.TCPConnector(limit=concurrency)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for car in cars:
            url = car.get('url')
            if url:
                tasks.append((car, asyncio.create_task(fetch(session, url))))

        print(f'Enriching {len(tasks)} listings...')

        updated = 0
        for car, task in tasks:
            html = await task
            info = parse_listing(html, base_url='https://neuf.kifal.ma')
            changed = False
            for k, v in info.items():
                if v is not None and (car.get(k) != v):
                    car[k] = v
                    changed = True
            if changed:
                updated += 1

        print(f'Updated {updated} listings out of {len(tasks)}')

    # Write back
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Saved enriched JSON')


if __name__ == '__main__':
    asyncio.run(enrich_all())
