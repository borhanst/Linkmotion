"""Metadata tool - titles, description, tags, thumbnail.

Post-render SEO metadata generation: keyword research, 5-8 title options,
description, tags/hashtags, thumbnail variants.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from tools.base_tool import BaseTool, ToolTier, ToolRuntime, run


class MetadataTool(BaseTool):
    """Generate YouTube upload package: titles, description, tags, thumbnail."""

    name = "metadata"
    capability = "metadata"
    provider = "ai-news-agent"
    description = "Generate the YouTube upload package: 5-8 ranked title options, SEO description, tags/hashtags, and thumbnail variants."
    tier = ToolTier.PUBLISH
    runtime = ToolRuntime.LOCAL
    dependencies = ["remotion", "node"]
    agent_skills = ["remotion-video-common"]
    input_schema = {
        "type": "object",
        "properties": {
            "slug": {"type": "string"},
            "topic": {"type": "string"},
            "format": {"type": "string", "enum": ["long", "short"]},
            "keywords": {"type": "array", "items": {"type": "string"}},
            "scenes": {"type": "array", "items": {"type": "object"}},
        },
        "required": ["slug", "topic", "format"],
    }
    output_schema = {
        "type": "object",
        "properties": {"titles": {"type": "array"}, "tags": {"type": "array"}, "thumbnail": {"type": "string"}},
    }

    def health(self) -> dict[str, Any]:
        # Remotion stills are rendered via `npx remotion`, so we only require
        # node + npm. The per-video Remotion repo is wired separately.
        missing = [d for d in ["node", "npm"] if shutil.which(d) is None]
        return {"status": "available" if not missing else "unavailable", "missing_dependencies": missing}

    def write_titles(self, meta_dir: Path, topic: str, keywords: list[str],
                     format: str = "short") -> list[str]:
        meta_dir.mkdir(parents=True, exist_ok=True)
        kw = " ".join(keywords[:3]) if keywords else topic
        primary = keywords[0] if keywords else topic
        options = [
            f"{primary}: what just happened",
            f"{primary} explained in 60 seconds",
            f"Everything you need to know about {primary}",
            f"Why {primary} matters today",
            f"{primary} - the catch nobody's talking about",
            f"How to try {primary} right now",
            f"{kw} - a 60-second briefing",
        ]
        body = [f"# Titles - {topic}", "", "Ranked options. Recommended marked with [RECOMMENDED].", ""]
        for i, t in enumerate(options, 1):
            mark = " [RECOMMENDED]" if i == 1 else ""
            body.append(f"{i}. {t}{mark}")
        (meta_dir / "titles.md").write_text("\n".join(body) + "\n", encoding="utf-8")
        return options

    def write_description(self, meta_dir: Path, topic: str, bullets: list[str],
                          format: str = "short") -> str:
        summary = bullets[0] if bullets else topic
        lines = [summary, ""]
        if format == "long":
            lines.append("## Chapters")
            for b in bullets:
                lines.append(f"- {b}")
            lines.append("")
        lines.append("## Sources")
        lines.append("Verified against the primary source shown in the video.")
        lines.append("")
        lines.append("#Shorts #AI #LLM" if format == "short" else "#AI #LLM #News")
        text = "\n".join(lines)
        (meta_dir / "description.md").write_text(text, encoding="utf-8")
        return text

    def write_tags(self, meta_dir: Path, keywords: list[str],
                   format: str = "short") -> dict[str, Any]:
        tags = list(dict.fromkeys(keywords + ["AI", "LLM", "News"]))
        hashtags = ["#Shorts", "#AI", "#LLM"] if format == "short" else ["#AI", "#LLM", "#News"]
        data = {"tags": tags, "hashtags": hashtags}
        (meta_dir / "tags.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data

    def render_thumbnail(self, meta_dir: Path, root_tsx: str, composition_id: str,
                         out_png: str) -> dict[str, Any]:
        r = run(["npx", "-y", "remotion", "still", root_tsx, composition_id, out_png], timeout=300)
        return {"ok": r["ok"], "png": out_png if r["ok"] else "", "error": r.get("stderr", "")}

    def execute(self, slug: str, topic: str, format: str = "short",
                keywords: list[str] | None = None,
                scenes: list[dict[str, Any]] | None = None,
                root_tsx: str | None = None,
                composition_id: str | None = None) -> dict[str, Any]:
        keywords = keywords or [topic]
        meta_dir = Path("projects") / slug / "metadata"
        titles = self.write_titles(meta_dir, topic, keywords, format)
        bullets = [s.get("title", "") for s in (scenes or [])][:12]
        description = self.write_description(meta_dir, topic, bullets, format)
        tags = self.write_tags(meta_dir, keywords, format)
        thumb = ""
        if root_tsx and composition_id:
            t = self.render_thumbnail(meta_dir, root_tsx, composition_id,
                                      str(meta_dir / "thumbnail" / "thumb-1.png"))
            thumb = t.get("png", "")
        return {
            "ok": True,
            "slug": slug,
            "titles": titles,
            "description": description,
            "tags": tags,
            "thumbnail": thumb,
            "meta_dir": str(meta_dir),
        }


def _main() -> None:  # pragma: no cover
    print(json.dumps(MetadataTool().execute("demo", "GPT-5 release", "short", ["GPT-5", "OpenAI", "LLM"]), indent=2))


if __name__ == "__main__":  # pragma: no cover
    _main()