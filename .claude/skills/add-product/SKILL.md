---
name: add-product
description: Add, change, reprice or remove a Be DC merchandise product (SKU) on the storefront. Use whenever a product, price, Printful link, product photo, Be ___ phrase or product DC fact changes.
---

# Add or change a Be DC product

A product lives in **four** places. A change is only done when all four agree.

| # | Place | What to change |
|---|---|---|
| 1 | `data/products.json` | Use `python scripts/add_product.py --id <slug> --title "B★DC …" --price 00.00 --desc "…" --be "Be …" --fact "…"` to add. Edit the JSON directly to change or remove. |
| 2 | `index.html` → `#shop` | Copy an existing `<article class="product-card" data-slug="…">` block. Match `data-slug` to the JSON `id`, and the title, price, Be ___ phrase and fact. |
| 3 | `assets/js/main.js` → `PRINTFUL_LINKS` | Add the slug. Use `''` until Jaap gives the real Printful URL (the card then shows "Notify me"). Never guess a URL. |
| 4 | `product-pricing-sheet.md` | Add a row: blank cost, retail, margin. Mark estimated costs as estimates. |

Product image: `assets/img/product-<slug>.jpg`, about the same size and aspect ratio as the others. Only use photos Jaap provided.

## Steps
1. Get from Jaap: name, blank (e.g. Bella+Canvas 3001), Printful cost, retail price, photo, Printful link (or "not yet").
2. Write the Be ___ phrase and DC fact with the `be-dc-brand` skill. Check the phrase isn't already used.
3. Make the four edits.
4. Verify:
   - `python -m json.tool data/products.json > /dev/null`
   - `node --check assets/js/main.js`
   - Every `data-slug` in `index.html` has a matching `id` in `products.json` and a key in `PRINTFUL_LINKS`, and the prices match.
   - Open the page locally (`npm start`) and look at the shop at desktop and phone width.
5. Report the four edits and paste the check output.

## Pricing guardrail
The current line runs 39% (hat) to 63% (mug) margin over Printful base cost, priced as a lifestyle brand, not a souvenir stand. If a new or changed price falls below 39%, or the base cost is still an estimate, flag it to Jaap instead of publishing. Remember the site promises free shipping over $50, which Printful still charges for.
