"""Inspiration library - the agent's personal bank of deconstructed references.

Storage (git-ignored, per user request): <root>/inspiration/<owner>/<slug>/
    inspiration.json   - validated record (schemas/inspiration.json)
    profile.md         - the deconstruction notes (agent-authored from analysis)
    analysis.json      - raw analysis output (channel/video analysis, raw probe)
    frames/            - sampled reference frames (never reused as video assets)

The inspiration folder is STANDALONE at the project root. Its single
manifest - inspiration/manifest.json - lists every entry across all users;
the agent reads that manifest FIRST, picks what a stage needs (ratio / type /
tags / pipeline), then loads the matching folders:

    from lib.inspiration import load_for, read_manifest
    read_manifest()              # the quick table the LLM skims
    load_for(ratio="9:16", type="visual", best_for="ai-news-short")

Every user has MULTIPLE inspirations, and one analyzed source can yield SEVERAL
different inspirations (structure / visual / pacing / hooks / thumbnail / tone)
each with its own ratio (9-16 / 16-9 / 1-1). Loading is need-based:

Source kinds accepted at creation:
    video       - one YouTube video URL        (tools/channel_analysis)
    channel     - a YouTube channel URL        (tools/channel_analysis)
    raw         - a local video file           (ffprobe + ffmpeg frame sampling)
    description - free-text description of the style/technique wanted

IMPORTANT: everything here is INSPIRATION ONLY. Study the TECHNIQUE, never the
wording - run lib/originality.check() on anything derived before publishing.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema

from lib.paths import ROOT

INSPIRATION_DIR = ROOT / "inspiration"
SCHEMA_PATH = ROOT / "schemas" / "inspiration.json"
MANIFEST_NAME = "manifest.json"

SOURCE_KINDS = ("video", "channel", "raw", "description")
INSPIRATION_TYPES = ("full", "structure", "visual", "pacing", "hooks", "thumbnail", "tone")
RATIOS = ("9:16", "16:9", "1:1", "4:5", "auto")

_RATIO_ALIASES = {
    "9x16": "9:16", "16x9": "16:9", "1x1": "1:1", "4x5": "4:5", "vertical": "9:16",
    "horizontal": "16:9", "square": "1:1", "portrait": "9:16", "landscape": "16:9",
}


# --------------------------------------------------------------------------- #
# Paths & naming
# --------------------------------------------------------------------------- #

def root_dir() -> Path:
    """The git-ignored inspiration root: <root>/inspiration/ (standalone)."""
    return INSPIRATION_DIR


def default_owner() -> str:
    owner = os.environ.get("AI_NEWS_AGENT_USER", "").strip().lower()
    if owner:
        return _slug_token(owner)
    return _slug_token(os.environ.get("USER", "") or "local")


def slugify(text: str) -> str:
    """Kebab-case slug from arbitrary text (name / url / description)."""
    return _slug_token("-".join(_slug_words(text)))


def user_dir(owner: str, create: bool = False) -> Path:
    d = root_dir() / owner
    if create:
        d.mkdir(parents=True, exist_ok=True)
    return d


def _slug_words(text: str) -> list[str]:
    # strip URLs down to their path words so links make readable slugs
    cleaned = text
    if "://" in text:
        cleaned = "/".join(text.split("://", 1)[1].split("/")[1:]) or text
    raw = "".join(ch if ch.isalnum() or ch in "-_ " else " " for ch in cleaned)
    words: list[str] = []
    for w in raw.lower().split():
        token = _slug_token(w)
        if token:
            words.append(token)
    return words or ["inspiration"]


def _slug_token(text: str) -> str:
    slug = " ".join(text.split()).replace(" ", "-")
    return slug.strip("_-").lower()[:40] or "inspiration"


# --------------------------------------------------------------------------- #
# Manifest - the single list file the LLM reads to pick an inspiration
# --------------------------------------------------------------------------- #

def manifest_path() -> Path:
    return root_dir() / MANIFEST_NAME


def _root_rel(path: str | None, folder: str | None) -> str | None:
    """Resolve a stored path to a repo-root-relative location (LLM-readable)."""
    if not path:
        return None
    p = Path(path)
    if not p.is_absolute():
        candidate = Path(folder) / p if folder else p
        if candidate.is_file() or candidate.is_dir():
            p = candidate
    if p.is_file() or p.is_dir() or str(p).count("/") > 0:
        try:
            rel = p if p.is_absolute() else ROOT / str(p)
            return str(Path(rel).resolve().relative_to(ROOT))
        except ValueError:
            return str(p)
    return None


def read_manifest() -> list[dict[str, Any]]:
    """The entries list from inspiration/manifest.json ([] if not built yet)."""
    f = manifest_path()
    if not f.is_file():
        return []
    data = json.loads(f.read_text(encoding="utf-8"))
    return list(data.get("inspirations", []))


def update_manifest() -> list[dict[str, Any]]:
    """Rebuild inspiration/manifest.json from every user's records.

    One flat, LLM-readable list file with root-relative `profile`/`frames`
    pointers so the agent can go straight to what it needs.
    """
    entries: list[dict[str, Any]] = []
    for item in list_inspirations():
        record, folder = item["record"], item["folder"]
        entries.append({
            "owner": record["owner"],
            "slug": record["slug"],
            "name": record["name"],
            "source": record["source"],
            "ratio": record["ratio"],
            "type": record["type"],
            "tags": record.get("tags", []),
            "best_for": record.get("best_for", []),
            "linked_playbooks": record.get("linked_playbooks", []),
            "profile": _root_rel(record.get("profile_file"), folder)
                       or None,
            "analysis": _root_rel(record.get("analysis_file"), folder),
            "frames": _root_rel(record.get("frames_dir"), folder),
            "notes": record.get("notes", ""),
            "created": record.get("created", ""),
        })
    manifest = {
        "version": 1,
        "updated": _now_iso(),
        "purpose": "Inspiration bank manifest (git-ignored). READ THIS FIRST, "
                   "pick by need (ratio / type / tags / best_for), then open the "
                   "entry's `profile` and study the TECHNIQUE only - never copy "
                   "wording. Query programmatically via lib.inspiration.load_for().",
        "count": len(entries),
        "inspirations": entries,
    }
    manifest_path().write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return entries


# --------------------------------------------------------------------------- #
# Record CRUD
# --------------------------------------------------------------------------- #

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _validate_record(record: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=record, schema=schema)


def create(
    name: str,
    *,
    source_kind: str,
    source_ref: str = "",
    owner: str | None = None,
    ratio: str = "auto",
    type: str = "full",
    tags: list[str] | tuple[str, ...] = (),
    best_for: list[str] | tuple[str, ...] = (),
    linked_playbooks: list[str] | tuple[str, ...] = (),
    notes: str = "",
    slug: str | None = None,
    profile_file: str | Path | None = None,
    profile_text: str | None = None,
    analysis: dict[str, Any] | None = None,
    frames: str | Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Create one inspiration record folder.

    profile_file  - path to an existing deconstruction .md to link or copy in
    profile_text  - or write the profile from a string
    analysis      - raw analysis dict (saved as analysis.json)
    frames        - directory of reference frames to copy into frames/
    """
    if source_kind not in SOURCE_KINDS:
        raise ValueError(f"source_kind must be one of {SOURCE_KINDS}: {source_kind!r}")
    if type not in INSPIRATION_TYPES:
        raise ValueError(f"type must be one of {INSPIRATION_TYPES}: {type!r}")
    ratio = _normalize_ratio(ratio)

    owner = owner or default_owner()
    base_slug = slug or slugify(name)
    folder = user_dir(owner, create=True) / base_slug
    if folder.exists() and not overwrite:
        raise FileExistsError(f"inspiration exists: {folder} (use overwrite=True)")

    folder.mkdir(parents=True, exist_ok=True)
    record: dict[str, Any] = {
        "slug": base_slug,
        "owner": owner,
        "name": name or base_slug,
        "source": {"kind": source_kind, "ref": source_ref, "analyzed_at": _now_iso()},
        "ratio": ratio,
        "type": type,
        "tags": [t for t in tags if t],
        "best_for": [b for b in best_for if b],
        "linked_playbooks": [p for p in linked_playbooks if p],
        "notes": notes,
        "created": _now_iso(),
    }

    if profile_file is not None:
        src = Path(profile_file)
        if src.exists():
            shutil.copy(src, folder / "profile.md")
            record["profile_file"] = "profile.md"
        else:
            record["profile_file"] = str(src)
    if profile_text:
        profile_path = folder / "profile.md"
        record.setdefault("profile_file", "profile.md")
        profile_path.write_text(profile_text.rstrip() + "\n", encoding="utf-8")
    if analysis is not None:
        (folder / "analysis.json").write_text(
            json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")
        record["analysis_file"] = "analysis.json"
    if frames is not None and Path(frames).is_dir():
        shutil.copytree(frames, folder / "frames", dirs_exist_ok=True)
        record["frames_dir"] = "frames"
    elif frames is not None:
        record["frames_dir"] = str(frames)

    _validate_record(record)
    (folder / "inspiration.json").write_text(
        json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    update_manifest()
    return {"record": record, "folder": str(folder)}


def get(owner: str | None, slug: str) -> dict[str, Any] | None:
    """One record with its folder path, None if absent."""
    folder = user_dir(owner or default_owner()) / slug
    f = folder / "inspiration.json"
    if not f.is_file():
        return None
    record = json.loads(f.read_text(encoding="utf-8"))
    return {"record": record, "folder": str(folder)}


def list_inspirations(
    owner: str | None = None,
    ratio: str | None = None,
    type: str | None = None,
    tag: str | None = None,
    best_for: str | None = None,
) -> list[dict[str, Any]]:
    """All matching records (owner omitted = every user's library)."""
    returns: list[dict[str, Any]] = []
    roots: list[Path] = []
    if owner:
        roots.append(user_dir(owner))
    elif root_dir().is_dir():
        roots = [d for d in root_dir().iterdir() if d.is_dir()]
    for udir in roots:
        if not udir.is_dir():
            continue
        for folder in sorted(udir.iterdir()):
            f = folder / "inspiration.json"
            if not f.is_file():
                continue
            record = json.loads(f.read_text(encoding="utf-8"))
            if ratio and record.get("ratio") != _normalize_ratio(ratio):
                continue
            if type and record.get("type") != type:
                continue
            if tag and tag not in record.get("tags", []):
                continue
            if best_for and best_for not in record.get("best_for", []):
                continue
            returns.append({"record": record, "folder": str(folder)})
    return returns


# --------------------------------------------------------------------------- #
# Need-based loading
# --------------------------------------------------------------------------- #

def load_for(
    *,
    ratio: str | None = None,
    type: str | None = None,
    tags: list[str] | tuple[str, ...] = (),
    best_for: str | None = None,
    owner: str | None = None,
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Pick the inspirations that best match the need.

    Score: exact type +3, exact ratio +3 ("auto" adapts to anything +1),
    +2 per best_for hit, +1 per shared tag. Returns top `limit`.
    """
    candidates = list_inspirations(owner=owner)
    tags = [t for t in tags if t]
    scored: list[tuple[float, dict[str, Any]]] = []
    for item in candidates:
        record = item["record"]
        base = 0.0
        if type:
            base += 3.0 if record.get("type") == type else 0.0
        if ratio:
            base += (3.0 if record.get("ratio") == _normalize_ratio(ratio)
                     else 1.0 if record.get("ratio") == "auto" else 0.0)
        if best_for:
            base += 2.0 * sum(1 for b in record.get("best_for", []) if b == best_for)
        if tags:
            base += sum(1.0 for tag in record.get("tags", []) if tag in tags)
        if base <= 0.0:
            continue  # unrelated to this need - bonus points never rescue it
        score = base + (1.0 if record.get("linked_playbooks") else 0.0)
        scored.append((score, item))
    scored.sort(key=lambda pair: (-pair[0], pair[1]["record"]["slug"]))
    return [item for score, item in scored if score > 0.0][:limit]


# --------------------------------------------------------------------------- #
# Source analysis (video / channel / raw / description)
# --------------------------------------------------------------------------- #

def analyze(source_kind: str, source_ref: str, *,
            count: int = 6, max_videos: int = 8) -> dict[str, Any]:
    """Analyze a source and return raw material for deconstruction.

    The agent turns this output into different inspiration records (structure,
    visual, pacing, ...) each with its own ratio and tags.
    """
    if source_kind in ("video", "channel"):
        from tools.channel_analysis import ChannelAnalysisTool
        tool = ChannelAnalysisTool()
        mode = "video" if source_kind == "video" else "channel"
        # transcript only useful for a single video - keep channel mode fast
        result = tool.execute(mode=mode, url=source_ref, max_videos=max_videos)
        if source_kind == "video" and not result.get("transcript"):
            result = tool.execute(mode=mode, url=source_ref, include_transcript=True,
                                  max_videos=max_videos)
        return result
    if source_kind == "raw":
        return analyze_raw_video(source_ref, count=count)
    if source_kind == "description":
        return {"ok": True, "description": source_ref,
                "note": "deconstruction happens at authoring time"}
    raise ValueError(f"unknown source_kind: {source_kind!r}")


def analyze_raw_video(path: str | Path, count: int = 6,
                      out_dir: str | Path | None = None) -> dict[str, Any]:
    """Probe a local video file and grab `count` evenly-spaced frames.

    Frames are for style deconstruction ONLY - never reused as produced assets.
    """
    src = Path(path).expanduser()
    if not src.is_file():
        return {"ok": False, "error": f"file not found: {src}"}
    ffprobe = shutil.which("ffprobe")
    ffmpeg = shutil.which("ffmpeg")
    if not ffprobe or not ffmpeg:
        return {"ok": False, "error": "ffprobe/ffmpeg required for raw video analysis"}

    probe = subprocess.run(
        [ffprobe, "-v", "error", "-print_format", "json", "-show_entries",
         "format=duration", "-show_streams", str(src)],
        capture_output=True, text=True, timeout=60,
    )
    try:
        info = json.loads(probe.stdout or "{}")
    except json.JSONDecodeError:
        return {"ok": False, "error": f"ffprobe failed: {probe.stderr[-300:]}"}

    video = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), {})
    duration = float(info.get("format", {}).get("duration") or video.get("duration") or 0)
    width, height = int(video.get("width", 0)), int(video.get("height", 0))
    fps_text = video.get("r_frame_rate", "0/1")
    num, _, den = fps_text.partition("/")
    fps = float(num) / float(den or 1) if den and float(den) else 0.0

    frames: list[str] = []
    out = Path(out_dir) if out_dir else src.parent / f"{src.stem}-inspiration-frames"
    out.mkdir(parents=True, exist_ok=True)
    if duration > 0 and width and height:
        probes = [duration * (i + 0.5) / count for i in range(count)]
        for i, ts in enumerate(probes):
            target = out / f"frame_{i + 1:02d}_t{int(ts)}s.jpg"
            r = subprocess.run(
                [ffmpeg, "-y", "-ss", f"{ts:.2f}", "-i", str(src),
                 "-frames:v", "1", "-vf", "scale=640:-1", str(target)],
                capture_output=True, timeout=60,
            )
            if r.returncode == 0 and target.exists():
                frames.append(str(target))

    guess = _guess_ratio(width, height)
    return {"ok": True, "source": str(src), "duration_s": round(duration, 2),
            "width": width, "height": height, "fps": round(fps, 2),
            "ratio": f"{width}:{height}", "guessed_ratio": guess,
            "frame_count": len(frames), "frames": frames}


def _guess_ratio(width: int, height: int) -> str:
    if not width or not height:
        return "auto"
    aspect = width / height
    options = {9 / 16: "9:16", 16 / 9: "16:9", 1.0: "1:1", 4 / 5: "4:5"}
    return min(options.items(), key=lambda kv: abs(kv[0] - aspect))[1]


def _normalize_ratio(ratio: str) -> str:
    r = (ratio or "auto").strip().lower().replace("x", ":").replace(".", ":")
    if r in RATIOS:
        return r
    if r in _RATIO_ALIASES:
        return _RATIO_ALIASES[r]
    raise ValueError(f"ratio must be one of {RATIOS} or a common alias: {ratio!r}")


# --------------------------------------------------------------------------- #
# Convenience: create several inspirations from one analyzed source
# --------------------------------------------------------------------------- #

def create_split(
    name: str,
    *,
    source_kind: str,
    source_ref: str,
    splits: list[dict[str, Any]],
    owner: str | None = None,
    analysis: dict[str, Any] | None = None,
    frames: str | Path | None = None,
    overwrite: bool = False,
) -> list[dict[str, Any]]:
    """One analysis -> multiple inspiration records.

    Each split dict overrides: name, type, ratio, tags, best_for, notes,
    slug, profile_text. Common fields fall back to the top-level arguments.
    Example: create_split("WorldofAI", source_kind="channel", source_ref=url,
        splits=[{"type": "visual", "ratio": "16:9", ...},
                {"type": "structure", "ratio": "16:9", ...}])
    """
    created = []
    for split in splits:
        kw = dict(split)
        split_name = kw.pop("name", name)
        # multiple records from one source need distinct folders:
        # derive the slug from name + flavor when the split carries no slug
        kw.setdefault("slug", slugify(
            f"{split_name}-{kw.get('type', 'full')}-{kw.get('ratio', 'auto')}"))
        kw.setdefault("owner", owner)
        created.append(create(
            split_name,
            source_kind=source_kind,
            source_ref=source_ref,
            analysis=analysis,
            frames=frames,
            overwrite=overwrite,
            **kw,
        ))
    return created


# --------------------------------------------------------------------------- #
# CLI: python -m lib.inspiration <list|show|create|analyze>
# --------------------------------------------------------------------------- #

def _cli(argv: list[str]) -> int:
    import argparse
    import sys
    parser = argparse.ArgumentParser(
        prog="lib.inspiration",
        description="Inspiration library - bank of deconstructed references.",
    )
    sub = parser.add_subparsers(dest="command")

    p_list = sub.add_parser("list", help="list matching inspirations")
    p_list.add_argument("--owner")
    p_list.add_argument("--ratio")
    p_list.add_argument("--type")
    p_list.add_argument("--tag")
    p_list.add_argument("--best-for")
    p_list.add_argument("--json", action="store_true")

    p_show = sub.add_parser("show", help="show one inspiration record")
    p_show.add_argument("slug")
    p_show.add_argument("--owner")
    p_show.add_argument("--json", action="store_true")

    p_cr = sub.add_parser("create", help="register a new inspiration")
    p_cr.add_argument("name")
    p_cr.add_argument("--kind", required=True, choices=SOURCE_KINDS)
    p_cr.add_argument("--ref", default="", help="URL / file path / description text")
    p_cr.add_argument("--owner")
    p_cr.add_argument("--ratio", default="auto", choices=RATIOS)
    p_cr.add_argument("--type", default="full", choices=INSPIRATION_TYPES)
    p_cr.add_argument("--tag", action="append", default=[])
    p_cr.add_argument("--best-for", action="append", default=[])
    p_cr.add_argument("--playbook", action="append", default=[],
                      help="style playbook already derived from this inspiration")
    p_cr.add_argument("--profile", help="path to an existing profile .md")
    p_cr.add_argument("--analysis", help="path to analysis.json to embed")
    p_cr.add_argument("--frames", help="directory of frames to copy in")
    p_cr.add_argument("--note", default="")
    p_cr.add_argument("--slug")
    p_cr.add_argument("--overwrite", action="store_true")

    p_an = sub.add_parser("analyze", help="analyze a source without creating records")
    p_an.add_argument("--kind", required=True, choices=SOURCE_KINDS)
    p_an.add_argument("--ref", required=True)
    p_an.add_argument("--count", type=int, default=6, help="frames (raw video)")
    p_an.add_argument("--max-videos", type=int, default=8, help="channel mode")

    sub.add_parser("manifest", help="rebuild inspiration/manifest.json list file")

    a = parser.parse_args(argv if argv is not None else sys.argv[1:])
    if a.command == "list":
        items = list_inspirations(owner=a.owner, ratio=a.ratio, type=a.type,
                                  tag=a.tag, best_for=a.best_for)
        if a.json:
            print(json.dumps(items, indent=2, ensure_ascii=False))
            return 0
        print(f"{len(items)} inspiration(s) in {root_dir().relative_to(ROOT)}:\n")
        for item in items:
            r = item["record"]
            print(f"  {r['owner']}/{r['slug']}")
            print(f"    name:   {r['name']}")
            print(f"    source: {r['source']['kind']} {r['source']['ref'][:80]}")
            print(f"    ratio:  {r['ratio']}   type: {r['type']}")
            if r["tags"]:
                print(f"    tags:   {', '.join(r['tags'])}")
            if r["best_for"]:
                print(f"    best:   {', '.join(r['best_for'])}")
            print()
        return 0

    if a.command == "show":
        item = get(a.owner, a.slug)
        if item is None:
            print(f"not found: {a.slug}")
            return 1
        print(json.dumps(item, indent=2, ensure_ascii=False))
        return 0

    if a.command == "create":
        made = create(
            a.name,
            source_kind=a.kind,
            source_ref=a.ref,
            owner=a.owner,
            ratio=a.ratio,
            type=a.type,
            tags=a.tag,
            best_for=a.best_for,
            linked_playbooks=a.playbook,
            notes=a.note,
            slug=a.slug,
            profile_file=a.profile,
            analysis=(json.loads(Path(a.analysis).read_text(encoding="utf-8"))
                      if a.analysis else None),
            frames=a.frames,
            overwrite=a.overwrite,
        )
        rec = made["record"]
        print("[ok] created " + made["folder"])
        print(f"  name: {rec['name']}  ratio: {rec['ratio']}  type: {rec['type']}")
        return 0

    if a.command == "analyze":
        result = analyze(a.kind, a.ref, count=a.count, max_videos=a.max_videos)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    entries = update_manifest()
    if a.command == "manifest":
        print(f"[ok] wrote {manifest_path().relative_to(ROOT)} ({len(entries)} entries)")
        for e in entries:
            print(f"  {e['owner']}/{e['slug']}  ratio={e['ratio']}  type={e['type']}  "
                  f"best={','.join(e['best_for']) or '-'}")
        return 0

    parser.print_help()
    return 0


def main(argv: list[str] | None = None) -> int:  # pragma: no cover
    return _cli(argv)


if __name__ == "__main__":
    raise SystemExit(main())
