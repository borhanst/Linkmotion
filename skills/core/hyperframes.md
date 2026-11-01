# HyperFrames

Core skill: render plain HTML compositions to deterministic MP4 video.

## When to use

Authoring a scene as HTML rather than React. HyperFrames is the better fit when:

- The scene reuses existing web material (a captured page, a template, a design
  export) that would need rewriting as React.
- The scene is data-driven (a card filled from a JSON payload) and you want the
  authoring surface to stay boring and LLM-friendly.
- You want byte-identical output for caching, or you want the composition to
  diff cleanly in a PR.
- The scene uses GSAP, Lottie, WAAPI, or CSS animations - these drop in
  close to as-is.

Remotion stays the default for bespoke, programmatic, long-form content.

## Official skills (Layer 3)

Load these before writing scene code - they carry the correct API knowledge for
the installed version:

- `hyperframes` - router; load this first, it dispatches to the rest
- `hyperframes-html-authoring` - authoring HTML compositions

Do not write scene code from memory - the installed version may differ.

## Setup

```bash
npx hyperframes render <dir> -c composition.html -o out.mp4 -f 30 --crf 23
```

The CLI is non-interactive by default - safe to call from tools and pipelines.
No install step beyond `node` + `npm` on PATH; the CLI resolves via `npx`.

## Composition contract

A composition is one HTML document. The renderer reads it the way a browser
does, then samples it deterministically frame by frame.

- **Root**: the first element carrying both `data-width` and `data-height` is the
  composition root. Anything outside it is ignored.
- **Duration**: `data-duration` on the root (seconds). If omitted, inferred from
  the longest child track.
- **Tracks**: every direct child of the root with `data-start` or `data-duration`
  becomes a track. Tracks may overlap; layering is source order + `z-index`.
- **Media**: `<img>`, `<video>`, `<audio>` are supported as tracks.

## Determinism rules

- Pause the timeline before capturing; the renderer seeks each frame.
- No wall clocks (`Date.now()`, `setTimeout`-driven motion), no unseeded
  `Math.random()`. Use CSS `animation-delay` / `animation-duration` or the
  adapter runtime (GSAP/Lottie/WAAPI) with a paused timeline.
- Same input -> same bytes, every machine, every run.

## Frame adapters

Bring your own animation runtime: GSAP, Lottie, Web Animations, Anime.js, or a
custom frame adapter. The adapter must expose a `pause()` and a `seek(seconds)`
so the renderer can drive it deterministically.

## Project layout (per video)

All composition code lives inside the project, never globally:

```
projects/<slug>/src/hyperframes/<scene-id>/
  composition.html     # the composition
  assets/              # local images/video/audio referenced by the HTML
renders/<scene-id>.mp4
```

Refer to media with relative paths inside `assets/`. Never reference absolute
paths or URLs that won't resolve at render time.

## Component reuse

Before authoring a scene from scratch, check the project's own prior scenes
under `projects/<slug>/src/hyperframes/<scene-id>/` and their `assets/`. Clone
a fitting `composition.html` and customize only what differs
(name/title/kicker, logo/brand, data from `research.md`, palette from the style
playbook). Never silently duplicate a composition that already does the job.
Log the reuse to `projects/<slug>/engine_decisions.json`.

## Agent authoring

- Write one HTML file per scene. Keep it self-contained.
- Use `data-width`/`data-height` matching the proposal's aspect ratio
  (1920x1080 for 16:9, 1080x1920 for 9:16).
- Use `data-start`/`data-duration` on tracks for timing.
- Ground captions in the narration; sync entrance timing to spoken phrases.
- Validate before rendering: `npx hyperframes lint <dir>`.

## Docs

Check `hyperframes.video/docs` for anything not verified against the installed
version before writing scene code.