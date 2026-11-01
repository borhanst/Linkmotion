"""Load a visual style playbook from styles/*.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from lib.paths import styles_dir


def load_playbook(name: str) -> dict[str, Any]:
    path = styles_dir() / f"{name}.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"playbook not found: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    raw.setdefault("name", name)
    return raw


def list_playbooks() -> list[str]:
    return sorted(p.stem for p in styles_dir().glob("*.yaml"))


def get_playbook_for(pipeline: str) -> str:
    """Recommended playbook for a pipeline, from its manifest."""
    from lib.pipeline_loader import PipelineManifest
    m = PipelineManifest.load(pipeline)
    rec = m.compatible_playbooks.get("recommended") or []
    return rec[0] if rec else "clean-professional"


def main() -> int:  # pragma: no cover
    import json
    print("Playbooks:", ", ".join(list_playbooks()))
    print(json.dumps(load_playbook("flat-motion-graphics"), indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())