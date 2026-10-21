## What and why
<!-- One or two sentences. Link the intent folder if there is one: intent/YYYY-MM-DD-name/ -->

## Risk tier
<!-- Low / Medium / High — see docs/code-review-process.md. The change sets the tier, not who wrote it. -->

## Testing
<!-- Paste real output, not "tested". -->
- [ ] `python -m json.tool data/products.json > /dev/null`
- [ ] `node --check assets/js/main.js`
- [ ] Looked at the page locally (desktop + phone width) — screenshot if anything visible changed
- [ ] `verifier` subagent report:
- [ ] `code-reviewer` subagent: <count line from its summary>

## How to revert
<!-- Usually: "Revert this PR on GitHub; Pages redeploys main in ~1 min." Say if anything outside the repo also changes (Printful, DNS, Gmail). -->

## Outside the repo
<!-- Printful products/prices, domain DNS, email — anything that must change together with this PR. "None" is fine. -->
