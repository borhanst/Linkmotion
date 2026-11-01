"""YouTube source tool.

Fetches a video's metadata (title, description, channel, duration, thumbnail)
via the oEmbed API and its auto-generated transcript via youtubetranscript.com.
No API key required.
"""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from tools.base_tool import BaseTool, ToolTier, ToolRuntime


@dataclass
class VideoInfo:
    video_id: str
    url: str
    title: str = ""
    channel: str = ""
    description: str = ""
    thumbnail: str = ""
    transcript: str = ""
    transcript_segments: list[dict[str, Any]] = field(default_factory=list)
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "video_id": self.video_id,
            "url": self.url,
            "title": self.title,
            "channel": self.channel,
            "description": self.description,
            "thumbnail": self.thumbnail,
            "transcript": self.transcript,
            "transcript_segments": self.transcript_segments,
            "error": self.error,
        }


class YouTubeSourceTool(BaseTool):
    name = "youtube_source"
    capability = "youtube_source"
    provider = "youtube-oembed"
    description = "Fetch a YouTube video's description and auto-generated transcript via keyless endpoints."
    tier = ToolTier.SOURCE
    runtime = ToolRuntime.API
    dependencies: list[str] = []
    agent_skills: list[str] = []
    input_schema = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "YouTube video URL or 11-char video ID."},
            "include_transcript": {"type": "boolean", "default": True},
        },
        "required": ["url"],
    }
    output_schema = {
        "type": "object",
        "properties": {
            "video_id": {"type": "string"},
            "title": {"type": "string"},
            "channel": {"type": "string"},
            "description": {"type": "string"},
            "transcript": {"type": "string"},
        },
    }

    def health(self) -> dict[str, Any]:
        return {"status": "available", "missing_dependencies": []}

    @staticmethod
    def _extract_id(url_or_id: str) -> str:
        s = url_or_id.strip()
        m = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})", s)
        if m:
            return m.group(1)
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
            return s
        return ""

    def _oembed(self, video_id: str) -> dict[str, Any]:
        url = "https://www.youtube.com/oembed?url=" + urllib.parse.quote(
            f"https://www.youtube.com/watch?v={video_id}", safe=""
        ) + "&format=json"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (ai-news-agent)"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8", errors="ignore"))
        except Exception as e:
            return {"error": str(e)}

    def _transcript(self, video_id: str) -> tuple[str, list[dict[str, Any]]]:
        # Try youtubetranscript.com (keyless)
        endpoints = [
            f"https://youtubetranscript.com/?server_vid={video_id}",
        ]
        text_parts: list[str] = []
        segments: list[dict[str, Any]] = []
        for ep in endpoints:
            req = urllib.request.Request(ep, headers={"User-Agent": "Mozilla/5.0 (ai-news-agent)"})
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    raw = resp.read().decode("utf-8", errors="ignore")
            except Exception:
                continue
            # Parse transcript lines: <text start=".." dur="..">...</text>
            for m in re.finditer(r'<text[^>]*start="([^"]*)"[^>]*dur="([^"]*)"[^>]*>(.*?)</text>', raw, re.DOTALL):
                seg_text = re.sub(r"<[^>]+>", "", m.group(3)).strip()
                if seg_text:
                    segments.append({"start": float(m.group(1)), "dur": float(m.group(2)), "text": seg_text})
                    text_parts.append(seg_text)
            if segments:
                break
        # Fallback: try the timedtext API
        if not segments:
            try:
                url = ("https://video.google.com/timedtext?lang=en&v=" + video_id)
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (ai-news-agent)"})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    raw = resp.read().decode("utf-8", errors="ignore")
                for m in re.finditer(r'<text[^>]*start="([^"]*)"[^>]*dur="([^"]*)"[^>]*>(.*?)</text>', raw, re.DOTALL):
                    seg_text = re.sub(r"<[^>]+>", "", m.group(3)).strip()
                    if seg_text:
                        segments.append({"start": float(m.group(1)), "dur": float(m.group(2)), "text": seg_text})
                        text_parts.append(seg_text)
            except Exception:
                pass
        return " ".join(text_parts), segments

    def fetch(self, url: str, include_transcript: bool = True) -> VideoInfo:
        vid = self._extract_id(url)
        info = VideoInfo(video_id=vid, url=url if vid else url)
        if not vid:
            info.error = "could not extract video id"
            return info
        info.url = f"https://www.youtube.com/watch?v={vid}"
        oe = self._oembed(vid)
        if "error" in oe:
            info.error = oe["error"]
        else:
            info.title = oe.get("title", "")
            info.channel = oe.get("author_name", "")
            info.thumbnail = oe.get("thumbnail_url", "")
        # Description is not in oEmbed; attempt to scrape from watch page
        try:
            req = urllib.request.Request(info.url, headers={"User-Agent": "Mozilla/5.0 (ai-news-agent)"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
            m = re.search(r'"shortDescription":"(.*?)"', html, re.DOTALL)
            if m:
                desc = m.group(1).encode("utf-8").decode("unicode_escape")
                info.description = desc
        except Exception:
            pass
        if include_transcript:
            t, segs = self._transcript(vid)
            info.transcript = t
            info.transcript_segments = segs
        return info

    def execute(self, url: str, include_transcript: bool = True) -> dict[str, Any]:
        info = self.fetch(url, include_transcript=include_transcript)
        return {"ok": not info.error or bool(info.title or info.transcript), **info.to_dict()}


def _main() -> None:  # pragma: no cover
    import sys
    u = sys.argv[1] if len(sys.argv) > 1 else "https://www.youtube.com/watch?v=T87R8PHWDpQ"
    print(json.dumps(YouTubeSourceTool().execute(u), indent=2, ensure_ascii=False)[:4000])


if __name__ == "__main__":  # pragma: no cover
    _main()
