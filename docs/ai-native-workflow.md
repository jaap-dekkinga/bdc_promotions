# How we build the Be DC site with Claude

Adapted from Anthropic Academy's *The AI-Native SDLC Playbook* (academy.claude.com/courses/ai-native-sdlc-playbook, reviewed 2026-10-21).
The course is written for large, regulated engineering teams. Be DC is one owner, one static site and a print-on-demand store,
so this keeps the parts that pay off at this size and says plainly what to skip.

## The idea in one paragraph

Claude writes code faster than one person can plan, check and ship it, so the slow parts become deciding *what* to build and checking *that it's right*.
The playbook's answer: every step ends in a small file committed to the repo (`intent.md` → `spec.md` → `plan.md` → code + tests → PR with review),
and the next step reads it. Git then records who asked for what, what Claude produced, and who approved it. Jaap stays the decision-maker; Claude does the drafting and the checking.

## The loop, for one change

All files for a change live in one folder: `intent/YYYY-MM-DD-short-name/`.

| Stage | You do | Claude does | File |
|---|---|---|---|
| **1. Plan** | Describe the problem in your own words: what's wrong, who it affects, what better looks like, what's out of scope. | Asks questions, fills in `intent/_TEMPLATE.md`. | `intent.md` |
| **2. Design** | Check it solves your problem. Answer flagged concerns. | Turns the intent into requirements + design, applying the `be-dc-brand` skill, and flags conflicts. | `spec.md` |
| **3. Build** | Read the plan, ask "what could this break?", approve. | In **plan mode**: lists files to change, order of work, risks, and how it'll prove it works. Then implements. | `plan.md`, code |
| **4. Test** | Nothing, unless a check fails twice. | Runs the checks in `CLAUDE.md`, looks at the page, runs the `verifier` subagent. Pastes the output. | output in PR |
| **5. Deploy** | Do the part your risk tier asks for, then merge. | Reviews with `code-reviewer` against `REVIEW.md` (max 3 rounds), opens a PR from the template, fixes findings. CI validates, then Pages deploys. Full process: `docs/code-review-process.md`. | PR |
| **6. Maintain** | Decide: fix now, later, or ignore. | Notices something off (site down, catalog out of sync, a customer email pattern) and writes it up as a new `intent.md`. | new `intent.md` |

Small fixes (a typo, one price) can skip 1–2 and go straight to plan mode. Use the full loop for anything that touches checkout links, pricing, the catalog, the deploy, or a partner.

### Prompts that work

**Stage 1 (in the Claude project or Claude Code):**
> I want to change something on the Be DC site. Here's the problem: … Ask me the questions a good analyst would ask about scope, who it's for, constraints and how we'll know it worked. Then write `intent/<date>-<name>/intent.md` from `intent/_TEMPLATE.md`.

**Stage 2:**
> Read `intent/<folder>/intent.md` and write `spec.md` next to it: requirements and design for this static site. Apply the be-dc-brand skill and the rules in CLAUDE.md. List any concerns clearly, especially where rules conflict or a question in the intent is still open.

**Stage 3 (Claude Code, start in plan mode with Shift+Tab):**
> Read `intent.md` and `spec.md` in `intent/<folder>/`. Plan the change: files that change, order of work, risks, and the checks that prove it works. Then tell me what this could break, which step is riskiest, and what you decided not to do.
>
> When the plan is approved: save it as `plan.md` in that folder, implement it, run the Definition of done from CLAUDE.md, and have the verifier subagent check it.

**Bug fixes:** ask Claude to first write a check that shows the bug (e.g. a script that compares `products.json` with the cards in `index.html`), confirm it fails, commit it, and only then fix the code without touching the check.

## What's set up in this repo

| File | Playbook lesson | What it does here |
|---|---|---|
| `CLAUDE.md` | The CLAUDE.md | Commands, conventions, and the mistakes Claude tends to make on this site. Claude reads it every session. Keep it under a page. |
| `intent/_TEMPLATE.md` | Capture as intent.md | Same sections as the course template, adjusted for a shop. |
| `intent/2026-10-21-publish-only-the-storefront/` | — | First real intent: the deploy publishes every file, including the pricing sheet with margins. |
| `.claude/skills/be-dc-brand/` | Skills as institutional knowledge | Colors, type, B★DC spelling, Be ___ phrases, honest DC facts, no ®. |
| `.claude/skills/add-product/` | Skills as institutional knowledge | The four places a product lives, and how to keep them in sync. |
| `.claude/agents/verifier.md` | Parallel sessions and subagents | Report-only check in a fresh context before Claude says "done". |
| `REVIEW.md` | AI in the PR review loop | Bugs / security & privacy / compliance passes, Important vs Nit, max 5 nits. |
| `.github/workflows/static.yml` | CI/CD integration | Already in place: validate on every push and PR, deploy only from `main` after validation. Publishes only `index.html` + `assets/`. |
| `.claude/agents/site-improver.md` | Stage 6 (maintain) | Weekly live check + SEO/link previews; writes up to 3 draft intents. |
| `.claude/agents/marketing-planner.md` + `skills/free-marketing/` | — | $0 marketing: two-week content calendar and to-dos in `../bdc-growth/`. |
| `.claude/agents/collaborator-outreach.md` + `skills/partner-outreach/` | — | DC collaborator research, prospect list and Gmail drafts. Jaap sends. |
| `.claude/settings.json` + `.claude/hooks/require_approval.py` | Hooks | Forces a prompt before any email send and before any push, merge or workflow run. |

## Adopt now, later, or skip

**Now (free, no setup beyond these files)**
- `CLAUDE.md` + the rule "same mistake twice → add it to CLAUDE.md".
- Plan mode as the default start for any code change.
- Intent folders for anything non-trivial.
- The two skills and the verifier.
- Work on a branch and merge through a PR, even solo. It gives CI a chance to fail before the live site does, and the PR is the record.

**Later (when it's worth an hour)**
- **One-command check.** The CI checks live inline in `static.yml`. Moving them into `scripts/check.py` and calling that from both CI and `CLAUDE.md` gives Claude the exact same feedback loop as CI. Good second intent.
- **Claude PR review** with `anthropics/claude-code-action` in GitHub Actions, reading `REVIEW.md`. Needs an Anthropic API key as a repo secret; costs cents per PR.
- **Hooks** in `.claude/settings.json`. Two that fit this repo:
  - block edits to `.github/workflows/**` unless you've said so in the session (the deploy is the one thing that can take the shop offline);
  - block `git push` to `main` so every change goes through a PR.
  A hook is a small script that exits `2` to block and prints why. Skills are advice; hooks are enforced.
- **Scheduled check (Stage 6 light).** A weekly scheduled task: load the live site, confirm it returns 200, every shop button points to a Printful URL or "Notify me", and catalog and page agree. Anything off becomes a new `intent.md`.

**Skip at this size**
- Managed/enterprise settings, MDM, sandbox profiles, OpenTelemetry, approved plugin marketplaces.
- Eval suites in CI (20–50 benchmark tasks). Revisit only if several people or agents work on the site.
- Statistical control bands. With Printful Quick Store sales you'll see problems in your inbox before a 3σ alert would fire.
- Many parallel sessions. One or two is plenty; the limit is how much you can review.

## Keeping score (lightweight)

The course measures each stage. For one person, three numbers are enough, all readable from Git and GitHub:
- **Idea → live:** days from an `intent.md` commit to the merge that ships it.
- **First-pass green:** share of Claude's PRs where CI passes the first time. Low means `CLAUDE.md` or the checks need work.
- **Repeat mistakes:** how often you add to "Things Claude gets wrong". Should slow down over time.

## Source of truth

The repo is the source of truth for the site and its decisions. The Claude project "be dc" holds the background (story, trademark, presentations, launch plan) and mirrors these files for chats in claude.ai.
When the two disagree, the repo wins for anything about the site.
