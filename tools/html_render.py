"""HTML render tool - render animated HTML (GSAP/Anime.js) pages to MP4 via Playwright.

Two rendering paths:

- ``frames`` (default): frame-stepped, deterministic rendering. A captured
  master GSAP timeline is paused and seeked to exact frame times while
  Playwright screenshots each frame, which is then encoded with FFmpeg.
  Output is buttery and frame-accurate - no dropped/extra frames regardless
  of machine load.
- ``record`` (fallback): the legacy real-time screen recording path, used when
  the page has no drivable GSAP timeline (e.g. Anime.js or CSS-only pages).
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from tools.base_tool import BaseTool, ToolTier, ToolRuntime, run

# Injected before any page script runs. When the page loads gsap (UMD builds
# assign to window.gsap), we intercept the assignment and wrap the top-level
# creation methods (to/from/fromTo/set/timeline) so every top-level tween and
# timeline is captured into a single *paused* master timeline we can step.
#
# Wrapping is deferred to a microtask because UMD builds assign an empty
# exports object first and populate it afterwards (the setter runs before
# `gsap.to` exists yet). Microtasks run before the next classic <script>, so
# author code created *later in the page* is always captured.
#
# Adding each top-level object at position 0 of the master preserves its own
# internal `delay`, so the visual schedule matches real-time playback.
_CAPTURE_JS = r"""
(() => {
  const MASTER = '__gsmaster';
  const STATE = '__gscapture';
  const capture = (g) => {
    if (window[STATE]) return;
    window[STATE] = true;
    const master = g.timeline({ paused: true });
    window[MASTER] = master;
    const wrap = (fn) => function (...args) {
      const o = fn.apply(this, args);
      if (o && typeof o.totalDuration === 'function') {
        try { master.add(o, 0); } catch (e) { /* non-addable object */ }
      }
      return o;
    };
    for (const k of ['to', 'from', 'fromTo', 'set']) {
      if (typeof g[k] === 'function') g[k] = wrap(g[k]);
    }
    if (typeof g.timeline === 'function') g.timeline = wrap(g.timeline);
  };
  let gsapVal;
  Object.defineProperty(window, 'gsap', {
    configurable: true,
    get() { return gsapVal; },
    set(v) {
      gsapVal = v;
      if (v) Promise.resolve().then(() => { try { capture(v); } catch (e) { /* no-op */ } });
    },
  });
})();
"""

# Runs after load. Returns true when a drivable master timeline exists.
_SETUP_JS = r"""
() => {
  const m = window.__gsmaster;
  if (!m || typeof m.totalDuration !== 'function') return false;
  try { gsap.ticker.lagSmoothing(0); } catch (e) { /* older builds */ }
  try { m.seek(0, false); } catch (e) { return false; }
  return true;
}
"""

# Seek the master timeline to an absolute time (pause -> seek keeps renders
# deterministic because the playhead only moves when we move it).
_SEEK_JS = r"""
(t) => {
  const m = window.__gsmaster;
  if (!m) return false;
  try { m.pause(0); m.seek(t, false); } catch (e) { return false; }
  return true;
}
"""


class HtmlRenderTool(BaseTool):
    """Render a self-contained HTML composition to MP4 by recording the browser."""

    name = "html_render"
    capability = "video_compose"
    provider = "playwright-html"
    description = (
        "Render an HTML page animated with GSAP/Anime.js (or any web animation) to MP4 "
        "by recording the browser viewport with Playwright, then encoding with FFmpeg."
    )
    tier = ToolTier.GENERATE
    runtime = ToolRuntime.LOCAL
    dependencies = ["playwright", "ffmpeg"]
    agent_skills = ["web-explainer-video", "web-explainer-video-animation"]
    input_schema = {
        "type": "object",
        "properties": {
            "html_path": {"type": "string", "description": "Path to the HTML composition file."},
            "out_mp4": {"type": "string"},
            "duration_sec": {"type": "number", "default": 6.0},
            "fps": {"type": "integer", "default": 30},
            "viewport": {"type": "array", "items": {"type": "integer"}, "default": [1920, 1080]},
            "crf": {"type": "integer", "default": 23},
            "mode": {
                "type": "string", "enum": ["auto", "frames", "record"], "default": "auto",
                "description": (
                    "frames = deterministic frame-stepped GSAP seek + screenshots; "
                    "record = real-time screen recording; auto = frames, then record."
                ),
            },
        },
        "required": ["html_path", "out_mp4"],
    }
    output_schema = {
        "type": "object",
        "properties": {"ok": {"type": "boolean"}, "out_mp4": {"type": "string"}, "duration_sec": {"type": "number"}},
    }

    def health(self) -> dict[str, Any]:
        missing: list[str] = []
        try:
            import playwright  # noqa: F401
        except ImportError:
            missing.append("playwright-python")
        if shutil.which("ffmpeg") is None:
            missing.append("ffmpeg")
        return {"status": "available" if not missing else "unavailable", "missing_dependencies": missing}

    def render(self, html_path: str, out_mp4: str, duration_sec: float = 6.0,
               fps: int = 30, viewport: list[int] | None = None,
               crf: int = 23, mode: str = "auto") -> dict[str, Any]:
        """Render an HTML composition to MP4.

        mode="auto": frame-stepped GSAP rendering first; falls back to real-time
        recording when the page has no captured GSAP master timeline.
        """
        if mode not in ("auto", "frames", "record"):
            return {"ok": False, "out_mp4": out_mp4, "error": f"unknown mode: {mode}"}
        if mode == "record":
            return self._render_record(html_path, out_mp4, duration_sec, fps, viewport, crf)

        result = self.render_frames(html_path, out_mp4, duration_sec, fps, viewport, crf)
        if result["ok"] or mode == "frames":
            return result
        return self._render_record(html_path, out_mp4, duration_sec, fps, viewport, crf)

    def render_frames(self, html_path: str, out_mp4: str, duration_sec: float = 6.0,
                      fps: int = 30, viewport: list[int] | None = None,
                      crf: int = 23) -> dict[str, Any]:
        """Deterministic frame-stepped render.

        Drives the page's captured GSAP master timeline to exact frame times
        (t = i / fps) and screenshots each frame, so the output MP4 contains
        exactly round(duration_sec * fps) frames, every run identical.
        """
        viewport = viewport or [1920, 1080]
        html_file = Path(html_path).resolve()
        if not html_file.is_file():
            return {"ok": False, "out_mp4": out_mp4, "error": f"html not found: {html_file}"}

        try:
            from playwright.sync_api import sync_playwright  # type: ignore
        except ImportError as e:
            return {"ok": False, "out_mp4": out_mp4, "error": f"playwright unavailable: {e}"}

        out_path = Path(out_mp4)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        frames_dir = out_path.parent / "_frames"
        if frames_dir.exists():
            shutil.rmtree(frames_dir, ignore_errors=True)
        frames_dir.mkdir(parents=True, exist_ok=True)

        total_frames = max(1, round(duration_sec * fps))
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                context = browser.new_context(
                    viewport={"width": viewport[0], "height": viewport[1]},
                    device_scale_factor=1,
                )
                context.add_init_script(_CAPTURE_JS)
                page = context.new_page()
                page.goto(html_file.as_uri(), wait_until="networkidle", timeout=60000)
                # Fonts and the captured timeline must be ready before frame 0,
                # otherwise identical runs could rasterize different pixels.
                page.evaluate("document.fonts.ready.then(() => true)")
                if not page.evaluate(_SETUP_JS):
                    browser.close()
                    return {"ok": False, "out_mp4": out_mp4,
                            "error": "no drivable GSAP master timeline found (page may use Anime.js/CSS only)"}

                # Warm-up frame: first screenshot may allocate buffers / settle
                # first-paint state; discard it so frame 0 is clean.
                page.evaluate(_SEEK_JS, 0)
                page.screenshot(type="png")

                for i in range(total_frames):
                    t = i / float(fps)
                    if not page.evaluate(_SEEK_JS, t):
                        browser.close()
                        return {"ok": False, "out_mp4": out_mp4, "error": f"GSAP seek failed at t={t}"}
                    page.screenshot(path=str(frames_dir / f"f{i:05d}.png"), type="png")
                browser.close()
        except Exception as e:
            return {"ok": False, "out_mp4": out_mp4, "error": f"frame render failed: {e}"}

        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps), "-start_number", "0",
            "-i", str(frames_dir / "f%05d.png"),
            "-frames:v", str(total_frames),
            "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(out_path),
        ]
        r = run(cmd, timeout=1800)
        shutil.rmtree(frames_dir, ignore_errors=True)
        if not r["ok"]:
            return {"ok": False, "out_mp4": out_mp4, "error": r["stderr"] or r["stdout"]}

        dur = self._probe_duration(str(out_path))
        return {"ok": True, "out_mp4": str(out_path), "duration_sec": dur,
                "mode": "frames", "frames": total_frames, "fps": fps}

    def _render_record(self, html_path: str, out_mp4: str, duration_sec: float = 6.0,
                       fps: int = 30, viewport: list[int] | None = None,
                       crf: int = 23) -> dict[str, Any]:
        """Legacy real-time screen-recording render (fallback path)."""
        viewport = viewport or [1920, 1080]
        html_file = Path(html_path).resolve()
        if not html_file.is_file():
            return {"ok": False, "out_mp4": out_mp4, "error": f"html not found: {html_file}"}

        out_path = Path(out_mp4)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        record_dir = out_path.parent / "_record"
        record_dir.mkdir(parents=True, exist_ok=True)

        try:
            from playwright.sync_api import sync_playwright  # type: ignore
        except ImportError as e:
            return {"ok": False, "out_mp4": out_mp4, "error": f"playwright unavailable: {e}"}

        webm_path = None
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                context = browser.new_context(
                    viewport={"width": viewport[0], "height": viewport[1]},
                    record_video_dir=str(record_dir),
                    record_video_size={"width": viewport[0], "height": viewport[1]},
                )
                page = context.new_page()
                page.goto(html_file.as_uri(), wait_until="load", timeout=60000)
                page.wait_for_timeout(int((duration_sec + 0.5) * 1000))
                page.close()
                context.close()
                browser.close()

            webms = sorted(record_dir.glob("*.webm"), key=lambda f: f.stat().st_mtime, reverse=True)
            if not webms:
                return {"ok": False, "out_mp4": out_mp4, "error": "no webm produced by playwright"}
            webm_path = webms[0]
        except Exception as e:
            return {"ok": False, "out_mp4": out_mp4, "error": f"recording failed: {e}"}

        cmd = [
            "ffmpeg", "-y", "-i", str(webm_path),
            "-r", str(fps),
            "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(out_path),
        ]
        r = run(cmd, timeout=1800)
        try:
            if webm_path and Path(webm_path).exists():
                Path(webm_path).unlink()
        except Exception:
            pass

        if not r["ok"]:
            return {"ok": False, "out_mp4": out_mp4, "error": r["stderr"] or r["stdout"]}

        dur = self._probe_duration(str(out_path))
        return {"ok": True, "out_mp4": str(out_path), "duration_sec": dur,
                "mode": "record", "fps": fps}

    def concat(self, scene_mp4s: list[str], out_mp4: str) -> dict[str, Any]:
        """Concatenate scene MP4s into one final video."""
        out_path = Path(out_mp4)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        list_file = out_path.parent / "_concat.txt"
        lines = [f"file '{Path(p).resolve()}'" for p in scene_mp4s]
        list_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(list_file),
            "-c", "copy",
            str(out_path),
        ]
        r = run(cmd, timeout=1800)
        try:
            list_file.unlink(missing_ok=True)
        except Exception:
            pass
        if not r["ok"]:
            return {"ok": False, "out_mp4": out_mp4, "error": r["stderr"] or r["stdout"]}
        dur = self._probe_duration(str(out_path))
        return {"ok": True, "out_mp4": str(out_path), "duration_sec": dur}

    def _probe_duration(self, mp4: str) -> float:
        r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "json", mp4], timeout=60)
        if not r["ok"]:
            return 0.0
        try:
            return float(json.loads(r["stdout"]).get("format", {}).get("duration", 0.0))
        except Exception:
            return 0.0

    def execute(self, html_path: str, out_mp4: str, duration_sec: float = 6.0,
                fps: int = 30, viewport: list[int] | None = None,
                crf: int = 23, mode: str = "auto") -> dict[str, Any]:
        return self.render(html_path, out_mp4, duration_sec, fps, viewport, crf, mode)


def _main() -> None:  # pragma: no cover
    print(json.dumps(HtmlRenderTool().health(), indent=2))


if __name__ == "__main__":  # pragma: no cover
    _main()
