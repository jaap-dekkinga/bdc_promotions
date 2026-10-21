---
name: web-accessibility
description: WCAG 2.2 AA accessibility rules for the Be DC site, including pre-computed contrast for the brand colors. Use when building or reviewing any HTML, CSS, color choice, image, form, navigation or animation on the site.
---

# Web accessibility (WCAG 2.2 AA) — Be DC

## Brand color contrast (computed 2026-10-21)

| Text / foreground | Background | Ratio | Normal text (4.5:1) | Large text & UI parts (3:1) |
|---|---|---|---|---|
| White `#FFFFFF` | Navy `#002664` | 14.4:1 | ✔ | ✔ |
| Navy `#002664` | White | 14.4:1 | ✔ | ✔ |
| White `#FFFFFF` | Red `#BB133E` | 6.4:1 | ✔ | ✔ |
| Red `#BB133E` | White | 6.4:1 | ✔ | ✔ |
| **Red `#BB133E`** | **Navy `#002664`** | **2.2:1** | ✘ | ✘ |

**Never put red text, red icons or thin red lines on navy.** Use white on navy, and red only on white or as a filled button with white text.
For greys or any new color, compute the ratio before using it:

```python
def lum(h):
    c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
def ratio(a, b):
    hi, lo = sorted([lum(a), lum(b)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)
print(round(ratio("6B7280", "FFFFFF"), 2))
```

Large text = at least 24px regular or 18.66px bold.

## Checklist

**Structure**
- One `h1`; headings in order without skipping levels; landmarks: `header`, `nav`, `main`, `footer`.
- A "Skip to content" link as the first focusable element.
- `lang="en"` on `<html>`.

**Images**
- Product images: `alt` says what it is and its color ("B★DC hoodie in navy, logo on the chest").
- Purely decorative images: `alt=""`. The logo: `alt="B★DC — Be DC"`.
- No important text baked into images without the same text in HTML.

**Keyboard and focus**
- Everything clickable is reachable with Tab, in visual order, and works with Enter/Space.
- Visible `:focus-visible` outline with at least 3:1 contrast against its background; never `outline: none` without a replacement.
- Sticky header must not hide the focused element or an anchor target (`scroll-margin-top` on sections).
- Mobile menu toggle: a `<button>` with `aria-expanded` and `aria-controls`; Esc closes it; focus returns to the toggle.

**Touch and zoom**
- Tap targets at least 44×44px (WCAG minimum is 24×24; 44 is the comfortable target) with space between them.
- Page works at 200% zoom and at 320px wide without horizontal scrolling. Never disable zoom in the viewport meta.

**Forms**
- Every field has a visible `<label>` (placeholder is not a label), the right `type` and `autocomplete` (`name`, `email`).
- Errors appear next to the field in text, not color alone, and are announced (`aria-live="polite"` on the status message).
- Required fields are marked in text.

**Links and buttons**
- Link text makes sense on its own; seven "Shop this design" buttons need context, e.g. `aria-label="Shop the B★DC hoodie"`.
- Links opening a new tab say so (visually or in the accessible name) and use `rel="noopener"`.
- Buttons for actions, links for navigation.

**Motion**
- Respect `prefers-reduced-motion: reduce`: no auto-rotating text, parallax or large movement.
- Nothing flashes more than 3 times per second.

**Text**
- Body at least 16px, line-height at least 1.5, paragraphs at most ~75 characters wide.
- Text can be resized and spacing adjusted (WCAG 1.4.12) without content being cut off.
