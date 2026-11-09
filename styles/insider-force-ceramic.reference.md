# Reference: "Ceramic Diagram" style (deconstruction of @InsiderForce)

> **Purpose:** user-approved reference design. When asked to "make it in the
> InsiderForce style" or when this playbook is selected, read this file + the
> frames below and reproduce the TECHNIQUE. Never copy their wording, scripts,
> or specific framings verbatim (originality rules still apply, see
> `lib/originality.py`).
>
> Sampled from 5 shorts (802K / 414K / 43K / 45K / newest 13K views), Nov 2026.
> ~29 sampled frames across 2 videos confirmed zero layout violations.

## Frames (in `inspiration/borhan/insiderforce-ceramic-diagram/frames/`)

| File | Shows |
|---|---|
| `hook-countdown-intro.png` | Classic hook frame: hub icon + 4 satellite tiles + 2-line type with anchor emphasis |
| `hub-diagram-icons.png` | Hub-and-spoke logo diagram the day the 802K video uses (mixed real logos) |
| `countdown-node.png` | "#3" gray beat marker + satellite tile hanging above hub |
| `countdown-bar.png` | Matte-black 3D "02" bar variant of the countdown device |
| `ui-dark-mockup.png` | Dark terminal UI inside white-framed card + coral starbursts |
| `dark-cinematic-card.png` | Foggy fantasy screenshot inside white browser card (variation case) |

## Invariant layout (never violated in sample)

```
┌─────────────────────────┐
│   HERO VISUAL           │  top ~55%: one focal object, centered
│                         │
├─────────────────────────┤
│   2-5 SHORT TYPE LINES  │  bottom ~30%, sentence case
│   anchors bold, rest    │  muted gray
├─────────────────────────┤
│   insiderforce.io       │  watermark, light gray, every beat
└─────────────────────────┘
```

- Background is FLAT near-white `#F1F0EE` - no gradient, no texture, ever.
- Exactly ONE hero visual per beat. If two objects exist, one is foreground
  and one is blurred behind (rack-focus tells the viewer which).
- No faces. No real screen recordings. All UI is reconstructed as mockups.

## The 3 hero-visual types

1. **3D product render** - laptop / GPU stack / tablet, neutral studio light,
   soft offset shadow. Slight non-zero camera angle, off-axis landing.
2. **Hub-and-spoke icon diagram** - logos inside white ceramic tiles/circles
   connected by thin lines to a central white circle. Lines draw outward from
   hub. Tiles tilt ±6deg and sit at varied depths (some blurred).
3. **Floating UI card** - white-framed browser/terminal card, content either
   light re-rendered website (frosted text sharpening in) or dark cinematic
   screenshot. Always with visible heavy border-radius + drop shadow.

## Typography system (the signature element)

- Inter/Helvetica, sentence case, tight line height (1.15).
- Per line: 1-2 **bold `#1A1A1A` anchor words**; everything else `#B7B5B2`.
  Weight/color contrast, not size contrast, carries emphasis.
- Escape hatches (one per video max each):
  - italic phrase ("*you actually need*")
  - white italic-on-matte-black pill
  - coral starburst beside/between type
- Numbers/beats as device: "#3" plain gray text, or "02" on matte-black 3D bar.
- Big single-icon beats (one starburst, one mascot) act as breathers.

## Motion language

- **Signature:** everything enters BLURRED and sharpens (blur 14px -> 0,
  scale 1.04 -> 1.0, ~0.7s power2.out). Cheap, AI-premium, mimics rack focus.
- Connector lines scale-draw from hub. Type lines rise word-by-word; the
  anchor word lands last, with a tiny overshoot.
- No camera shake, no parallax beyond 0-0.6% drift, no b-roll.
- Beat = one claim. 9-11s cadence. Cut on what they call a "beat marker"
  (#3 / 02 / → bullet).

## Production recipe for our pipeline (Remotion/hyperframes mapping)

| InsiderForce element | Our implementation |
|---|---|
| Near-white flat bg | tokens: `--bg: #F1F0EE` |
| Hero stills | `broll` / image-gen: "product render on flat light-gray bg, soft studio shadow" |
| Type frames | kit component: hook-card / bullet-reveal with mixed-weight word spans |
| Rack-focus entrance | CSS blur keyframes, or Remotion spring on `filter: blur()` |
| Countdown markers | kit: stat-countup variant / next-frame card |
| Coral accent | `--accent: #E2725B` (only one saturated hue in the video) |

## When to use / not use

- **Use:** AI tool/news shorts, list formats, "this changes X" single-claim
  stories. Matches Vertical 9:16, mobile-first scanning.
- **Do NOT use** for: dark/moody topics (needs near-white bg), data-heavy
  charts (it has only 3 hero types, all illustrative).
- Per-video uniqueness note: The style engine enforces unique signatures per
  slug. When user requests THIS style, keep the **system** (layout grammar,
  blur-in motion, ceramic tiles, flat white bg, mixed-weight type) identical
  and swap only the **accent hue + font hum** per video so the ledger still
  logs a distinct signature; the ledger entry cites this playbook as base.
