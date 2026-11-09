# Reference: "Signal Card" style (deconstruction of @intheworldofai / WorldofAI)

> **Purpose:** user-approved reference design. When asked to "make it in the
> WorldofAI style", select this playbook. Reproduce the TECHNIQUE — dark stage,
> brand-coded evidence cards, red-box highlights, labeled B-roll, energetic
> first-person VO. **Never copy their scripts, titles, or specific framings
> verbatim** (`lib/originality.py` still applies; narration tone spec lives in
> `skills/creative/narration-tone.md`).
>
> Deconstructed 2026-11-10 from 5 latest uploads + channel profile in
> `inspiration/worldofai-channel-profile.md` (transcripts, frames,
> thumbnails).

## Frames (in `frames/`, 640px samples from the 28-min news roundup)

| File | Shows |
|---|---|
| `frame_100.jpg` | Evidence card: X-based tracking card on teal/ember gradient, red-box highlight on the key model name, source attribution INSIDE the card |
| `frame_40.jpg` | Config/diff screenshot card on cyan gradient: red/green diff lines, red-box highlight of the changed line, company icon top-right |
| `frame_200.jpg` | Full-screen dark animated technical diagram: monospace labels, dashed callout lines, supply/return arrows (for infra stories) |
| `frame_900.jpg` | Full-screen B-roll: AI-generated footage with bold white subject label bottom-left ("Claude Opus 5.5") and source credit top-right (@loktar00) |
| `frame_1600.jpg` | Mainstream-press quote card: white card, serif body with underlined source link, on dark violet gradient |
| `woa_thumb_aZMKzHhlTh8.jpg` | Thumbnail template: brand-color border + dark particle-wave bg + huge glowing white headline + logo with verified check |

## Invariant stage grammar

```
┌───────────────────────────────────────────┐
│  STAGE  near-black + soft ambient gradient│  (teal → ember drift, no hard edges)
│                                           │
│      ┌───────────────────────────┐        │
│      │  DARK EVIDENCE CARD       │        │  ~70% width, radius 12,
│      │  brand-colored accents    │        │  hairline border, drop shadow
│      └───────────────────────────┘        │
│  source: @handle / outlet · date (muted)  │  attribution inside/under card
└───────────────────────────────────────────┘
```

- Background is DARK but never flat black: perpetual soft gradient drift.
- The card is the hero. One card per beat; zoom-punch into the region being
  narrated.
- **Accent color = the story company's brand color** (seen across all 10 latest
  uploads). This is what makes every different topic feel on-brand instantly.
- No watermark of the channel itself on cards; attribution belongs to the SOURCE
  of each artifact (their "Tracked by @StatsWire • x.com/StatsWire" pattern).
- Opens fast: first card visible ~5s; zero logo animation.

## The 5 card types (evidence hierarchy)

1. **X-post card** — the "receipt" for leaks/rumors: red-box highlight on the key
   handle/model name. Vertical post screenshot OR re-styled dark card.
2. **Terminal/diff card** — config JSON or git-style diff, red/green line
   coloring, red-box on the changed line. Green/teal or violet gradient stage.
3. **Technical diagram** — infra/stories: dark full-screen animated diagram,
   monospace labels, dashed callouts, arrows (SUPPLY/RETURN-style labeling).
4. **Demo/B-roll full-screen** — AI-generated content with bold bottom-left label
   ("FABLE 5.5:") + creator credit top-right. The label names the SUBJECT while
   VO narrates behavior.
5. **Press quote card** — mainstream coverage (CNBC-type): light card, serif
   quote, source link underlined.

## Motion language

- Signature: card fade+rise entrance (y+18, blur 8→0, ~0.5s power3.out).
- Red-box annotation lands ~0.4s after the card, subtle pulse, then camera
  punch-in 1→1.15.
- Beat cadence: a card 15-35s, inside 2-4 min story blocks; story boundary =
  music dip ~1s + fresh card.
- Perpetual bg drift; nothing fully static.

## What stays FIXED vs what VARIES per video

| Fixed (the identity) | Varies (uniqueness ledger) |
|---|---|
| Dark stage + ambient gradient drift | Gradient hue pairing (teal/ember, blue/orange, violet/cyan...) |
| Card system + red-box highlight | Which card types dominate |
| Brand-color accent rule | Typography pair (keep 800-weight display headline) |
| Bottom-left subject labels on B-roll | Label font treatment slightly |
| Fast open, no logo intro | Hook composition |

## Thumbnail grammar (publish stage)

Brand-color border frame → dark particle-wave background → company logo +
verified check top-left → small colored kicker line → massive white glow
headline (product/code name). reproduced via `metadata` tool template.

## Production recipe for our pipeline

| WorldofAI element | Our implementation |
|---|---|
| Dark stage + gradient | tokens.css: `--bg`, `--bg-gradient`; gradient drift via kit bg |
| Evidence cards | kit `hook-card`/`compare-split` restyled as dark signal card |
| Red-box highlight | dedicated GSAP beat insert (scale-in + pulse) |
| Technical diagram | `minimalist-diagram`-style HTML beat with mono labels |
| B-roll + labels | `broll` tool clips + `lower-thirds` for subject label |
| Press quote card | simple HTML beat, serif face |
| Captions | `lib/captions.py` word-timed chunks (BEATS their no-captions UX) |
| Narration | `skills/creative/narration-tone.md` + `ai-news-long` script beats |
