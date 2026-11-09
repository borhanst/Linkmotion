"""Channel & video analysis tool.

Deconstructs one YouTube channel or one video so the agent can produce a
"channel profile" or mine "video ideas" from it:

- video metadata: title, description, tags, views, publish date, category,
  duration, chapters, all thumbnail URLs
- transcript with timestamps (reuses the keyless fetchers in youtube_source)
- channel profile: recent uploads -> cadence, duration stats, view
  median/outliers, title patterns, recurring topics
- frame sampling (optional): yt-dlp + ffmpeg stills at transcript-timestamp
  boundaries -> grounded scene/animation analysis

IMPORTANT - inspiration only. Everything this tool returns is raw material for
learning TECHNIQUE (structure, framing, pacing). Wording must not be reused.
Run lib/originality.check() on any title/outline/script derived from a source
before presenting it.
"""

from __future__ import annotations

import json
import re
import statistics
import tempfile
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.base_tool import BaseTool, ToolTier, ToolRuntime, run
from tools.youtube_source import YouTubeSourceTool

_USER_AGENT = "Mozilla/5.0 (ai-news-agent)"

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for", "with",
    "how", "why", "what", "is", "are", "was", "this", "that", "you", "your",
    "it", "its", "at", "by", "from", "new", "vs", "my", "we", "i", "be", "do",
    "can", "not", "no", "so", "up", "out", "about", "into", "get", "if",
}


# --------------------------------------------------------------------------- #
# JSON helpers
# --------------------------------------------------------------------------- #

def _extract_yt_json(html: str, key: str) -> dict[str, Any]:
    """Pull a top-level `var key = {...};` JSON blob out of a YouTube page.

    Tolerates escaped prefixes and unknown trailing bytes via raw_decode.
    """
    marker = f'"{key}":'
    idx = html.find(marker)
    if idx == -1:
        marker = f"var {key} = "
        idx = html.find(marker)
        if idx == -1:
            return {}
        idx += len(marker)
        raw = html[idx:]
    else:
        idx += len(marker)
        raw = html[idx:]
    try:
        obj, _ = json.JSONDecoder().raw_decode(raw.lstrip())
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    return {}


def _fetch(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(
        url, headers={
            "User-Agent": _USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
            "Cookie": "CONSENT=YES+cb; SOCS=CAI",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def _walk_texts(obj: Any) -> list[str]:
    """Collect every human-readable text node from a ytInitialData blob."""
    out: list[str] = []
    if isinstance(obj, dict):
        if "simpleText" in obj and isinstance(obj["simpleText"], str):
            out.append(obj["simpleText"])
        runs = obj.get("runs")
        if isinstance(runs, list):
            out.append("".join(r.get("text", "") for r in runs if isinstance(r, dict)))
        for v in obj.values():
            out.extend(_walk_texts(v))
    elif isinstance(obj, list):
        for v in obj:
            out.extend(_walk_texts(v))
    return [t for t in (s.strip() for s in out) if t]


def _first_match(obj: Any, dataclass_key: str, pattern: str) -> str:
    """First walked text matching a regex."""
    # cheap targeted search in raw JSON text is unreliable across layouts;
    # walk structured text nodes instead.
    texts = _walk_texts(obj)
    rx = re.compile(pattern)
    for t in texts:
        if dataclass_key in t or rx.search(t):
            m = rx.search(t)
            if m:
                return m.group(0)
    return ""


# --------------------------------------------------------------------------- #
# Parsing helpers
# --------------------------------------------------------------------------- #

def parse_duration(text: str) -> int:
    """"12:34" / "1:02:03" -> seconds; 0 if unparseable."""
    parts = [p for p in text.strip().split(":") if p.isdigit()]
    if not parts or len(parts) > 3:
        return 0
    secs = 0
    for p in parts:
        secs = secs * 60 + int(p)
    return secs


def parse_relative_ago(text: str) -> float:
    """"3 weeks ago" / "11h ago" -> approx days (0.0 if unparseable)."""
    m = re.search(
        r"(\d+)\s*"
        r"(seconds?|secs?|minutes?|mins?|hours?|hrs?|days?|weeks?|months?|years?|"
        r"s|m|h|d|w)\s+ago", text, re.I)
    if not m:
        return 0.0
    n = int(m.group(1))
    unit = m.group(2).lower()[0] if len(m.group(2)) <= 1 else m.group(2).lower()
    unit_days = {
        "s": 1 / 86400, "m": 1 / 1440, "h": 1 / 24, "d": 1, "w": 7, "y": 365.25,
        "second": 1 / 86400, "sec": 1 / 86400, "minute": 1 / 1440, "min": 1 / 1440,
        "hour": 1 / 24, "hr": 1 / 24, "day": 1, "week": 7, "month": 30.44,
        "year": 365.25,
    }
    return n * unit_days.get(unit, 0.0)


def parse_compact_number(text: str) -> int:
    """"1.2M views" / "3,417" -> int (0 if unparseable)."""
    m = re.search(r"([\d.,]+)\s*([KMB]?)", text)
    if not m:
        return 0
    try:
        val = float(m.group(1).replace(",", ""))
    except ValueError:
        return 0
    return int(val * {"": 1, "K": 1_000, "M": 1_000_000, "B": 1_000_000_000}[m.group(2)])


def title_patterns(titles: list[str]) -> dict[str, Any]:
    """Surface the channel's recurring title techniques."""
    n = len(titles)
    if n == 0:
        return {}
    rx_number = re.compile(r"^\W*\d+\b")
    rx_caps = re.compile(r"\b[A-Z]{2,}\b")
    rx_emoji = re.compile(
        "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F02F]", re.UNICODE
    )
    rx_hook = re.compile(r"^(how to|why|the (best|worst|truth)|i |we |you )\b", re.I)
    stat = {
        "samples": n,
        "avg_title_chars": round(statistics.mean(len(t) for t in titles), 1),
        "starts_with_number": sum(1 for t in titles if rx_number.search(t)) / n,
        "uses_question": sum(1 for t in titles if "?" in t) / n,
        "uses_all_caps_word": sum(1 for t in titles if rx_caps.search(t)) / n,
        "uses_emoji": sum(1 for t in titles if rx_emoji.search(t)) / n,
        "uses_hook_prefix": sum(1 for t in titles if rx_hook.match(t)) / n,
    }
    ratios = [k for k in stat if k not in ("samples", "avg_title_chars")]
    stat["dominant_pattern"] = max(ratios, key=lambda k: stat[k]) if ratios else ""
    # repeated leading bigrams - recurring formats like "I built ..." / "Why X"
    tok = re.compile(r"[A-Za-z0-9']+")
    lead = Counter(
        "_".join(tok.findall(t.lower())[:2])
        for t in titles if len(tok.findall(t)) >= 2
    )
    stat["repeated_leading_two_words"] = [
        {"two_words": k.replace("_", " "), "count": c}
        for k, c in lead.most_common(5) if c >= 2
    ]
    return stat


def topic_terms(titles: list[str], descriptions: list[str], top: int = 12) -> list[dict[str, Any]]:
    """Top content words + bigrams across titles and descriptions."""
    words: Counter = Counter()
    bigrams: Counter = Counter()
    for text in titles + descriptions:
        toks = [w.lower() for w in re.findall(r"[A-Za-z0-9']+", text)
                if w.lower() not in _STOPWORDS and len(w) > 2]
        words.update(toks)
        bigrams.update(f"{a} {b}" for a, b in zip(toks, toks[1:]))
    merged = words.most_common(top * 2)
    return [
        {"term": t, "count": c}
        for t, c in merged[:top]
    ], [
        {"term": t, "count": c}
        for t, c in bigrams.most_common(top) if c >= 2
    ]


def parse_chapters(description: str) -> list[dict[str, Any]]:
    """Chapter lines in a description: '0:00 Intro' -> [{time, label}]."""
    chapters: list[dict[str, Any]] = []
    for line in description.splitlines():
        m = re.search(r"\(?(?:(\d{1,2}):)?(\d{1,2}):(\d{2})\)?\s*[-–—|:]?\s*(.+)", line)
        if not m or not m.group(4).strip():
            continue
        secs = (int(m.group(1) or 0) * 3600) + int(m.group(2)) * 60 + int(m.group(3))
        if secs == 0 and not m.group(1) and chapters:
            continue  # stray "00:00" mid-list coverage
        chapters.append({"time_sec": secs, "label": m.group(4).strip()})
    return chapters


# --------------------------------------------------------------------------- #
# Dataclasses
# --------------------------------------------------------------------------- #

@dataclass
class VideoAnalysis:
    video_id: str
    url: str = ""
    title: str = ""
    channel: str = ""
    channel_url: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    view_count: int = 0
    like_count: str = ""
    publish_date: str = ""      # ISO date, from microformat
    duration_sec: int = 0
    category: str = ""
    chapters: list[dict[str, Any]] = field(default_factory=list)
    thumbnails: list[str] = field(default_factory=list)
    transcript: str = ""
    transcript_segments: list[dict[str, Any]] = field(default_factory=list)
    naming: str = ""            # which fields failed to resolve, for the agent
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass
class ChannelVideo:
    video_id: str
    title: str
    duration_sec: int = 0
    published_ago_days: float = 0.0
    published_text: str = ""
    views: int = 0
    views_text: str = ""
    thumbnail: str = ""
    url: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass
class ChannelProfile:
    source: str                     # handle or URL as given
    channel_id: str = ""
    name: str = ""
    handle: str = ""
    url: str = ""
    description: str = ""
    subscriber_text: str = ""
    video_count_text: str = ""
    avatar: str = ""
    sampled_videos: list[ChannelVideo] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)
    title_patterns: dict[str, Any] = field(default_factory=dict)
    topics: dict[str, Any] = field(default_factory=dict)
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = dict(self.__dict__)
        d["sampled_videos"] = [v.to_dict() for v in self.sampled_videos]
        return d


# --------------------------------------------------------------------------- #
# Tool
# --------------------------------------------------------------------------- #

class ChannelAnalysisTool(BaseTool):
    name = "channel_analysis"
    capability = "channel_analysis"
    provider = "youtube-scrape"
    description = (
        "Deconstruct one YouTube channel or video: metadata, tags, transcript "
        "with timestamps, chapters, thumbnails, channel cadence/duration/view "
        "stats, title patterns and topics, plus optional frame sampling for "
        "scene/animation analysis. Inspiration-only input for channel profiles "
        "and mined video ideas - never for copying."
    )
    tier = ToolTier.ANALYZE
    runtime = ToolRuntime.API
    dependencies: list[str] = []   # core analysis is keyless HTTP; frames need yt-dlp+ffmpeg
    agent_skills = ["creative/channel-profiling", "creative/idea-mining"]
    input_schema = {
        "type": "object",
        "properties": {
            "mode": {"type": "string", "enum": ["video", "channel", "frames"]},
            "url": {"type": "string", "description": "Video URL/ID, channel URL/@handle, or video for frames."},
            "include_transcript": {"type": "boolean", "default": True},
            "max_videos": {"type": "integer", "default": 15},
            "timestamps_sec": {"type": "array", "items": {"type": "number"}},
            "out_dir": {"type": "string"},
        },
        "required": ["mode", "url"],
    }
    output_schema = {
        "type": "object",
        "properties": {
            "video": {"type": "object"},
            "channel": {"type": "object"},
            "frames": {"type": "array"},
        },
    }

    def __init__(self) -> None:
        self._yts = YouTubeSourceTool()

    def health(self) -> dict[str, Any]:
        missing = [d for d in ("yt-dlp", "ffmpeg") if _which(d) is None]
        return {
            "status": "available",
            "missing_dependencies": [],
            "notes": "core analysis is keyless HTTP; frame sampling limited without: " + (", ".join(missing) or "none"),
            "frames_available": not missing,
        }

    # ------------------------------- video ------------------------------ #

    def analyze_video(self, url: str, include_transcript: bool = True) -> VideoAnalysis:
        a = VideoAnalysis(video_id=self._yts._extract_id(url))
        if not a.video_id:
            a.error = "could not extract video id"
            return a
        a.url = f"https://www.youtube.com/watch?v={a.video_id}"

        oe = self._yts._oembed(a.video_id)
        if "error" not in oe:
            a.title = oe.get("title", "")
            a.channel = oe.get("author_name", "")
            a.channel_url = oe.get("author_url", "")
            a.thumbnails.append(oe.get("thumbnail_url", ""))

        try:
            html = _fetch(a.url)
            pr = _extract_yt_json(html, "ytInitialPlayerResponse")
            vf = pr.get("videoDetails", {}) or {}
            mf = (pr.get("microformat", {}) or {}).get("playerMicroformatRenderer", {}) or {}
            a.title = a.title or vf.get("title", "")
            a.channel = a.channel or vf.get("author", "")
            a.channel_url = a.channel_url or f"https://www.youtube.com/{vf.get('externalChannelId', '')}"
            a.description = ((mf.get("description") or {}).get("simpleText", "")) or a.description
            if not a.description:
                m = re.search(r'"shortDescription":"(.*?)"(,"isCrawlable|$)', html, re.DOTALL)
                if m:
                    a.description = m.group(1).encode("utf-8").decode("unicode_escape")
            a.tags = list(vf.get("keywords", []))
            a.view_count = int(vf.get("viewCount", 0) or 0)
            a.like_count = _like_count_from_html(html)
            a.publish_date = mf.get("publishDate", "") or mf.get("uploadDate", "")
            a.duration_sec = int(mf.get("lengthSeconds", "0") or 0)
            a.category = mf.get("category", "")
            ths = mf.get("thumbnail", {}).get("thumbnails", []) or []
            for t in ths:
                u = t.get("url", "")
                if u and u not in a.thumbnails:
                    a.thumbnails.append(u)
            for suffix in ("maxresdefault", "sddefault", "hqdefault"):
                u = f"https://i.ytimg.com/vi/{a.video_id}/{suffix}.jpg"
                if u not in a.thumbnails:
                    a.thumbnails.append(u)
            a.chapters = parse_chapters(a.description)
        except Exception as e:  # keep partial data, note the failure
            a.naming = f"watch-page scrape failed: {e}"

        if include_transcript:
            text, segs = self._yts._transcript(a.video_id)
            a.transcript = text
            a.transcript_segments = segs

        missing = [f for f in ("title", "description", "publish_date") if not getattr(a, f)]
        if missing:
            a.naming = (a.naming + "; " if a.naming else "") + "missing: " + ", ".join(missing)
        return a

    # ------------------------------ channel ----------------------------- #

    def analyze_channel(self, source: str, max_videos: int = 15) -> ChannelProfile:
        p = ChannelProfile(source=source)
        path = self._canonical_channel_path(source)
        if not path:
            p.error = "could not normalize channel handle/URL"
            return p
        p.url = f"https://www.youtube.com{path}"
        try:
            html = _fetch(p.url + "/videos?hl=en")
        except Exception as e:
            p.error = f"channel fetch failed: {e}"
            return p

        meta = _extract_yt_json(html, "ytInitialData")
        chan_meta = _extract_yt_json(html, "ytInitialPlayerResponse")  # channel pages often lack it
        if not meta and not chan_meta:
            p.error = "no ytInitialData on channel page (consent wall or layout change)"
            return p
        cmr = _find_key(meta, "channelMetadataRenderer")
        if isinstance(cmr, dict):
            p.channel_id = cmr.get("externalId", "")
            p.name = cmr.get("title", "")
            p.description = cmr.get("description", "")
            vanity = cmr.get("vanityChannelUrl", "")
            p.handle = vanity.rsplit("/", 1)[-1] if vanity else ""
            av = cmr.get("avatar", {}).get("thumbnails", []) or []
            p.avatar = max(av, key=lambda t: t.get("width", 0)).get("url", "") if av else ""
        head = _find_key(meta, "pageHeaderRenderer") or _find_key(meta, "c4TabbedHeaderRenderer")
        if isinstance(head, dict):
            texts = _walk_texts(head)
            if not p.name:
                p.name = next((t for t in texts if t and not any(
                    c.isdigit() for c in t) and "subscriber" not in t.lower() and "video" not in t.lower()), "")
            p.subscriber_text = _regex_first(texts, r"[\d.,]+[KMB]?\s+subscribers?")
            p.video_count_text = _regex_first(texts, r"[\d.,]+[KMB]?\s+videos?")

        p.sampled_videos = _grid_videos(meta, cap=max_videos)
        if not p.sampled_videos:
            p.error = "no videos parsed from the Videos tab (layout change?)"
            return p

        p.stats = _channel_stats(p.sampled_videos)
        titles = [v.title for v in p.sampled_videos]
        descriptions = [p.description]  # channel description frames the topics
        terms, bigrams = topic_terms(titles, descriptions)
        p.title_patterns = title_patterns(titles)
        p.topics = {"top_terms": terms, "top_bigrams": bigrams}
        return p

    @staticmethod
    def _canonical_channel_path(source: str) -> str:
        s = source.strip()
        if re.fullmatch(r"@[A-Za-z0-9._-]+", s):
            return f"/{s}"
        m = re.search(r"youtube\.com(/(?:@[^/?#]+|/channel/[^/?#]+|/c/[^/?#]+|/user/[^/?#]+))", s)
        if m:
            return m.group(1)
        if re.fullmatch(r"UC[A-Za-z0-9_-]{22}", s):
            return f"/channel/{s}"
        if re.fullmatch(r"[A-Za-z0-9._-]{3,}", s) and " " not in s:
            return f"/@{s.lstrip('@')}"
        return ""

    # ------------------------------ frames ------------------------------ #

    _FRAMES_DEPS = ("yt-dlp", "ffmpeg")

    def frames_available(self) -> bool:
        return all(_which(d) for d in self._FRAMES_DEPS)

    def sample_frames(self, url: str, timestamps_sec: list[float], out_dir: str,
                      width: int = 640) -> dict[str, Any]:
        """Download a low-res copy of the video and extract stills at timestamps.

        Used for scene/animation STYLE analysis (text overlays, palette, motion
        density) - the frames are for the deconstruction, never to be reused as
        assets in a produced video.
        """
        if not self.frames_available():
            return {"ok": False, "error": "frame sampling needs yt-dlp + ffmpeg on PATH"}
        vid = self._yts._extract_id(url) or url
        d = Path(out_dir)
        d.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp:
            dl = run([
                _which("yt-dlp"), "-f", "best[height<=480][vcodec^=avc]/best[height<=480]/best",
                "--no-playlist", "-o", str(Path(tmp) / "src.mp4"),
                f"https://www.youtube.com/watch?v={vid}", "--quiet",
            ], timeout=600)
            if not dl["ok"] or not (Path(tmp) / "src.mp4").exists():
                return {"ok": False, "error": "yt-dlp download failed", "stderr": dl.get("stderr", "")[-500:]}
            src = str(Path(tmp) / "src.mp4")
            frames: list[str] = []
            for i, ts in enumerate(timestamps_sec):
                out = str(d / f"frame-{i + 1:02d}-t{int(ts)}s.jpg")
                r = run([
                    _which("ffmpeg"), "-y", "-ss", f"{float(ts):.2f}", "-i", src,
                    "-frames:v", "1", "-vf", f"scale={width}:-1", out,
                ], timeout=60)
                if r["ok"]:
                    frames.append(out)
            return {"ok": bool(frames), "frames": frames,
                    "requested": len(timestamps_sec), "extracted": len(frames)}

    # ------------------------------ execute ----------------------------- #

    def execute(self, mode: str, url: str, include_transcript: bool = True,
                max_videos: int = 15, timestamps_sec: list[float] | None = None,
                out_dir: str | None = None) -> dict[str, Any]:
        if mode == "video":
            a = self.analyze_video(url, include_transcript=include_transcript)
            return {"ok": not a.error, "naming": a.naming, **a.to_dict()}
        if mode == "channel":
            p = self.analyze_channel(url, max_videos=max_videos)
            return {"ok": not p.error, **p.to_dict()}
        if mode == "frames":
            if not out_dir:
                return {"ok": False, "error": "out_dir required for frames mode"}
            return self.sample_frames(url, timestamps_sec or [], out_dir)
        return {"ok": False, "error": f"unknown mode: {mode}"}


# --------------------------------------------------------------------------- #
# Small shared utilities (module-level so tests can target them)
# --------------------------------------------------------------------------- #

def _which(binname: str) -> str | None:
    """Resolve a binary name to a path, without spamming shutil in hot paths."""
    import shutil
    return shutil.which(binname)


def _find_key(obj: Any, key: str) -> Any:
    """Depth-first find of the first dict value under `key`."""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = _find_key(v, key)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = _find_key(v, key)
            if r is not None:
                return r
    return None


def _regex_first(texts: list[str], pattern: str) -> str:
    rx = re.compile(pattern)
    for t in texts:
        m = rx.search(t)
        if m:
            return m.group(0)
    return ""


def _like_count_from_html(html: str) -> str:
    # likes live behind interactive endpoints now; grab the axis text if present
    m = re.search(r'expandedLikeCountIfLikedIndicator":"([^"]+)"', html)
    return m.group(1).replace("\\u0026", "&") if m else ""


def _channel_video_from_lockup(lockup: dict[str, Any]) -> ChannelVideo | None:
    """Parse a new-layout `lockupViewModel` item into a ChannelVideo.

    YouTube's Videos tab has migrated from `videoRenderer` to this view model;
    both are supported so the tool keeps working during the transition.
    """
    vid = lockup.get("contentId", "")
    # watch-page long forms are exactly 11 chars; guard against playlists/other ids
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", vid or ""):
        return None
    meta_vm: Any = (_find_key(lockup, "lockupMetadataViewModel") or {})
    title = (meta_vm.get("title") or {}).get("content", "") if isinstance(meta_vm, dict) else ""

    published_text, views_text = "", ""
    rows: Any = _find_key(meta_vm, "metadataRows") or []
    for row in rows if isinstance(rows, list) else []:
        for part in (row.get("metadataParts") or []):
            text = (part.get("text") or {}).get("content", "")
            icon = ((part.get("leadingIcon") or {}).get("name") or "")
            if "PLAY_ARROW" in icon:
                views_text = text
            elif re.search(r"\bago\b", text.lower()):
                published_text = text

    duration = 0
    thumb_vm = ((lockup.get("contentImage") or {}).get("thumbnailViewModel")
                or _find_key(lockup, "thumbnailViewModel"))
    for overlay in ((thumb_vm or {}).get("overlays") or []):
        for badge in ((overlay.get("thumbnailBottomOverlayViewModel") or {}).get("badges") or []):
            dur_text = (badge.get("thumbnailBadgeViewModel") or {}).get("text", "")
            if re.fullmatch(r"[\d:]+", dur_text or ""):
                duration = parse_duration(dur_text)

    thumbs = ((thumb_vm or {}).get("image") or {}).get("sources") or []
    best = max(thumbs, key=lambda t: t.get("width", 0)) if thumbs else None

    cv = ChannelVideo(
        video_id=vid,
        title=title,
        duration_sec=duration,
        published_ago_days=parse_relative_ago(published_text) if published_text else 0.0,
        published_text=published_text,
        views=parse_compact_number(views_text) if views_text else 0,
        views_text=views_text,
        thumbnail=best.get("url", "") if best else "",
    )
    cv.url = f"https://www.youtube.com/watch?v={vid}"
    return cv


def _grid_videos(meta: dict[str, Any], cap: int) -> list[ChannelVideo]:
    """Walk the Videos tab grid for video items (current + legacy layouts)."""
    seen: list[str] = []
    videos: list[ChannelVideo] = []

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            lockup = node.get("lockupViewModel")
            if isinstance(lockup, dict):
                cv = _channel_video_from_lockup(lockup)
                if cv and cv.video_id not in seen:
                    seen.append(cv.video_id)
                    videos.append(cv)
                return  # nothing else of value inside a lockup item
            vr: Any = node.get("videoRenderer") or node.get("gridVideoRenderer")
            if not vr:
                ri = node.get("richItemRenderer")
                if isinstance(ri, dict):
                    vr = (ri.get("content") or {}).get("videoRenderer")
            if isinstance(vr, dict):
                vid = vr.get("videoId", "")
                if vid and vid not in seen:
                    seen.append(vid)
                    title_items = _walk_texts(vr.get("title") or {})
                    pub = _walk_texts(vr.get("publishedTimeText") or {})
                    view = _walk_texts(vr.get("viewCountText") or {})
                    length = _walk_texts(vr.get("lengthText") or {})
                    thumbs = (vr.get("thumbnail") or {}).get("thumbnails") or []
                    cv = ChannelVideo(
                        video_id=vid,
                        title=title_items[0] if title_items else "",
                        duration_sec=parse_duration(length[0]) if length else 0,
                        published_ago_days=parse_relative_ago(pub[0]) if pub else 0.0,
                        published_text=pub[0] if pub else "",
                        views=parse_compact_number(view[0]) if view else 0,
                        views_text=view[0] if view else "",
                        thumbnail=thumbs[-1].get("url", "") if thumbs else "",
                    )
                    cv.url = f"https://www.youtube.com/watch?v={vid}"
                    videos.append(cv)
            for v in node.values():
                visit(v)
        elif isinstance(node, list):
            for v in node:
                visit(v)

    visit(meta)
    return [v for v in videos][:cap]


def _channel_stats(videos: list[ChannelVideo]) -> dict[str, Any]:
    durs = [v.duration_sec for v in videos if v.duration_sec > 0]
    gaps: list[float] = []
    agos = sorted((v.published_ago_days for v in videos if v.published_ago_days > 0), reverse=True)
    for a, b in zip(agos, agos[1:]):
        gaps.append(a - b)
    avg_gap = statistics.mean(gaps) if gaps else 0.0
    staleness = statistics.mean(v.published_ago_days for v in videos if v.published_ago_days > 0) \
        if any(v.published_ago_days > 0 for v in videos) else 0.0
    views = sorted(v.views for v in videos if v.views > 0)
    median_views = statistics.median(views) if views else 0
    outliers = [v for v in videos if median_views and v.views >= 3 * median_views]
    return {
        "sampled": len(videos),
        "uploads_per_week": round(7 / avg_gap, 2) if avg_gap > 0.5 else 0.0,
        "avg_upload_gap_days": round(avg_gap, 1) if avg_gap else 0.0,
        "avg_published_ago_days": round(staleness, 1),
        "avg_duration_sec": round(statistics.mean(durs)) if durs else 0,
        "median_duration_sec": round(statistics.median(durs)) if durs else 0,
        "duration_spread_sec": {
            "min": min(durs), "max": max(durs)
        } if durs else {},
        "median_views": median_views,
        "view_range": {"min": min(views), "max": max(views)} if views else {},
        "outliers": [
            {"title": v.title, "url": v.url, "views": v.views, "views_multiple_of_median":
                round(v.views / median_views, 1) if median_views else 0}
            for v in outliers
        ],
    }


def _main() -> None:  # pragma: no cover
    import sys
    args = sys.argv[1:]
    tool = ChannelAnalysisTool()
    if not args:
        print("usage: python -m tools.channel_analysis video <url> | channel @handle [max] | frames <url> <outdir> t1,t2,...")
        return
    if args[0] == "video" and len(args) > 1:
        out = tool.execute("video", args[1])
    elif args[0] == "channel" and len(args) > 1:
        out = tool.execute("channel", args[1], max_videos=int(args[2]) if len(args) > 2 else 15)
    elif args[0] == "frames" and len(args) > 3:
        ts = [float(t) for t in args[3].split(",")]
        out = tool.execute("frames", args[1], timestamps_sec=ts, out_dir=args[2])
    else:
        return
    print(json.dumps(out, indent=2, ensure_ascii=False)[:6000])


if __name__ == "__main__":  # pragma: no cover
    _main()
