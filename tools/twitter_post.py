"""Twitter/X post tool.

Fetches the data needed to render the same design card as a given Twitter/X
post (keyless, via Twitter's official oEmbed endpoint plus page metadata) and
can also capture a best-effort screenshot of the post or of a rendered copy of
its card.

Primary (keyless) sources
------------------------
* https://publish.twitter.com/oembed?url=<post_url>  -> official tweet card HTML + author
* https://x.com/<user>/status/<id>                   -> og:title / og:description / og:image

Optional richer fields (timestamps, like/retweet counts) can be unlocked by
setting the TWITTER_BEARER_TOKEN env var so the tool can call
api.x.com/2/tweets/<id>?tweet.fields=created_at,public_metrics.

Usage (console)
---------------
python -m tools.twitter_post "https://x.com/NASA/status/2116263878807998722"
"""

from __future__ import annotations

import html as html_mod
import json
import os
import re
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from tools.base_tool import BaseTool, ToolRuntime, ToolStability, ToolTier

# --------------------------------------------------------------------------- #
# Tweet data model
# --------------------------------------------------------------------------- #


@dataclass
class TwitterPost:
    """Structured representation of a Twitter/X post + its card markup."""

    url: str
    author_name: str
    author_screen_name: str
    created_at: str | None
    created_at_raw: str | None
    text: str
    raw_text: str
    entities: dict[str, list[str]] = field(
        default_factory=lambda: {"urls": [], "media": [], "hashtags": [], "mentions": []}
    )
    media_urls: list[str] = field(default_factory=list)
    media_kind: str = "none"
    has_media: bool = False
    card_html: str = ""
    card_width: int = 0
    card_height: int = 0
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "author_name": self.author_name,
            "author_screen_name": self.author_screen_name,
            "created_at": self.created_at,
            "created_at_raw": self.created_at_raw,
            "text": self.text,
            "raw_text": self.raw_text,
            "entities": self.entities,
            "media_urls": self.media_urls,
            "media_kind": self.media_kind,
            "has_media": self.has_media,
            "card_html": self.card_html,
            "card_width": self.card_width,
            "card_height": self.card_height,
            "extra": dict(self.extra),
        }

    # ------------------------------------------------------------------ #
    # Rendering helpers
    # ------------------------------------------------------------------ #

    def render_card_html(self, style: str = "default") -> str:
        if style == "retweet":
            return _retweet_card_html(self)
        return _card_html(self)

    def screenshot_path(self, output_dir: str, width: int = 640, height: int = 640) -> str:
        slug = re.sub(r"[^a-zA-Z0-9_-]", "_", self.author_screen_name) or "post"
        tid = re.sub(r"[^a-zA-Z0-9_-]", "_", (self.url.split("/")[-1] or "post"))
        return str(Path(output_dir) / slug / f"{tid}.png")


# --------------------------------------------------------------------------- #
# Card HTML builders (self-contained, no external JS)
# --------------------------------------------------------------------------- #


def _card_html(post: TwitterPost) -> str:
    avatar = post.media_urls[0] if post.has_media and post.media_urls else "https://via.placeholder.com/48"
    img = ""
    if post.has_media and post.media_urls:
        img = f'<div class="media"><img src="{html_mod.escape(post.media_urls[0])}" alt=""></div>'
    date_html = ""
    if post.created_at:
        date_html = f'<div class="date">{html_mod.escape(post.created_at)}</div>'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html_mod.escape(post.author_screen_name)}</title>
<style>
  :root {{ --bg: #ffffff; --text: #1c1e21; --text2: #536471; --border: #e4e6e9; --accent: #1d9bf0; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:var(--bg); font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; display:flex; justify-content:center; padding:24px; color:var(--text); }}
  .card {{ width: 560px; max-width:100%; background:#fff; border:1px solid var(--border); border-radius:16px; overflow:hidden; display:flex; flex-direction:column; }}
  .top {{ display:flex; gap:12px; padding:12px 14px; align-items:center; }}
  .avatar {{ width:48px; height:48px; border-radius:50%; overflow:hidden; flex-shrink:0; }}
  .avatar img {{ width:100%; height:100%; object-fit:cover; }}
  .meta {{ flex:1; min-width:0; }}
  .meta .name {{ font-weight:600; font-size:15px; line-height:1.2; }}
  .meta .handle {{ color:var(--text2); font-size:14px; }}
  .meta .date {{ color:var(--text2); font-size:13px; margin-top:2px; }}
  .body {{ padding:12px 14px; font-size:15px; line-height:1.5; word-wrap:break-word; }}
  .body .text {{ white-space:pre-wrap; }}
  .media img {{ width:100%; border-radius:12px; display:block; }}
  .footer {{ display:flex; justify-content:space-between; padding:10px 14px; font-size:13px; color:var(--text2); border-top:1px solid var(--border); }}
  .footer .actions span {{ margin-left:6px; }}
</style>
</head>
<body>
  <div class="card">
    <div class="top">
      <div class="avatar"><img src="{html_mod.escape(avatar)}" alt=""></div>
      <div class="meta">
        <div class="name">{html_mod.escape(post.author_name)}</div>
        <div class="handle">@{html_mod.escape(post.author_screen_name)}</div>
        {date_html}
      </div>
    </div>
    <div class="body"><div class="text">{html_mod.escape(post.text)}</div>{img}</div>
    <div class="footer">
      <span><span class="actions">♥ {post.extra.get("favorite_count", "—")} · ↻ {post.extra.get("retweet_count", "—")}</span></span>
    </div>
  </div>
</body>
</html>
"""


def _retweet_card_html(post: TwitterPost) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  body {{ margin:0; background:#fff; font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; padding:16px; color:#1c1e21; }}
  .tweet {{ max-width:560px; border:1px solid #e4e6e9; border-radius:16px; overflow:hidden; }}
  .tweet p {{ margin:0 14px 12px; font-size:15px; line-height:1.5; white-space:pre-wrap; }}
  .tweet .meta {{ font-size:13px; color:#536471; }}
</style>
</head>
<body>
  <div class="tweet">{post.card_html}</div>
</body>
</html>
"""


def _widget_wrapper_html(url: str, theme: str = "light") -> str:
    """Wrapper page that renders the official Twitter embed widget.

    Loading widgets.js on a page containing a `blockquote.twitter-tweet`
    pointing at the post URL makes Twitter's own script render the *real*
    tweet UI (avatar, verified badge, fonts, counts) right inside our page —
    no api key, no login. This is what we screenshot for the "proof" visual.
    """
    bg = "#15202b" if theme == "dark" else "#ffffff"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
  body {{ margin:0; padding:24px; background:{bg}; display:flex; justify-content:center;
         font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }}
  .tweet-wrap {{ max-width:550px; width:100%; }}
</style>
</head>
<body>
  <div class="tweet-wrap">
    <blockquote class="twitter-tweet" data-theme="{theme}" data-conversation="none" data-dnt="true">
      <a href="{html_mod.escape(url)}"></a>
    </blockquote>
  </div>
  <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
</body>
</html>
"""


# --------------------------------------------------------------------------- #
# Tool
# --------------------------------------------------------------------------- #


class TwitterPostTool(BaseTool):
    """Fetch a Twitter/X post's data and (optionally) capture a screenshot."""

    name = "twitter_post"
    capability = "social_card"
    provider = "twitter-x"
    description = (
        "Fetch a Twitter/X post URL and extract the data to render the same design card "
        "(official tweet card markup, author, text, date, media). Captures a 'proof' "
        "screenshot by rendering the official Twitter embed widget (widgets.js) in "
        "headless Chromium and screenshotting the real tweet UI; falls back to a "
        "self-contained card recreation if the widget cannot render. Keyless: uses "
        "Twitter's official oEmbed endpoint + page metadata. Optionally requires "
        "TWITTER_BEARER_TOKEN for richer fields (timestamps, counts)."
    )
    tier = ToolTier.SOURCE
    runtime = ToolRuntime.LOCAL
    stability = ToolStability.BETA
    dependencies: list[str] = ["requests"]
    agent_skills: list[str] = ["web-explainer-video"]

    # ------------------------------------------------------------------ #
    # Schema
    # ------------------------------------------------------------------ #
    input_schema = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Twitter/X post URL (x.com / twitter.com, incl. mobile.)."},
            "screenshot": {"type": "boolean", "default": False, "description": "Capture a screenshot of the post / its card."},
            "render_card": {"type": "boolean", "default": True, "description": "Render a self-contained HTML card reproducing the tweet's design."},
            "output_dir": {"type": "string", "description": "Directory for artifacts (default: out/twitter_posts)."},
            "width": {"type": "integer", "default": 640, "minimum": 120, "maximum": 1920},
            "height": {"type": "integer", "default": 640, "minimum": 120, "maximum": 1080},
        },
        "required": ["url"],
    }
    output_schema = {
        "type": "object",
        "properties": {
            "url": {"type": "string"},
            "fetched": {"type": "boolean"},
            "tweet": {"type": "object"},
            "screenshot_path": {"type": "string"},
            "screenshot_ok": {"type": "boolean"},
            "screenshot_method": {"type": "string"},
            "screenshot_resolution": {"type": "string"},
            "screenshot_note": {"type": "string"},
            "card_html_path": {"type": "string"},
            "card_html": {"type": "string"},
            "reproduced_card_html": {"type": "string"},
        },
    }

    # ------------------------------------------------------------------ #
    # Health
    # ------------------------------------------------------------------ #
    def health(self) -> dict[str, Any]:
        missing = []
        try:
            import requests  # noqa: F401
        except ImportError:
            missing.append("requests")
        try:
            import playwright  # noqa: F401
        except ImportError:
            missing.append("playwright")
        return {"status": "unavailable" if missing else "available", "missing_dependencies": missing}

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def fetch(self, url: str, fetch_extra: bool = True) -> TwitterPost:
        """Resolve a Twitter/X post URL to structured data + card markup."""
        norm = self._normalize_url(url)
        m = re.search(r"(?:mobile\.)?(?:x|twitter)\.com/(?P<screen>[^/]+)/status/(?P<id>\d+)", norm)
        if not m:
            raise ValueError(
                f"Not a Twitter/X post URL: {url!r}. Expected https://x.com/<screen>/status/<id>"
            )
        screen_name = m.group("screen")
        post_id = m.group("id")

        post = self._fetch_oembed(norm)
        self._enrich_from_page(norm, post)
        if fetch_extra:
            self._enrich_extra(screen_name, post_id, post)
        return post

    def capture_screenshot(
        self,
        post: TwitterPost,
        width: int = 640,
        height: int = 640,
        output_dir: str | None = None,
    ) -> dict[str, Any]:
        """Capture the post as a high-resolution "proof" visual.

        Preferred method: the official Twitter embed widget (widgets.js) is
        rendered in headless Chromium and the rendered iframe element is
        screenshotted — this is the genuine Twitter UI. If widgets.js is
        unreachable or fails to render, falls back to a faithful,
        self-contained recreation of the post's card.
        Returns {"path", "ok", "method", "resolution", "note"}.
        """
        output_dir = output_dir or str(Path("out") / "twitter_posts")
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        fname = f"{re.sub(r'[^a-zA-Z0-9_-]', '_', post.author_screen_name)}_({post.url.split('/')[-1]}).png"
        out_path = Path(output_dir) / fname
        out_path.parent.mkdir(parents=True, exist_ok=True)

        shot = self._capture_widget(post, out_path)
        if not shot["ok"]:
            shot = self._capture_card(post, out_path, width, height)
        return shot

    def _capture_widget(self, post: TwitterPost, out_path: Path) -> dict[str, Any]:
        """Render the official embed widget and screenshot the real tweet UI."""
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
        except Exception as e:  # pragma: no cover - defensive
            return {"path": "", "ok": False, "method": "twitter_widget", "resolution": None,
                    "note": f"playwright unavailable: {e}"}
        try:
            with sync_playwright() as p:
                b = p.chromium.launch()
                # Generous viewport so the full tweet renders before we clip to it.
                pg = b.new_page(viewport={"width": 1280, "height": 1600})
                pg.set_content(_widget_wrapper_html(post.url), wait_until="load")
                try:
                    # widgets.js replaces the blockquote with iframe#twitter-widget-N
                    # (a second `rufous-sandbox` analytics iframe is created at 0x0).
                    pg.wait_for_selector("iframe[id^='twitter-widget-']", timeout=20000)
                except Exception:
                    b.close()
                    return {"path": "", "ok": False, "method": "twitter_widget", "resolution": None,
                            "note": "embed widget did not render (network/blocked), falling back"}
                frame_el = pg.locator("iframe[id^='twitter-widget-']").first
                pg.wait_for_timeout(1500)  # let widget paint media/counts
                frame_el.screenshot(path=str(out_path))
                bbox = frame_el.bounding_box() or {}
                b.close()
        except Exception as e:  # pragma: no cover - defensive
            return {"path": "", "ok": False, "method": "twitter_widget", "resolution": None,
                    "note": f"widget capture failed: {e}"}
        return {
            "path": str(out_path),
            "ok": True,
            "method": "twitter_widget",
            "resolution": (int(bbox.get("width", 0)), int(bbox.get("height", 0))),
            "note": (
                "Official Twitter embed widget (widgets.js) rendered in headless "
                "Chromium — screenshot of the real tweet UI (avatar, name, date, "
                "text, media, counts) usable as authentic proof in the video."
            ),
        }

    def _capture_card(
        self,
        post: TwitterPost,
        out_path: Path,
        width: int = 640,
        height: int = 640,
    ) -> dict[str, Any]:
        """Fallback: screenshot the faithful self-contained card recreation."""
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
            with sync_playwright() as p:
                b = p.chromium.launch()
                pg = b.new_page(viewport={"width": width, "height": height})
                pg.set_content(self.render_card(post), wait_until="load")
                pg.wait_for_timeout(500)
                pg.screenshot(
                    path=str(out_path),
                    clip={"x": 0, "y": 0, "width": width, "height": height},
                )
                b.close()
        except Exception as e:  # pragma: no cover - defensive
            return {
                "path": "",
                "ok": False,
                "method": "playwright_card",
                "resolution": (width, height),
                "note": f"capture failed: {e}",
            }

        return {
            "path": str(out_path),
            "ok": True,
            "method": "playwright_card",
            "resolution": (width, height),
            "note": (
                "Fallback: faithful recreation of the post's design card in headless "
                "Chromium (official embed widget unavailable); covers the post's "
                "card design but is not the raw x.com UI."
            ),
        }

    def render_card(self, post: TwitterPost, style: str = "default") -> str:
        return post.render_card_html(style)

    def execute(self, url: str, screenshot: bool = False, render_card: bool = True,
                output_dir: str | None = None, width: int = 640, height: int = 640) -> dict[str, Any]:
        post = self.fetch(url)
        out_dir = Path(output_dir) if output_dir else Path("out") / "twitter_posts"

        result: dict[str, Any] = {
            "url": post.url,
            "fetched": True,
            "tweet": post.to_dict(),
            "screenshot_path": None,
            "screenshot_ok": False,
            "screenshot_method": None,
            "card_html_path": None,
            "card_html": post.card_html,
            "reproduced_card_html": post.render_card_html(),
        }

        if render_card:
            slug = re.sub(r"[^a-zA-Z0-9_-]", "_", post.author_screen_name) or "post"
            tid = re.sub(r"[^a-zA-Z0-9_-]", "_", (post.url.split("/")[-1] or "post"))
            folder = out_dir / slug
            folder.mkdir(parents=True, exist_ok=True)
            card_path = folder / f"{tid}.html"
            card_path.write_text(post.card_html, encoding="utf-8")
            result["card_html_path"] = str(card_path)

            reproduced = folder / f"{tid}_card.html"
            reproduced.write_text(post.render_card_html(), encoding="utf-8")
            result["reproduced_card_html"] = str(reproduced)

        if screenshot:
            shot = self.capture_screenshot(post, width, height, str(out_dir))
            result["screenshot_path"] = shot["path"]
            result["screenshot_ok"] = shot["ok"]
            result["screenshot_method"] = shot["method"]
            result["screenshot_resolution"] = shot.get("resolution")
            result["screenshot_note"] = shot.get("note")
        return result

    # ------------------------------------------------------------------ #
    # Internal steps
    # ------------------------------------------------------------------ #
    @staticmethod
    def _normalize_url(url: str) -> str:
        url = urllib.parse.urldefrag(url).url
        url = urllib.parse.urlparse(url).geturl()
        url = re.sub(r"^(https?://)?(www\.)?", "https://", url, count=1)
        url = re.sub(r"^https?://(?:mobile\.)?(?:x|twitter)\.com", "https://x.com", url, count=1)
        return url.rstrip("/")

    def _fetch_oembed(self, url: str) -> TwitterPost:
        oembed_url = f"https://publish.twitter.com/oembed?url={urllib.parse.quote(url, safe='')}"
        try:
            resp = requests.get(oembed_url, timeout=30)
        except Exception as e:
            raise RuntimeError(f"oEmbed request failed: {e}") from e
        if resp.status_code != 200:
            raise RuntimeError(f"oEmbed returned HTTP {resp.status_code} for {url}")
        data = resp.json()

        card_html = data.get("html", "") or ""
        p_match = re.search(r"<p[^>]*>(.*?)</p>", card_html, re.S)
        body_html = p_match.group(1) if p_match else ""

        raw_text = re.sub(r"<br\s*/?>", " ", body_html, flags=re.I)
        raw_text = re.sub(r"<[^>]+>", "", raw_text)
        raw_text = html_mod.unescape(raw_text)
        raw_text = re.sub(r"\s+", " ", raw_text).strip()

        created_at, created_at_raw = None, None
        m = re.search(r"(\w{3,9}\s+\d{1,2},\s+\d{4})", card_html)
        if m:
            created_at_raw = m.group(1)
            try:
                datetime.strptime(m.group(1), "%B %d, %Y")
                created_at = m.group(1)
            except ValueError:
                pass

        if created_at_raw:
            # The attribution footer ("— NASA (@NASA) October 30, 2026") sits outside
            # the <p> so the tweet body never carries the handle/date.
            pass

        media_urls = list(
            dict.fromkeys(
                "https://pic.twitter.com/" + m for m in re.findall(r"pic\.twitter\.com/([a-zA-Z0-9]{6,})", card_html)
            )
        )
        return TwitterPost(
            url=url,
            author_name=str(data.get("author_name", "")).strip() or "Unknown",
            author_screen_name=str(data.get("author_url", "")).rstrip("/").split("/")[-1],
            created_at=created_at,
            created_at_raw=created_at_raw,
            text=raw_text,
            raw_text=raw_text,
            entities={
                "urls": list(dict.fromkeys(f"https://t.co/{m.group(1)}" for m in re.finditer(r"https://t.co/([a-zA-Z0-9]+)", card_html))),
                "media": media_urls,
                "hashtags": [],
                "mentions": [],
            },
            media_urls=media_urls,
            media_kind="photo" if media_urls else "none",
            has_media=bool(media_urls),
            card_html=card_html,
            card_width=int(data.get("width") or 0),
            card_height=int(data.get("height") or 0),
            extra={},
        )

    def _enrich_from_page(self, url: str, post: TwitterPost) -> None:
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}, timeout=30)
        except Exception:
            return
        if resp.status_code != 200:
            return
        html = resp.text
        og = {}
        for key in ("title", "description", "image", "alt"):
            m = re.search(rf'<meta[^>]+property="og:{key}"[^>]+content="([^"]*)"', html, re.I)
            if m:
                og[key] = m.group(1)
        if og.get("title"):
            post.author_name = og["title"].split("(", 1)[0].strip() or post.author_name
        if og.get("description"):
            post.raw_text = re.sub(r"<[^>]+>", " ", og["description"])
            post.raw_text = re.sub(r"\s+", " ", post.raw_text).strip()
        if og.get("image"):
            og["image"] = html_mod.unescape(og["image"])
            post.media_urls = list(dict.fromkeys([og["image"]] + post.media_urls))
            post.has_media = True
            post.media_kind = "photo"

    def _enrich_extra(self, screen_name: str, post_id: str, post: TwitterPost) -> None:
        token = os.environ.get("TWITTER_BEARER_TOKEN", "").strip()
        if not token:
            return
        api = f"https://api.x.com/2/tweets/{post_id}?tweet.fields=created_at,public_metrics"
        try:
            resp = requests.get(api, headers={"Authorization": f"Bearer {token}"}, timeout=30)
            if resp.status_code == 200:
                payload = resp.json()
                post.extra["created_at"] = (payload.get("data") or {}).get("created_at")
                metrics = (payload.get("data") or {}).get("public_metrics") or {}
                post.extra["retweet_count"] = metrics.get("retweet_count")
                post.extra["favorite_count"] = metrics.get("favorite_count")
                post.extra["reply_count"] = metrics.get("reply_count")
                post.extra["quote_count"] = metrics.get("quote_count")
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    # Screenshot (playwright card render is the authoritative screenshot)
    # ------------------------------------------------------------------ #


def _main() -> None:  # pragma: no cover
    import sys

    if len(sys.argv) < 2:
        print("usage: python -m tools.twitter_post <twitter_post_url> [--screenshot]")
        return
    url = sys.argv[1]
    screenshot = "--screenshot" in sys.argv[2:]
    tool = TwitterPostTool()
    result = tool.execute(url, screenshot=screenshot, render_card=True, width=640, height=640)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    _main()
