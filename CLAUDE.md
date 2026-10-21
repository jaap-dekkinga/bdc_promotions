# CLAUDE.md — Be DC storefront (`bdc_promotions`)

Single-page static storefront for **B★DC**, Washington, DC's city logo and motto. Owner: Jaap Dekkinga.
No framework, no build step. Deploys to GitHub Pages from `main` via `.github/workflows/static.yml`.
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
| New product in Printful | `printful-product-creator` agent → `python scripts/printful_create.py <draft.json>` (dry run); `--apply` only after Jaap's OK | payload printed / `Created Printful product …` |
| Pull from Printful | GitHub → Actions → **Printful sync** → Run workflow (it also runs daily) | a `Printful sync <date>` PR, or "nothing to do" |

CI (`static.yml` → `validate` job) also checks: required product fields, unique ids/slugs, numeric prices,
that every `assets/…` path in `index.html` exists, that the shop cards match `data/products.json`, that no tracked file contains a token-like string, and HTML Tidy has no `Error:` lines. Deploy runs only if validate passes.

## Definition of done

Before saying a change is finished, run every check above that applies and paste the output.
If you changed anything visible, open the page (local server + browser or screenshot) and look at it at desktop and phone width.
If a check fails, fix the code. Never weaken or delete a CI check to make it pass.

## Layout

```
index.html                 the whole site: story, Be ___ platform, DC facts, shop (generated cards), contact
assets/css/style.css       brand styles
assets/js/main.js          nav toggle, PRINTFUL_LINKS map, contact form (mailto)
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
.claude/agents/printful-product-creator.md drafts a product; creates it in Printful only after Jaap's OK
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
- Prices in `index.html`, `data/products.json` and `product-pricing-sheet.md` must match. Change all three together.
- Plain HTML/CSS/vanilla JS. No frameworks, bundlers or npm dependencies beyond `serve`.
- Contact goes to `bdcpromotions@gmail.com` (mailto in `main.js` and footer in `index.html`).

## Things Claude gets wrong here

- **Catalog drift:** the shop cards in `index.html` are generated from `data/products.json` between the `shop:start` / `shop:end` markers. Never edit them by hand: change the JSON and run `python scripts/render_shop.py` (CI fails if they differ). Only `status: "live"` products with a Be ___ phrase, a fact and an image are shown.
- **Printful token:** never in the repo, a file, a command, chat or a log. GitHub uses the `PRINTFUL_TOKEN` repository secret (read-only scope `sync_products/read`); this PC uses Windows Credential Manager `bdc-printful` (write scope `sync_products`, for `printful_create.py`). Only `scripts/printful_api.py` reads it, and only Jaap stores or rotates it. `.claude/hooks/guard_secrets.py` denies token-like strings anywhere, commands that read the token or list the environment, and token-reading code in any code file other than the three Printful scripts. `require_approval.py` asks before `printful_create.py --apply`, any shell command that names the Printful client, the write flag or `api.printful.com`, running any other `scripts/printful_*.py`, and any edit to the Printful scripts, `.claude/hooks/`, `.claude/settings*.json` or `.github/workflows/`. Both match text, so they stop mistakes, not a determined attacker. If a token is ever pasted or committed, tell Jaap to revoke it at once.
- **Hook changes can lock the session.** The hooks fail closed: a hook that crashes blocks every tool call, including the edit that would fix it (it happened once, Jaap had to fix it by hand). Change a hook on a copy in the scratchpad, test it there with piped JSON, and only then copy it over the live file.
- **Shop buttons:** a slug with `""` in `PRINTFUL_LINKS` shows "Notify me" on purpose. Don't invent Printful URLs; leave `""` until Jaap provides the real link.
- **Two deploy workflows:** `static.yml` is the active one. `deploy-pages.yml` is manual-only on purpose. Don't put it back on `push`.
- **The GitHub repo is public.** The deploy now publishes only `index.html` + `assets/`, but every committed file is still readable on GitHub. Don't add secrets, customer data, or private business notes. If `index.html` starts loading a file outside `assets/`, add it to the "Collect storefront files" step in `static.yml`.
- **Jaap approves every email send and every deploy.** `.claude/settings.json` runs `.claude/hooks/require_approval.py` before each tool call; it forces a permission prompt for mail-send tools and commands (including SMTP) and for any `git push`, `gh pr merge`, `gh workflow run`, GitHub API merges/ref/content writes and auto-merge, even in auto mode. If it can't read a tool call, it asks. Gmail *drafts* are fine. It matches text, so it can't see a click on "Send" in a browser tool: never send email through Gmail on the web. Don't weaken or bypass the hook.
- **No PR without the review agents.** Claude once opened a PR without running `verifier` and `code-reviewer`. `.claude/hooks/require_reviews.py` now logs each run of those subagents per branch (in `.git/claude-reviews.jsonl`) and denies `gh pr create` / `gh pr ready` until both have run on the branch, or while the PR body says either was "not run". Don't write to that log by hand.
- **Marketing and outreach output is private.** Prospect lists, contact names, email drafts, content calendars and reports go in `../bdc-growth/`, never in this repo. Agents draft; Jaap sends emails and publishes posts.
- **Trademark:** the US application (serial 99376168) is pending. Don't add ® anywhere. Don't make legal claims about the mark.
- **Don't add tracking scripts, cookie banners, or third-party embeds** without an intent that says so.

When Claude makes the same mistake twice, add the correction to this list.
