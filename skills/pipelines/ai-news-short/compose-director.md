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
2. Mux with edge-tts audio: `ffmpeg -y -i renders/beat-N.mp4 -i audio/beat-N.mp3 -c:v copy -c:a aac -shortest renders/beat-N-av.mp4`
3. Concatenate all `beat-N-av.mp4` into `out/<slug>.mp4` with ffmpeg concat (`-c copy`).
4. Verify final duration with ffprobe (must be inside 45-75s).

### Review after compose
Run `python -m lib.reviewer <slug> compose projects/<slug>/render_report.json` and confirm output exists, duration inside window, and engine decisions logged.

### Design system implementation (compose stage)
When authoring each `composition.html`:
- Inline the brand's `primary_color`, `secondary_color`, `accent_color`, and `dark_bg` from `proposal.md` → `design_system`.
- Embed the brand logo SVG (from `design_system.logo_svg_url`) as an inline `<svg>` in hook/verdict scenes.
- Apply `typography_display`/`typography_ui` via inline CSS `font-family`.
- Use GSAP easing matching `design_system.motion_style` (spring → `back.out`/`elastic.out`; linear → `power3.out`).
- Keep the same palette and easing across all 5 beats so the video feels like one brand piece.
