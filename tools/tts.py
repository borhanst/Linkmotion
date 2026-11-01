"""edge-tts narration tool - male voice, per-beat audio + word timestamps.

Wraps the user's existing edge-tts workflow. Per-beat audio files make it
possible to resync/regenerate a single beat later without re-cutting the
whole video.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.base_tool import BaseTool, ToolTier, ToolRuntime, run


@dataclass
class TTSResult:
    ok: bool
    mp3: str = ""
    srt: str = ""
    duration_sec: float = 0.0
    words: list[dict[str, Any]] = field(default_factory=list)
    voice: str = ""
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok, "mp3": self.mp3, "srt": self.srt,
            "duration_sec": self.duration_sec, "words": self.words,
            "voice": self.voice, "error": self.error,
        }


class TTSTool(BaseTool):
    """edge-tts narration with word-level timestamps."""

    name = "tts"
    capability = "tts"
    provider = "edge"
    description = "Generate male-voice narration per beat with edge-tts, including word-level timestamps for caption sync."
    tier = ToolTier.VOICE
    runtime = ToolRuntime.LOCAL
    dependencies = ["edge-tts", "ffprobe"]
    agent_skills = ["remotion-video-common"]
    input_schema = {
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "out_mp3": {"type": "string"},
            "voice": {"type": "string", "default": "en-US-GuyNeural"},
            "rate": {"type": "string", "default": "+0%"},
        },
        "required": ["text", "out_mp3"],
    }
    output_schema = {
        "type": "object",
        "properties": {"ok": {"type": "boolean"}, "duration_sec": {"type": "number"}, "words": {"type": "array"}},
    }

    def health(self) -> dict[str, Any]:
        missing = [d for d in ["ffprobe"] if shutil.which(d) is None]
        try:
            import edge_tts  # noqa: F401
        except ImportError:
            missing.append("edge-tts")
        return {"status": "available" if not missing else "unavailable", "missing_dependencies": missing}

    def synthesize(self, text: str, out_mp3: str, voice: str = "en-US-GuyNeural",
                   rate: str = "+0%") -> TTSResult:
        out_srt = str(Path(out_mp3).with_suffix(".srt"))
        Path(out_mp3).parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "edge-tts", "--voice", voice, "--rate", rate,
            "--text", text, "--write-media", out_mp3, "--write-subtitles", out_srt,
        ]
        r = run(cmd, timeout=300)
        if not r["ok"]:
            return TTSResult(ok=False, error=r["stderr"] or r["stdout"], voice=voice)

        dur = self._probe_duration(out_mp3)
        words = self._parse_srt(out_srt)
        return TTSResult(ok=True, mp3=out_mp3, srt=out_srt, duration_sec=dur,
                         words=words, voice=voice)

    def _probe_duration(self, mp3: str) -> float:
        r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "json", mp3], timeout=60)
        if not r["ok"]:
            return 0.0
        try:
            return float(json.loads(r["stdout"]).get("format", {}).get("duration", 0.0))
        except Exception:
            return 0.0

    def _parse_srt(self, srt_path: str) -> list[dict[str, Any]]:
        """Parse an SRT into word-level entries (best-effort)."""
        p = Path(srt_path)
        if not p.is_file():
            return []
        words: list[dict[str, Any]] = []
        try:
            content = p.read_text(encoding="utf-8").strip()
        except Exception:
            return words
        blocks = re_split_blocks(content)
        for b in blocks:
            lines = b.splitlines()
            if len(lines) < 2:
                continue
            # line 1: index, line 2: timing, rest: text
            timing = lines[1]
            text = " ".join(lines[2:]).strip()
            start, end = _parse_srt_time_pair(timing)
            for w in text.split():
                words.append({"word": w, "start": start, "end": end})
        return words

    def execute(self, text: str, out_mp3: str, voice: str = "en-US-GuyNeural",
                rate: str = "+0%") -> dict[str, Any]:
        return self.synthesize(text, out_mp3, voice, rate).to_dict()


def re_split_blocks(content: str) -> list[str]:
    out: list[str] = []
    cur: list[str] = []
    for line in content.splitlines():
        if line.strip() == "":
            if cur:
                out.append("\n".join(cur))
                cur = []
        else:
            cur.append(line)
    if cur:
        out.append("\n".join(cur))
    return out


def _parse_srt_time_pair(timing: str) -> tuple[float, float]:
    """'00:00:01,200 --> 00:00:03,400' -> (1.2, 3.4)"""
    import re
    m = re.search(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", timing)
    if not m:
        return 0.0, 0.0
    h1, m1, s1, ms1, h2, m2, s2, ms2 = (int(x) for x in m.groups())
    return (h1 * 3600 + m1 * 60 + s1 + ms1 / 1000.0,
            h2 * 3600 + m2 * 60 + s2 + ms2 / 1000.0)


def _main() -> None:  # pragma: no cover
    import sys
    text = " ".join(sys.argv[1:]) or "Hello from AI News Agent."
    print(json.dumps(TTSTool().synthesize(text, "/tmp/kilo/test.mp3").to_dict(), indent=2))


if __name__ == "__main__":  # pragma: no cover
    _main()