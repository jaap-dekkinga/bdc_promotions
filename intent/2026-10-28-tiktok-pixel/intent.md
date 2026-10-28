# Add the TikTok Pixel

- **Author:** the owner (drafted with Claude)
- **Date:** 2026-10-28
- **Status:** accepted
- **Source:** idea

## Problem
TikTok ads and posts can't be measured: there's no way to see which TikTok visitors reach bedc.shop or click through to the shop.

## Proposed outcome
The TikTok Pixel (ID `DBH4743C77UF910632U0`, TikTok's own snippet) loads on every page view of bedc.shop and records a page view.

## Affected users and systems
- Pages / sections of `index.html`: `<head>`
- Outside services: TikTok (analytics.tiktok.com)

## Constraints
- Budget: $0 (the pixel is free).
- CLAUDE.md requires an intent for tracking scripts: this is it. The owner decided to add it.
- The pixel sets cookies and sends visit data to TikTok for advertising.

## Out of scope
- Event tracking beyond page views (e.g. "Shop this design" clicks) — a later change.
- A cookie banner or privacy page — see open questions.

## Open questions
- [ ] Add a short privacy notice (what the pixel collects, how to opt out) and decide whether visitors need a "Do Not Sell or Share" link (California) or consent before it loads.
