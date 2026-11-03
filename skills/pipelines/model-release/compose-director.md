# Compose Director - Model Release

Assemble beats into a composition and render the final MP4.

## Load the official skills first

Before authoring any beat, load the engine's official skill so the coding agent
has the correct API knowledge (import paths, code patterns, constraints,
parameters). These are Layer 3 skills installed in the user's environment:

- Remotion: `remotion-best-practices` (router) + `remotion-create`, `remotion-markup`,
  `remotion-render`, `remotion-captions`, `remotion-multimedia`,
  `remotion-interactivity`, `remotion-studio`
- HyperFrames: `hyperframes` (router) + `hyperframes-html-authoring`

Load them via the skill tool before writing beat code. Do not guess from memory -
the installed version may differ from what you know.

## Component reuse (check before authoring)

Before writing a beat from scratch, check whether an existing component already
fits and only needs customizing:

1. **Scan the project's own components.** For Remotion look under
   `projects/<slug>/src/remotion/<beat-id>/components/` and any shared
   `components/` the video reuses. For HyperFrames look under
   `projects/<slug>/src/hyperframes/<beat-id>/assets/` and prior beats'
   `composition.html`.
2. **Match by purpose.** A card with the same structure (hook / announcement /
   benchmarks / pricing / verdict), a benchmarks table, a pricing row, a model
   identifier card - reuse it.
3. **Customize, don't duplicate.** If a component fits, clone it and change only
   what differs:
   - **Name / title / kicker** - from the storyboard.
   - **Logo / brand** - from the research brief (lab name, model string).
   - **Data** - from `research.md` data points (numbers, dates, prices, benchmarks).
   - **Palette** - from the style playbook.
   Never silently duplicate a component that already does the job.
4. **Log the reuse.** Append to `projects/<slug>/engine_decisions.json`:
   `{"beat_id": "...", "reused_from": "<path>", "customized": ["title", "data"]}`.
5. **If nothing fits**, author a new component and record it as new.

## Dual-engine composition

Each beat is authored and rendered independently under
`projects/<slug>/src/<engine>/<beat-id>/`, then concatenated into the final
MP4. The LLM picks the engine per beat:

| Engine | Authoring | When to use |
|---|---|---|
| `remotion` | React component (`index.tsx`) | Bespoke programmatic UI, charts, motion graphics |
| `hyperframes` | Plain HTML (`composition.html`) | Existing web material, templates, data-driven cards, GSAP/Lottie |

Default: **Remotion**. Switch to **HyperFrames** for a beat that is better
expressed as HTML/CSS (a captured benchmarks/pricing page, a template card).

Decision framework: `lib/engine_selector.py`. Heuristic fallback:
`web`/`media`/`social` beats -> HyperFrames, everything else -> Remotion.
Always set an explicit `engine` field on the beat so the choice is auditable;
log all decisions to `projects/<slug>/engine_decisions.json`.

## Input

`projects/<slug>/storyboard.json`, `projects/<slug>/assets/manifest.json`

## Tools

Required: `video_compose` (Remotion) and/or `video_compose_hyperframes` (HyperFrames).
Query `python -m ai_news_agent preflight` to see which are available.

## Process

1. **Decide the engine per beat** and write `projects/<slug>/engine_decisions.json`.
2. **Author the beat** under `projects/<slug>/src/<engine>/<beat-id>/`:
   - Remotion: `index.tsx` + shared components under `components/`.
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
5. **Preview each beat before the next.**

## Motion system

Follow `remotion-youtube-video` skill: determinism contract, animation picker,
visual picker, transition picker, banned list. 16:9 by default (1920x1080);
9:16 (1080x1920) for a Shorts variant.

## Build ONE beat at a time

Preview each beat before the next.

## Output: `projects/<slug>/render_report.json`

```json
{"slug": "...", "out_mp4": "out/<slug>.mp4", "duration_sec": 88.4,
 "fps": 30, "composition_id": "<slug>-full", "ok": true}
```

## Success criteria

- Output exists and plays.
- ffprobe duration inside 60-120s.
- Captions word-synced.
- Aspect ratio matches the proposal.

## HTML renderer (default)

Default engine is now plain HTML + GSAP/Anime.js recorded via Playwright (`tools/html_render.py`). See `skills/core/html-render.md`. Lower thirds: `components/html/lower-third.html`. Page transitions: `components/html/page-transition.html`.
