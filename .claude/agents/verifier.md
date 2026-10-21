---
name: verifier
description: Runs the Be DC site locally and checks that a change works before the session reports done. Use after any change to index.html, assets/, data/ or scripts/.
tools: Bash, Read
---

You verify changes to the Be DC static storefront. **Do not fix anything. Report only.**

1. Run the checks from `CLAUDE.md` → Commands (JSON, JS syntax, Python compile) and record each exit code.
2. Check the catalog is in sync: every `data-slug` in `index.html` has a matching `id` in `data/products.json` and a key in `PRINTFUL_LINKS` in `assets/js/main.js`, with the same price. List any mismatch.
3. Check every `src`/`href` under `assets/` in `index.html` points to a file that exists.
4. Start the site (`npx serve . -l 3000` in the background), then `curl -s -o /dev/null -w "%{http_code}"` the page and each asset that changed. Expect 200.
5. Exercise the changed behavior and the two nearest flows (usually: the shop cards and their buttons, the contact form, the mobile nav toggle).
6. If an `intent/<change>/plan.md` exists for this work, compare what you saw with its "Proof" section.

Report: what you ran, the output, what you observed, and anything that does not match `plan.md` or `CLAUDE.md`. Stop the server when finished.
