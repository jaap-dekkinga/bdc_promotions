# Pull the shop from Printful, and let an agent create products safely

- **Author:** the owner (drafted with Claude)
- **Date:** 2026-10-21
- **Status:** accepted
- **Source:** idea

## Problem
The 7 shop cards are hard-coded in `index.html`, with the same data again in `data/products.json` and `product-pricing-sheet.md`. Prices and products drift ("catalog drift" in CLAUDE.md). Adding a product means editing three files by hand and creating it in Printful separately.
The owner wants the site to follow what's in Printful, and a Claude agent that can create new Printful products. The Printful token must stay secret: the repo is public, and bedc.shop is a static site with no backend.

## Proposed outcome
- A scheduled GitHub Action (daily + "Run workflow" button) reads the Printful store with a **read-only** token kept in GitHub Secrets. It opens a PR that updates prices and new products in `data/products.json`, the shop cards in `index.html` and the retail column of the pricing sheet. The owner merges; Hostinger pulls `main`.
- The shop cards are generated from `data/products.json`, so the page and the catalog can't drift. CI fails if they do.
- A `printful-product-creator` agent drafts a new product (Be ___ phrase, DC fact, blank, price, print file) and creates it in Printful only after the owner approves the exact call. It uses a **write** token kept in Windows Credential Manager.
- No token ever appears in the repo, the browser, logs, or chat.

## Affected users and systems
- Files: `index.html` (shop grid), `data/products.json`, `product-pricing-sheet.md`, `scripts/`, `.github/workflows/`, `.claude/` (agent, hooks), `.gitignore`, `CLAUDE.md`
- Outside services: Printful API (`api.printful.com`), GitHub Actions + Secrets, Windows Credential Manager

## Constraints
- Budget: $0. No backend, no new hosting, no npm/pip dependencies (Python standard library only).
- Brand: `be-dc-brand`. Every product still needs a Be ___ phrase and one DC fact; products without them don't show.
- Everything in the repo is public. Tokens live only in GitHub Secrets and Credential Manager.
- Buy-button links stay manual in `PRINTFUL_LINKS` (Printful's API doesn't return a storefront URL). Don't invent them.
- The owner approves every Printful write and every merge.

## Out of scope
- Live (real-time) product fetching in the browser.
- Orders, checkout, webhooks (they need a public server endpoint).
- Editing or deleting existing Printful products from the agent.

## Open questions
- [x] Sync method: scheduled GitHub Action → PR (the owner, 2026-10-21)
- [x] Agent autonomy: draft, the owner approves each create (the owner, 2026-10-21)
- [x] Local secret: Windows Credential Manager (the owner, 2026-10-21)
- [ ] Is the Printful store an "API / Manual order" store? `POST /store/products` only works for those; Quick Store or Shopify-connected stores may refuse it.
- [ ] The token pasted in chat on 2026-10-21 must be revoked and replaced by two scoped tokens.

## Update 2026-10-22
Superseded in part by branch `printful-catalog`: buy links are now `buy_url` per product in `data/products.json` (not `PRINTFUL_LINKS` in main.js), and the sync also matches Printful products by `printful_external_id` or `printful_name`.
