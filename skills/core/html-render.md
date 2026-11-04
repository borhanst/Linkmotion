# HTML Render (Playwright)

Core skill: render a self-contained HTML page (animated with GSAP/Anime.js or any
web animation) to MP4 via Playwright + FFmpeg.

There are two render paths:

- **frames (default, deterministic)** — the page's GSAP tweens/timelines are
  captured into a single paused master timeline, which is seeked to exact
  frame times `t = i / fps` while Playwright screenshots each frame. Every
  run is byte-identical; no dropped or duplicated frames, no motion blur from
  real-time variance.
- **record (fallback, real-time)** — the legacy screen-recording path, used
  automatically when a page has no drivable GSAP timeline (Anime.js, CSS-only
  or plain pages).

## When to use

- Scene is authored as HTML + GSAP/Anime.js/CSS animations.
- Need screen-record style walkthrough of a real or mocked page.
- Lower thirds, page transitions, B-roll overlays.

## Usage

```python
from tools.html_render import HtmlRenderTool
t = HtmlRenderTool()
t.render("projects/<slug>/src/html/<scene>/index.html", "projects/<slug>/renders/<scene>.mp4",
         duration_sec=6.0, fps=30, viewport=[1920, 1080])
# mode="auto" (default) uses frames rendering, falls back to record.
# mode="frames" errors instead of silently falling back.
# mode="record" forces the legacy path.
```

## Determinism rules (frames mode)

- Captions and effects injected by `lib/captions.burn` are top-level `gsap.to`
  calls, so they are captured and driven like any other page tween - captions
  land on the exact word (see `lib/captions.py`).
- Any top-level `gsap.to/from/fromTo/set/timeline(...)` in the page is
  captured automatically; its internal `delay` keeps its visual schedule.
- Pages must load GSAP from a CDN (or vendor) and create their animation from
  a synchronous `<script>`; the tool injects a capture shim before page code.
- Screenshots happen after `document.fonts.ready` + `networkidle`, so font
  loading and CDN fetches cannot shift pixels between runs.
- Pure CSS keyframe animations are NOT derived from the GSAP clock and are
  not frame-locked - keep time-critical animation in GSAP.

## Concat scenes

```python
t.concat(["renders/a.mp4", "renders/b.mp4"], "out/<slug>.mp4")
```

## Authoring rules

- Self-contained HTML; load GSAP/Anime.js from CDN or vendor.
- Animations must complete within `duration_sec`.
- Use 1920x1080 or 1080x1920 to match proposal aspect ratio.
