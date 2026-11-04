"""SFX tool - beat-boundary sound effects, synthesized or CC0 assets, mixed under narration.

Keeps the audio pipeline fully local and deterministic:

- ``synth`` renders classic transition sounds (whoosh, pop, tick, sweep) with
  FFmpeg lavfi generators - no network, reproducible bytes.
- ``mix`` places SFX events at fixed offsets under a narration track with
  ``adelay`` + ``amix`` (normalize=0, duration=first), so narration timing is
  never shifted.

CC0 assets from a CDN (e.g. freesound/kenney packs) can be dropped into
``assets/sfx/`` and referenced by path in ``events`` instead of synthesized.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from tools.base_tool import BaseTool, ToolTier, ToolRuntime, run

# Synthesized effects via ffmpeg lavfi. Each is a short, dry one-shot.
SYNTHS: dict[str, list[str]] = {
    # Airy filtered-noise swell with fast attack/decay.
    "whoosh": [
        "-f", "lavfi", "-i",
        "anoisesrc=color=pink:d={dur}:a=0.8:r=44100,"
        "highpass=f=250,lowpass=f=3800,"
        "afade=t=in:d={fdur},afade=t=out:st={out_st}:d={odur}",
    ],
    # Classic UI 'pop': decaying sine blip.
    "pop": [
        "-f", "lavfi", "-i",
        "aevalsrc='sin(2*PI*740*t)*exp(-18*t)':s=44100:d={dur}",
        "-f", "lavfi", "-i",
        "aevalsrc='sin(2*PI*440*t)*exp(-14*t)*0.4':s=44100:d={dur}",
    ],
    # Short UI tick for word/beat boundaries.
    "tick": [
        "-f", "lavfi", "-i",
        "aevalsrc='(sin(2*PI*2400*t)+0.5*sin(2*PI*1200*t))*exp(-55*t)*0.5':s=44100:d={dur}",
    ],
    # Rising tone sweep for transitions into the next scene.
    "sweep": [
        "-f", "lavfi", "-i",
        "aevalsrc='0.45*sin(2*PI*(180+700*t)*t)':s=44100:d={dur},"
        "afade=t=in:d={fdur},afade=t=out:st={out_st}:d={odur}",
    ],
}

DURATIONS: dict[str, float] = {"whoosh": 0.6, "pop": 0.25, "tick": 0.1, "sweep": 0.5}


class SfxTool(BaseTool):
    """Synthesize and mix beat-boundary SFX locally with FFmpeg."""

    name = "sfx"
    capability = "sfx"
    provider = "ffmpeg"
    description = (
        "Synthesize transition SFX (whoosh/pop/tick/sweep) or use CC0 asset files, "
        "and mix them at exact offsets under the narration track (narration timing untouched)."
    )
    tier = ToolTier.VOICE
    runtime = ToolRuntime.LOCAL
    dependencies = ["ffmpeg"]
    agent_skills = []
    input_schema = {
        "type": "object",
        "properties": {
            "op": {"type": "string", "enum": ["synth", "mix"]},
            "kind": {"type": "string", "enum": list(SYNTHS), "description": "synth kind"},
            "out_wav": {"type": "string", "description": "synth: output file"},
            "duration": {"type": "number", "description": "synth: seconds (default per kind)"},
            "narration": {"type": "string", "description": "mix: narration audio (mp3/wav)"},
            "out_mix": {"type": "string", "description": "mix: output file"},
            "events": {
                "type": "array",
                "description": 'mix: [{"path": ..., "at": seconds, "gain_db": -10}]',
                "items": {"type": "object"},
            },
        },
        "required": ["op"],
    }
    output_schema = {
        "type": "object",
        "properties": {"ok": {"type": "boolean"}, "out": {"type": "string"}
                       , "duration_sec": {"type": "number"}},
    }

    def synthesize(self, kind: str, out_wav: str, duration: float | None = None,
                   gain_db: float = -6.0) -> dict[str, Any]:
        """Render one synthesized SFX to file. Deterministic bytes for same inputs."""
        if kind not in SYNTHS:
            return {"ok": False, "out": out_wav, "error": f"unknown kind '{kind}', known: {sorted(SYNTHS)}"}
        dur = round(duration if duration and duration > 0 else DURATIONS[kind], 3)
        out_path = Path(out_wav)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # Fade windows (1/3 in, 1/3 out) for the airy kinds.
        fdur = round(min(dur / 3, 0.25), 3)
        odur = round(min(dur / 3, 0.3), 3)
        template = list(SYNTHS[kind])
        subs = {"dur": f"{dur}", "fdur": f"{fdur}", "odur": f"{odur}",
                "out_st": f"{max(0.0, dur - odur):.3f}"}
        cmd = ["ffmpeg", "-y", "-v", "error"]
        cmd += [part.format(**subs) for part in template]
        cmd += ["-filter_complex", f"amix=inputs=2:duration=longest:normalize=0,volume={gain_db}dB"
                if kind == "pop" else f"volume={gain_db}dB",
                "-ar", "44100", "-ac", "1",
                str(out_path)]
        r = run(cmd, timeout=120)
        if not r["ok"]:
            return {"ok": False, "out": str(out_path), "error": r["stderr"] or r["stdout"]}
        return {"ok": True, "out": str(out_path), "kind": kind, "duration_sec": self._probe(out_path)}

    def mix(self, narration: str, events: list[dict[str, Any]], out_mix: str) -> dict[str, Any]:
        """Mix SFX events under narration at exact offsets.

        events: [{"path": <audio file>, "at": <seconds>, "gain_db": <-10>}].
        Sample rate/channel conversion happens per-input so any narration/SFX
        format combination works; narration duration is preserved.
        """
        narr_path = Path(narration)
        if not narr_path.is_file():
            return {"ok": False, "out": out_mix, "error": f"narration not found: {narr_path}"}
        loaded = [e for e in events if e.get("path")]
        for e in loaded:
            if not Path(e["path"]).is_file():
                return {"ok": False, "out": out_mix, "error": f"sfx asset missing: {e['path']}"}

        out_path = Path(out_mix)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(narr_path)]
        for e in loaded:
            cmd += ["-i", str(e["path"])]

        filters = ["[0:a]aformat=sample_rates=48000:channel_layouts=mono[narr]"]
        labels = ["[narr]"]
        for i, e in enumerate(loaded, start=1):
            at_ms = max(0, round(float(e.get("at", 0.0)) * 1000))
            gain = float(e.get("gain_db", -10.0))
            filters.append(
                f"[{i}:a]aformat=sample_rates=48000:channel_layouts=mono,"
                f"adelay={at_ms}|{at_ms},volume={gain}dB[s{i}]"
            )
            labels.append(f"[s{i}]")
        filters.append(
            f"{ ''.join(labels) }amix=inputs={len(labels)}:duration=first:dropout_transition=0:normalize=0[mix]"
        )
        narr_dur = self._probe(narr_path)
        cmd += [
            "-filter_complex", ";".join(filters),
            "-map", "[mix]",
            "-ar", "48000", "-ac", "1",
        ]
        # Preserve exactly the narration length when its probe succeeded.
        if narr_dur > 0:
            cmd += ["-t", f"{narr_dur:.3f}"]
        if out_path.suffix.lower() in (".mp3", ".m4a"):
            cmd += ["-c:a", "libmp3lame" if out_path.suffix.lower() == ".mp3" else "aac", "-q:a", "2"]
        else:
            cmd += ["-c:a", "pcm_s16le"]
        cmd += [str(out_path)]

        r = run(cmd, timeout=600)
        if not r["ok"]:
            return {"ok": False, "out": str(out_path), "error": r["stderr"] or r["stdout"]}
        dur = self._probe(out_path)
        return {"ok": True, "out": str(out_path), "duration_sec": dur,
                "events": [{"at": e.get("at", 0.0), "gain_db": e.get("gain_db", -10.0),
                            "path": e["path"]} for e in loaded]}

    def _probe(self, path: Path | str) -> float:
        r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "json", str(path)], timeout=60)
        if not r["ok"]:
            return 0.0
        try:
            return float(json.loads(r["stdout"]).get("format", {}).get("duration", 0.0))
        except Exception:
            return 0.0

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        op = kwargs.get("op", "synth")
        if op == "mix":
            return self.mix(kwargs["narration"], kwargs.get("events", []), kwargs["out_mix"])
        return self.synthesize(kwargs.get("kind", "whoosh"), kwargs["out_wav"],
                               kwargs.get("duration", None), kwargs.get("gain_db", -6.0))


def _main() -> None:  # pragma: no cover
    import sys
    if len(sys.argv) >= 4 and sys.argv[1] == "synth":
        kind, out = sys.argv[2], sys.argv[3]
        dur = float(sys.argv[4]) if len(sys.argv) > 4 else None
        print(json.dumps(SfxTool().synthesize(kind, out, dur), indent=2))
        return
    print(json.dumps(SfxTool().health(), indent=2))


if __name__ == "__main__":
    _main()
