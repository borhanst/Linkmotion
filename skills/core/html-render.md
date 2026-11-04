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

## Scene debugging - run `tools/scene_doctor.py` BEFORE rendering

Every failure below has cost a user-visible defect and a re-render round.
`python -m tools.scene_doctor projects/<slug>/src/html/` checks all of them
statically (exit 1 on FAIL). Fix FAILs; investigate WARNs.

| Symptom in the render | Root cause | Rule |
|---|---|---|
| White background, fallback fonts, accents invisible | Stylesheet path depth wrong - beats live at `src/html/<beat>/`, so project files are **3** levels up (`../../../style/tokens.css`). The `../../` form resolves to `src/style/` (404) and `var(--*)` all resolve to nothing | Link depth: `src/html/<beat>/` → `../../../`; `src/html/_kit/` → `../../../` |
| Empty holes where captures should be | Same path bug on `<img src>`; remote images also risk nondeterminism | All assets local; `scene_doctor` FAILs on missing, WARNs on remote |
| Title/cards pushed off-canvas or clipped at the right edge | No `box-sizing: border-box` - padding adds to `width:100%` (`.stage` becomes e.g. 1260px on a 1080 canvas) | First line of every scene `<style>`: `* { margin:0; padding:0; box-sizing:border-box; }` |
| An element never appears (no error, just missing) | Element pre-hidden with CSS `opacity:0` but revealed via `.from({opacity:0})` - that animates **0 → current(0)** | Pre-hidden elements must be revealed with `.to({opacity:1})` (a bare `.from({y:26})` may accompany it). `scene_doctor` FAILs on this combo |
| Caption chunks appear at different heights (a "paragraph") | `.cap-chunk` is `display:inline-block`, so chunks flow and wrap | `lib/captions.py` anchors them (`position:absolute; left:50%; bottom:0; transform:translateX(-50%)`). If a beat overrides caption CSS, the override must live in `<head>` BEFORE the caption script - GSAP parses the computed transform when `gsap.set` first touches the chunk; an override parsed later gets dropped |
| Stat count-up shows the wrong number (e.g. 90.0K instead of 90.4K) | `roundProps` rounds the tweened object to integers | Format inside `onUpdate` (`v.toFixed(1) + "K"`); never `roundProps` a value that needs decimals |
| Overlay boxes/highlights drift off the words they mark | Overlay positioned in view coords while the image zooms independently, or coords eyeballed from a scaled screenshot | Put overlays INSIDE the transformed wrapper (they inherit the motion), and measure targets from the live DOM (`Range.getBoundingClientRect`), converting by the crop offset and device scale |
| GSAP timeline not found by frames mode | Animations in CSS keyframes or Anime.js only | Time-critical motion in GSAP top-level calls; CSS only for static styling |

## Verify the render - extract and LOOK at frames

`render ok` only means frames were written. Before presenting any beat or the
concat, pull frames at key moments (each highlight, each reveal, start/middle/
end) and actually view them:

```bash
ffmpeg -y -i renders/beat-2.mp4 -ss 1.4 -vframes 1 /tmp/opencode/check-b2.png
```

Checklist per frame: theme applied (dark bg, brand fonts), all images visible,
overlays on their targets, captions centered on one line, nothing overlapping,
safe zones respected. Cheap, and it catches what "ok: true" hides.
