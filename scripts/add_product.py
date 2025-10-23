#!/usr/bin/env python3
"""
Simple helper to add a product to data/products.json.

Usage:
  python scripts/add_product.py --id sticker-2 --title "Sticker 2" --price 2.50 --desc "New sticker"
"""
import argparse
import json
from pathlib import Path

DATA = Path('data/products.json')

def load():
    if DATA.exists():
        return json.loads(DATA.read_text())
    return []

def save(products):
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(products, indent=2))
    print(f"Saved {len(products)} products to {DATA}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--id', required=True)
    p.add_argument('--title', required=True)
    p.add_argument('--price', required=True)
    p.add_argument('--desc', default='')
    p.add_argument('--currency', default='EUR')
    args = p.parse_args()
    products = load()
    products.append({
        "id": args.id,
        "title": args.title,
        "description": args.desc,
        "price": str(args.price),
        "currency": args.currency
    })
    save(products)

if __name__ == '__main__':
    main()
