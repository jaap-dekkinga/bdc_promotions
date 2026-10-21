---
name: apparel-storefront-ux
description: UX and conversion best practices for a story-led apparel and city-brand storefront like Be DC. Use when designing, building or reviewing any page section, product card, shop flow, copy, imagery, email capture, or social-share preview on the Be DC site.
---

# Apparel storefront UX — Be DC

Be DC sells a city identity first and T-shirts second. The page has to make people **get it → feel it → want it → buy or sign up**, mostly on a phone, mostly arriving from a social post or a QR sticker.

## 1. First screen (375px wide, no scrolling)
- The B★DC mark, one line on what it means ("Washington, DC's own logo and motto"), and one primary action: **Shop**.
- A lifestyle photo of the mark being worn in DC beats a flat product mockup here.
- Nothing else competes: no second red button, no carousel.

## 2. Story that sells
- Skimmable: short paragraphs, subheads that work on their own, the B / ★ / DC meaning shown as a visual breakdown, not a wall of text.
- The founder and origin (Dutch founder, I amsterdam inspiration) build trust; keep them human and short.
- "Be ___" is the hook: make the blank feel fillable (examples, a rotating word with a reduced-motion fallback, the star as the blank).
- Put a "Shop" link at the end of every story section; don't make people scroll back up.

## 3. Product cards
- Same image aspect ratio, crop, angle and background on every card. Image first, then name, price, the Be ___ phrase. The DC fact is secondary detail.
- Price always visible, in USD, never only on hover.
- One button per card. Label says what happens: "Shop this design" (leaves for Printful; open in a new tab and say "opens our Printful shop") or "Notify me" (not for sale yet; leads to a one-step email signup, not a long form).
- Near the grid, not only in the footer: "Printed to order · ships in 2–5 business days · free shipping over $50".
- 2 columns from tablet up, 1 on small phones is fine for 7 products; avoid horizontal product carousels on mobile.

## 4. Apparel essentials once a product is live
Size guide and fit notes (Bella+Canvas 3001 runs unisex), available colors shown as swatches, material and care, returns/reprint policy (Printful's), front and back views where both are printed. If these live on Printful, link to them clearly.

## 5. Trust, honestly
- Real photos, the real story, a real contact address, the "Be ___" partners shown only as ideas unless they've agreed.
- **Never:** fake or AI-written reviews/testimonials, fake scarcity ("only 3 left"), countdown timers, exit-intent pop-ups, pre-ticked opt-ins, hidden shipping costs, confirmshaming ("No thanks, I don't love DC").

## 6. Email capture
One field, clear value ("Be first when the shop opens — one email, no spam"), placed after the story or in "Notify me". Confirm what happens after submit.

## 7. Social and sharing
Most traffic comes from shares, so the preview is the first impression:
- `<title>` and meta description that say what B★DC is.
- Open Graph + Twitter card tags with a 1200×630 image (mark + a DC scene), `og:url`, `og:type=website`.
- Favicon and apple-touch-icon from the star or the tag logo.

## 8. Modern patterns that fit a one-page brand site
- Sticky bottom "Shop" bar on mobile after the hero scrolls away.
- Lookbook row: 3–5 lifestyle photos at DC landmarks, edge to edge.
- Large type with tight leading for headlines; generous whitespace; navy as the base, red only for primary actions and the star.
- Subtle motion only (fade/slide under 300ms), always disabled under `prefers-reduced-motion`.

## 9. Performance is UX
- Hero image: not lazy-loaded, sized for its slot, WebP/AVIF with a JPEG fallback, explicit `width`/`height`.
- Everything below the fold: `loading="lazy"`, explicit dimensions (no layout shift).
- Fonts: only the weights used, `display=swap`.
- Targets: Largest Contentful Paint < 2.5s and Cumulative Layout Shift < 0.1 on a mid-range phone.
