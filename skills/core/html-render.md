# HTML Render (Playwright)

Core skill: render a self-contained HTML page (animated with GSAP/Anime.js or any
web animation) to a deterministic-ish MP4 by recording the browser viewport with
Playwright, then encoding with FFmpeg.

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
```

## Concat scenes

```python
t.concat(["renders/a.mp4", "renders/b.mp4"], "out/<slug>.mp4")
```

## Authoring rules

- Self-contained HTML; load GSAP/Anime.js from CDN or vendor.
- Animations must complete within `duration_sec` (recording is real-time).
- Use 1920x1080 or 1080x1920 to match proposal aspect ratio.
