# Code review process — Be DC storefront

Adapted on 2026-10-21 from "Solving code review at Anthropic" (claude.dev blog, Oct 15 2026), scaled from Anthropic's monorepo to one owner and one static site.

**Goal:** Jaap spends as little time as possible reviewing, **without more broken deploys or rollbacks than before**. The question for each change isn't "did a human read every line?" but "what could go wrong, and which check (automated or Jaap) is the right one to catch it?"

## The layers

| # | Layer | Who | When | Blocks merge? |
|---|---|---|---|---|
| 1 | **Verify before the PR**: checks from `CLAUDE.md` with pasted output, look at the page, `verifier` subagent | Claude | while building | — |
| 2 | **Bug review**: `code-reviewer` subagent (or `/code-review`) against `REVIEW.md` | Claude | before opening the PR, again after fixes | Open **Important** findings |
| 3 | **Security review**: `/security-review` in Claude Code | Claude | Medium and High tier | Open findings |
| 4 | **CI**: the `validate` job in `static.yml` | GitHub | every push / PR | Yes (required check) |
| 5 | **Risk-tiered human check** | Jaap | before merging | High tier |
| 6 | **Deploy from `main` only**, after `validate` | GitHub | on merge | — |
| 7 | **Detect and roll back**: revert the PR; Pages redeploys in about a minute | Jaap / Claude | after deploy | — |

Every Important or Security finding must end **fixed**, or **closed with a one-line reason** in the PR. Nothing is silently ignored.

## Risk tiers

The change sets the tier, not who wrote it. `code-reviewer` proposes one; Jaap can raise it.

| Tier | Touches | Jaap's part |
|---|---|---|
| **Low** | Copy and typos, `docs/`, `intent/`, CSS polish with no layout change | Skim the summary line. Merge when CI and review are green. |
| **Medium** | Layout, JS behavior, product descriptions, Be ___ phrases, DC facts, `scripts/` | Read the review summary and the screenshots. Check facts yourself. |
| **High** | `.github/workflows/**`, `PRINTFUL_LINKS`, any price, `CNAME`/domain, contact address, anything that changes what's published | Read the diff yourself. Click every changed shop link on the live site after deploy. |

Rules carried over from the post:
- An agent's approval never counts as Jaap's.
- If a commit is added after Jaap looked (an agent fix, a merge), a High-tier change needs another look.
- **Circuit breaker:** after any revert or live-site breakage, treat the next 5 PRs one tier higher.

## The loop for one PR

1. Claude builds and verifies (layer 1), then runs `code-reviewer` with the changed files and the intent folder.
2. Claude fixes Important findings, then re-runs the reviewer as **round 2, new changes only**, passing the previous findings so nothing repeats.
3. **Cap: 3 rounds.** If Important findings are still open after round 3, stop and rethink the approach with Jaap. At Anthropic, about 59% of what kept being flagged in long loops was old code, not new bugs.
4. Claude opens the PR using the template (Testing, Risk tier, How to revert, Outside the repo).
5. CI runs. Jaap does his tier's part and merges.

**Deep review** (High tier, or anything touching money): run `code-reviewer` **twice in parallel**, in separate contexts, and keep only the findings both report (findings only one run reports go to Questions). This is the one-person version of the post's "several hunters, verifiers vote".

## Getting less noise over time

**Log the outcome of every finding** in `review-evals/outcomes.md`: *fixed*, *wrong*, *intentional* or *doesn't matter*. Once a month:
- Many *wrong* → tighten the evidence rules in `REVIEW.md`.
- Many *doesn't matter* → drop that kind of finding or lower the nit cap.
- The same *fixed* finding twice → move it into `CLAUDE.md` or a CI check, so it's prevented instead of caught.

**Turn breakages into evals.** Every bug that reaches the live site becomes a case in `review-evals/cases.md`. When `REVIEW.md`, `code-reviewer.md`, `CLAUDE.md` or the model changes, re-run the cases. Keep the change only if as many or more cases are caught and the clean case stays clean.

**Pre-existing bugs** aren't the current change's fault. They're listed separately and become an `intent.md` if worth fixing. Optional: a monthly scheduled task that runs `code-reviewer` over the whole repo to surface them early.

## GitHub settings (one-time, ~5 minutes)

Settings → Branches → add a rule for `main`:
- Require a pull request before merging (approvals: 0, since GitHub doesn't let you approve your own PR; your tier check replaces it).
- Require status check **Validate site** to pass.
- Block force pushes.

Optional later: run Claude in GitHub on every PR with `anthropics/claude-code-action`, pointed at `REVIEW.md` (needs an `ANTHROPIC_API_KEY` repo secret).

## What only Jaap does

- **Should we build this at all?** Direction, taste and scope belong in the intent, before code exists. Closing a PR is cheap.
- **Money and exposure:** prices, Printful links, what gets published, the domain.
- **Truth:** DC facts and partner claims carry the brand's name.
- **Ownership:** whoever's name is on the merge owns the result. Small changes and one-click reverts keep that cheap.

Before changing an unfamiliar part of the site, ask Claude for a short explainer of that part. It teaches more than reading a diff.

## Keeping score

Readable from GitHub and `review-evals/outcomes.md`:
- **Rounds to green:** reviews needed before a PR passes (Anthropic went from 2.08 to 1.32 on average). Target: mostly 1.
- **Noise:** share of findings marked *wrong* or *doesn't matter*.
- **Guardrail:** reverts and live-site breakages per month. If this goes up, review time was moved rather than saved.
