"""Resumable per-video state + append-only decision log.

The checkpoint is the single source of truth for "what's done" on a video when
the user switches sessions. The decision_log is append-only history (the
board's Decisions rail and the run's audit trail).
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from lib.paths import project_slug_dir


# --------------------------------------------------------------------------- #
# Progress
# --------------------------------------------------------------------------- #

@dataclass
class Progress:
    slug: str = ""
    pipeline: str = ""
    format: str = "short"          # short | long
    topic: str = ""
    source_type: str = "topic"     # topic | transcript | blog | url
    source_ref: str = ""
    stage: str = "intake"
    total_scenes: int | None = None
    current_scene: int = 0
    voice: str = ""
    palette: dict = field(default_factory=dict)
    notes: str = ""
    updated_at: str = ""

    def path(self) -> Path:
        return project_slug_dir(self.slug) / "progress.json"

    def save(self) -> None:
        self.updated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        p = self.path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, slug: str) -> "Progress":
        p = project_slug_dir(slug) / "progress.json"
        if not p.is_file():
            return cls(slug=slug)
        return cls(**{k: v for k, v in json.loads(p.read_text(encoding="utf-8")).items() if k in cls.__dataclass_fields__})


def init_progress(slug: str, pipeline: str, topic: str, source_ref: str = "") -> Progress:
    pr = project_slug_dir(slug)
    (pr / "audio").mkdir(parents=True, exist_ok=True)
    (pr / "assets" / "raw").mkdir(parents=True, exist_ok=True)
    (pr / "metadata").mkdir(parents=True, exist_ok=True)
    prog = Progress(
        slug=slug,
        pipeline=pipeline,
        topic=topic,
        source_type="url" if source_ref else "topic",
        source_ref=source_ref,
        stage="intake",
    )
    prog.save()
    return prog


# --------------------------------------------------------------------------- #
# Decision log (append-only)
# --------------------------------------------------------------------------- #

@dataclass
class DecisionEntry:
    category: str
    subject: str
    decision: str
    options_considered: list[str] = field(default_factory=list)
    rejected_because: str = ""
    confidence: str = "medium"      # low | medium | high
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DecisionLog:
    """Append-only audit trail. A changed mid-run choice appends a NEW entry
    reusing the same category + subject, with the superseded option moved into
    options_considered and rejected_because noting it was changed."""

    def __init__(self, slug: str):
        self.slug = slug
        self.path = project_slug_dir(slug) / "decision_log.jsonl"

    def append(self, entry: DecisionEntry) -> None:
        entry.timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")

    def log(self, category: str, subject: str, decision: str,
            options_considered: list[str] | None = None,
            rejected_because: str = "",
            confidence: str = "medium") -> None:
        self.append(DecisionEntry(
            category=category,
            subject=subject,
            decision=decision,
            options_considered=options_considered or [],
            rejected_because=rejected_because,
            confidence=confidence,
        ))

    def all_entries(self) -> list[DecisionEntry]:
        if not self.path.is_file():
            return []
        out: list[DecisionEntry] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            out.append(DecisionEntry(**{k: v for k, v in d.items() if k in DecisionEntry.__dataclass_fields__}))
        return out

    def summary(self) -> str:
        lines = []
        for e in self.all_entries():
            lines.append(f"- [{e.category}] {e.subject}: {e.decision}")
        return "\n".join(lines) if lines else "(no decisions recorded)"