"""Web search + fetch tool.

Research and verification for AI news / model releases. Grounds every claim
in a page we actually show.
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from tools.base_tool import BaseTool, ToolTier, ToolRuntime


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"title": self.title, "url": self.url, "snippet": self.snippet}


class WebSearchTool(BaseTool):
    """Search the web and return ranked results.

    Uses the DuckDuckGo HTML endpoint (no API key required). Falls back to a
    configured search URL if DDG is unreachable.
    """

    name = "web_search"
    capability = "web_search"
    provider = "duckduckgo"
    description = "Search the web for AI news / model-release research and verification."
    tier = ToolTier.SOURCE
    runtime = ToolRuntime.API
    dependencies: list[str] = []
    agent_skills: list[str] = []
    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query."},
            "num_results": {"type": "integer", "default": 8, "minimum": 1, "maximum": 20},
        },
        "required": ["query"],
    }
    output_schema = {
        "type": "object",
        "properties": {
            "results": {"type": "array", "items": {"type": "object"}},
            "query": {"type": "string"},
        },
    }

    def health(self) -> dict[str, Any]:
        return {"status": "available", "missing_dependencies": []}

    def search(self, query: str, num_results: int = 8) -> list[SearchResult]:
        out: list[SearchResult] = []
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (ai-news-agent research)"}
        )
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
        except Exception:
            return out

        import re
        # DuckDuckGo HTML result anchors
        for m in re.finditer(
            r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            html, re.DOTALL,
        ):
            raw_url = m.group(1)
            title = re.sub(r"<[^>]+>", "", m.group(2)).strip()
            if not title:
                continue
            # DDG wraps URLs in a redirect; unwrap if present
            if "uddg=" in raw_url:
                qs = urllib.parse.parse_qs(urllib.parse.urlparse(raw_url).query)
                raw_url = qs.get("uddg", [raw_url])[0]
            out.append(SearchResult(title=title, url=raw_url))
            if len(out) >= num_results:
                break
        return out

    def fetch(self, url: str, max_chars: int = 8000) -> dict[str, Any]:
        """Fetch a page and return plain text (best-effort HTML->text)."""
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (ai-news-agent research)"}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")
        except Exception as e:
            return {"ok": False, "url": url, "error": str(e), "text": ""}

        import re
        # Strip scripts/styles
        raw = re.sub(r"<script[\s\S]*?</script>", " ", raw, flags=re.IGNORECASE)
        raw = re.sub(r"<style[\s\S]*?</style>", " ", raw, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", raw)
        text = re.sub(r"\s+", " ", text).strip()
        return {"ok": True, "url": url, "text": text[:max_chars], "chars": len(text)}

    def execute(self, query: str, num_results: int = 8,
                fetch_top: int = 0) -> dict[str, Any]:
        results = self.search(query, num_results)
        fetched: list[dict[str, Any]] = []
        for r in results[:fetch_top]:
            fetched.append(self.fetch(r.url))
        return {
            "ok": True,
            "query": query,
            "results": [r.to_dict() for r in results],
            "fetched": fetched,
            "count": len(results),
        }


# Convenience: allow `python -m tools.web_search`
def _main() -> None:  # pragma: no cover
    import sys
    q = " ".join(sys.argv[1:]) or "AI news today"
    print(json.dumps(WebSearchTool().execute(q, num_results=5), indent=2, ensure_ascii=False))


if __name__ == "__main__":  # pragma: no cover
    _main()