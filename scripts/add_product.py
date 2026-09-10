#!/usr/bin/env python3
"""
Simple helper to add a product to data/products.json.

This file is the catalog reference for the Be DC starter line. The storefront
(index.html) currently hard-codes the same seven products so it can be served as
flat HTML; keep the two in sync when you change one.

Usage:
  python scripts/add_product.py --id sticker-2 --title "B★DC Sticker" --price 4.00 \
    --desc "Die-cut B★DC sticker." --be "Be stuck" --fact "A DC fact for the hang-tag."
"""
import argparse
import json
from pathlib import Path

DATA = Path('data/products.json')

def load():
    if DATA.exists():
        return json.loads(DATA.read_text(encoding='utf-8'))
    return []

def save(products):
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(products, indent=2) + "\n", encoding='utf-8')
    print(f"Saved {len(products)} products to {DATA}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--id', required=True)
    p.add_argument('--title', required=True)
    p.add_argument('--price', required=True)
    p.add_argument('--desc', default='')
    p.add_argument('--slug', default='', help='URL slug; defaults to --id')
    p.add_argument('--be', default='', help='the "Be ___" phrase for this piece')
    p.add_argument('--fact', default='', help='DC fact for the product card / hang-tag')
    p.add_argument('--currency', default='USD')
    args = p.parse_args()
    products = load()
    products.append({
        "id": args.id,
        "slug": args.slug or args.id,
        "title": args.title,
        "be": args.be,
        "description": args.desc,
        "dc_fact": args.fact,
        "price": str(args.price),
        "currency": args.currency
    })
    save(products)

if __name__ == '__main__':
    main()
