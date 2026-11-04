# Compose Director - AI News Long

Assemble 12-20 scenes into a composition and render.

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
2. **Match by purpose.** A card with the same structure (hook / stat / verdict /
   subscribe-ask), a web walkthrough, a media frame, a social feed, an
   engagement overlay - reuse it.
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

Each scene is authored and rendered independently under
`projects/<slug>/src/<engine>/<scene-id>/`, then concatenated into the final
MP4. The LLM picks the engine per scene:

| Engine | Authoring | When to use |
|---|---|---|
| `remotion` | React component (`index.tsx`) | Bespoke programmatic UI, charts, long-form, motion graphics |
| `hyperframes` | Plain HTML (`composition.html`) | Existing web material, templates, data-driven cards, GSAP/Lottie |

Default: **Remotion**. Switch to **HyperFrames** for a scene that is better
expressed as HTML/CSS (a captured page, a template card, an existing animation).

Decision framework: `lib/engine_selector.py`. Heuristic fallback:
`web`/`media`/`social` scenes -> HyperFrames, everything else -> Remotion.
Always set an explicit `engine` field on the scene so the choice is auditable;
log all decisions to `projects/<slug>/engine_decisions.json`.

## Input

`projects/<slug>/storyboard.json`, `projects/<slug>/assets/manifest.json`

## Tools

Required: `video_compose` (Remotion) and/or `video_compose_hyperframes` (HyperFrames).
Query `python -m ai_news_agent preflight` to see which are available.

## Process

1. **Decide the engine per scene** and write `projects/<slug>/engine_decisions.json`.
2. **Author the scene** under `projects/<slug>/src/<engine>/<scene-id>/`:
   - Remotion: `index.tsx` + shared components under `components/`.
   - HyperFrames: `composition.html` + local media under `assets/`.
3. **Render the scene** to `projects/<slug>/renders/<scene-id>.mp4`:
   ```bash
   python -c "from lib.engine_selector import render_scene; print(render_scene(scene, '<slug>'))"
   ```
   or directly:
   ```bash
   npx remotion render src/<slug>/src/remotion/<scene>/index.tsx <slug>-<scene> renders/<scene>.mp4 --fps 30 --crf 23
   npx hyperframes render src/<slug>/src/hyperframes/<scene> -c composition.html -o renders/<scene>.mp4 -f 30 --crf 23
   ```
4. **Register the composition** in `src/videos/<slug>/index.tsx` with `<Series>`
   (or offset `<Sequence>`s) applying the picked transitions between scenes.
5. **Add the one import + one call** in `src/Root.tsx`.
6. **Concatenate** the per-scene MP4s into `out/<slug>.mp4` with FFmpeg.
7. **Render**:
   ```bash
   npx remotion render src/Root.tsx <slug>-full out/<slug>.mp4 --fps 30 --crf 23
   ```

## Build ONE scene at a time

Preview each scene before the next. Sanity-check total duration against the
7-8 minute minimum - if short, revisit the script, don't pad scenes.

## Output: `projects/<slug>/render_report.json`

```json
{"slug": "...", "out_mp4": "out/<slug>.mp4", "duration_sec": 545.2,
 "fps": 30, "composition_id": "<slug>-full", "ok": true}
```

## Success criteria

- Output exists and plays.
- ffprobe duration >= 480s.
- Captions: OFF by default for long-form. Only if the user explicitly asked for
  captions, burn them - and they must be word-synced.
- 16:9 framing, chapter transitions per motion system.

## HTML renderer (default)

Default engine is now plain HTML + GSAP/Anime.js rendered via Playwright (`tools/html_render.py`). See `skills/core/html-render.md`. Lower thirds: `components/html/lower-third.html`. Page transitions: `components/html/page-transition.html`.

Render `mode="auto"` (default) uses **frame-stepped deterministic rendering**: the page's GSAP timeline is seeked to exact frame times and screenshotted per frame, so output is frame-accurate and reproducible. Captions: **do not burn captions by default for long-form**. Only burn word-timed 1-2-word chunks with `lib/captions.py` when the user explicitly asked for captions. Optional beat-boundary SFX: `tools/sfx.py` (synth + mix under narration).
