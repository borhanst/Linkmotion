# AI News Agent - CLI entry point.

# Usage:
#   python -m ai_news_agent              # preflight + capability menu
#   python -m ai_news_agent preflight   # tool registry
#   python -m ai_news_agent pipelines   # list pipeline manifests
#   python -m ai_news_agent init <slug> <pipeline> "<topic>" [source_url]

from __future__ import annotations

import json
import sys
from pathlib import Path

from lib import paths
from lib.checkpoint import init_progress
from lib.config import get_config
from lib.pipeline_loader import PipelineManifest


def cmd_preflight() -> int:
    from tools.tool_registry import registry
    registry.discover()
    print(registry.summary())
    return 0


def cmd_pipelines() -> int:
    from lib.paths import pipeline_dir
    for p in sorted(pipeline_dir().glob("*.yaml")):
        m = PipelineManifest.load(p.stem)
        print(f"{m.name:<22} v{m.version:<6} {m.stability:<10} {len(m.stages)} stages - {m.description.splitlines()[0] if m.description else ''}")
    return 0


def cmd_init(slug: str, pipeline: str, topic: str, source_ref: str = "") -> int:
    m = PipelineManifest.load(pipeline)
    prog = init_progress(slug, pipeline, topic, source_ref)
    prog.format = "short" if "short" in pipeline else "long"
    prog.stage = "research"
    prog.total_scenes = len(m.stages)
    prog.save()
    print(f"Initialized project '{slug}' for pipeline '{pipeline}'.")
    print(f"  progress: {prog.path()}")
    print(f"  Next stage: research-director")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        print("Commands: preflight | pipelines | init <slug> <pipeline> <topic> [url]")
        return 0
    cmd = argv[0]
    if cmd == "preflight":
        return cmd_preflight()
    if cmd == "pipelines":
        return cmd_pipelines()
    if cmd == "init":
        if len(argv) < 4:
            print("usage: init <slug> <pipeline> <topic> [source_url]")
            return 2
        return cmd_init(argv[1], argv[2], argv[3], argv[4] if len(argv) > 4 else "")
    print(f"unknown command: {cmd}")
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())