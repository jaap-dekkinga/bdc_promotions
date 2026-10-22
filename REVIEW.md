# REVIEW.md — review policy for the Be DC storefront

Read by the `code-reviewer` subagent, by `/code-review` in Claude Code, and by any Claude PR review in GitHub.
Owner: Jaap. Findings inform the decision; they never approve. An agent's "looks good" never counts as a human approval.
Process and risk tiers: `docs/code-review-process.md`.

## What failure looks like here

Look for these first. They are what actually costs Be DC money or credibility.

| Area | Failure means… | Example |
|---|---|---|
| Product cards, prices, facts | **it lies** | A card says $28, the pricing sheet and Printful say $32. A DC fact that isn't true, or a 2010 statistic presented as current. |
| Shop buttons, links | **it misroutes** | The hoodie button opens the polo's Printful page. A live product whose `buy_url` is missing or wrong, so it shows "Notify me" or opens the wrong page. |
| Contact form | **it drops a lead** | The mailto address, subject or body is broken, so the message never arrives. |
| Layout | **it can't be used on a phone** | Horizontal scroll or an unreachable button at ~375px. |
| Deploy / repo | **it exposes or takes down the shop** | A private file served publicly; a workflow change that skips `validate` or deploys from a branch. |
| Brand | **it isn't B★DC** | Off-palette color, "BDC" in copy, ® on a pending mark. |

## Passes

Tag every finding with its pass: **Bug**, **Security**, or **Compliance** (against `intent/<change>/spec.md` + `plan.md`, the `be-dc-brand` skill, and `CLAUDE.md`).
Security can also be checked separately with `/security-review`; an open Security finding blocks the merge.

## Evidence

Every finding needs a `file:line`, the concrete input or state that triggers it, and what goes wrong.
Don't infer a bug from a name or a guess. If you can't point to the line and the failure, it's a **Question**, not a finding.

## Severity tags

- **Important**: one of the failures in the table above, or a crash/regression.
- **Nit**: wording, naming, readability. **At most 5**; give the rest as a count.
- **Pre-existing**: a real problem this change didn't introduce. List separately so it isn't the author's fault and doesn't block; it becomes a new `intent.md` if worth fixing.

Drop style-only, "consider…", and cleanup-only findings that don't change behavior.

## Bug classes

When a finding is one instance of a pattern (a missing `rel="noopener"`, a price that differs in one place), say so and list **every** instance in the repo, so it gets fixed once.

## Re-reviews (convergence)

- Round 1 reviews the whole change. Rounds 2+ review **only the new commits since the last review**.
- Never repeat a finding already raised. If it was dismissed with a reason, it stays dismissed.
- After **3 rounds** with Important findings still open, stop listing new nits and say: "Reconsider the approach" with one sentence on why.

## Don't report

- What the CI `validate` job already checks: JSON validity, JS syntax, missing `assets/` files, HTML Tidy errors.
- Binary files in `assets/img/`. CRLF vs LF line endings.
- Files under `intent/` and `docs/` for anything except broken links or contradictions with the code.

## Summary format

Start with the count, then the verdict:
`2 Important, 3 Nits, 1 Pre-existing — fix before merging.` or `0 findings — nothing to fix.`
Then the risk tier (Low / Medium / High, see the process doc) with a one-line reason.

## Feeding back

- Same finding in two PRs → add the rule to `CLAUDE.md` → "Things Claude gets wrong here", or a check in CI.
- A bug that reached the live site → add a case to `review-evals/cases.md`.
- If the change makes `CLAUDE.md` or this file out of date, say so.
