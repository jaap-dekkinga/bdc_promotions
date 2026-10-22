# Be DC — storefront (`bdc_promotions`)

A single-page static site for **B★DC**, Washington, DC's first city logo and motto:
the story of the mark, the "Be ___" platform, the DC facts that started the project
in 2010, a seven-piece print-on-demand starter shop, and a contact form.

No framework, no build step — just `index.html` + `assets/`. Live at https://bedc.shop
(Hostinger, which pulls `main`); a copy also deploys to GitHub Pages on every push to `main`.

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

1. **Printful links** — in `data/products.json`, set each live product's `buy_url` to its
   Printful Quick Store link, then run `python scripts/render_shop.py`. Any product left `""` shows a **Notify me** button that routes
   to the contact form instead of a dead link, so the site is safe to publish before
   the store is ready.
2. **Contact email** — done. The form and the footer link both point to
   `bdcpromotions@gmail.com` (`assets/js/main.js`, search for `mailto:`, and
   `index.html`). To change it again later, or to wire it to a free formspree.io
   endpoint so messages land quietly in an inbox instead of opening Mail, see the
   second TODO in `assets/js/main.js`.

Keep `data/products.json` and the hard-coded cards in `index.html` in sync — the JSON
is the catalog reference (`scripts/add_product.py` appends to it); the HTML is what
actually renders.

## Deploying

- **bedc.shop (live):** Hostinger (hPanel Git deploy) pulls `main` into the site folder.
  The root `.htaccess` makes it serve only `/`, `index.html`, `assets/` (and the SSL
  renewal path `.well-known/acme-challenge/`); every other
  repo file returns 404 there.
- **GitHub Pages copy:** `.github/workflows/static.yml` validates every push and PR, and on
  `main` copies `index.html` + `assets/` into `_site` and deploys that to
  `jaap-dekkinga.github.io/bdc_promotions/`.
- Keep the two allowlists (`.htaccess` and the "Collect storefront files" step) in step.
- `deploy-pages.yml` is the older gh-pages/peaceiris variant, set to manual
  (`workflow_dispatch`) only so the two workflows don't race over the same deployment.

## Printful

- **Products come from Printful.** The **Printful sync** workflow (daily, or Actions → Printful
  sync → Run workflow) reads the store and opens a PR that updates prices, adds new Printful
  products as drafts, and re-renders the shop. Nothing changes on bedc.shop until that PR is merged.
- **New products:** the `printful-product-creator` Claude agent drafts the product, shows the exact
  API call, and creates it only after approval (`scripts/printful_create.py --apply`).
- **The token is never in this repo.** One-time setup, done by Jaap:
  1. In Printful (Settings → API → Tokens), create two private tokens: one with only
     `sync_products/read` (for GitHub), one with `sync_products` (for this PC).
  2. GitHub: `gh secret set PRINTFUL_TOKEN` and paste the read-only token at the prompt
     (or Settings → Secrets and variables → Actions). Then Settings → Actions → General →
     allow GitHub Actions to create pull requests.
  3. This PC: `cmdkey /generic:bdc-printful /user:printful /pass` and paste the write token
     at the prompt (stored in Windows Credential Manager).
  4. For an account-level token, also set the repository variable `PRINTFUL_STORE_ID`.

## Files

```
index.html                   the whole site (story, platform, facts, shop, contact)
assets/css/style.css         brand styles — navy #002664 / red #BB133E
assets/js/main.js            nav toggle, Printful link config, contact form
assets/img/                  real logo, hero, and product images
data/products.json           catalog reference for the 7 starter SKUs (USD)
scripts/add_product.py       append a product to data/products.json
product-pricing-sheet.md     SKU costs, retail prices, and margins for Printful (private numbers)
.github/workflows/static.yml CI validate + GitHub Pages copy
.htaccess                    bedc.shop allowlist (only /, index.html, assets/, ACME path)
```
