# Agents for site improvement, free marketing and collaborator outreach

- **Author:** the owner (drafted with Claude)
- **Date:** 2026-10-21
- **Status:** accepted (implemented on branch growth-agents)
- **Source:** idea

## Problem
bedc.shop is live, but nobody is working on it between the owner's sessions: nothing checks it, nobody plans posts, and nobody reaches out to DC shops, events, creators or artists.
A review on 2026-10-21 found internal files public on the site, all 7 products on "Notify me" (nothing buyable), and no link preview tags, which makes every shared post look bare.

## Proposed outcome
Three Claude Code subagents, run by hand or once a week, that only report and draft:
- `site-improver`: live health, leaks, shop buttons, catalog sync, SEO/link previews → report + up to 3 draft intents.
- `marketing-planner`: $0 channels → two-week content calendar with captions + ranked to-dos.
- `collaborator-outreach`: finds DC collaborators → prospect list + Gmail drafts + follow-ups. The owner sends.
A hook makes Claude Code ask the owner before any email is sent and before any push, merge or workflow run that could deploy.

## Affected users and systems
- Files: `.claude/agents/`, `.claude/skills/free-marketing/`, `.claude/skills/partner-outreach/`, `.claude/settings.json`, `.claude/hooks/require_approval.py`, `CLAUDE.md`
- Outside the repo: `../bdc-growth/` (private working files)
- Outside services: Gmail (drafts only), a local weekly scheduled task in the Claude desktop app

## Constraints
- Budget: $0/month. Any spend is the owner's decision.
- Brand: follows the `be-dc-brand` skill; partner phrases are proposals, never endorsements.
- The repo is public on GitHub: prospect names, contacts, drafts and plans never go in it.
- Agents never send, post, commit, push or deploy.

## Out of scope
- Paid ads, an email-list tool, analytics scripts (each needs its own intent).
- Changing the site itself; the agents only propose intents.

## Open questions
- [ ] Should the private `bdc-growth` folder become a *private* GitHub repo for backup?
- [ ] Which Gmail account should drafts land in: bdcpromotions@gmail.com or the owner's own?
