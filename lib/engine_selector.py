"""Engine selection: pick Remotion or HyperFrames per scene.

The LLM (stage director) decides which engine fits each scene. This module
exposes the decision framework, a structured scene spec, and a single render
entry point that dispatches to the right tool.

Decision factors (documented for the LLM):

| Factor | Remotion | HyperFrames |
|---|---|---|
| Authoring | React component (TSX) | Plain HTML + data-* attributes |
| Best for | Complex programmatic UI, charts, bespoke motion, long-form | Existing web material, templates, data-driven renders, agent-authored clips |
| Build step | Bundler required | None; HTML plays as-is |
| Determinism | Frame-accurate | Byte-identical across runs |
| License | Source-available (paid >3 people) | Apache 2.0 |
| Existing material | Rewritten as React | Drops in close to as-is |

Default: Remotion (matches the existing compose-director skills). Switch to
HyperFrames when a scene is better expressed as HTML/CSS (existing page,
template, data-driven card, Lottie/GSAP animation).
"""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class CompositionEngine(str, Enum):
    REMOTION = "remotion"
    HYPERFRAMES = "hyperframes"


@dataclass
class EngineDecision:
    """The LLM's per-scene engine choice + rationale."""

    scene_id: str
    engine: str  # "remotion" | "hyperframes"
    reason: str = ""
    author_path: str = ""  # where the authored scene lives (tsx or html)
    composition_id: str = ""  # remotion composition id (hyperframes ignores)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def recommend_engine(scene: dict[str, Any]) -> str:
    """Heuristic fallback when the LLM has not decided.

    Picks HyperFrames for scenes that are HTML/template-like, Remotion for
    everything else. The LLM should always override this with an explicit
    `engine` field on the scene.
    """
    scene_type = scene.get("type", "")
    if scene_type in {"web", "media", "social"}:
        return CompositionEngine.HYPERFRAMES.value
    return CompositionEngine.REMOTION.value


def resolve_engine(scene: dict[str, Any]) -> str:
    """Return the engine for a scene: explicit > heuristic."""
    explicit = scene.get("engine")
    if explicit in (CompositionEngine.REMOTION.value, CompositionEngine.HYPERFRAMES.value):
        return explicit
    return recommend_engine(scene)


def render_scene(scene: dict[str, Any], slug: str, fps: int = 30, crf: int = 23) -> dict[str, Any]:
    """Render one scene to its own MP4 using the scene's chosen engine.

    The authored source lives under projects/<slug>/src/<engine>/<scene-id>/.
    Returns a render report fragment: {ok, out_mp4, duration_sec, engine}.
    """
    from lib.paths import project_slug_dir

    engine = resolve_engine(scene)
    scene_id = scene.get("id", "scene")
    out_dir = project_slug_dir(slug) / "renders"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_mp4 = str(out_dir / f"{scene_id}.mp4")

    src_dir = project_slug_dir(slug) / "src" / engine / scene_id
    if engine == CompositionEngine.HYPERFRAMES.value:
        from tools.hyperframe_compose import HyperFrameComposeTool
        composition_html = str(src_dir / "composition.html")
        if not Path(composition_html).is_file():
            return {"ok": False, "engine": engine, "scene_id": scene_id,
                    "error": f"composition not found: {composition_html}"}
        tool = HyperFrameComposeTool()
        result = tool.render(composition_html, out_mp4, fps, crf)
    else:
        from tools.video_compose import VideoComposeTool
        root_tsx = str(src_dir / "index.tsx")
        composition_id = scene.get("composition_id", f"{slug}-{scene_id}")
        if not Path(root_tsx).is_file():
            return {"ok": False, "engine": engine, "scene_id": scene_id,
                    "error": f"remotion root not found: {root_tsx}"}
        tool = VideoComposeTool()
        result = tool.render(root_tsx, composition_id, out_mp4, fps, crf)

    result.update({"engine": engine, "scene_id": scene_id})
    return result


def health() -> dict[str, Any]:
    """Report which engines are usable in this environment."""
    out: dict[str, Any] = {}
    missing = [d for d in ["node", "npm"] if shutil.which(d) is None]
    for engine in CompositionEngine:
        out[engine.value] = {"available": not missing, "missing_dependencies": missing}
    return out


def _main() -> None:  # pragma: no cover
    print(json.dumps(health(), indent=2))


if __name__ == "__main__":  # pragma: no cover
    _main()