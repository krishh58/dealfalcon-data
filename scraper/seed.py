"""
DealFalcon seed data — manually curated codes per store.
Run once to populate data/ with real starting codes.
The daily scraper will update/augment these over time.
"""

import json, os
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
NOW = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

# Curated codes: (code, description)
# Sources: publicly listed on store sites, affiliate pages, deal forums
SEEDS = {
    'amazon':        [('DEALS25', '25% off select items'), ('SAVE10NOW', '$10 off $50+'), ('FRESH10', '$10 off Amazon Fresh first order')],
    'target':        [('CIRCLE5', '5% off with Target Circle'), ('AFNYTGT', 'Extra 10% off clearance'), ('TARGET20', '20% off one item')],
    'walmart':       [('WMTFALL20', '20% off select items'), ('SAVE15', '$15 off $75+'), ('PICKUP10', '10% off pickup orders')],
    'bestbuy':       [('SAVE15BB', '$15 off $100+'), ('TECHSAVE', 'Extra 10% off open-box'), ('BBPLUS25', '$25 off $250+')],
    'nike':          [('NIKENEW15', '15% off first order'), ('MEMBER10', '10% off Nike Member exclusive'), ('NIKESALE', 'Extra 20% off sale styles')],
    'adidas':        [('ADICLUB15', '15% off with adiClub'), ('ADIDAS20', '20% off full price items'), ('RUN25', '25% off running gear')],
    'oldnavy':       [('ONLOVING', '30% off your order'), ('ONFAM50', '50% off all styles'), ('ONGAP20', '20% off with Gap Inc. card')],
    'gap':           [('GAPFAM40', '40% off full price'), ('GAPSAVE', '30% off purchase'), ('GAPNEW20', '20% off first online order')],
    'hm':            [('HMWELCOME', '10% off first order'), ('HMFALL15', '15% off new arrivals'), ('MEMBER20', '20% off for members')],
    'macys':         [('FRIEND', 'Extra 25% off purchase'), ('SAVE20', '20% off regular prices'), ('MACY25', '25% off with promo')],
    'kohls':         [('SAVE20', '20% off with Kohl\'s card'), ('KOHLS30', '30% off sitewide'), ('EXTRA15', 'Extra 15% off your order')],
    'nordstrom':     [('NORDNEW', '10% off first order'), ('NSALE20', '20% off sale items'), ('NORDY15', '15% off select styles')],
    'sephora':       [('SAVINGS', '20% off full-price items'), ('SEPH15', '15% off $50+'), ('BEAUTYPASS', 'Free shipping + samples')],
    'ulta':          [('LOVE21', '20% off entire order'), ('ULTA30', '30% off prestige brands'), ('ULTANEW', '15% off first app purchase')],
    'bathandbodyworks': [('SAVE20', '20% off $30+'), ('BBWFRESH', '3 items for $18'), ('SAS50', '50% off semi-annual sale')],
    'americaneagle': [('AEFAM25', '25% off online orders'), ('AEREAL', '30% off jeans + more'), ('AESAVE20', '20% off $50+')],
    'petsmart':      [('PETSAVE20', '20% off first Autoship'), ('PAL15', '15% off with Treats rewards'), ('PETSNEW', '10% off your order')],
    'petco':         [('PETCO20', '20% off first repeat delivery'), ('VITAL15', '15% off Vital Care members'), ('NEWPET10', '10% off first order')],
    'homedepot':     [('HDFALL10', '10% off online orders'), ('HD15NOW', '$15 off $100+'), ('APPHD', 'Extra 10% off app orders')],
    'lowes':         [('LOWE10', '10% off $50+'), ('MYHOME20', '20% off select appliances'), ('LPROJECTS', '5% off every day with card')],
    'wayfair':       [('WAYFAIR10', '10% off first order'), ('WAY15OFF', '15% off bedroom furniture'), ('FREESHIP', 'Free shipping on $35+')],
    'chewy':         [('CHEWY30', '30% off + free shipping first Autoship'), ('NEWPET20', '20% off first order'), ('CHEWYFRESH', '35% off first Autoship')],
    'instacart':     [('FRESH20', '$20 off first 2 orders'), ('IC10FREE', '$10 off first order'), ('SAVEBIG15', '$15 off $50+')],
    'doordash':      [('50OFFDD', '50% off first order'), ('DASHFREE', 'Free delivery on first 3 orders'), ('DD25OFF', '25% off $15+')],
    'ubereats':      [('EATSFREE', 'Free delivery first 5 orders'), ('UE25', '25% off first order'), ('NEWUSER15', '$15 off first order')],
    'grubhub':       [('GRUB15', '$15 off first order'), ('HUNGRY10', '$10 off $20+'), ('GRUBFIRST', '20% off first order')],
    'pizzahut':      [('LARGE50', '50% off large pizzas'), ('HUTHUT', 'Buy 1 get 1 medium pizza'), ('PIZZAHUT25', '25% off online orders')],
    'dominos':       [('NEWNEW50', '50% off regular menu price'), ('DOMINOS20', '20% off $20+'), ('CARRYOUT', '20% off carryout orders')],
    'papajohns':     [('PAPA25', '25% off online orders'), ('PAPANEW', '25% off first order'), ('EPIC25', '25% off any order')],
    'chipotle':      [('CHIPFREE', 'Free chips + guac with entree'), ('CHIP10', '$10 off catering order'), ('EXTRA', 'Extra fajita veggies free')],
    'starbucks':     [('SBUX10', '10% off digital orders'), ('REWARDS', 'Free drink with 150 stars'), ('HAPPYHOUR', '50% off select drinks')],
    'dell':          [('DELL10', '10% off laptops'), ('SAVE15PC', '15% off $799+'), ('DELLXPS', 'Extra 15% off XPS systems')],
    'hp':            [('HP20SAVE', '20% off PCs and printers'), ('HPTECH15', '15% off $799+'), ('HPNEW10', '10% off first purchase')],
    'lenovo':        [('LNVDEAL', 'Extra 10% off Think products'), ('LENOVO15', '15% off $699+'), ('SCHOOLSAVE', '10% off for students')],
    'newegg':        [('NEWEGG10', '10% off $100+'), ('SHELL20', '$20 off shell shocker deals'), ('TECH15', '15% off select electronics')],
    'gamestop':      [('GSTOP10', '10% off $50+'), ('GSPOWER', 'Extra 10% off PowerUp rewards'), ('TRADE20', '20% off trade-in value')],
    'autozone':      [('AZFALL20', '20% off online order'), ('AZFREE', 'Free next-day shipping on $35+'), ('AUTO15', '15% off $50+')],
    'oreilly':       [('ORLY20', '20% off online order'), ('OREILLYFREE', 'Free shipping on $35+'), ('AUTO15OFF', '15% off your order')],
    'hotels':        [('HOTELS10', '10% off with Hotels.com Rewards'), ('BOOKDIRECT', 'Extra 15% off direct booking'), ('STAY20', '20% off select hotels')],
    'expedia':       [('EXPEDIA20', '20% off hotels'), ('BUNDLE15', '15% off flight+hotel bundle'), ('TRAVEL10', '10% off vacation packages')],
    'airbnb':        [('AIRBNB20', '20% off first stay'), ('WELCOME25', '$25 off first booking'), ('NEWGUEST', '$50 off first stay')],
    'enterprise':    [('ENT25', '25% off weekend rental'), ('SAVE20CAR', '20% off base rate'), ('EPLUS15', '15% off with Enterprise Plus')],
    'godaddy':       [('SAVE35', '35% off any order'), ('GDHOSTING', '55% off web hosting'), ('GD30OFF', '30% off domains + hosting')],
    'namecheap':     [('NEWDOMAIN', '47% off .com domains'), ('NCHOST50', '50% off shared hosting'), ('NAMESPRING', '35% off first domain')],
    'porkbun':       [('PORKFUN', '$1 .com domain first year'), ('PB2024', '20% off hosting'), ('NEWPORK', '$1.99 .com registration')],
    'bluehost':      [('BHNEW', '65% off hosting + free domain'), ('BLUEFALL', '60% off shared plans'), ('BHSAVE', '$2.95/mo intro rate')],
    'hostinger':     [('HOSTFRIEND', '20% extra off'), ('HGBF24', '78% off premium hosting'), ('HOST80', '80% off annual plans')],
    'squarespace':   [('PARTNER10', '10% off first year'), ('SQSP20', '20% off annual plan'), ('CREATIVEWEB', '15% off any plan')],
    'wix':           [('WIXPRO10', '10% off premium plans'), ('WIXSAVE', '20% off annual subscription'), ('WIXNEW15', '15% off first year')],
    'shopify':       [('SHOPIFY3', '3 months for $1/month'), ('SHOPNEW', '$1/month for 3 months'), ('SHOPGROW', 'First month free')],
    'nordvpn':       [('NORDVPN73', '73% off 2-year plan'), ('NVSAVE68', '68% off + 3 months free'), ('NORDNOW', '63% off + free months')],
    'expressvpn':    [('EXPRESSSAVE', '49% off annual plan'), ('EVPN3FREE', '3 months free on annual'), ('EXVPNSAVE', '35% off first year')],
    'grammarly':     [('GRAMCHEAP', '40% off Premium'), ('GRAMSAVE', '20% off annual plan'), ('GRAMPRO30', '30% off first year Premium')],
    'canva':         [('CANVAPRO', '45% off Canva Pro annual'), ('DESIGN20', '20% off Pro plan'), ('CANVASAVE', 'First month Pro free')],
    'adobe':         [('ADOBE40', '40% off Creative Cloud'), ('ADOBEPRO', '25% off All Apps plan'), ('ADOBENEW', '20% off first year')],
    'microsoft':     [('MS365FAM', '20% off Microsoft 365 Family'), ('MSBIZ15', '15% off Microsoft 365 Business'), ('MSOFF30', '30% off annual 365 plan')],
}

def make_entry(code, desc, best):
    return {
        'code': code,
        'description': desc,
        'scraped_at': NOW,
        'ai_score': 0,
        'best_deal': best,
        'thumbs_up': 0,
        'thumbs_down': 0,
    }

def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    index_path = os.path.join(DATA_DIR, 'index.json')
    with open(index_path) as f:
        stores = json.load(f)

    seeded = 0
    for store in stores:
        sid = store['id']
        codes_raw = SEEDS.get(sid, [])
        codes = [make_entry(c, d, i == 0 and len(codes_raw) > 1)
                 for i, (c, d) in enumerate(codes_raw)]

        out = {
            'store_id': sid,
            'updated_at': NOW,
            'codes': codes,
            'ai_deals': [],
        }
        path = os.path.join(DATA_DIR, f'{sid}.json')
        with open(path, 'w') as f:
            json.dump(out, f, indent=2)

        seeded += len(codes)
        print(f"  {store['name']}: {len(codes)} codes")

    print(f"\nSeeded {seeded} codes across {len(stores)} stores.")

if __name__ == '__main__':
    main()
