#!/usr/bin/env python3
"""
Create one new product in Printful from a draft file, then add it to the
catalog and the shop. Used by the printful-product-creator agent.

Without --apply this is a dry run: it checks the draft against the brand
rules and the Printful catalog, and prints the exact API call. Nothing is
created. With --apply it calls POST /store/products (a hook makes Claude ask
Jaap first), adds the product to data/products.json and re-renders the shop.
The token needs scope sync_products (write); see scripts/printful_api.py.

Draft file (JSON), for example ../bdc-growth/printful-drafts/sticker.json:
  {
    "slug": "sticker",
    "title": "B★DC Sticker",
    "name": "Sticker",
    "be": "Be stuck",
    "dc_fact": "One checkable sentence about DC.",
    "description": "Die-cut vinyl sticker with the B★DC mark.",
    "alt": "B★DC die-cut sticker",
    "variants": [{"variant_id": 10163, "retail_price": "4.00"}],
    "files": [{"type": "default", "url": "https://.../print-file.png"}]
  }
variant_id comes from the Printful catalog (GET /products/{product_id}).
Each file needs an https "url" or a Printful file library "id".

Usage:
  python scripts/printful_create.py DRAFT.json            dry run
  python scripts/printful_create.py DRAFT.json --apply    create it
"""
import argparse
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import printful_api as pf  # noqa: E402
import render_shop  # noqa: E402

BE = re.compile(r"^Be [a-z]+$")


def check_draft(draft, products):
    problems = []
    slug = draft.get("slug", "")
    if not render_shop.SLUG.match(slug) or len(slug) > 40:
        problems.append("slug: lowercase letters, digits and dashes, at most 40 characters")
    if any(p["slug"] == slug or p["id"] == slug for p in products):
        problems.append(f"slug {slug!r} is already in data/products.json")
    title = draft.get("title", "")
    if "B★DC" not in title or "BDC" in title.replace("B★DC", ""):
        problems.append('title must contain "B★DC" (with the star) and never "BDC"')
    be = draft.get("be", "")
    if not BE.match(be):
        problems.append('be: "Be" plus one lowercase word, e.g. "Be stuck"')
    elif any((p.get("be") or "").lower() == be.lower() for p in products):
        problems.append(f"be: {be!r} is already used by another product")
    fact = (draft.get("dc_fact") or "").strip()
    if not fact or re.search(r"[.!?]\s+[A-Z]", fact) or len(fact) > 220:
        problems.append("dc_fact: exactly one checkable sentence (be-dc-brand)")
    for field in ("title", "name", "description", "dc_fact", "alt"):
        if "®" in str(draft.get(field, "")):
            problems.append(f"{field}: no ® (the trademark is pending)")
    variants = draft.get("variants") or []
    if not variants:
        problems.append("variants: at least one {variant_id, retail_price}")
    for v in variants:
        try:
            if int(v["variant_id"]) <= 0 or Decimal(str(v["retail_price"])) <= 0:
                raise ValueError
        except (KeyError, ValueError, TypeError, InvalidOperation):
            problems.append(f"variant {v}: needs a positive variant_id and retail_price")
    files = draft.get("files") or []
    if not files:
        problems.append("files: at least one print file (https url or Printful file id)")
    for f in files:
        if not (str(f.get("url", "")).startswith("https://") or isinstance(f.get("id"), int)):
            problems.append(f"file {f}: needs an https url or an integer file library id")
    return problems


def check_catalog(variants):
    """Look up each variant in Printful's public catalog (no token needed)."""
    names = []
    for v in variants:
        info = pf.request("GET", f"/products/variant/{int(v['variant_id'])}", auth=False) or {}
        variant = info.get("variant") or {}
        names.append(f"{v['variant_id']}: {variant.get('name', '?')} "
                     f"(Printful base price {variant.get('price', '?')} {variant.get('currency', '')})".rstrip())
    return names


def payload(draft):
    files = [{k: f[k] for k in ("type", "url", "id", "options") if k in f} for f in draft["files"]]
    return {
        "sync_product": {"external_id": draft["slug"], "name": draft["title"]},
        "sync_variants": [{
            "external_id": f"{draft['slug']}-{int(v['variant_id'])}",
            "variant_id": int(v["variant_id"]),
            "retail_price": f"{Decimal(str(v['retail_price'])):.2f}",
            "files": files,
        } for v in draft["variants"]],
    }


def main():
    # allow_abbrev=False: "--ap" must not count as "--apply" (the approval hook matches the full flag).
    ap = argparse.ArgumentParser(description="Create a Printful product from a draft file.", allow_abbrev=False)
    ap.add_argument("draft", help="draft JSON file")
    ap.add_argument("--apply", action="store_true", help="really create it (otherwise dry run)")
    ap.add_argument("--skip-catalog-check", action="store_true", help="don't look up variants in the public catalog")
    args = ap.parse_args()
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")

    draft = json.loads(Path(args.draft).read_text(encoding="utf-8"))
    products = json.loads(render_shop.DATA.read_text(encoding="utf-8"))
    problems = check_draft(draft, products)
    if problems:
        sys.exit("Draft not ready:\n- " + "\n- ".join(problems))

    try:
        if not args.skip_catalog_check:
            print("Catalog variants:\n  " + "\n  ".join(check_catalog(draft["variants"])))
        body = payload(draft)
        print("\nPOST https://api.printful.com/store/products\n" + json.dumps(body, indent=2, ensure_ascii=False))
        if not args.apply:
            print("\nDry run: nothing was created. Re-run with --apply after Jaap approves.")
            return

        token = pf.get_token()
        try:
            pf.request("GET", f"/store/products/@{draft['slug']}", token=token)
            sys.exit(f"A Printful product with external ID {draft['slug']!r} already exists. Not creating a duplicate.")
        except pf.PrintfulError as e:
            if "HTTP 404" not in str(e):
                raise
        created = pf.request("POST", "/store/products", body=body, token=token, allow_write=True) or {}
    except pf.PrintfulError as e:
        sys.exit(f"printful_create: {e}")

    prices = [Decimal(str(v["retail_price"])) for v in draft["variants"]]
    products.append({
        "id": draft["slug"], "slug": draft["slug"], "status": "live",
        "title": draft["title"], "name": draft.get("name") or draft["title"],
        "be": draft["be"], "description": draft.get("description", ""), "dc_fact": draft["dc_fact"],
        "price": f"{min(prices):.2f}", "currency": "USD",
        "image": "", "alt": draft.get("alt") or draft["title"],
        "printful_id": created.get("id"),
    })
    render_shop.DATA.write_text(json.dumps(products, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    page = render_shop.PAGE.read_text(encoding="utf-8")
    render_shop.PAGE.write_text(render_shop.render(page, products), encoding="utf-8")
    print(f"\nCreated Printful product {created.get('id')} and added {draft['slug']!r} to data/products.json.")
    print("It shows on the site once it has an image: the next Printful sync downloads the thumbnail,")
    print("or add a photo under assets/img/ and set \"image\". Also add a row to product-pricing-sheet.md.")


if __name__ == "__main__":
    main()
