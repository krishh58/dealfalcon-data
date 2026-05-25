"""
DealFalcon coupon scraper.
Uses curl_cffi to impersonate Chrome's TLS fingerprint — bypasses Cloudflare
without needing a browser binary.
Sources per store: CouponFollow → CouponBirds → RetailMeNot (fallback chain)
"""

import json
import os
import re
import time
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from curl_cffi import requests as cffi_requests

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
INDEX_PATH = os.path.join(DATA_DIR, 'index.json')
NOW = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

SESSION = cffi_requests.Session(impersonate="chrome124")

# ── helpers ───────────────────────────────────────────────────────────────────

_SKIP = {
    'SHOW CODE', 'GET CODE', 'CLICK HERE', 'REVEAL CODE', 'SEE CODE',
    'VIEW CODE', 'COPY CODE', 'USE CODE', 'SALE', 'DEAL', 'N/A', 'ONLINE',
}

def _get(url):
    try:
        r = SESSION.get(url, timeout=20)
        if r.status_code == 200:
            return r.text
        print(f"    HTTP {r.status_code}: {url}")
    except Exception as e:
        print(f"    GET failed ({url}): {e}")
    return None

def clean_code(raw):
    if not raw:
        return None
    code = re.sub(r'\s+', '', raw.strip().upper())
    if len(code) < 3 or len(code) > 25:
        return None
    if code in _SKIP:
        return None
    if not re.search(r'[A-Z0-9]', code):
        return None
    # Must be alphanumeric (with optional dash/underscore)
    if not re.fullmatch(r'[A-Z0-9_\-]+', code):
        return None
    return code

def clean_desc(raw, fallback='Discount code'):
    desc = re.sub(r'\s+', ' ', (raw or '')).strip()
    return desc[:120] if len(desc) > 4 else fallback

def dedupe(codes):
    seen, out = set(), []
    for c in codes:
        k = c['code']
        if k not in seen:
            seen.add(k)
            out.append(c)
    return out


# ── scrapers ──────────────────────────────────────────────────────────────────

def scrape_couponfollow(domain):
    html = _get(f'https://couponfollow.com/site/{domain}')
    if not html:
        return []
    soup = BeautifulSoup(html, 'lxml')
    codes = []

    # data-code attributes
    for el in soup.find_all(attrs={'data-code': True}):
        code = clean_code(el.get('data-code', ''))
        if not code:
            continue
        desc_el = el.find(class_=re.compile(r'title|desc|name|offer', re.I)) \
                  or el.find(['h3', 'h4', 'p'])
        desc = clean_desc(desc_el.get_text() if desc_el else '', f'Discount at {domain}')
        codes.append({'code': code, 'description': desc})

    # JSON-LD
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string or '')
            items = []
            if isinstance(data, dict) and data.get('@type') == 'ItemList':
                items = data.get('itemListElement', [])
            elif isinstance(data, list):
                for d in data:
                    if isinstance(d, dict) and d.get('@type') == 'ItemList':
                        items += d.get('itemListElement', [])
            for item in items:
                offer = item.get('item', item)
                code = clean_code(offer.get('alternateName') or offer.get('name', ''))
                if code:
                    codes.append({
                        'code': code,
                        'description': clean_desc(offer.get('description', ''), f'Discount at {domain}')
                    })
        except Exception:
            pass

    return codes


def scrape_couponbirds(domain):
    html = _get(f'https://www.couponbirds.com/codes/{domain}')
    if not html:
        return []
    soup = BeautifulSoup(html, 'lxml')
    codes = []

    for el in soup.select(
        'span.coupon-code, .code-text, [class*="coupon-code"], '
        'input[readonly], [data-clipboard-text], [data-coupon-code]'
    ):
        raw = (el.get('data-clipboard-text') or el.get('data-coupon-code')
               or el.get('value') or el.get_text())
        code = clean_code(raw)
        if not code:
            continue
        parent = el.find_parent(class_=re.compile(r'coupon|offer|deal', re.I))
        desc = f'Discount at {domain}'
        if parent:
            d = parent.find(class_=re.compile(r'title|desc', re.I))
            if d:
                desc = clean_desc(d.get_text(), desc)
        codes.append({'code': code, 'description': desc})

    return codes


def scrape_retailmenot(domain):
    html = _get(f'https://www.retailmenot.com/view/{domain}')
    if not html:
        return []
    soup = BeautifulSoup(html, 'lxml')
    codes = []

    for el in soup.find_all(attrs={'data-code': True}):
        code = clean_code(el.get('data-code', ''))
        if not code:
            continue
        parent = el.find_parent(['article', 'div'], class_=re.compile(r'offer|coupon|promo', re.I))
        desc = f'Discount at {domain}'
        if parent:
            t = parent.find(class_=re.compile(r'title|headline', re.I)) or parent.find(['h3', 'h4'])
            if t:
                desc = clean_desc(t.get_text(), desc)
        codes.append({'code': code, 'description': desc})

    # Also try input fields with codes
    for el in soup.select('input[type=text][value], input[readonly][value]'):
        val = el.get('value', '')
        code = clean_code(val)
        if code:
            codes.append({'code': code, 'description': f'Discount at {domain}'})

    return codes


def scrape_dealhack(domain):
    slug = domain.replace('.com', '').replace('.', '-')
    html = _get(f'https://dealhack.com/coupons/{slug}')
    if not html:
        return []
    soup = BeautifulSoup(html, 'lxml')
    codes = []

    for el in soup.select('[data-clipboard-text], [data-coupon-code], .coupon-code'):
        raw = (el.get('data-clipboard-text') or el.get('data-coupon-code') or el.get_text())
        code = clean_code(raw)
        if not code:
            continue
        parent = el.find_parent(class_=re.compile(r'coupon|offer|deal|promo', re.I))
        desc = f'Discount at {domain}'
        if parent:
            d = parent.find(class_=re.compile(r'title|desc|name', re.I))
            if d:
                desc = clean_desc(d.get_text(), desc)
        codes.append({'code': code, 'description': desc})

    return codes


# ── store entry point ─────────────────────────────────────────────────────────

SCRAPERS = [scrape_couponfollow, scrape_couponbirds, scrape_retailmenot, scrape_dealhack]

def scrape_store(store):
    domain = store['domain']
    print(f"  [{store['name']}] {domain}")
    all_codes = []

    for fn in SCRAPERS:
        if len(dedupe(all_codes)) >= 8:
            break
        try:
            batch = fn(domain)
            if batch:
                print(f"    {fn.__name__.replace('scrape_', '')}: {len(batch)} found")
            all_codes += batch
        except Exception as e:
            print(f"    {fn.__name__} error: {e}")
        time.sleep(1)

    codes = dedupe(all_codes)[:20]

    result = []
    for i, c in enumerate(codes):
        result.append({
            'code': c['code'],
            'description': c['description'],
            'scraped_at': NOW,
            'ai_score': 0,
            'best_deal': i == 0 and len(codes) > 1,
            'thumbs_up': 0,
            'thumbs_down': 0,
        })

    return {
        'store_id': store['id'],
        'updated_at': NOW,
        'codes': result,
        'ai_deals': [],
    }


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(INDEX_PATH) as f:
        stores = json.load(f)

    print(f"Scraping {len(stores)} stores...\n")
    total = 0

    for i, store in enumerate(stores):
        try:
            data = scrape_store(store)
            count = len(data['codes'])
            total += count
            with open(os.path.join(DATA_DIR, f"{store['id']}.json"), 'w') as f:
                json.dump(data, f, indent=2)
            print(f"    -> {count} codes\n")
        except Exception as e:
            print(f"  ERROR {store['id']}: {e}\n")

        if i < len(stores) - 1:
            time.sleep(2)

    print(f"Done. {total} codes across {len(stores)} stores.")


if __name__ == '__main__':
    main()


if __name__ == '__main__':
    main()
