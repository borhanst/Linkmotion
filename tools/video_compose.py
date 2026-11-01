"""Remotion video composition tool.

Wraps the user's existing Remotion repo. Renders a per-video composition to
MP4 with captions, animations, and audio. Reuses the repo's motion system.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from tools.base_tool import BaseTool, ToolTier, ToolRuntime, run


class VideoComposeTool(BaseTool):
    """Render a Remotion composition to MP4."""

    name = "video_compose"
    capability = "video_compose"
    provider = "remotion"
    description = "Render a Remotion composition (React scene components) to MP4 with captions, animations, and narration audio."
    tier = ToolTier.GENERATE
    runtime = ToolRuntime.LOCAL
    dependencies = ["remotion", "node", "npm"]
    agent_skills = ["remotion-video-common", "remotion-youtube-video", "remotion-youtube-shorts"]
    input_schema = {
        "type": "object",
        "properties": {
            "root_tsx": {"type": "string", "description": "Path to the Remotion root entry (e.g. src/Root.tsx)."},
            "composition_id": {"type": "string"},
            "out_mp4": {"type": "string"},
            "fps": {"type": "integer", "default": 30},
            "crf": {"type": "integer", "default": 23},
        },
        "required": ["root_tsx", "composition_id", "out_mp4"],
    }
    output_schema = {
        "type": "object",
        "properties": {"ok": {"type": "boolean"}, "out_mp4": {"type": "string"}, "duration_sec": {"type": "number"}},
    }

    def health(self) -> dict[str, Any]:
        # Remotion is invoked via `npx remotion` at render time, so we only
        # require node + npm on PATH (the Remotion repo is wired separately).
        missing = [d for d in ["node", "npm"] if shutil.which(d) is None]
        return {"status": "available" if not missing else "unavailable", "missing_dependencies": missing}

    def render(self, root_tsx: str, composition_id: str, out_mp4: str,
               fps: int = 30, crf: int = 23) -> dict[str, Any]:
        Path(out_mp4).parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "npx", "-y", "remotion", "render", root_tsx, composition_id, out_mp4,
            "--fps", str(fps), "--crf", str(crf),
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

    def execute(self, root_tsx: str, composition_id: str, out_mp4: str,
                fps: int = 30, crf: int = 23) -> dict[str, Any]:
        return self.render(root_tsx, composition_id, out_mp4, fps, crf)


def _main() -> None:  # pragma: no cover
    print(json.dumps(VideoComposeTool().health(), indent=2))


if __name__ == "__main__":  # pragma: no cover
    _main()