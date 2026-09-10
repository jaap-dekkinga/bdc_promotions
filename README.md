# Be DC — storefront (`bdc_promotions`)

A single-page static site for **B★DC**, Washington, DC's first city logo and motto:
the story of the mark, the "Be ___" platform, the DC facts that started the project
in 2010, a seven-piece print-on-demand starter shop, and a contact form.

No framework, no build step — just `index.html` + `assets/`. Deploys to GitHub Pages
on every push to `main`.

## What's real vs. placeholder

- **Real:** the logo files, product photos, and lifestyle photography (from the Be DC
  project folder), the origin story in Jaap's own words, and the 2010 DC research
  figures — honestly framed as *why the project started*, not current-year stats.
- **Per-product content:** every card carries its own `Be ___` phrase and a "Did you
  know" DC fact, the way I LOVE NY packs a fact card with each item and DCMetroStore
  organizes the store around the Metro map. See the competitor storefront scan for
  the reasoning.
- **Placeholder:** the product photos are mock-ups of the blanks, not final printed
  samples. Retail prices are set for a lifestyle-brand feel (see
  `product-pricing-sheet.md`); the two "estimate" costs there (polo, hat) need the
  real Printful numbers before launch.

## Two edits before this is fully live

1. **Printful links** — open `assets/js/main.js`, find `PRINTFUL_LINKS` near the top,
   and paste each product's public URL against the matching slug once your Printful
   Quick Store is set up. Any slug left `""` shows a **Notify me** button that routes
   to the contact form instead of a dead link, so the site is safe to publish before
   the store is ready.
2. **Contact email** — the form opens the visitor's mail app addressed to
   `hello@b-dc.org` (`assets/js/main.js`, search for `mailto:`). Swap in the address
   you want to receive mail at, or wire it to a free formspree.io endpoint (second
   TODO in the same file) so messages land quietly in an inbox.

Keep `data/products.json` and the hard-coded cards in `index.html` in sync — the JSON
is the catalog reference (`scripts/add_product.py` appends to it); the HTML is what
actually renders.

## Deploying (GitHub Pages, $0/month)

`.github/workflows/static.yml` runs on every push to `main`: it uploads the repo root
and deploys it to GitHub Pages. Nothing to configure beyond **Settings → Pages →
Source: GitHub Actions**.

- `deploy-pages.yml` is the older gh-pages/peaceiris variant, now set to manual
  (`workflow_dispatch`) only so the two workflows don't race over the same
  deployment. Use one or the other, not both on push.
- To serve the site at `b-dc.org`, add a `CNAME` file at the repo root containing
  `b-dc.org` and point a DNS `CNAME` record at the Pages address.

## Files

```
index.html                   the whole site (story, platform, facts, shop, contact)
assets/css/style.css         brand styles — navy #002664 / red #BB133E
assets/js/main.js            nav toggle, Printful link config, contact form
assets/img/                  real logo, hero, and product images
data/products.json           catalog reference for the 7 starter SKUs (USD)
scripts/add_product.py       append a product to data/products.json
product-pricing-sheet.md     SKU blank costs, retail prices, and margins for Printful
.github/workflows/static.yml active GitHub Pages deploy
```
