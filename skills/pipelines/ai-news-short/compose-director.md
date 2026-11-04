# Compose Director - AI News Short

Assemble beats into a composition and render the final MP4.

## Load the official skills first

Before authoring any scene, load the engine's official skill so the coding
agent has the correct API knowledge (import paths, code patterns, constraints,
parameters). These are Layer 3 skills installed in the user's environment:

- Remotion: `remotion-best-practices` (router) + `remotion-create`, `remotion-markup`,
  `remotion-render`, `remotion-captions`, `remotion-multimedia`,
  `remotion-interactivity`, `remotion-studio`
- HyperFrames: `hyperframes` (router) + `hyperframes-html-authoring`

Load them via the skill tool before writing scene code. Do not guess from
memory - the installed version may differ from what you know.

## Component reuse (check before authoring)

Before writing a scene from scratch, check whether an existing component already
fits and only needs customizing:

1. **Scan the project's own components.** For Remotion look under
   `projects/<slug>/src/remotion/<scene-id>/components/` and any shared
   `components/` the video reuses. For HyperFrames look under
   `projects/<slug>/src/hyperframes/<scene-id>/assets/` and prior scenes'
   `composition.html`.
2. **Match by purpose.** A card with the same structure (hook / stat / verdict),
   a web walkthrough, a media frame, a social feed - reuse it.
3. **Customize, don't duplicate.** If a component fits, clone it and change only
   what differs:
   - **Name / title / kicker** - from the storyboard.
   - **Logo / brand** - from the research brief (lab name, model string).
   - **Data** - from `research.md` data points (numbers, dates, prices, benchmarks).
   - **Palette** - from the style playbook.
   Never silently duplicate a component that already does the job.
4. **Log the reuse.** Append to `projects/<slug>/engine_decisions.json`:
   `{"scene_id": "...", "reused_from": "<path>", "customized": ["title", "data"]}`.
5. **If nothing fits**, author a new component and record it as new.

## Dual-engine composition

Each beat is authored and rendered independently under
`projects/<slug>/src/<engine>/<beat-id>/`, then concatenated into the final
MP4. The LLM picks the engine per beat:

| Engine | Authoring | When to use |
|---|---|---|
| `remotion` | React component (`index.tsx`) | Bespoke programmatic UI, charts, long-form, motion graphics |
| `hyperframes` | Plain HTML (`composition.html`) | Existing web material, templates, data-driven cards, GSAP/Lottie |

Default: **Remotion**. Switch to **HyperFrames** for a beat that is better
expressed as HTML/CSS (a captured page, a template card, an existing animation).

Decision framework: `lib/engine_selector.py` (`recommend_engine`,
`resolve_engine`, `render_scene`). Heuristic fallback: `web`/`media`/`social`
beats -> HyperFrames, everything else -> Remotion. Always set an explicit
`engine` field on the beat so the choice is auditable.

## Input

`projects/<slug>/storyboard.json`, `projects/<slug>/assets/manifest.json`

## Tools

Required: `video_compose` (Remotion) and/or `video_compose_hyperframes` (HyperFrames).
Query `python -m ai_news_agent preflight` to see which are available.

## Process

1. **Decide the engine per beat.** Write the decision + rationale into
   `projects/<slug>/engine_decisions.json` (an `EngineDecision` per beat).
2. **Author the beat** under `projects/<slug>/src/<engine>/<beat-id>/`:
   - Remotion: `index.tsx` + any shared components under `components/`.
   - HyperFrames: `composition.html` + local media under `assets/`.
3. **Render the beat** to `projects/<slug>/renders/<beat-id>.mp4`:
   ```bash
   python -c "from lib.engine_selector import render_scene; print(render_scene(beat, '<slug>'))"
   ```
   or directly:
   ```bash
   npx remotion render src/<slug>/src/remotion/<beat>/index.tsx <slug>-<beat> renders/<beat>.mp4 --fps 30 --crf 23
   npx hyperframes render src/<slug>/src/hyperframes/<beat> -c composition.html -o renders/<beat>.mp4 -f 30 --crf 23
   ```
4. **Concatenate** the per-beat MP4s into `out/<slug>.mp4` with FFmpeg.
5. **Preview each beat before the next.** Never batch-generate all beats.

## Motion system

Follow the repo's Motion graphics system (`remotion-youtube-video` skill):
- Spring easing default: `spring({frame, fps, config:{damping:12, mass:0.6, stiffness:120}}).
- 9:16 framing, 1080x1920.
- Captions word-synced to edge-tts timestamps - big, bold, high-contrast,
  1-2 words at a time, centered.
- Loop-friendly last beat.
- Nothing fully static: slow drift / Ken-Burns.
- Banned: CSS transitions, wall-clock, unseeded randomness, particle bursts,
  lens flares, camera shake, holds longer than ~15f with nothing moving.

For HyperFrames beats: paused timeline + `data-start`/`data-duration` +
CSS/GSAP/Lottie; no wall clocks, no unseeded randomness.

## Build ONE beat at a time

Preview each beat before the next.

## Output: `projects/<slug>/render_report.json`

```json
{"slug": "...", "out_mp4": "out/<slug>.mp4", "duration_sec": 60.1,
 "fps": 30, "composition_id": "<slug>-full", "ok": true,
 "engine": "mixed", "beats": [{"id": "hook", "engine": "remotion", "mp4": "renders/hook.mp4"}]}
```

## Success criteria

- Output exists and plays.
- ffprobe duration inside 45-75s.
- Captions word-synced.
- 9:16 safe-zone check.
- Every beat has an explicit, logged engine decision.

## HTML renderer (default)

Default engine is now plain HTML + GSAP/Anime.js recorded via Playwright (`tools/html_render.py`). See `skills/core/html-render.md`. Lower thirds: `components/html/lower-third.html`. Page transitions: `components/html/page-transition.html`.

## Lessons learned (composition / render)

### Default engine: html_render (Playwright) — not Remotion
For Shorts built from page captures and cards, use the HTML engine. It requires only Playwright + ffmpeg (no Node/Remotion install). Load GSAP from CDN (`https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js`) inside self-contained HTML.

### Per-beat authoring (1080x1920 Shorts)
- Author each beat as self-contained `composition.html` with inline GSAP animations that complete within `duration_sec`.
- Use viewport `[1080, 1920]`, fps 30, crf 23.
- Add a dark mesh-gradient background + brand accent colors + a bottom caption bar synced to the narration phrase.
- Never more than two `web` scenes in a row; open/close with `card` scenes.

### Render + mux + concat (per beat)
1. `html_render.render(composition.html, renders/beat-N.mp4, duration_sec=..., viewport=[1080,1920])` → video-only MP4.
   Default `mode="auto"` now uses **frame-stepped rendering** (GSAP master timeline seeked at exact fps, screenshot per frame): deterministic, no dropped frames. Pages without GSAP fall back to real-time recording automatically. See `skills/core/html-render.md`.
2. Captions: burn word-timed captions into the beat HTML *before* rendering with `lib.captions.burn(html, tts_words)` — 1-2 word chunks popping in/out on the edge-tts `WordBoundary` timestamps (`tools/tts.py` returns true per-word offsets). Re-render after burning.
3. Optional SFX at beat boundaries: `tools/sfx.py` — `SfxTool().synthesize("whoosh"/"pop"/"tick"/"sweep", path)` (ffmpeg-synthesized, deterministic) or drop CC0 assets in `assets/sfx/`, then `SfxTool().mix("audio/beat-N.mp3", events, "audio/beat-N-mixed.mp3")` with `events=[{"path":..., "at": sec, "gain_db": -14}]`. Narration timing is preserved exactly.
4. Mux with edge-tts audio: `ffmpeg -y -i renders/beat-N.mp4 -i audio/beat-N.mp3 -c:v copy -c:a aac -shortest renders/beat-N-av.mp4`
5. Concatenate all `beat-N-av.mp4` into `out/<slug>.mp4` with ffmpeg concat (`-c copy`).
6. Verify final duration with ffprobe (must be inside 45-75s).

### Review after compose
Run `python -m lib.reviewer <slug> render_report projects/<slug>/render_report.json` and confirm output exists, duration inside window, and engine decisions logged.

### Scene QA gate - before presenting ANY beat or the concat

1. **Static check (cheap, first):** `python -m tools.scene_doctor projects/<slug>/src/html/` - catches broken stylesheet/image paths, GSAP issues, the `.from(opacity:0)`-on-hidden-element bug, and caption stacking before a single frame renders. Fix every FAIL.
2. **Frame check (always):** extract frames at key moments and view them - `ffmpeg -y -i renders/beat-N.mp4 -ss <t> -vframes 1 /tmp/opencode/qa-bN.png`. Key moments: each highlight/reveal time from the storyboard actions, plus start/middle/end. Verify: theme applied, images visible, overlays on target, captions centered on one line, no overlap, 9:16 safe zones. See `skills/core/html-render.md` for the full failure-mode table.
3. Only then preview to the user. Never present on the strength of `ok: true` alone - frame extraction has caught theme loss, missing captures, invisible elements, and caption stacking that all rendered "successfully".

### Overlay/highlight pattern for web scenes (user preference)

- NO stroked ring boxes - use **soft background highlights** (accent tint + glow, no border): `.hlmark { position:absolute; border-radius:14px; background:color-mix(in srgb, var(--accent) 30%, transparent); box-shadow:0 0 36px color-mix(in srgb, var(--accent) 45%, transparent); }`
- Highlights live INSIDE the same wrapper as the screenshot so Ken-Burns zoom/pan moves them with the image - never position them in view coords while the image transforms independently.
- Measure targets from the LIVE page (`Range.getBoundingClientRect` on the exact text), then convert: `image_px = (page_css - crop_offset) * device_scale_factor`. Never eyeball from a scaled-down screenshot.
- If the interesting element sits near the crop edge, shift the image (`margin-left:-Npx`) and re-aim the zoom origin at it - verify the element is inside the view window at t=0 AND at max zoom.

### Design system implementation (compose stage)

**Start from the video's generated Style DNA, never from palette hand-picks.**
`projects/<slug>/style/tokens.css` (generated by `lib/style_engine.ensure_style`
at the proposal stage) is the ONLY source of color/typography/motif/easing:

- Copy the beat's starting point from the cloned kit:
  `projects/<slug>/src/html/_kit/<component>.html` -> `src/html/<beat>/index.html`
  (hook-card, stat-countup, bullet-reveal, compare-split, chart-bars,
  lower-third, transition - see `skills/core/style-engine.md`).
- Edit only the `<!-- CONTENT -->` slots; theme via `var(--*)` tokens only.
- Easing family + transition variant come from `style/design-system.md`
  (the video's genes) - do not swap to another video's look.
When authoring each `composition.html`:
- Inline the brand's `primary_color`, `secondary_color`, `accent_color`, and `dark_bg` from `proposal.md` → `design_system`.
- Embed the brand logo SVG (from `design_system.logo_svg_url`) as an inline `<svg>` in hook/verdict scenes.
- Apply `typography_display`/`typography_ui` via inline CSS `font-family`.
- Use GSAP easing matching `design_system.motion_style` (spring → `back.out`/`elastic.out`; linear → `power3.out`).
- Keep the same palette and easing across all 5 beats so the video feels like one brand piece.
