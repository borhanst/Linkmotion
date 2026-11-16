# Thumbnail Style — "Receipts" layout (project-agnostic)

Core skill for publish-stage YouTube thumbnails. Describes a reusable 1280x720
layout: a project-owned capture under a dark gradient, a big model/title word,
a short payoff line, one numeric badge, and a source/provenance line.

Use when creating YouTube thumbnail variants, writing publish metadata, or when
the user asks how a thumbnail looks / wants a repeatable thumbnail style.

**Reference example only:** `projects/2026-11-qwen4-max-long/metadata/thumbnail/thumb-1.png`
originated this layout. Its palette, capture, wording and source label are
*examples* — for any other project, substitute that project's own tokens,
approved capture, copy and source line.

## Visual spec (1280x720, 16:9)

Layer order, bottom to top:

1. **Capture** — an image the project is allowed to use (its own capture,
   screenshot or asset), cover-cropped to fill 1280x720. Set a focus point per
   image so the subject stays visible. thumb-1 used a hero capture at focus
   `(0.52, 0.48)`.
2. **Overlay** — horizontal gradient of the project's `--bg`, alpha `244` at
   x=0 down to `148` at x=1279. Left (text side) near-opaque; right stays
   visible. This is the flat, high-contrast look.
3. **Accent bar** — vertical 10px bar at x=72..82, y=156..520, gradient
   `--accent` (top) → `--accent2` (bottom).
4. **Headline** — model name or topic, bold 112px, `--text`, at `(104, 150)`,
   black drop shadow `(+4,+5)`.
5. **Payoff** — 2–4 words, bold 56px, `--accent2`, at `(108, 292)`, same shadow.
6. **Badge** — rounded rect (radius 16) at `(108, 396)`, fill `--surface`,
   3px `--accent` border; one number in `--accent2` at 44px.
7. **Source line** — the project's source label + date (e.g. source domain ·
   date), `--muted`, 22px, at `(104, 664)`.

## Rules

- **3–6 words of bold text max**: headline + short payoff + one numeric badge.
- Read the target project's `style/tokens.css` for `--bg`, `--surface`,
  `--text`, `--muted`, `--accent`, `--accent2` — never hardcode another
  project's palette. The script accepts `--tokens` for this.
- Headline/payoff are always light or accent-colored on the dark overlay;
  never light-on-light. If a capture is bright, strengthen the overlay alpha.
- The badge number must be a real figure from that video, verbatim.
- Source line is mandatory and must follow the project's provenance policy.
- Use only imagery the project is permitted to show.
- Generate 2–3 variants: swap capture + payoff + badge, keep the layout fixed.

## Reproduce

General command (all content args are explicit — no project defaults):

```bash
python skills/core/scripts/make_thumbnail.py \
  --capture <path-to-approved-image.png> \
  --title "MODEL-NAME" --sub "THE RECEIPTS" --badge "−62% / TASK" \
  --source-label "source.example · Nov 16, 2026" \
  --tokens projects/<slug>/style/tokens.css \
  --focus-x 0.52 --focus-y 0.48 \
  --out projects/<slug>/metadata/thumbnail/thumb-1.png
```

To reproduce the original thumb-1 exactly, use its capture, the qwen.ai source
label, and `projects/2026-11-qwen4-max-long/style/tokens.css`. The project-local
reference implementation for all three original variants is
`projects/2026-11-qwen4-max-long/src/make_thumbnails.py`.

## QA

Open every PNG at 100% and check: capture visible on the right, all words fully
inside the canvas with no clipping, badge border intact, source line legible,
no light background behind light text. Confirm 1280x720 with Pillow or `file`.
