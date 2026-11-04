"""CLI entry point: python -m ai_news_agent <command>.

Commands:
    preflight    - verify the tool registry + external render dependencies
    pipelines    - list available pipeline manifests from pipeline_defs/
    init         - scaffold projects/<slug>/ for a new video production

Run with no arguments for usage help.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys

from lib.checkpoint import init_progress
from lib.pipeline_loader import PipelineManifest


# --------------------------------------------------------------------------- #
# preflight
# --------------------------------------------------------------------------- #

def preflight() -> int:
    """Report tool availability + external render dependencies."""
    from tools.tool_registry import registry

    missing_externals: list[str] = []
    for exe in ("ffmpeg", "ffprobe"):
        if shutil.which(exe) is None:
            missing_externals.append(exe)
    for mod_check in ("playwright", "edge_tts", "yaml", "jsonschema"):
        try:
            __import__(mod_check)
        except ImportError:
            missing_externals.append(mod_check)

    registry.discover()

    print("== External dependencies ==")
    if missing_externals:
        for name in missing_externals:
            print(f"  [MISSING] {name}")
    else:
        print("  [ok] ffmpeg, ffprobe, playwright, edge-tts, pyyaml, jsonschema")

    print()
    print(registry.summary())

    unavailable = [t for t in registry.all_tools() if t.health()["status"] != "available"]
    ok = not unavailable and not missing_externals
    if not ok:
        print("\n[PREFLIGHT INCOMPLETE] resolve missing entries above.")
    else:
        print("\n[PREFLIGHT OK] all tools and dependencies available.")
    return 0 if ok else 1


# --------------------------------------------------------------------------- #
# pipelines
# --------------------------------------------------------------------------- #

def pipelines() -> int:
    """List every pipeline manifest and its stages."""
    names = PipelineManifest.list_all()
    print(f"Available pipelines ({len(names)}):\n")
    for name in names:
        m = PipelineManifest.load(name)
        stages = " -> ".join(m.stage_names()) or "(no stages)"
        print(f"  {m.name}  (v{m.version}, {m.stability})")
        print(f"    {m.description.strip()}")
        print(f"    stages: {stages}")
        rec = m.compatible_playbooks.get("recommended") or []
        if rec:
            print(f"    recommended styles: {', '.join(rec)}")
        print()
    return 0


# --------------------------------------------------------------------------- #
# init
# --------------------------------------------------------------------------- #

_SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def init(slug: str, pipeline: str, topic: str, source_url: str = "") -> int:
    """Scaffold projects/<slug>/ + progress.json for a new video."""
    if not _SLUG_RE.match(slug):
        print(f"error: slug must be kebab-case (a-z, 0-9, dashes): {slug!r}")
        return 2
    try:
        PipelineManifest.load(pipeline)
    except FileNotFoundError:
        print(f"error: unknown pipeline {pipeline!r}. Available:")
        print("  " + ", ".join(PipelineManifest.list_all()))
        return 2

    prog = init_progress(slug, pipeline, topic, source_url)
    print(f"[ok] project initialized: projects/{slug}/")
    print(f"  pipeline:    {pipeline}")
    print(f"  topic:       {topic}")
    print(f"  source:      {prog.source_type}" + (f" ({prog.source_ref})" if source_url else ""))
    print()
    print("Next steps (per AGENT_GUIDE.md):")
    print(f"  1. Read pipeline_defs/{pipeline}.yaml")
    print("  2. Run: python -m ai_news_agent preflight")
    print(f"  3. For each stage, read skills/pipelines/{pipeline}/<stage>-director.md BEFORE working")
    print(f"  4. After each stage: python -m lib.reviewer")
    print(f"  5. Checkpoint progress.json + ask approval when the stage requires it")
    return 0


# --------------------------------------------------------------------------- #
# parser
# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ai_news_agent",
        description="AI-News-Agent production CLI.",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("preflight", help="verify tools + dependencies")

    sub.add_parser("pipelines", help="list pipeline manifests")

    p_init = sub.add_parser("init", help="scaffold a new video project")
    p_init.add_argument("slug", help="kebab-case project slug (e.g. 2026-10-gpt5-short)")
    p_init.add_argument("pipeline", help="pipeline name from pipeline_defs/")
    p_init.add_argument("topic", help="topic / story / brief for the video")
    p_init.add_argument("source_url", nargs="?", default="", help="optional source URL (YouTube, blog, article)")

    args = parser.parse_args(argv)
    if args.command == "preflight":
        return preflight()
    if args.command == "pipelines":
        return pipelines()
    if args.command == "init":
        return init(args.slug, args.pipeline, args.topic, args.source_url)
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
