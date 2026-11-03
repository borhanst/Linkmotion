"""Engine selection: pick HTML (GSAP/Anime.js) per scene.

Default engine is now plain HTML recorded via Playwright. Remotion and
HyperFrames remain available for backward compatibility but are no longer
the default.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class CompositionEngine(str, Enum):
    HTML = "html"
    REMOTION = "remotion"
    HYPERFRAMES = "hyperframes"


@dataclass
class EngineDecision:
    scene_id: str
    engine: str
    reason: str = ""
    author_path: str = ""
    composition_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def recommend_engine(scene: dict[str, Any]) -> str:
    return CompositionEngine.HTML.value


def resolve_engine(scene: dict[str, Any]) -> str:
    explicit = scene.get("engine")
    if explicit in (CompositionEngine.HTML.value, CompositionEngine.REMOTION.value,
                    CompositionEngine.HYPERFRAMES.value):
        return explicit
    return recommend_engine(scene)


def render_scene(scene: dict[str, Any], slug: str, fps: int = 30, crf: int = 23) -> dict[str, Any]:
    from lib.paths import project_slug_dir

    engine = resolve_engine(scene)
    scene_id = scene.get("id", "scene")
    out_dir = project_slug_dir(slug) / "renders"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_mp4 = str(out_dir / f"{scene_id}.mp4")

    src_dir = project_slug_dir(slug) / "src" / engine / scene_id
    if engine == CompositionEngine.HTML.value:
        from tools.html_render import HtmlRenderTool
        index_html = str(src_dir / "index.html")
        if not Path(index_html).is_file():
            return {"ok": False, "engine": engine, "scene_id": scene_id,
                    "error": f"composition not found: {index_html}"}
        tool = HtmlRenderTool()
        duration = float(scene.get("duration_sec", 6.0))
        result = tool.render(index_html, out_mp4, duration, fps,
                             scene.get("viewport", [1920, 1080]), crf)
    elif engine == CompositionEngine.HYPERFRAMES.value:
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
    out: dict[str, Any] = {}
    missing = [d for d in ["node", "npm"] if shutil.which(d) is None]
    for engine in CompositionEngine:
        out[engine.value] = {"available": True, "missing_dependencies": []}
    return out


def _main() -> None:  # pragma: no cover
    print(json.dumps(health(), indent=2))


if __name__ == "__main__":  # pragma: no cover
    _main()
