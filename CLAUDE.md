# CLAUDE.md — Be DC storefront (`bdc_promotions`)

Single-page static storefront for **B★DC**, Washington, DC's city logo and motto. Owner: the B★DC founder.
No framework, no build step. Live at https://bedc.shop (a host that pulls `main`; `.htaccess` limits what it serves). `.github/workflows/static.yml` validates every push and deploys the GitHub Pages copy from `main`.
Merch is print-on-demand through Printful. There is no cart, checkout or backend in this repo, and there shouldn't be one.

## Commands

| What | Command | Healthy output |
|---|---|---|
| Serve locally | `npm start` (= `npx serve .`) | `Serving!` on http://localhost:3000 |
| Check catalog JSON | `python -m json.tool data/products.json > /dev/null` | no output, exit 0 |
| Check JS syntax | `node --check assets/js/main.js` | no output, exit 0 |
| Check Python | `python -m py_compile scripts/*.py .claude/hooks/*.py` | no output, exit 0 |
| Check shop cards | `python scripts/render_shop.py --check` | `OK: shop shows N of N products, in sync…` |
| Check for secrets | `python .claude/hooks/guard_secrets.py scan` | `OK: no token-like strings in N tracked files` |
| Add a product (local only) | `python scripts/add_product.py --id … --title … --name … --price … --be "Be …" --fact "…" --image assets/img/… --alt …` | `Saved N products…`, then `Rendered N of N products…` |
| New product in Printful | `printful-product-creator` agent → `python scripts/printful_create.py <draft.json>` (dry run); `--apply` only after the owner's OK | payload printed / `Created Printful product …` |
| Pull from Printful | GitHub → Actions → **Printful sync** → Run workflow (it also runs daily) | a `Printful sync <date>` PR, or "nothing to do" |

CI (`static.yml` → `validate` job) also checks: required product fields, unique ids/slugs, numeric prices,
that every `assets/…` path in `index.html` exists, that the shop cards match `data/products.json`, that no tracked file contains a token-like string, and HTML Tidy has no `Error:` lines. Deploy runs only if validate passes.

## Definition of done

Before saying a change is finished, run every check above that applies and paste the output.
If you changed anything visible, open the page (local server + browser or screenshot) and look at it at desktop and phone width.
If a check fails, fix the code. Never weaken or delete a CI check to make it pass.

## Layout

```
.htaccess                  bedc.shop allowlist: only /, index.html, assets/ (+ ACME path); keep in step with static.yml
index.html                 the whole site: story, Be ___ platform, DC facts, shop (generated cards), contact
assets/css/style.css       brand styles
assets/js/main.js          nav toggle, shop buttons (from each card's data-buy-url), contact form (mailto)
assets/img/                logo, hero and product images (binary; don't regenerate or rename)
data/products.json         the catalog and source of the shop cards (live + draft products, USD)
scripts/add_product.py     appends to products.json and re-renders the shop
scripts/render_shop.py     generates the shop cards in index.html from products.json
scripts/printful_sync.py   pulls the Printful store (run by .github/workflows/printful-sync.yml)
scripts/printful_create.py creates one Printful product from a draft (dry run unless --apply)
scripts/printful_api.py    Printful client; the only code that reads the token
product-pricing-sheet.md   cost / retail / margin per SKU (private numbers; repo is public)
intent/                    intent.md → spec.md → plan.md per change (see docs/ai-native-workflow.md)
.claude/skills/            be-dc-brand, add-product, apparel-storefront-ux, web-accessibility, site-screenshots,
                           free-marketing, partner-outreach
.claude/agents/verifier.md report-only check before "done"
.claude/agents/code-reviewer.md read-only bug + readability review before a PR
.claude/agents/ui-ux-designer.md read-only UX/UI, accessibility and conversion review for visible changes
.claude/agents/site-improver.md live health + SEO/sharing check, turns top findings into intent.md drafts
.claude/agents/marketing-planner.md $0 marketing: 2-week content calendar + ranked to-dos (in ../bdc-growth/)
.claude/agents/collaborator-outreach.md finds DC collaborators, writes Gmail drafts (never sends)
.claude/agents/printful-product-creator.md drafts a product; creates it in Printful only after the owner's OK
../bdc-growth/             PRIVATE, outside the repo: prospects.csv, outreach-log.md, content-calendar.md, reports/
REVIEW.md                  review policy (what failure looks like, tags, round cap)
docs/code-review-process.md  review layers, risk tiers, eval + noise loop
review-evals/              planted-bug cases for the reviewer + finding outcomes log
.github/pull_request_template.md  Testing / Risk tier / How to revert
```

## Conventions

- Brand: navy `#002664`, red `#BB133E`, white. Big Shoulders Display (headlines), Inter (body), IBM Plex Mono (labels/data). Use the `be-dc-brand` skill for anything visible.
- Write the mark as **B★DC** (with the star) in copy; "Be DC" when spoken/motto. Never "BDC" in customer-facing text.
- Every product has a `Be ___` phrase and one DC fact. Facts must be true today or clearly framed as the 2010 research that started the project.
- **Prices come from the Printful store, automatically.** The daily Printful sync copies each linked product's Printful retail price (lowest variant) into `data/products.json`, the shop card and the pricing sheet's retail and margin cells, and opens a PR. Never set or "fix" a price by hand on the site: the owner changes prices in Printful, and the next sync brings them in. The three places must still match; the sync keeps them in step. If a synced price falls below the 39% margin floor, say so in the PR, but don't block or override it.
- Plain HTML/CSS/vanilla JS. No frameworks, bundlers or npm dependencies beyond `serve`.
- Contact goes to `bdcpromotions@gmail.com` (mailto in `main.js` and footer in `index.html`).

## Things Claude gets wrong here

- **Catalog drift:** the shop cards in `index.html` are generated from `data/products.json` between the `shop:start` / `shop:end` markers. Never edit them by hand: change the JSON and run `python scripts/render_shop.py` (CI fails if they differ). Only `status: "live"` products with a Be ___ phrase, a fact and an image are shown. The sync links a catalog product to Printful by `printful_id`, else `printful_external_id` (the `#…` ID in the Printful dashboard), the slug, or `printful_name`; set one of those before a sync, or it adds the Printful product as a duplicate draft.
- **Printful token:** never in the repo, a file, a command, chat or a log. GitHub uses the `PRINTFUL_TOKEN` repository secret (read-only scope `sync_products/read`); this PC uses Windows Credential Manager `bdc-printful` (write scope `sync_products`, for `printful_create.py`). Only `scripts/printful_api.py` reads it, and only the owner stores or rotates it. `.claude/hooks/guard_secrets.py` denies token-like strings anywhere, commands that read the token or list the environment, and token-reading code in any code file other than the three Printful scripts. `require_approval.py` asks before `printful_create.py --apply`. `printful_api.py` hands out the token only when the running program is `scripts/printful_sync.py` or `printful_create.py`, and allows writes only from `printful_create.py`, so copies, helper files (any extension) and `python -c` are refused. All of this stops mistakes and ordinary shortcuts, not deliberate tampering (spoofing `__main__`, patching the gate): never try to get around it. The owner chose to keep the write token on this PC knowing that. Docs may mention the client and `--apply` only in `docs/`, `intent/`, `review-evals/`, `.claude/agents/`, `.claude/skills/` and top-level `*.md`. If a token is ever pasted or committed, tell the owner to revoke it at once.
- **Hook changes can lock the session.** The hooks fail closed: a hook that crashes blocks every tool call, including the edit that would fix it (it happened once, the owner had to fix it by hand). Change a hook on a copy in the scratchpad, test it there with piped JSON, and only then copy it over the live file.
- **Shop buttons:** a product with `"buy_url": ""` in `data/products.json` shows "Notify me" on purpose. Don't invent Printful URLs; leave `""` until the owner provides the real Quick Store link. The sync never sets it (Printful's API has no buy links).
- **Two deploy workflows:** `static.yml` is the active one. `deploy-pages.yml` is manual-only on purpose. Don't put it back on `push`.
- **bedc.shop is not GitHub Pages.** It is Hostinger (hPanel Git deploy; responses carry `platform: hostinger` and `Server: hcdn`), which pulls `main` into the site folder. `.htaccess` makes it serve only `index.html`, `assets/` and `.well-known/acme-challenge/`. `static.yml` deploys the GitHub Pages copy (`jaap-dekkinga.github.io/bdc_promotions/`). Change both allowlists together.
- **The GitHub repo is public.** The deploys publish only `index.html` + `assets/`, but every committed file is still readable on GitHub. Don't add secrets, customer data, or private business notes. If `index.html` starts loading a file outside `assets/`, add it to the "Collect storefront files" step in `static.yml` and to `.htaccess`.
- **The owner approves every email send, every deploy and every new Printful product, and nothing else.** `.claude/settings.json` runs `.claude/hooks/require_approval.py` before each tool call. It asks for mail-send tools and commands (including SMTP); for anything that changes `main`, which bedc.shop deploys from (a push to `main`, or a push while on `main`; `gh pr merge`; `gh workflow run`; GitHub API merges/ref/content writes; auto-merge); and for `printful_create.py --apply`. Pushing a feature branch, editing files and running checks don't ask: the owner doesn't want extra prompts. If it can't read a tool call, it asks. Gmail *drafts* are fine. It matches text, so it can't see a click on "Send" in a browser tool: never send email through Gmail on the web. Don't weaken or bypass the hook.
- **No PR without the review agents.** Claude once opened a PR without running `verifier` and `code-reviewer`. `.claude/hooks/require_reviews.py` now logs each run of those subagents per branch (one file per run in `.git/claude-reviews/`) and denies `gh pr create` / `gh pr ready` until both have run on the branch, or while the PR body says either was "not run". Don't write to that log by hand.
- **Marketing and outreach output is private.** Prospect lists, contact names, email drafts, content calendars and reports go in `../bdc-growth/`, never in this repo. Agents draft; the owner sends emails and publishes posts.
- **Trademark:** the US application (serial 99376168) is pending. Don't add ® anywhere. Don't make legal claims about the mark.
- **Don't add tracking scripts, cookie banners, or third-party embeds** without an intent that says so.

When Claude makes the same mistake twice, add the correction to this list.
