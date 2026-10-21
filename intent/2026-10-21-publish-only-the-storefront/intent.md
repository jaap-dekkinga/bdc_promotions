# Publish only the storefront, not the whole repo

- **Author:** Jaap Dekkinga (drafted with Claude)
- **Date:** 2026-10-21
- **Status:** accepted (implemented on branch growth-agents)
- **Source:** site problem

## Problem
The deploy step in `.github/workflows/static.yml` uploads the entire repo root (`path: '.'`) to GitHub Pages.
Every file in the repo is therefore public, including files never meant for shoppers.
Checked 2026-10-21: `https://jaap-dekkinga.github.io/bdc_promotions/product-pricing-sheet.md` loads and shows blank costs and margins per SKU.
The new working files (`CLAUDE.md`, `REVIEW.md`, `intent/`, `docs/`, `.claude/`) would be published too as soon as they are pushed.
Anyone, including competitors and partners being pitched, can read internal pricing and plans.

## Proposed outcome
The live site serves only what a shopper needs: `index.html`, `assets/`, and anything `index.html` actually loads.
Internal files stay in the repo for Jaap and Claude but return 404 on the live site.

## Affected users and systems
- `.github/workflows/static.yml` (the `deploy` job)
- Possibly `data/products.json` (keep public only if the page loads it; today it doesn't)
- GitHub Pages; later the `b-dc.org` domain (a `CNAME` file must be in the published folder)

## Constraints
- $0/month, still GitHub Pages
- `validate` job keeps running on the full repo as it does now
- No change to how the site looks

## Out of scope
- Moving to Shopify or another host (Phase 2 of the launch plan)
- Changing the pricing itself

## Open questions
- [ ] Is anything already linking to the public `README.md` or pricing sheet? (Assume no.)
- [ ] Copy-to-a-`_site`-folder step, or move the site files into a `site/` folder in the repo?
- [ ] Should `deploy-pages.yml` (manual fallback) get the same fix or be deleted?

## Update 2026-10-21
- The `_site` change (PR #1) fixed the GitHub Pages copy, but **bedc.shop is Hostinger** (hPanel Git deploy of `main`), not GitHub Pages, so the files stayed public there.
- Follow-up: a root `.htaccess` allowlist (branch `htaccess-allowlist`) makes bedc.shop serve only `/`, `index.html` and `assets/`.
- The pricing sheet's costs stay readable in the public GitHub repo and its history; removing them from the repo would be a separate intent.
