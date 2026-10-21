---
name: partner-outreach
description: Rules and templates for reaching potential B★DC (Be DC) collaborators — DC shops and cafés, events and organizations, creators and press, artists and designers. Use when finding prospects, writing a first email or follow-up, or deciding what to offer a partner.
---

# Collaborator outreach for B★DC

Goal: a few real relationships with DC people and places that make B★DC visible, not volume.
Agents research and write **Gmail drafts**. **Jaap reviews and sends every email.** A hook (`.claude/hooks/require_approval.py`) forces a prompt on mail-send tools and commands. It can't see browser clicks, so never open Gmail on the web to send.

## Where things live (private, outside the public repo)
- `../bdc-growth/prospects.csv`: columns `name,segment,website,public_contact,contact_source_url,why_fit,proposed_be_phrase,offer,status,first_contact,last_contact,next_step,notes`
- `../bdc-growth/outreach-log.md`: one line per action, newest first.
- `status` values: `researched` → `drafted` → `sent` (only Jaap sets this, or it's inferred from Gmail Sent) → `replied` → `talking` → `partner` / `closed`.

## Segments and what to offer
| Segment | Examples of who | Offer that fits | Proposed phrase idea |
|---|---|---|---|
| DC shops & cafés | Independent gift shops, bookstores, coffee shops, museum-adjacent stores, hotel shops | Consignment or small wholesale order of totes/mugs; a counter card with QR to bedc.shop | Be awake (café), Be prepared (bookstore) |
| Events & orgs | Neighborhood BIDs and Main Streets, races, festivals, sports clubs, nonprofits | Co-branded Be ___ tee for volunteers/runners at cost; a share of proceeds to the cause | Be challenged (race), Be together (festival) |
| Creators & press | DC Instagram/TikTok creators, local blogs, newsletters, podcasts, local-news "makers" beats | A free piece to keep, no posting required; the origin story as a feature | Be seen |
| Artists & designers | DC illustrators, muralists, typographers | A limited Be ___ drop with their design, credited, revenue share agreed in writing | Their own word |

Phrases are **proposals** to the partner. Never say or imply a partner endorses or sponsors Be DC before a signed agreement.

## Research rules
- Use only **public business** contact details: a contact page, a press/partnerships address, a business email on the official site or official social profile. Record the URL where you found it in `contact_source_url`.
- No personal emails or phone numbers, no guessed addresses (`firstname@…`), no scraping people's private profiles, no data-broker sites.
- Prefer organisations with a visible DC/local identity and recent activity (posted in the last 3 months).
- Before adding anyone, search `prospects.csv` and Gmail (`search_threads` for their domain or name) so nobody is contacted twice.

## Email rules
- From B★DC (bdcpromotions@gmail.com), signed by Jaap Dekkinga, founder of B★DC. Honest about who Jaap is and that it's a small project.
- ≤ 120 words. Subject ≤ 7 words, specific to them, no clickbait, no "Re:" tricks.
- Structure: one line on why *them* (something specific and true from their site) → what B★DC is in one sentence → one concrete offer from the table → one easy ask (a 15-minute call or "can I drop off a sample?") → link to https://bedc.shop.
- End with: "If this isn't for you, just say so and I won't follow up."
- One follow-up at most, 10+ days after a sent email with no reply, shorter than the first. Then `closed`.
- Never: attachments, tracking pixels, promises of money or exclusivity, legal claims about the trademark (it is *pending*; no ®), or invented facts.
- Brand voice from `be-dc-brand`: proud, short, a bit playful.

## Example first email (shop)
Subject: A DC mug for your counter?

Hi <name>,
I love that <shop> stocks <specific local thing>. I'm Jaap, and I make B★DC, a city logo for Washington where the star stands for any word: Be awake, Be seen, Be DC.
Would you try a small consignment of B★DC mugs and totes by the register? No cost to you; I'd bring them by and set up a little card.
Could I drop off a sample next week? https://bedc.shop
If this isn't for you, just say so and I won't follow up.
Jaap Dekkinga, B★DC
