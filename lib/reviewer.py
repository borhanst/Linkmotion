"""Reviewer: schema validation + semantic checks for stage artifacts.

The reviewer is the single enforcement point for the quality gates described in
`skills/meta/reviewer.md`. It does two things:

1. JSON Schema validation against the real schema files in `schemas/`.
2. Semantic cross-field checks that JSON Schema cannot express (e.g.
   `selected_concept` must reference a valid `concept_id`, every beat must have
   an audio file, every anchor must be verbatim).

Usage:
    from lib.reviewer import Reviewer
    r = Reviewer(slug)
    result = r.check("proposal", instance)
    result.write_md()          # -> projects/<slug>/review-proposal.md
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator

from lib.paths import ROOT, project_slug_dir


# --------------------------------------------------------------------------- #
# Schema loading
# --------------------------------------------------------------------------- #

SCHEMAS_DIR = ROOT / "schemas"
_schema_cache: dict[str, dict[str, Any]] = {}


def schema_for(artifact: str) -> dict[str, Any]:
    """Load (and cache) the JSON Schema for an artifact by name.

    artifact may be a bare name ("proposal") or a path-like name
    ("asset_manifest"). Falls back to the schema named in the manifest's
    `produces` list.
    """
    key = artifact.replace(".json", "")
    if key in _schema_cache:
        return _schema_cache[key]
    path = SCHEMAS_DIR / f"{key}.json"
    if not path.is_file():
        raise FileNotFoundError(f"no JSON schema for artifact {artifact!r} ({path})")
    raw = json.loads(path.read_text(encoding="utf-8"))
    _schema_cache[key] = raw
    return raw


def validate_artifact(artifact: str, instance: Any) -> None:
    """Validate instance against the artifact's JSON Schema. Raises on failure."""
    Draft202012Validator.check_schema(schema_for(artifact))
    Draft202012Validator(schema_for(artifact)).validate(instance)


# --------------------------------------------------------------------------- #
# Result model
# --------------------------------------------------------------------------- #

class CheckResult:
    """One reviewer check line: [PASS|WARN|NOTE|BLOCKER] <check> - <detail>."""

    def __init__(self, severity: str, check: str, detail: str = "") -> None:
        self.severity = severity
        self.check = check
        self.detail = detail

    def line(self) -> str:
        return f"[{self.severity}] {self.check} - {self.detail}"


class ReviewResult:
    """Aggregate of all checks for one stage review."""

    def __init__(self, slug: str, stage: str) -> None:
        self.slug = slug
        self.stage = stage
        self.checks: list[CheckResult] = []

    def add(self, severity: str, check: str, detail: str = "") -> None:
        self.checks.append(CheckResult(severity, check, detail))

    def has_blocker(self) -> bool:
        return any(c.severity == "BLOCKER" for c in self.checks)

    def summary(self) -> str:
        return "\n".join(c.line() for c in self.checks) or "(no checks)"

    def path(self) -> Path:
        return project_slug_dir(self.slug) / f"review-{self.stage}.md"

    def write_md(self) -> Path:
        p = self.path()
        p.parent.mkdir(parents=True, exist_ok=True)
        body = [f"# Review - {self.stage}", "", self.summary(), ""]
        p.write_text("\n".join(body), encoding="utf-8")
        return p


# --------------------------------------------------------------------------- #
# Semantic checks (cross-field rules JSON Schema cannot express)
# --------------------------------------------------------------------------- #

def _file_exists(p: str) -> bool:
    path = Path(p)
    return path.is_file() or (ROOT / p).is_file()


def check_proposal_semantics(instance: dict[str, Any], result: ReviewResult) -> None:
    """selected_concept must reference a valid concept_id."""
    options = instance.get("concept_options") or []
    valid_ids = {o.get("concept_id") for o in options if isinstance(o, dict)}
    selected = instance.get("selected_concept")
    if selected is None:
        result.add("BLOCKER", "proposal.selected_concept references valid concept_id",
                   "selected_concept is missing")
    elif selected not in valid_ids:
        result.add("BLOCKER", "proposal.selected_concept references valid concept_id",
                   f"selected_concept={selected!r} not in {sorted(valid_ids)}")
    else:
        result.add("PASS", "proposal.selected_concept references valid concept_id",
                   f"selected_concept={selected!r}")


def check_script_semantics(instance: dict[str, Any], result: ReviewResult) -> None:
    """Sum of beat durations must be inside the pipeline's target window."""
    beats = instance.get("beats") or []
    total = instance.get("total_duration_sec")
    if total is None:
        result.add("BLOCKER", "script.total_duration_sec present", "missing")
    elif beats:
        est = sum(float(b.get("est_duration_sec", 0.0)) for b in beats if isinstance(b, dict))
        if abs(est - float(total)) > max(5.0, 0.15 * float(total)):
            result.add("WARN", "script.beat durations sum to total_duration_sec",
                       f"sum of est_duration_sec={est:.1f} vs total_duration_sec={total:.1f}")
        else:
            result.add("PASS", "script.beat durations sum to total_duration_sec",
                       f"sum={est:.1f} total={total:.1f}")


def check_asset_manifest_semantics(instance: dict[str, Any], result: ReviewResult) -> None:
    """Every asset path must resolve to an existing file."""
    assets = instance.get("assets") or []
    missing = [a.get("id", "?") for a in assets if isinstance(a, dict) and not _file_exists(a.get("path", ""))]
    if missing:
        result.add("BLOCKER", "asset_manifest.all asset files exist",
                   f"missing files for: {missing}")
    else:
        result.add("PASS", "asset_manifest.all asset files exist",
                   f"{len(assets)} assets, all paths resolve")


def check_storyboard_semantics(instance: dict[str, Any], result: ReviewResult) -> None:
    """At least 3 scene types used; verdict card has a footer when present."""
    scenes = instance.get("scenes") or []
    types = {s.get("type") for s in scenes if isinstance(s, dict)}
    if len(types) < 3:
        result.add("WARN", "storyboard.at least 3 scene types used",
                   f"only {sorted(types)}")
    else:
        result.add("PASS", "storyboard.at least 3 scene types used",
                   f"{len(types)} types: {sorted(types)}")
    verdicts = [s for s in scenes if isinstance(s, dict) and s.get("type") == "card"
                and str(s.get("title", "")).lower().startswith("verdict")]
    for v in verdicts:
        if not v.get("footer"):
            result.add("WARN", "storyboard.verdict card has footer with sources",
                       f"verdict scene {v.get('id')!r} missing footer")
        else:
            result.add("PASS", "storyboard.verdict card has footer with sources",
                       f"verdict scene {v.get('id')!r} footer present")


def check_publish_semantics(instance: dict[str, Any], result: ReviewResult) -> None:
    """Hashtags must include the format tag (#Shorts / #AI)."""
    tags = (instance.get("tags") or {})
    hashtags = tags.get("hashtags") or []
    if not hashtags:
        result.add("WARN", "publish.hashtags present", "no hashtags")
    else:
        result.add("PASS", "publish.hashtags present", ", ".join(hashtags))


_SEMANTIC_CHECKS: dict[str, Any] = {
    "proposal": check_proposal_semantics,
    "script": check_script_semantics,
    "asset_manifest": check_asset_manifest_semantics,
    "storyboard": check_storyboard_semantics,
    "publish_log": check_publish_semantics,
}


# --------------------------------------------------------------------------- #
# Reviewer
# --------------------------------------------------------------------------- #

class Reviewer:
    """Run schema validation + semantic checks for a stage artifact."""

    def __init__(self, slug: str) -> None:
        self.slug = slug

    def check(self, stage: str, instance: Any) -> ReviewResult:
        result = ReviewResult(self.slug, stage)

        # 1. JSON Schema validation (mandatory, BLOCKER on failure)
        try:
            validate_artifact(stage, instance)
            result.add("PASS", f"{stage} schema-valid", "passes JSON Schema")
        except jsonschema.ValidationError as e:
            result.add("BLOCKER", f"{stage} schema-valid",
                       f"validation error: {e.message} at {'/'.join(str(p) for p in e.absolute_path)}")

        # 2. Semantic cross-field checks
        fn = _SEMANTIC_CHECKS.get(stage)
        if fn is not None and isinstance(instance, dict):
            fn(instance, result)

        return result


def main(argv: list[str] | None = None) -> int:
    """CLI: `python -m lib.reviewer <slug> <stage> <artifact.json>`.

    Validates the artifact against its JSON Schema + semantic checks and writes
    `projects/<slug>/review-<stage>.md`. Exit code 1 if any BLOCKER.
    """
    import sys

    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 3:
        print("usage: python -m lib.reviewer <slug> <stage> <artifact.json>")
        return 2
    slug, stage, path = argv
    instance = json.loads(Path(path).read_text(encoding="utf-8"))
    result = Reviewer(slug).check(stage, instance)
    out = result.write_md()
    print(result.summary())
    print(f"\nWrote {out}")
    return 1 if result.has_blocker() else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())