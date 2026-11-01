"""Dual-engine composition: Remotion (React) and HyperFrames (HTML)."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.base_tool import BaseTool, ToolTier, ToolRuntime, run


class HyperFrameComposeTool(BaseTool):
    """Render a HyperFrames HTML composition to MP4."""

    name = "video_compose_hyperframes"
    capability = "video_compose"
    provider = "hyperframes"
    description = "Render a HyperFrames HTML composition (plain HTML + data-* timing) to MP4 with captions, animations, and narration audio."
    tier = ToolTier.GENERATE
    runtime = ToolRuntime.LOCAL
    dependencies = ["node", "npm"]
    agent_skills = ["hyperframes", "hyperframes-html-authoring"]
    input_schema = {
        "type": "object",
        "properties": {
            "composition_html": {"type": "string", "description": "Path to the HyperFrames composition HTML file."},
            "out_mp4": {"type": "string"},
            "fps": {"type": "integer", "default": 30},
            "crf": {"type": "integer", "default": 23},
        },
        "required": ["composition_html", "out_mp4"],
    }
    output_schema = {
        "type": "object",
        "properties": {"ok": {"type": "boolean"}, "out_mp4": {"type": "string"}, "duration_sec": {"type": "number"}},
    }

    def health(self) -> dict[str, Any]:
        missing = [d for d in ["node", "npm"] if shutil.which(d) is None]
        return {"status": "available" if not missing else "unavailable", "missing_dependencies": missing}

    def render(self, composition_html: str, out_mp4: str,
               fps: int = 30, crf: int = 23) -> dict[str, Any]:
        Path(out_mp4).parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "npx", "-y", "hyperframes", "render", str(Path(composition_html).parent),
            "-c", str(Path(composition_html).name),
            "-o", out_mp4,
            "-f", str(fps),
            "--crf", str(crf),
        ]
        r = run(cmd, timeout=1800)
        if not r["ok"]:
            return {"ok": False, "out_mp4": out_mp4, "error": r["stderr"] or r["stdout"]}
        dur = self._probe_duration(out_mp4)
        return {"ok": True, "out_mp4": out_mp4, "duration_sec": dur}

    def _probe_duration(self, mp4: str) -> float:
        r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "json", mp4], timeout=60)
        if not r["ok"]:
            return 0.0
        try:
            return float(json.loads(r["stdout"]).get("format", {}).get("duration", 0.0))
        except Exception:
            return 0.0

    def execute(self, composition_html: str, out_mp4: str,
                fps: int = 30, crf: int = 23) -> dict[str, Any]:
        return self.render(composition_html, out_mp4, fps, crf)


def _main() -> None:  # pragma: no cover
    print(json.dumps(HyperFrameComposeTool().health(), indent=2))


if __name__ == "__main__":  # pragma: no cover
    _main()