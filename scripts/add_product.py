#!/usr/bin/env python3
"""
Simple helper to add a product to data/products.json.

data/products.json is the source for the shop: after saving, this re-renders
the shop cards in index.html (scripts/render_shop.py). The product is shown
only with status "live", a Be ___ phrase, a DC fact and an image; otherwise
it's saved as a draft.

For a product that should also exist in Printful, use the
printful-product-creator agent (scripts/printful_create.py) instead.

Usage:
  python scripts/add_product.py --id sticker-2 --title "B★DC Sticker" --name "Sticker" \
    --price 4.00 --desc "Die-cut B★DC sticker." --be "Be stuck" --fact "A DC fact for the hang-tag." \
    --image assets/img/product-sticker-2.jpg --alt "B★DC die-cut sticker"
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_shop  # noqa: E402

DATA = render_shop.DATA


def load():
    if DATA.exists():
        return json.loads(DATA.read_text(encoding='utf-8'))
    return []


def save(products):
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(products, indent=2, ensure_ascii=False) + "\n", encoding='utf-8')
    print(f"Saved {len(products)} products to {DATA.relative_to(render_shop.ROOT)}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--id', required=True)
    p.add_argument('--title', required=True)
    p.add_argument('--price', required=True)
    p.add_argument('--name', default='', help='short label on the card; defaults to --title')
    p.add_argument('--desc', default='')
    p.add_argument('--slug', default='', help='URL slug; defaults to --id')
    p.add_argument('--be', default='', help='the "Be ___" phrase for this piece')
    p.add_argument('--fact', default='', help='DC fact for the product card / hang-tag')
    p.add_argument('--image', default='', help='image path under assets/')
    p.add_argument('--alt', default='', help='image alt text; defaults to --title')
    p.add_argument('--currency', default='USD')
    args = p.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    products = load()
    ready = bool(args.be and args.fact and args.image)
    products.append({
        "id": args.id,
        "slug": args.slug or args.id,
        "status": "live" if ready else "draft",
        "title": args.title,
        "name": args.name or args.title,
        "be": args.be,
        "description": args.desc,
        "dc_fact": args.fact,
        "price": str(args.price),
        "currency": args.currency,
        "image": args.image,
        "alt": args.alt or args.title,
        "printful_id": None
    })
    save(products)
    if not ready:
        print("Saved as a draft (needs --be, --fact and --image to show on the site).")
    page = render_shop.PAGE.read_text(encoding="utf-8")
    try:
        render_shop.PAGE.write_text(render_shop.render(page, products), encoding="utf-8")
    except ValueError as e:
        sys.exit(f"render_shop: {e}")
    print(f"Rendered {sum(1 for q in products if render_shop.is_shown(q))} of {len(products)} products into index.html")


if __name__ == '__main__':
    main()
