---
name: add-product
description: Add, change, reprice or remove a Be DC merchandise product (SKU) on the storefront. Use whenever a product, price, Printful link, product photo, Be ___ phrase or product DC fact changes.
---

# Add or change a Be DC product

A product lives in these places. A change is only done when they agree.

| # | Place | What to change |
|---|---|---|
| 1 | Printful | New products: the `printful-product-creator` agent (`scripts/printful_create.py`, dry run first, `--apply` only after the owner's OK). Prices: always the Printful store's. The owner sets them in the Printful dashboard; the daily **Printful sync** PR brings them into the catalog, cards and pricing sheet. Never set a price by hand. |
| 2 | `data/products.json` | The source for the shop. Fields: `id`/`slug` (same), `status` (`live` or `draft`), `title` (with B★DC), `name` (short card label), `be`, `description`, `dc_fact`, `price`, `currency`, `image`, `alt`, `buy_url` (Quick Store link), `printful_id`, and `printful_external_id` (the `#…` ID in the Printful dashboard) or `printful_name` so the sync can link it. Add with `python scripts/add_product.py …`, or edit the JSON. |
| 3 | `index.html` → `#shop` | **Generated.** Run `python scripts/render_shop.py` after any JSON change; never edit the cards by hand. Only `live` products with a phrase, a fact and an image are shown. |
| 4 | `data/products.json` → `buy_url` | The product's Printful Quick Store link. Leave `""` until the owner gives the real link (the card then shows "Notify me"). Never guess a URL. |
| 5 | `product-pricing-sheet.md` | A row with blank, base cost, retail, margin. Mark estimated costs as estimates. The sync updates retail and margin for linked products. |

Product image: `assets/img/product-<slug>.jpg` (the owner's photos) or `assets/img/printful/<slug>.*` (downloaded by the sync). Images must be under `assets/`: bedc.shop serves nothing else.

## Steps
1. Get from the owner: name, blank (e.g. Bella+Canvas 3001), Printful cost, photo or Printful mockup, print file, buy link (or "not yet"). The starting price is the Printful store price; after that the sync keeps it in step.
2. Write the Be ___ phrase and DC fact with the `be-dc-brand` skill. Check the phrase isn't already used.
3. Make the edits above (for a new Printful product, the agent does 1–3).
4. Verify:
   - `python -m json.tool data/products.json > /dev/null`
   - `python scripts/render_shop.py --check`
   - `node --check assets/js/main.js`
   - Open the page locally (`npm start`) and look at the shop at desktop and phone width.
5. Report the edits and paste the check output.

## Pricing guardrail
The current line runs 39% (hat) to 63% (mug) margin on the retail price ((retail − Printful base cost) ÷ retail), priced as a lifestyle brand, not a souvenir stand. The sync PR flags a margin below 39%, an estimated base cost, or a missing one; the store's price still wins. Remember the site promises free shipping over $50, which Printful still charges for.
