# Reviewer eval cases

Re-run these whenever `REVIEW.md`, `.claude/agents/code-reviewer.md`, `CLAUDE.md` or the model changes.
Keep a change to the reviewer only if it catches **at least as many** cases and case 0 stays clean.

**How to run a case:** on a throwaway branch, make the planted change, then ask Claude:
"Run the code-reviewer subagent on the changes in this branch versus main." Record caught / missed, and whether the `file:line` was right. Delete the branch.

| # | Planted change | Expected finding | Tag / tier |
|---|---|---|---|
| 0 | **Clean:** fix a typo in one product description, in both `index.html` and `products.json` | `0 findings — nothing to fix` | Low |
| 1 | Change the hat price to `$32` in `index.html` only | Price mismatch with `products.json` and the pricing sheet (**it lies**) | Important, High |
| 2 | Give `tshirt-white` the hoodie's `buy_url` in `data/products.json` | The tee button opens the hoodie's Printful page (**it misroutes**) | Important, High |
| 3 | In `static.yml`, delete `needs: validate` from the `deploy` job | Deploy no longer waits for validation | Important (Security/Bug), High |
| 4 | Add a new external link with `target="_blank"` and no `rel` | Missing `rel="noopener"`, reported once as a bug class listing every instance | Nit (Security), Medium |
| 5 | In `main.js`, remove `encodeURIComponent` from the mailto subject | Contact form breaks on `&` or `#` in the message (**it drops a lead**) | Important, High |
| 6 | Change a fact to "DC draws 16.4 million visitors a year" | 2009 figure presented as current (**it lies**) | Important (Compliance), Medium |
| 7 | Add "B★DC®" to the hero | Trademark is pending; ® not allowed | Important (Compliance), Medium |
| 8 | Any small change, with `product-pricing-sheet.md` still published by the deploy | Listed as **Pre-existing**, not blamed on this change | Pre-existing |

## Results log

| Date | What changed in the reviewer | Caught (of 8) | Case 0 clean? | Notes |
|---|---|---|---|---|
| | baseline | | | |

## Adding a case
When a bug reaches the live site: after the fix ships, add a row recreating the bug as it was, with the finding that should have caught it.
