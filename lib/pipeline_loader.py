"""Loader for pipeline_defs/*.yaml manifests."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from lib.paths import pipeline_dir


@dataclass
class StageDef:
    name: str
    skill: str
    produces: list[str] = field(default_factory=list)
    required_artifacts_in: list[str] = field(default_factory=list)
    optional_artifacts_in: list[str] = field(default_factory=list)
    tools_available: list[str] = field(default_factory=list)
    required_tools: list[str] = field(default_factory=list)
    optional_tools: list[str] = field(default_factory=list)
    checkpoint_required: bool = False
    human_approval_default: bool = False
    review_focus: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "StageDef":
        return cls(
            name=d.get("name", ""),
            skill=d.get("skill", ""),
            produces=list(d.get("produces", [])),
            required_artifacts_in=list(d.get("required_artifacts_in", [])),
            optional_artifacts_in=list(d.get("optional_artifacts_in", [])),
            tools_available=list(d.get("tools_available", [])),
            required_tools=list(d.get("required_tools", [])),
            optional_tools=list(d.get("optional_tools", [])),
            checkpoint_required=bool(d.get("checkpoint_required", False)),
            human_approval_default=bool(d.get("human_approval_default", False)),
            review_focus=list(d.get("review_focus", [])),
            success_criteria=list(d.get("success_criteria", [])),
        )


@dataclass
class PipelineManifest:
    name: str
    version: str
    description: str
    category: str = "generated"
    stability: str = "production"
    default_checkpoint_policy: str = "guided"
    required_skills: list[str] = field(default_factory=list)
    orchestration: dict[str, Any] = field(default_factory=dict)
    compatible_playbooks: dict[str, Any] = field(default_factory=dict)
    stages: list[StageDef] = field(default_factory=list)

    @classmethod
    def load(cls, name: str) -> "PipelineManifest":
        path = pipeline_dir() / f"{name}.yaml"
        if not path.is_file():
            raise FileNotFoundError(f"pipeline manifest not found: {path}")
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        stages = [StageDef.from_dict(s) for s in raw.get("stages", [])]
        return cls(
            name=raw.get("name", name),
            version=str(raw.get("version", "1.0")),
            description=raw.get("description", ""),
            category=raw.get("category", "generated"),
            stability=raw.get("stability", "production"),
            default_checkpoint_policy=raw.get("default_checkpoint_policy", "guided"),
            required_skills=list(raw.get("required_skills", [])),
            orchestration=dict(raw.get("orchestration", {})),
            compatible_playbooks=dict(raw.get("compatible_playbooks", {})),
            stages=stages,
        )

    @classmethod
    def list_all(cls) -> list[str]:
        return sorted(p.stem for p in pipeline_dir().glob("*.yaml"))

    def stage(self, name: str) -> StageDef:
        for s in self.stages:
            if s.name == name:
                return s
        raise KeyError(f"stage {name!r} not in pipeline {self.name}")

    def stage_names(self) -> list[str]:
        return [s.name for s in self.stages]


def load_pipeline(name: str) -> PipelineManifest:
    """Convenience loader used by the CLI / agent."""
    return PipelineManifest.load(name)