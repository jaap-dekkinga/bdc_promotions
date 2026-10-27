---
name: free-marketing
description: Playbook for free and low-cost marketing of B★DC (Be DC) merch: which channels, what to post, DC calendar hooks, community rules, and how to measure. Use when planning posts, a content calendar, a launch push, local press pitches, or any "how do we get the word out" question for Be DC.
---

# Free and low-cost marketing for B★DC

Budget: **$0** unless the owner approves a specific spend. Agents plan and draft; **the owner posts and sends**. Brand rules: `be-dc-brand` skill (it wins on any conflict).

## Check this first
- **Can people buy?** Read `buy_url` in `data/products.json`. While a product's link is `""`, posts about it must ask people to tap "Notify me" / email, not "shop now". If no product is buyable, the top to-do is always "Get Printful links live", and posts aim at building the email list and partners.
- **Does the link preview work?** If `index.html` has no Open Graph image, every shared link looks bare. Flag it to `site-improver` before a big push.

## Building blocks
Every post = one **Be ___ phrase** + one **DC fact** (checkable, one sentence, dated if it changes) + one image from `assets/img/` (or a photo the owner takes) + one link.

| Product | Phrase | Image |
|---|---|---|
| T-shirt white | Be seen | `product-tshirt-white.jpg`, `hero-*.jpg` |
| T-shirt grey | Be everyday | `product-tshirt-dark.jpg` |
| Hoodie | Be warm | `product-hoodie.jpg`, `product-hoodie-back.jpg` |
| Polo | Be sharp | `product-polo.jpg` |
| Hat | Be covered | `product-hat.jpg` |
| Tote | Be prepared | `product-tote.jpg` |
| Mug | Be awake | `product-mug.jpg` |

Re-read `data/products.json` before using this table; the catalog wins if they differ.
Links: `https://bedc.shop/?utm_source=<channel>&utm_medium=social&utm_campaign=<yyyy-mm-topic>` so clicks can be told apart later.

## Channels, in priority order
| Channel | Why | Cost / effort | What to do |
|---|---|---|---|
| Instagram (feed, Reels, Stories) | DC locals + visitors, visual | $0 / M | 3 posts a week. Reels: the "read it like the alphabet" B-★-DC reveal; "Be ___" street fill-in-the-blank. Location tags: National Mall, U Street, Navy Yard, Georgetown. |
| TikTok | Reach beyond followers | $0 / M | Repurpose Reels. Hooks: "DC never had a city logo. So I made one." |
| Threads / Bluesky | DC politics/policy crowd, journalists | $0 / S | One-line Be ___ + fact; reply to local news threads, don't hijack them. |
| Reddit r/washingtondc, r/dcmetro | Very local, allergic to ads | $0 / S | Participate first. At most one self-post when there's real news (launch, a partner), framed as "I made this", per subreddit rules. Never repost the same thing. |
| Nextdoor, neighborhood Facebook groups, listservs | Neighbors buy local | $0 / S | Only where self-promotion is allowed; read the group rules first. |
| Pinterest | Long-lived search traffic for DC gifts | $0 / S | Pins per product, "Washington DC gift" boards. |
| Local press & newsletters | Credibility, one-off spikes | $0 / M | Pitch the story (DC's first city mark, the 2010 research, the Constitution "B"), not the product. Hand the outreach to `collaborator-outreach`. |
| Email list | The only channel the owner owns | $0 / M | Every post points to "Notify me" until a list tool is approved via an intent. |
| Pop-ups, markets, events | Sell in person, photos for posts | low $ / L | Ask before spending: table fees need the owner's OK. |

## DC calendar hooks
Plan around these; **look up this year's exact dates** before scheduling and never invent an event.
- Jan: New year, "Be ___ this year" prompt. Feb: Black History Month (DC history facts, carefully sourced).
- Mar–Apr: National Cherry Blossom Festival (biggest visitor season). DC Emancipation Day, April 16.
- May–Jun: graduations ("Be proud"), Capital Pride.
- Jul 4; **Jul 16: Residence Act anniversary (1790)**, the B★DC "birthday" on the site.
- Sep–Oct: back to school/work ("Be awake" mug), Marine Corps Marathon (late Oct; "Be challenged" is a *proposal*, never claim a partnership).
- Nov–Dec: holiday gifts (tote, mug, hoodie), shipping-deadline reminders from Printful.
- Year-round: Nationals, Capitals, Wizards, Mystics, Spirit, D.C. United home games. Don't use team names or logos in a way that implies a licence.

## Content types that work for a city mark
- **Explainer:** what the B, the ★ and the striped DC mean (from the story section).
- **Fill in the blank:** "Be ___ in DC. What's yours?" Collect answers for future products.
- **Fact Friday:** one checkable DC fact + the matching phrase.
- **People wearing it:** ask buyers/friends for photos; repost only with permission and credit.
- **Behind the scenes:** the 2010 research, the trademark *pending* (no ®, no legal claims).

## Rules
- No paid ads, giveaways with purchase requirements, or bought followers without the owner's OK.
- No posting, DMs or emails by the agent. Drafts only.
- Don't claim DC.gov, a team, an event or a business endorses Be DC.
- Facts: stable history preferred; changing numbers need a source and year; 2010 stats framed as "when the project started in 2010…".
- All plans, calendars and drafts go to `../bdc-growth/`, never into the public repo.

## Measuring (free)
Weekly, ask the owner for: followers per channel, Instagram/TikTok views on the top post, "Notify me" emails received (Gmail search `to:bdcpromotions@gmail.com newer_than:7d`), and Printful orders once live. Keep the numbers in the weekly report; drop a channel after 6 weeks of nothing.
