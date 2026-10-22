#!/usr/bin/env python3
"""
Pull the Printful store into data/products.json, the shop cards and the
pricing sheet. Run by .github/workflows/printful-sync.yml, which turns any
change into a PR for Jaap to review. Needs only a read-only token
(scope sync_products/read). See scripts/printful_api.py for where it comes from.

What it changes:
  - price of each linked product (Printful's lowest variant retail price)
  - new Printful products -> added as status "draft": not on the page until
    someone adds a "Be ___" phrase and a DC fact and sets status "live"
  - a missing product image -> the Printful thumbnail, saved under assets/img/printful/
  - the retail and margin cells in product-pricing-sheet.md
It never deletes anything. Products missing from Printful are only reported.

Usage:
  python scripts/printful_sync.py [--summary summary.md]
"""
import argparse
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import printful_api as pf  # noqa: E402
import render_shop  # noqa: E402

ROOT = render_shop.ROOT
DATA = render_shop.DATA
SHEET = ROOT / "product-pricing-sheet.md"
IMAGE_DIR = Path("assets/img/printful")


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower().replace("b★dc", "")).strip("-")
    return slug[:40].strip("-") or "product"


def unique_slug(base, taken):
    slug, n = base, 2
    while slug in taken:
        slug, n = f"{base}-{n}", n + 1
    return slug


def lowest_price(variants):
    prices = [(Decimal(str(v["retail_price"])), v.get("currency") or "USD")
              for v in variants if not v.get("is_ignored") and v.get("retail_price") not in (None, "")]
    return min(prices) if prices else (None, None)


def fmt(amount):
    return f"{amount:.2f}"


def update_sheet(sheet, name, price, notes):
    """Set the Retail price cell (and Margin/Margin %) on the row whose first cell is `name`."""
    lines = sheet.split("\n")
    for i, line in enumerate(lines):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        # Rows may add detail in brackets: "Hat (embroidered)" is the Hat row.
        if len(cells) != 6 or not (cells[0] == name or cells[0].startswith(name + " (")):
            continue
        cells[3] = render_shop.money(price)
        cost = re.search(r"\$(\d+(?:\.\d+)?)", cells[2])
        if cost:
            margin = price - Decimal(cost.group(1))
            cells[4] = f"${margin:.2f}"
            cells[5] = f"{(margin / price * 100):.0f}%" if price else "?"
        lines[i] = "| " + " | ".join(cells) + " |"
        return "\n".join(lines)
    notes.append(f"- Pricing sheet has no row for **{name}**: add its blank, base cost and retail {render_shop.money(price)}.")
    return sheet


def sync(token, log):
    products = json.loads(DATA.read_text(encoding="utf-8"))
    sheet = SHEET.read_text(encoding="utf-8")
    by_id = {p["printful_id"]: p for p in products if p.get("printful_id")}
    by_slug = {p["slug"]: p for p in products}
    by_ext = {str(p["printful_external_id"]).lstrip("#"): p for p in products if p.get("printful_external_id")}
    by_name = {p["printful_name"].strip().lower(): p for p in products if p.get("printful_name")}
    changes, new, notes = [], [], []
    seen = set()

    for item in pf.list_store_products(token):
        if item.get("is_ignored"):
            continue
        detail = pf.request("GET", f"/store/products/{int(item['id'])}", token=token) or {}
        info = detail.get("sync_product") or item
        price, currency = lowest_price(detail.get("sync_variants") or [])
        pid = int(info["id"])
        seen.add(pid)
        local = by_id.get(pid)
        if local is None:
            # Not linked yet: match the Printful external ID (shown as #abc123 in the
            # dashboard) or the exact Printful product name, set in data/products.json.
            ext = str(info.get("external_id") or "")
            for candidate in (by_ext.get(ext), by_slug.get(ext),
                              by_name.get(str(info.get("name") or "").strip().lower())):
                if candidate is not None and not candidate.get("printful_id"):
                    local = candidate
                    break
        if price is None:
            notes.append(f"- **{info.get('name')}** (Printful {pid}) has no priced variants; skipped.")
            continue

        prices = {Decimal(str(v["retail_price"])) for v in detail.get("sync_variants") or []
                  if not v.get("is_ignored") and v.get("retail_price") not in (None, "")}
        if len(prices) > 1:
            notes.append(f"- **{info.get('name')}**: variant prices range {render_shop.money(min(prices))}–"
                         f"{render_shop.money(max(prices))}; the card shows the lowest.")

        if local is None:
            slug = unique_slug(slugify(info.get("name") or f"product-{pid}"), by_slug)
            local = {"id": slug, "slug": slug, "status": "draft", "title": info.get("name") or slug,
                     "name": info.get("name") or slug, "be": "", "description": "", "dc_fact": "",
                     "price": fmt(price), "currency": currency, "image": "", "alt": info.get("name") or slug,
                     "printful_id": pid}
            products.append(local)
            by_slug[slug] = local
            new.append(local)
        else:
            if local.get("printful_id") != pid:
                local["printful_id"] = pid
                changes.append(f"- Linked **{local['title']}** to Printful product {pid}.")
            old = Decimal(str(local["price"]))
            if currency != local.get("currency"):
                notes.append(f"- **{local['title']}**: Printful prices it in {currency}, the site in "
                             f"{local.get('currency')}. Price not changed; set the store currency in Printful.")
            elif old != price:
                changes.append(f"- **{local['title']}**: price {render_shop.money(old)} → {render_shop.money(price)}")
                local["price"] = fmt(price)
                sheet = update_sheet(sheet, local.get("name") or local["title"], price, notes)

        if not local.get("image") and info.get("thumbnail_url"):
            try:
                saved = pf.download_image(info["thumbnail_url"], ROOT / IMAGE_DIR / local["slug"])
                local["image"] = Path(saved).relative_to(ROOT).as_posix()
                changes.append(f"- **{local['title']}**: image from Printful → `{local['image']}`")
            except (pf.PrintfulError, OSError) as e:
                notes.append(f"- **{local['title']}**: couldn't download the Printful image ({e}).")

    for p in products:
        if p.get("printful_id") and p["printful_id"] not in seen:
            notes.append(f"- **{p['title']}** is linked to Printful product {p['printful_id']}, which is gone or ignored in Printful. Still on the site; remove or relink it.")
        elif not p.get("printful_id") and p.get("status") == "live":
            notes.append(f"- **{p['title']}** isn't linked to a Printful product yet (set `printful_id` or the Printful external ID `{p['slug']}`).")

    for p in new:
        sheet = update_sheet(sheet, p["name"], Decimal(p["price"]), notes)

    DATA.write_text(json.dumps(products, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    SHEET.write_text(sheet, encoding="utf-8")
    page = render_shop.PAGE.read_text(encoding="utf-8")
    render_shop.PAGE.write_text(render_shop.render(page, products), encoding="utf-8")

    summary = ["## Printful sync", ""]
    summary += changes or ["- No price or image changes."]
    if new:
        summary += ["", "### New in Printful (drafts, not on the site yet)",
                    "Add a `Be ___` phrase and a DC fact (be-dc-brand rules), check `name`/`alt`, then set `\"status\": \"live\"` in `data/products.json` and run `python scripts/render_shop.py`."]
        summary += [f"- **{p['title']}** → slug `{p['slug']}`, {render_shop.money(p['price'])}" for p in new]
    if notes:
        summary += ["", "### Needs a look"] + notes
    summary += ["", "Buy buttons are not changed: links are the `buy_url` fields in `data/products.json`, set by hand (Printful's API has no buy links)."]
    log("\n".join(summary))
    return "\n".join(summary) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Pull the Printful store into the catalog and shop.")
    ap.add_argument("--summary", help="write a markdown summary (for the PR body) to this file")
    args = ap.parse_args()
    for stream in (sys.stdout, sys.stderr):  # "★" on a Windows console
        stream.reconfigure(encoding="utf-8", errors="replace")
    try:
        summary = sync(pf.get_token(), print)
    except (pf.PrintfulError, ValueError, KeyError) as e:
        sys.exit(f"printful_sync: {e}")
    if args.summary:
        Path(args.summary).write_text(summary, encoding="utf-8")


if __name__ == "__main__":
    main()
