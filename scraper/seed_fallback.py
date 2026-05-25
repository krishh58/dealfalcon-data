"""
Runs after scrape.py. For any store with 0 codes, fills in curated seed codes.
Stores with scraped codes are left untouched.
"""

import json, os
from datetime import datetime, timezone
from seed import SEEDS, make_entry

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
NOW = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def main():
    index_path = os.path.join(DATA_DIR, 'index.json')
    with open(index_path) as f:
        stores = json.load(f)

    filled = 0
    for store in stores:
        sid = store['id']
        path = os.path.join(DATA_DIR, f'{sid}.json')

        existing = {'codes': []}
        if os.path.exists(path):
            try:
                with open(path) as f:
                    existing = json.load(f)
            except Exception:
                pass

        if len(existing.get('codes', [])) > 0:
            continue  # scraper found real codes, leave it alone

        codes_raw = SEEDS.get(sid, [])
        if not codes_raw:
            continue

        codes = [make_entry(c, d, i == 0 and len(codes_raw) > 1)
                 for i, (c, d) in enumerate(codes_raw)]

        out = {
            'store_id': sid,
            'updated_at': NOW,
            'codes': codes,
            'ai_deals': existing.get('ai_deals', []),
        }
        with open(path, 'w') as f:
            json.dump(out, f, indent=2)

        filled += 1
        print(f"  seeded {store['name']}: {len(codes)} codes")

    if filled:
        print(f"\nFilled {filled} stores with seed codes.")
    else:
        print("All stores had scraped codes — no fallback needed.")

if __name__ == '__main__':
    main()
