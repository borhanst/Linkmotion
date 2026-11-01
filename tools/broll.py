"""B-roll / media acquisition tool.

Searches the web for topic images and video, captures social-media posts and
screenshots from real URLs, downloads demo video clips referenced by
docs/articles, and catalogs user-supplied files. No stock-library APIs.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.base_tool import BaseTool, ToolTier, ToolRuntime


@dataclass
class MediaResult:
    kind: str               # image | video | social | user
    url: str
    title: str = ""
    snippet: str = ""
    source_url: str = ""
    license_note: str = ""
    local_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "url": self.url, "title": self.title,
                "snippet": self.snippet, "source_url": self.source_url,
                "license_note": self.license_note, "local_path": self.local_path}


class BrollTool(BaseTool):
    name = "broll"
    capability = "broll"
    provider = "ai-news-agent"
    description = "Acquire B-roll media from the web: topic images/video, social-media posts and screenshots, demo clips from docs/articles, plus user-supplied files."
    tier = ToolTier.SOURCE
    runtime = ToolRuntime.LOCAL
    dependencies = []
    agent_skills = ["broll-planning"]
    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "kinds": {"type": "array", "items": {"type": "string"},
                      "default": ["image", "social"]},
            "num_results": {"type": "integer", "default": 6, "minimum": 1, "maximum": 20},
            "output_dir": {"type": "string"},
            "user_files": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["query"],
    }
    output_schema = {
        "type": "object",
        "properties": {"results": {"type": "array"}, "count": {"type": "integer"}},
    }

    def health(self) -> dict[str, Any]:
        return {"status": "available", "missing_dependencies": []}

    # ------------------------------------------------------------------ #
    def search(self, query: str, num_results: int = 6) -> list[MediaResult]:
        """Web search for topic images/video + social posts."""
        from tools.web_search import WebSearchTool
        raw = WebSearchTool().search(query, num_results=max(num_results, 8))
        out: list[MediaResult] = []
        for r in raw:
            url = r.url.lower()
            kind = "image" if any(x in url for x in ("image", "img", "photo", "pic", ".jpg", ".png", ".webp")) else "social"
            if any(x in url for x in ("youtube.com", "vimeo.com", ".mp4", "video")):
                kind = "video"
            if any(x in url for x in ("reddit.com", "x.com", "twitter.com", "news.ycombinator.com", "discourse", "forum")):
                kind = "social"
            out.append(MediaResult(kind=kind, url=r.url, title=r.title, snippet=r.snippet,
                                   source_url=r.url, license_note="verify on page before use"))
        return out[:num_results]

    def download(self, url: str, output_dir: str, kind: str = "image") -> str:
        """Download a media file to output_dir. Returns local path or ''."""
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        ext = {"image": ".img", "video": ".mp4", "social": ".html", "user": ""}.get(kind, ".bin")
        dest = out_dir / f"{abs(hash(url))}{ext}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (ai-news-agent)"})
        try:
            with urllib.request.urlopen(req, timeout=45) as resp, open(dest, "wb") as f:
                f.write(resp.read())
            return str(dest)
        except Exception:
            return ""

    def catalog_user_files(self, files: list[str], output_dir: str) -> list[MediaResult]:
        """Catalog files the user supplied (images, videos, screenshots)."""
        out: list[MediaResult] = []
        for p in files:
            src = Path(p)
            if not src.is_file():
                continue
            kind = "video" if src.suffix.lower() in {".mp4", ".mov", ".webm", ".mkv"} else "image"
            dest_dir = Path(output_dir) / f"{kind}s"
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / src.name
            try:
                shutil.copy2(src, dest)
            except Exception:
                continue
            out.append(MediaResult(kind="user", url=str(dest), title=src.name,
                                   source_url="user-supplied", local_path=str(dest),
                                   license_note="user-provided - confirm rights"))
        return out

    def execute(self, query: str, kinds: list[str] | None = None,
                num_results: int = 6, output_dir: str | None = None,
                user_files: list[str] | None = None) -> dict[str, Any]:
        kinds = kinds or ["image", "social"]
        out_dir = output_dir or "/tmp/kilo/broll"
        results = self.search(query, num_results)
        if user_files:
            results += self.catalog_user_files(user_files, out_dir)
        if output_dir:
            for r in results:
                if r.kind in ("image", "video", "social") and not r.local_path:
                    r.local_path = self.download(r.url, out_dir, r.kind)
        return {"ok": True, "query": query, "count": len(results),
                "results": [r.to_dict() for r in results]}


def _main() -> None:  # pragma: no cover
    import sys
    q = " ".join(sys.argv[1:]) or "AI data center server room"
    print(json.dumps(BrollTool().execute(q, num_results=4), indent=2, ensure_ascii=False))


if __name__ == "__main__":  # pragma: no cover
    _main()