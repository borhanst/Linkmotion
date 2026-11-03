"""HTML render tool - record animated HTML (GSAP/Anime.js) pages to MP4 via Playwright."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from tools.base_tool import BaseTool, ToolTier, ToolRuntime, run


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
               crf: int = 23) -> dict[str, Any]:
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
        return {"ok": True, "out_mp4": str(out_path), "duration_sec": dur}

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
                crf: int = 23) -> dict[str, Any]:
        return self.render(html_path, out_mp4, duration_sec, fps, viewport, crf)


def _main() -> None:  # pragma: no cover
    print(json.dumps(HtmlRenderTool().health(), indent=2))


if __name__ == "__main__":  # pragma: no cover
    _main()
