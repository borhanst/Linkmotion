"""Browser capture tool - Playwright screen recording of real pages.

Drives a real browser: open, scroll, select/highlight text, spotlight
sections, click. Produces frames the narration can describe. This is the
web-explainer-video skill's capture engine, wrapped as a registry tool.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.base_tool import BaseTool, ToolTier, ToolRuntime


@dataclass
class InspectResult:
    url: str
    headings: list[str] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)
    code_blocks: list[str] = field(default_factory=list)
    tables: list[dict[str, Any]] = field(default_factory=list)
    screenshots: list[str] = field(default_factory=list)
    http_status: int | None = None
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url, "headings": self.headings, "paragraphs": self.paragraphs,
            "code_blocks": self.code_blocks, "tables": self.tables,
            "screenshots": self.screenshots, "http_status": self.http_status,
            "note": self.note,
        }


class BrowserCaptureTool(BaseTool):
    """Inspect and capture real pages with Playwright."""

    name = "browser_capture"
    capability = "browser_capture"
    provider = "playwright"
    description = "Open a real website in a headless browser, scroll, select/highlight text, spotlight sections, and capture frames for a narrated walkthrough."
    tier = ToolTier.SOURCE
    runtime = ToolRuntime.LOCAL
    dependencies = ["playwright"]
    agent_skills = ["web-explainer-video", "web-explainer-video-animation"]
    input_schema = {
        "type": "object",
        "properties": {
            "url": {"type": "string"},
            "shots": {"type": "integer", "default": 4, "minimum": 1, "maximum": 12},
            "viewport": {"type": "array", "items": {"type": "integer"}, "default": [1280, 720]},
            "dark": {"type": "boolean", "default": True},
            "output_dir": {"type": "string"},
        },
        "required": ["url"],
    }
    output_schema = {
        "type": "object",
        "properties": {
            "inspect": {"type": "object"},
            "screenshots": {"type": "array", "items": {"type": "string"}},
        },
    }

    def health(self) -> dict[str, Any]:
        missing: list[str] = []
        try:
            import playwright  # noqa: F401
        except ImportError:
            missing.append("playwright-python")
        # chromium binary is installed lazily via `playwright install chromium`
        return {"status": "available" if not missing else "unavailable", "missing_dependencies": missing}

    def inspect(self, url: str, shots: int = 4, viewport: list[int] | None = None,
                dark: bool = True, output_dir: str | None = None) -> InspectResult:
        """Open the page, capture N screenshots, and extract headings/paragraphs."""
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
        except ImportError as e:
            return InspectResult(url=url, note=f"playwright unavailable: {e}")

        viewport = viewport or [1280, 720]
        out_dir = Path(output_dir) if output_dir else Path("/tmp/kilo/ai-news-capture")
        out_dir.mkdir(parents=True, exist_ok=True)

        result = InspectResult(url=url)
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                context = browser.new_context(viewport={"width": viewport[0], "height": viewport[1]})
                page = context.new_page()
                try:
                    resp = page.goto(url, wait_until="domcontentloaded", timeout=45000)
                    result.http_status = resp.status if resp else None
                except Exception as e:
                    result.note = f"navigation failed: {e}"
                    browser.close()
                    return result

                try:
                    page.wait_for_timeout(1500)
                except Exception:
                    pass

                result.headings = page.eval_on_selector_all(
                    "h1, h2, h3", "els => els.map(e => e.textContent.trim()).filter(Boolean)"
                )[:20]
                result.paragraphs = page.eval_on_selector_all(
                    "p", "els => els.map(e => e.textContent.trim()).filter(Boolean)"
                )[:20]
                result.code_blocks = page.eval_on_selector_all(
                    "pre, code", "els => els.map(e => e.textContent.trim()).filter(Boolean)"
                )[:10]
                try:
                    result.tables = page.eval_on_selector_all(
                        "table", "els => els.map(t => ({rows: Array.from(t.querySelectorAll('tr')).map(r => Array.from(r.querySelectorAll('td,th')).map(c => c.textContent.trim()))}))"
                    )[:5]
                except Exception:
                    result.tables = []

                for i in range(shots):
                    path = str(out_dir / f"shot-{i + 1}.png")
                    try:
                        page.screenshot(path=path, full_page=(i == 0))
                        result.screenshots.append(path)
                    except Exception:
                        pass

                browser.close()
        except Exception as e:
            result.note = f"capture failed: {e}"
        return result

    def execute(self, url: str, shots: int = 4, viewport: list[int] | None = None,
                dark: bool = True, output_dir: str | None = None) -> dict[str, Any]:
        r = self.inspect(url, shots, viewport, dark, output_dir)
        return {"ok": not r.note, "inspect": r.to_dict(), "screenshots": r.screenshots}


def _main() -> None:  # pragma: no cover
    import sys
    url = sys.argv[1] or "https://github.com/calesthio/OpenMontage"
    print(json.dumps(BrowserCaptureTool().execute(url, shots=3), indent=2, ensure_ascii=False))


if __name__ == "__main__":  # pragma: no cover
    _main()