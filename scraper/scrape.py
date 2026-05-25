"""
DealFalcon coupon scraper — Playwright edition.
Uses a real Chromium browser to bypass JS/Cloudflare blocks.
Sources tried per store (in order):
  1. CouponFollow  2. Honey (JoinHoney)  3. CouponBirds
Outputs: data/{store_id}.json
"""

import json
import os
import re
import time
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
INDEX_PATH = os.path.join(DATA_DIR, 'index.json')

NOW = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


# ── code validation ───────────────────────────────────────────────────────────

_SKIP = {
    'SHOW CODE', 'GET CODE', 'CLICK HERE', 'REVEAL CODE', 'SEE CODE',
    'VIEW CODE', 'COPY CODE', 'USE CODE', 'SALE', 'DEAL', 'FREE', 'N/A',
}

def clean_code(raw):
    if not raw:
        return None
    code = raw.strip().upper()
    code = re.sub(r'\s+', '', code)        # remove internal spaces
    if len(code) < 3 or len(code) > 25:
        return None
    if code in _SKIP:
        return None
    if not re.search(r'[A-Z0-9]', code):   # must have alphanumerics
        return None
    return code

def clean_desc(raw, fallback='Discount code'):
    desc = re.sub(r'\s+', ' ', (raw or '')).strip()
    return desc[:120] if len(desc) > 5 else fallback

def dedupe(codes):
    seen, out = set(), []
    for c in codes:
        k = c['code']
        if k not in seen:
            seen.add(k)
            out.append(c)
    return out


# ── per-source scrapers ───────────────────────────────────────────────────────

def scrape_couponfollow(page, domain):
    codes = []
    try:
        page.goto(f'https://couponfollow.com/site/{domain}',
                  wait_until='domcontentloaded', timeout=20000)
        page.wait_for_timeout(2500)

        # data-code attributes (most reliable)
        for el in page.query_selector_all('[data-code]'):
            raw = el.get_attribute('data-code') or ''
            code = clean_code(raw)
            if not code:
                continue
            desc_el = el.query_selector('.offer-title, .title, h3, p')
            desc = clean_desc(desc_el.inner_text() if desc_el else '', f'Discount at {domain}')
            codes.append({'code': code, 'description': desc})

        # JSON-LD fallback
        for script in page.query_selector_all('script[type="application/ld+json"]'):
            try:
                data = json.loads(script.inner_text())
                items = []
                if isinstance(data, dict) and data.get('@type') == 'ItemList':
                    items = data.get('itemListElement', [])
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
    except PWTimeout:
        pass
    except Exception as e:
        print(f"    couponfollow error: {e}")
    return codes


def scrape_honey(page, domain):
    codes = []
    try:
        slug = domain.replace('.com', '').replace('.', '-')
        page.goto(f'https://www.joinhoney.com/shop/{slug}',
                  wait_until='domcontentloaded', timeout=20000)
        page.wait_for_timeout(2500)

        # Honey renders code pills with spans
        for el in page.query_selector_all('[class*="CodePill"], [class*="code-pill"], [data-code]'):
            raw = el.get_attribute('data-code') or el.inner_text()
            code = clean_code(raw)
            if code:
                codes.append({'code': code, 'description': f'Discount at {domain}'})

        # Also try searching for text that looks like promo codes in the page
        # Honey sometimes puts them in title tags or spans
        for el in page.query_selector_all('span, p'):
            text = el.inner_text().strip()
            if 3 <= len(text) <= 20 and re.fullmatch(r'[A-Z0-9_\-]+', text.upper()):
                code = clean_code(text)
                if code:
                    codes.append({'code': code, 'description': f'Honey code for {domain}'})
    except PWTimeout:
        pass
    except Exception as e:
        print(f"    honey error: {e}")
    return codes


def scrape_couponbirds(page, domain):
    codes = []
    try:
        page.goto(f'https://www.couponbirds.com/codes/{domain}',
                  wait_until='domcontentloaded', timeout=20000)
        page.wait_for_timeout(2500)

        for el in page.query_selector_all(
            'span.coupon-code, .code-text, [class*="coupon-code"], '
            'input[readonly], [data-clipboard-text]'
        ):
            raw = (el.get_attribute('data-clipboard-text') or
                   el.get_attribute('value') or
                   el.inner_text())
            code = clean_code(raw)
            if not code:
                continue
            # Try to find description from parent
            parent = el.evaluate_handle('el => el.closest("[class*=coupon],[class*=offer]")')
            desc = f'Discount at {domain}'
            try:
                title_el = parent.as_element().query_selector(
                    '[class*=title], [class*=desc], h3, h4')
                if title_el:
                    desc = clean_desc(title_el.inner_text(), desc)
            except Exception:
                pass
            codes.append({'code': code, 'description': desc})
    except PWTimeout:
        pass
    except Exception as e:
        print(f"    couponbirds error: {e}")
    return codes


def scrape_retailmenot(page, domain):
    codes = []
    try:
        page.goto(f'https://www.retailmenot.com/view/{domain}',
                  wait_until='domcontentloaded', timeout=20000)
        page.wait_for_timeout(3000)

        for el in page.query_selector_all('[data-code], [class*="promo-code"], span.code'):
            raw = el.get_attribute('data-code') or el.inner_text()
            code = clean_code(raw)
            if code:
                parent = el.evaluate_handle('el => el.closest("article,[class*=offer],[class*=coupon]")')
                desc = f'Discount at {domain}'
                try:
                    t = parent.as_element().query_selector('h3, h4, [class*=title]')
                    if t:
                        desc = clean_desc(t.inner_text(), desc)
                except Exception:
                    pass
                codes.append({'code': code, 'description': desc})
    except PWTimeout:
        pass
    except Exception as e:
        print(f"    retailmenot error: {e}")
    return codes


# ── store entry point ─────────────────────────────────────────────────────────

def scrape_store(page, store):
    domain = store['domain']
    print(f"  [{store['name']}] {domain}")

    all_codes = []
    for fn in [scrape_couponfollow, scrape_honey, scrape_couponbirds, scrape_retailmenot]:
        batch = fn(page, domain)
        if batch:
            print(f"    {fn.__name__.replace('scrape_','')}: {len(batch)} found")
        all_codes += batch
        if len(dedupe(all_codes)) >= 8:
            break

    codes = dedupe(all_codes)[:20]

    # Mark first as best deal if multiple
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

    print(f"Scraping {len(stores)} stores with Playwright...\n")
    total = 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
            ]
        )
        ctx = browser.new_context(
            user_agent=(
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/124.0.0.0 Safari/537.36'
            ),
            viewport={'width': 1280, 'height': 800},
            locale='en-US',
        )
        ctx.add_init_script(
            "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"
        )
        page = ctx.new_page()

        for i, store in enumerate(stores):
            try:
                data = scrape_store(page, store)
                count = len(data['codes'])
                total += count
                with open(os.path.join(DATA_DIR, f"{store['id']}.json"), 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"    -> {count} codes saved\n")
            except Exception as e:
                print(f"  ERROR on {store['id']}: {e}\n")

            if i < len(stores) - 1:
                time.sleep(2)

        browser.close()

    print(f"Done. {total} codes across {len(stores)} stores.")


if __name__ == '__main__':
    main()
