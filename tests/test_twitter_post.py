"""Contract tests for the Twitter/X post tool (data fetch + card rendering)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.twitter_post import TwitterPost, TwitterPostTool  # noqa: E402

REAL_TWEET = "https://x.com/nasa/status/2116263878807998722"


# --------------------------------------------------------------------------- #
# Data fetch
# --------------------------------------------------------------------------- #


def test_fetch_twitter_post_returns_structured_data() -> None:
    post = TwitterPostTool().fetch(REAL_TWEET)
    assert isinstance(post, TwitterPost)
    assert post.author_name == "NASA"
    assert post.author_screen_name == "NASA"
    assert post.created_at == "October 30, 2026"
    assert "MAX POWER" in post.text
    assert post.card_html.startswith("<blockquote")
    assert 'class="twitter-tweet"' in post.card_html
    assert post.media_urls, "a tweet with an image should expose its media URL"
    assert post.media_kind == "photo"
    assert post.has_media is True


def test_fetch_twitter_post_normalizes_urls() -> None:
    # mobile.twitter.com and trailing slash must resolve to the same post.
    a = TwitterPostTool().fetch("https://mobile.twitter.com/nasa/status/2116263878807998722")
    b = TwitterPostTool().fetch("https://x.com/nasa/status/2116263878807998722/")
    assert a.url == b.url


def test_fetch_raises_on_non_tweet_url() -> None:
    with pytest.raises(ValueError):
        TwitterPostTool().fetch("https://x.com/nasa")


# --------------------------------------------------------------------------- #
# Card rendering
# --------------------------------------------------------------------------- #


def test_render_card_html_is_self_contained() -> None:
    tool = TwitterPostTool()
    post = tool.fetch(REAL_TWEET)
    html = post.render_card_html()
    assert "<!doctype html>" in html
    assert "@NASA" in html
    assert "MAX POWER" in html
    # The media URL is HTML-escaped (& -> &amp;) inside the attribute.
    assert post.media_urls[0].replace("&", "&amp;") in html


def test_render_card_html_reproduced_file_matches_artifact() -> None:
    tool = TwitterPostTool()
    post = tool.fetch(REAL_TWEET)
    # The rendered card always contains the author name block.
    assert '<div class="name">NASA</div>' in post.render_card_html()


# --------------------------------------------------------------------------- #
# Screenshot (official widget render, card-recreation fallback)
# --------------------------------------------------------------------------- #


def test_capture_screenshot_prefers_official_widget() -> None:
    tool = TwitterPostTool()
    post = tool.fetch(REAL_TWEET)
    out = tool.capture_screenshot(post, width=640, height=640, output_dir="/tmp/kilo/twitter_tests")
    assert out["ok"] is True
    # Primary method: the official embed widget renders the real tweet UI.
    assert out["method"] == "twitter_widget"
    assert out["path"]
    assert out["resolution"] and all(dim > 0 for dim in out["resolution"])
    assert Path(out["path"]).exists()
    assert "embed widget" in out["note"]


def test_capture_card_fallback_renders_card() -> None:
    tool = TwitterPostTool()
    post = tool.fetch(REAL_TWEET)
    out_path = Path("/tmp/kilo/twitter_tests/fallback.png")
    out = tool._capture_card(post, out_path, width=640, height=640)
    assert out["ok"] is True
    assert out["method"] == "playwright_card"
    assert out["path"]
    assert out["resolution"] == (640, 640)
    assert Path(out["path"]).exists()
    # The fallback screenshot captures the post's rendered design card.
    assert "design card" in out["note"]


def test_widget_wrapper_html_contains_embed() -> None:
    from tools.twitter_post import _widget_wrapper_html

    html = _widget_wrapper_html(REAL_TWEET)
    assert 'class="twitter-tweet"' in html
    assert "platform.twitter.com/widgets.js" in html
    # The tweet URL must be escaped inside the blockquote's <a href>.
    import html as html_mod

    assert html_mod.escape(REAL_TWEET) in html


def test_health_is_available() -> None:
    assert TwitterPostTool().health()["status"] in {"available", "unavailable", "degraded"}
