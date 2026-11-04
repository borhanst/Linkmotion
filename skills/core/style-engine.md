# Style DNA Engine (per-video uniqueness)

Core skill: generate a UNIQUE visual identity for every video. No two projects
may share the same style signature. Run this at the **proposal stage** so the
user approves the look before any beat is authored.

## Why

The user requirement: *every video gets a different style and different
animation visual elements*. Hand-picking or reusing the last video's palette
violates that. This engine makes uniqueness systematic:

- Deterministic seed from the slug (same slug = same style, reproducible).
- Uniqueness ledger `styles/style_history.jsonl` lowers the weight of
  already-used genes, so consecutive projects diverge.
- ~10 palettes x 8 font pairs x 8 motion motifs x 5 easing families x 4
  caption styles x 4 transition languages = **256k possible signatures**.

## Usage

```python
from lib.style_engine import ensure_style
r = ensure_style("<slug>", "<topic>")          # idempotent; re-run is a no-op
r["signature"]      # "palette|typography|motif|easing|caption|transition"
r["tokens_css"]     # projects/<slug>/style/tokens.css
r["design_system_md"]
r["style_card"]     # one-page animated preview for user approval
r["kit_cloned"]     # components cloned into projects/<slug>/src/html/_kit/
```

CLI preview of the style card (show it to the user for approval):

```bash
python -m tools.html_render projects/<slug>/style/style-card.html \
  projects/<slug>/renders/style-card.mp4 --duration 5.5
```

## What the genes control

| Gene | Controls |
|---|---|
| palette | bg / surface / text / muted / accent / accent2 + gradient |
| typography | display + UI font pair (Google Fonts CDN injected in tokens.css) |
| motif | background system + dedicated CSS classes (mesh-blob, grid-terminal, glass-layers, neo-brutalist, paper-ink, particle-links, iso-stacks, gradient-swim) |
| easing | the GSAP entrance ease family all beats must use |
| caption | how narration captions appear on screen |
| transition | how beats cut (accent-wipe, zoom-punch, slide-stack, morph-dot) |

## Component kit

Shared templates live in `components/html/kit/` (hook-card, stat-countup,
bullet-reveal, compare-split, chart-bars, lower-third, transition). They read
the theme ONLY from `projects/<slug>/style/tokens.css`, so the same component
renders completely differently per video.

Compose flow per beat:
1. Copy a kit component: `projects/<slug>/src/html/_kit/<component>.html`
   -> `projects/<slug>/src/html/<beat>/index.html`
2. Edit ONLY the `<!-- CONTENT START/END -->` slots (text, data, numbers).
3. Render via `lib.engine_selector.render_scene` / `html_render`.

Never edit `_kit/` copies per-beat; never hardcode colors in a beat - always
`var(--accent)` etc. from tokens.css.

## Mid-run style changes

The design-system is approved at proposal. If it must change: append a new
DecisionLog entry and re-generate with `ensure_style` after deleting
`projects/<slug>/style/` and the old ledger line (style changes are rare and
must be explicit, never silent).

## Rules

- Every project MUST have `style/tokens.css` before composing beats.
- The style card is shown to the user at the proposal approval gate.
- Consecutive slugs must not share a full signature (the ledger enforces).
- Foreground animation uses the easing gene's GSAP string; background drift is
  always `sine.inOut` perpetual (nothing fully static).
