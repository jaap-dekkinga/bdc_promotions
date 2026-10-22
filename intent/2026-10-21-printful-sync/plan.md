# Plan: Printful sync, product-creator agent, secret handling

## Files
| File | Change |
|---|---|
| `scripts/printful_api.py` | New. Stdlib-only Printful client: token from `PRINTFUL_TOKEN` env (CI) or Windows Credential Manager target `bdc-printful` (local); optional `PRINTFUL_STORE_ID`; retries on 429 using `Retry-After`; never prints the token or request headers. |
| `scripts/render_shop.py` | New. Renders the shop cards between `<!-- shop:start -->` / `<!-- shop:end -->` in `index.html` from `data/products.json`. `--check` exits 1 if `index.html` is out of date. Renders only products with `status: live`, a Be ___ phrase, a fact and an image. |
| `scripts/printful_sync.py` | New. Reads the store (`GET /store/products`, `GET /store/products/{id}`), matches products by `printful_id` or `external_id == slug`, updates prices, records new Printful products as `status: draft` (not shown), downloads a thumbnail for products without an image, updates the pricing sheet's retail/margin cells, writes a markdown summary for the PR. Never deletes. |
| `scripts/printful_create.py` | New. Validates a product draft JSON, prints the exact payload (dry run by default); with `--apply` calls `POST /store/products` with `external_id = slug`, then adds the product to `data/products.json` and re-renders the shop. |
| `data/products.json` | Add `name`, `image`, `alt`, `status`, `printful_id` to the 7 products (display fields come from today's cards). |
| `index.html` | Shop grid becomes generated output between markers. Visible change: none, except the Notify-me message now uses the product title. |
| `.github/workflows/printful-sync.yml` | New. Daily + manual. Read-only token from `secrets.PRINTFUL_TOKEN`. If anything changed: one rolling branch `printful-sync-bot` (stops if anyone but the bot committed to it), PR to `main`, then dispatch `static.yml` on that branch so CI runs (PRs made with `GITHUB_TOKEN` don't trigger it). |
| `.github/workflows/static.yml` | Validate job gets two more checks: shop cards match `products.json` (`render_shop.py --check`) and a secret scan of tracked files. Nothing removed. |
| `.claude/agents/printful-product-creator.md` | New agent. |
| `.claude/hooks/require_approval.py` | Ask before `printful_create.py --apply` and any write to `api.printful.com`. |
| `.claude/hooks/guard_secrets.py` + `settings.json` | New. Deny writing token-like strings into files/commands and deny commands that read or print the stored token. |
| `.gitignore`, `CLAUDE.md`, `docs/`, `add-product` skill | Secret files ignored; docs describe the new flow. |

## Order
1. Client + renderer; regenerate today's 7 cards and confirm `index.html` renders identically.
2. Sync script with a fake Printful response (fixtures in a temp dir, not committed).
3. Create script (dry run against a fixture).
4. Hooks + CI checks + gitignore.
5. Workflow.
6. Docs. Verifier + two code-reviewer passes.

## Risks
- Rendering changes the shop HTML: compare old vs new card HTML; screenshot at 375 and 1280.
- A sync PR with a wrong price: Jaap reviews every PR; price changes are listed in the PR body.
- Token leak: env/Credential Manager only, never logged; hooks + CI scan + GitHub push protection.
- Can't test against the real API in this session (the pasted token must be revoked, and I won't use it). First real run is Jaap's "Run workflow" after he adds the new read-only secret.

## Proof
- `render_shop.py --check` passes on `main` content; visual check unchanged at 375/1280.
- Sync against fixtures: price change, new draft product, missing product, 429 retry.
- Create dry run prints the payload and makes no network write; `--apply` path guarded by the hook (pipe test).
- Secret scan finds a planted fake token in a temp copy and passes on the repo.

## Update 2026-10-22
Superseded in part by branch `printful-catalog`: buy links are now `buy_url` per product in `data/products.json` (not `PRINTFUL_LINKS` in main.js), and the sync also matches Printful products by `printful_external_id` or `printful_name`.
