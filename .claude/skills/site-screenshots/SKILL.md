---
name: site-screenshots
description: Capture full-page screenshots of the Be DC site at phone, tablet and desktop widths. Use before running the ui-ux-designer subagent, for before/after comparisons of a visible change, and as evidence in a PR.
---

# Screenshots of the Be DC site

The `ui-ux-designer` subagent is read-only and can't take screenshots, so the main session captures them and passes the file paths.

## Where to save
**Outside the repo**: the GitHub repo is public, so keep binaries and review artefacts out of it. Use a sibling folder:
`../review-screenshots/<YYYY-MM-DD>-<change>/`
Name files `<width>.png`, plus a `before-` prefix for the version on `main` when comparing.

## Steps
1. Start the site from the repo root: `npx serve . -l 3000` (run it in the background).
2. Capture three full-page screenshots:
   ```bash
   OUT=../review-screenshots/$(date +%F)-<change>
   mkdir -p "$OUT"
   npx playwright screenshot --full-page --viewport-size=375,812  http://localhost:3000 "$OUT/375.png"
   npx playwright screenshot --full-page --viewport-size=768,1024 http://localhost:3000 "$OUT/768.png"
   npx playwright screenshot --full-page --viewport-size=1280,800 http://localhost:3000 "$OUT/1280.png"
   ```
   - **On the owner's computer:** the first time, run `npx playwright install chromium`.
   - **In the cloud workspace:** use the preinstalled `playwright` command instead of `npx playwright` (npx can pull a version that doesn't match the installed browser), and don't run the install.
   If Playwright isn't available at all, use a browser tool: open http://localhost:3000, resize to each width, and capture the full page.
3. For a section close-up (e.g. the shop grid), also capture just that section: open the page at `#shop` and take a viewport screenshot.
4. For before/after: check out `main` in a worktree or stash the change, capture with the `before-` prefix, then return to the change and capture again.
5. Open each image with Read and confirm it shows the whole page (not blank, not cut off, fonts loaded). If fonts look like a fallback, wait a second and retake.
6. Stop the server.

## Handing off
Pass the absolute paths to the subagent, e.g.:
> Run the ui-ux-designer subagent on the shop section. Screenshots: <path>/375.png, <path>/768.png, <path>/1280.png (before: <path>/before-375.png …).
