import asyncio
import re
from typing import List, Dict, Any
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin

# Tokens we should ignore when extracting brand names (navigation noise)
_BAD_TOKENS = set([
    'compte','neuf','occasion','accueil','promo','offres','offre','actu','contact','faq','blog','video','videos','forum','services','salons'
])


async def fetch_wandaloo_new_versions(brand: str, model: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Attempt to scrape Wandaloo for new car versions for brand+model.
    Returns list of versions: {year,min,max,url}
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8'
    }

    # Build a few plausible Wandaloo search / section URLs
    q = quote(f"{brand} {model}")
    search_queries = [
        f"https://www.wandaloo.com/voiture-neuve/?s={q}",
        f"https://www.wandaloo.com/?s={q}",
        f"https://www.wandaloo.com/voiture-neuve/{quote(brand)}/{quote(model)}/",
    ]

    # helper to extract price number from text
    def extract_price(text: str):
        if not text:
            return None
        t = re.sub(r"[^0-9]", "", text)
        try:
            return int(t) if t else None
        except:
            return None

    results = []
    timeout = aiohttp.ClientTimeout(total=20)

    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        for url in search_queries:
            try:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        continue
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # find listing containers - common patterns
                    containers = soup.select('article, .listing, .result, .voiture-card, .listing-item')
                    if not containers:
                        # fallback - look for links that mention the model
                        containers = soup.find_all('a', href=True)

                    found = 0
                    for c in containers:
                        if found >= max_results:
                            break

                        # find link
                        link = c.find('a', href=True)
                        if not link:
                            # if container itself is an anchor
                            if c.name == 'a' and c.get('href'):
                                href = c.get('href')
                            else:
                                continue
                        else:
                            href = link.get('href')

                        full_url = href if href.startswith('http') else urljoin('https://www.wandaloo.com', href)

                        text = c.get_text(separator=' ', strip=True)
                        if model.lower() not in text.lower() and brand.lower() not in text.lower():
                            # skip unrelated items
                            continue

                        # Try extract price
                        price_match = re.search(r"(\d[\d\s\.,]*)(?:\s*(?:dh|dh\*|MAD|DH))", text, flags=re.I)
                        price = None
                        if price_match:
                            price = int(re.sub(r"[^0-9]", "", price_match.group(1)))

                        # try find year
                        year_match = re.search(r"\b(20\d{2})\b", text)
                        year = int(year_match.group(1)) if year_match else None

                        results.append({'title': text[:140], 'price': price, 'year': year, 'url': full_url})
                        found += 1

                    if results:
                        # aggregate by year if possible
                        by_year = {}
                        for r in results:
                            y = r.get('year') or 'unknown'
                            p = r.get('price')
                            if y not in by_year:
                                by_year[y] = {'min': None, 'max': None, 'urls': set()}
                            if p:
                                if by_year[y]['min'] is None or p < by_year[y]['min']:
                                    by_year[y]['min'] = p
                                if by_year[y]['max'] is None or p > by_year[y]['max']:
                                    by_year[y]['max'] = p
                            if r.get('url'):
                                by_year[y]['urls'].add(r.get('url'))

                        versions = []
                        for y, info in by_year.items():
                            if y == 'unknown':
                                continue
                            versions.append({'year': int(y), 'min': info['min'], 'max': info['max'], 'url': list(info['urls'])[0] if info['urls'] else ''})

                        # sort and return
                        versions.sort(key=lambda v: v['year'], reverse=True)
                        return versions

            except Exception:
                continue

    return []


async def fetch_wandaloo_model_listings(brand: str, model: str, max_results: int = 30) -> List[Dict[str, Any]]:
    """Return raw listing entries from Wandaloo for a brand+model (title, price, year, url).
    This does not aggregate by year; it returns each found listing so the frontend can
    display all available options.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8'
    }

    q = quote(f"{brand} {model}")
    urls = [
        f"https://www.wandaloo.com/voiture-neuve/?s={q}",
        f"https://www.wandaloo.com/?s={q}",
        f"https://www.wandaloo.com/neuf/{quote(brand)}/{quote(model)}/",
        f"https://www.wandaloo.com/neuf/{quote(brand)}/"
    ]

    results = []
    timeout = aiohttp.ClientTimeout(total=25)

    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        for url in urls:
            try:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        continue
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    containers = soup.select('article, .listing, .voiture-card, .listing-item, .result')
                    if not containers:
                        containers = soup.find_all('a', href=True)

                    found = 0
                    for c in containers:
                        if found >= max_results:
                            break

                        text = c.get_text(separator=' ', strip=True)
                        if model.lower() not in text.lower() and brand.lower() not in text.lower():
                            continue

                        # Extract price
                        price = None
                        price_match = re.search(r"(\d[\d\s\.,]*)(?:\s*(?:dh|mad|MAD|DH))", text, flags=re.I)
                        if price_match:
                            price = int(re.sub(r'[^0-9]', '', price_match.group(1)))

                        # Extract year
                        year = None
                        year_match = re.search(r"\b(20\d{2})\b", text)
                        if year_match:
                            year = int(year_match.group(1))

                        # URL
                        link = None
                        if c.name == 'a' and c.get('href'):
                            link = c.get('href')
                        else:
                            a = c.find('a', href=True)
                            if a:
                                link = a.get('href')

                        if link and not link.startswith('http'):
                            link = urljoin('https://www.wandaloo.com', link)

                        entry = {'title': text[:200], 'price': price, 'year': year, 'url': link}
                        results.append(entry)
                        found += 1

                    if results:
                        return results

            except Exception:
                continue

    return results


async def fetch_wandaloo_models(brand: str) -> List[str]:
    """Scrape the Wandaloo brand page for a list of models for the given brand.
    Returns a list of model names (best-effort).
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8'
    }
    candidate = f"https://www.wandaloo.com/neuf/{quote(brand)}/"
    timeout = aiohttp.ClientTimeout(total=20)
    models = []

    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        try:
            async with session.get(candidate) as resp:
                if resp.status != 200:
                    return []
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Common selectors where models appear: links in sections, list items, table rows
                anchors = soup.select('a[href*="/neuf/"]') + soup.select('a[href*="/voiture-neuve/"]')
                for a in anchors:
                    txt = (a.get_text() or '').strip()
                    if not txt:
                        continue
                    # Skip nav and CTA texts
                    low = txt.lower()
                    if any(t in low for t in ['neuf','voiture','marque','promo','offre','comparateur','accueil']):
                        continue
                    # Normalize
                    name = re.sub(r'[^A-Za-z0-9 \-]', ' ', txt).strip()
                    name = re.sub(r'\s+', ' ', name)
                    if name and name.title() not in models:
                        models.append(name.title())
                        if len(models) >= 120:
                            break
        except Exception:
            return []

    return models


async def fetch_wandaloo_brands(max_brands: int = 200, mode: str = 'both') -> List[str]:
    """Scrape Wandaloo to get a list of car brands available in Morocco.

    This function tries a couple of known Wandaloo pages (voiture-neuve and homepage),
    collects anchor texts that look like brand names and returns a normalized unique list.
    It's best-effort and may miss or include noisy entries; caller should fallback to
    authoritative DB if the result is empty.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8'
    }

    # Choose candidate pages depending on requested mode: 'neuf', 'occasion' or 'both'
    # 'neuf' should only hit the new-car sections to avoid pulling 'occasion' anchors
    if mode and mode.lower() == 'neuf':
        candidate_urls = [
            'https://www.wandaloo.com/voiture-neuve/marques/',
            'https://www.wandaloo.com/voiture-neuve/',
            'https://www.wandaloo.com/neuf/',
        ]
    elif mode and mode.lower() == 'occasion':
        candidate_urls = [
            'https://www.wandaloo.com/occasion/',
            'https://www.wandaloo.com/occasion/marques/',
        ]
    else:
        # conservative default: prefer new-car marque pages first then fallback to homepage
        candidate_urls = [
            'https://www.wandaloo.com/voiture-neuve/marques/',
            'https://www.wandaloo.com/voiture-neuve/',
            'https://www.wandaloo.com/voiture-neuve/marques',
            'https://www.wandaloo.com/',
        ]

    brands = []
    timeout = aiohttp.ClientTimeout(total=20)

    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        for url in candidate_urls:
            try:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        continue
                    text = await resp.text()
                    soup = BeautifulSoup(text, 'html.parser')

                    # If we're on the marques page, extract brand names from logo blocks first
                    if 'marques' in url.lower() or '/voiture-neuve/marques' in url.lower():
                        try:
                            logo_imgs = soup.select('div.item a img[alt]')
                            logo_brands = []
                            for img in logo_imgs:
                                alt = (img.get('alt') or '').strip()
                                if not alt:
                                    continue
                                # Normalize alt text (remove extra words like year or 'Neuve Maroc')
                                name = re.sub(r'\b\d{4}\b', '', alt)
                                name = re.sub(r'neuve|maroc', '', name, flags=re.I)
                                name = re.sub(r'[^A-Za-z0-9 \-]', ' ', name).strip()
                                name = re.sub(r'\s+', ' ', name)
                                if name and name.title() not in logo_brands:
                                    logo_brands.append(name.title())
                                    if len(logo_brands) >= max_brands:
                                        break
                            if logo_brands:
                                # If caller requested new-car brands, remove any logo-derived
                                # entries that reference 'occasion' or look like models (contain digits)
                                if mode and mode.lower() == 'neuf':
                                    logo_brands = [lb for lb in logo_brands if not re.search(r'\boccasion\b', lb, flags=re.I) and not re.search(r'\d', lb)]
                                if logo_brands:
                                    return logo_brands
                        except Exception:
                            pass

                    # Collect anchors, option tags, and list items that likely contain brand names
                    anchors = soup.find_all('a', href=True)
                    options = soup.find_all('option')
                    list_items = soup.find_all(['li', 'span', 'div'])

                    # Helper to normalize candidate text
                    def norm(txt: str) -> str:
                        return re.sub(r"[^A-Za-z0-9 \-]", '', txt).strip()

                    # Prefer anchors whose hrefs indicate a marque/brand page
                    for a in anchors:
                        href = a.get('href', '')
                        txt = (a.get_text() or '').strip()
                        if not txt:
                            continue
                        # Skip obvious occasion anchors when we only want neuf
                        if mode and mode.lower() == 'neuf' and 'occasion' in txt.lower():
                            continue
                        if len(txt) < 2 or len(txt) > 40:
                            continue
                        # Skip links explicitly for occasions when we're in neuf mode
                        if mode and mode.lower() == 'neuf' and '/occasion' in href.lower():
                            continue
                        if any(k in href.lower() for k in ['/marque', '/marques', '/voiture-neuve/']) or 'marque' in url.lower():
                            name = norm(txt).title()
                            if name and name not in brands:
                                brands.append(name)
                                if len(brands) >= max_brands:
                                    break

                    # Also consider option elements (sometimes used for brand filters)
                    if len(brands) < max_brands:
                        for o in options:
                            txt = (o.get_text() or '').strip()
                            if not txt or len(txt) < 2:
                                continue
                            if mode and mode.lower() == 'neuf' and 'occasion' in txt.lower():
                                continue
                            name = norm(txt).title()
                            if name and name not in brands:
                                brands.append(name)
                                if len(brands) >= max_brands:
                                    break

                    # Finally scan list items for uppercase brand-like words (e.g., ALFA ROMEO, AUDI)
                    if len(brands) < max_brands:
                        for el in list_items:
                            txt = (el.get_text() or '').strip()
                            if not txt or len(txt) < 2 or len(txt) > 40:
                                continue
                            # Look for tokens in ALL CAPS or TitleCase with short length
                            tokens = [t.strip() for t in re.split(r'[\n\r/|,]', txt) if t.strip()]
                            for t in tokens:
                                if len(t) < 2 or len(t) > 30:
                                    continue
                                # Heuristic: brand names are often 1-3 words and contain letters
                                if re.search(r'[A-Za-z]', t):
                                    candidate = norm(t).title()
                                    # Filter out very common non-brand words
                                    if candidate.lower() in ['voiture', 'neuve', 'occasion', 'marque', 'model', 'toutes']:
                                        continue
                                    if mode and mode.lower() == 'neuf' and 'occasion' in candidate.lower():
                                        continue
                                    if candidate and candidate not in brands:
                                        brands.append(candidate)
                                        if len(brands) >= max_brands:
                                            break
                            if len(brands) >= max_brands:
                                break
                            if len(brands) >= max_brands:
                                break

                    # Also extract brand names from images (logo alt attributes)
                    if len(brands) < max_brands:
                        imgs = soup.find_all('img', alt=True)
                        for img in imgs:
                            alt = (img.get('alt') or '').strip()
                            if not alt or len(alt) < 2 or len(alt) > 40:
                                continue
                            # Skip alt that clearly reference occasion when in neuf mode
                            if mode and mode.lower() == 'neuf' and 'occasion' in alt.lower():
                                # try to remove the token and continue if that yields a clean name
                                alt = re.sub(r'\boccasion\b', '', alt, flags=re.I).strip()
                                if not alt:
                                    continue
                            name = norm(alt).title()
                            # Some alts contain extra words like 'AUDI 2025 Neuve Maroc' -> take first token(s)
                            # Keep up to first 3 words that are alphabetic
                            tokens = [t for t in re.split(r'[\s\-_/|,]', name) if t]
                            candidate = ' '.join(tokens[:3])
                            # If mode is neuf, skip candidate with digits (model identifiers)
                            if mode and mode.lower() == 'neuf' and re.search(r'\d', candidate):
                                continue
                            if candidate and candidate not in brands:
                                brands.append(candidate)
                                if len(brands) >= max_brands:
                                    break

                    # If we are on the marques page, there's a distinct structure with many
                    # <div class="item"><a href="..."><img alt="AUDI" ...></a></div>
                    # Try to extract brand names from those specific blocks which are much
                    # less noisy than the global anchors scan above.
                    if 'marques' in url.lower() or '/voiture-neuve/marques' in url.lower():
                        try:
                            marque_items = soup.select('div.item')
                            for mi in marque_items:
                                # look for img alt or anchor title
                                img = mi.find('img')
                                a = mi.find('a')
                                candidate = None
                                if img and img.get('alt'):
                                    candidate = norm(img.get('alt'))
                                elif a and a.get('title'):
                                    candidate = norm(a.get('title'))
                                elif a and a.get_text():
                                    candidate = norm(a.get_text())

                                if candidate:
                                    # remove year/extra words like '2025 Neuve Maroc'
                                    candidate = re.sub(r'\b\d{4}\b', '', candidate)
                                    # take first 3 words at most
                                    toks = [t for t in re.split(r'[\s\-_/|,]', candidate) if t]
                                    name = ' '.join(toks[:3]).title()
                                    if name and name not in brands and name.lower() not in _BAD_TOKENS:
                                        brands.append(name)
                                        if len(brands) >= max_brands:
                                            break
                            # if we found a lot of brands here, prefer these cleaned results
                            if len(brands) >= 8:
                                break
                        except Exception:
                            pass
                    if brands:
                        break
            except Exception:
                continue

    # Final normalization: remove obviously invalid tokens and duplicates
    cleaned = []
    logo_candidates = []
    for b in brands:
        # remove trailing symbols
        name = re.sub(r"[^A-Za-z0-9 \-]", ' ', b).strip()
        if not name:
            continue
        # collapse multiple spaces
        name = re.sub(r'\s+', ' ', name)
        # simple length filter
        if len(name) < 2 or len(name) > 30:
            continue
        # normalize common short forms
        if name.lower() == 'vw':
            name = 'Volkswagen'
        # skip known bad tokens
        low = name.lower()
        if any(t in low for t in _BAD_TOKENS):
            continue
        # If caller asked for new-car brands, strip or skip entries that look like
        # occasion-specific anchors or model names (contain 'occasion' or digits)
        if mode and mode.lower() == 'neuf':
            # remove the word 'occasion' if present, then re-clean
            name = re.sub(r'\boccasion\b', '', name, flags=re.I).strip()
            if not name:
                continue
            # If still contains digits or is likely a model (e.g., '500X'), skip
            if re.search(r'\d', name):
                continue
            # If it contains words like 'voiture' or 'occas' skip
            if any(k in name.lower() for k in ['voiture', 'occas', 'annonce']):
                continue
        # skip phrases that are clearly navigation or CTA-like
        if any(phrase in low for phrase in ['poster annonce','comparer','promo','offres','nous contacter','accueil','erreur','toggle','social']):
            continue
        # remove numeric-only tokens
        if re.fullmatch(r'[0-9\s]+', name):
            continue

        # Keep up to first 3 words (brand names may contain 2 words like 'Alfa Romeo')
        toks = [t for t in name.split() if t]
        toks = toks[:3]
        final = ' '.join(toks).title()
        if final not in cleaned:
            cleaned.append(final)
            # track likely logo-derived names (all-caps or from img alts)
            if b.isupper() or (len(toks) <= 3 and all(x[0].isupper() or x.isupper() for x in toks if x)):
                logo_candidates.append(final)

    # If we got strong logo candidates, prefer them first (they are less noisy)
    result = []
    seen = set()
    for lb in logo_candidates + cleaned:
        if lb not in seen:
            seen.add(lb)
            result.append(lb)
            if len(result) >= max_brands:
                break

    # Final safety filter: if caller requested neuf, remove any 'occasion' or digit-bearing entries
    if mode and mode.lower() == 'neuf':
        filtered_result = [r for r in result if not re.search(r'\boccasion\b', r, flags=re.I) and not re.search(r'\d', r)]
        # If filtering removed everything, fall back to the unfiltered result but log
        if filtered_result:
            return filtered_result
        # else fall through and return original (to avoid empty responses)

    return result
