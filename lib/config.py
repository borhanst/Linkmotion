"""Loader for config.yaml - single source of truth for runtime settings."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from lib.paths import ROOT


@dataclass
class LLMConfig:
    provider: str = "anthropic"
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class BudgetConfig:
    mode: str = "warn"
    total_usd: float = 10.00
    reserve_pct: float = 0.10
    single_action_approval_usd: float = 0.50
    require_approval_for_new_paid_tool: bool = False


@dataclass
class CheckpointConfig:
    policy: str = "guided"
    storage_dir: str = "pipeline"


@dataclass
class OutputConfig:
    default_format: str = "mp4"
    default_codec: str = "libx264"
    default_audio_codec: str = "aac"
    default_resolution: str = "1920x1080"
    default_fps: int = 30
    default_crf: int = 23


@dataclass
class PathsConfig:
    pipeline_dir: str = "pipeline_defs"
    library_dir: str = "projects"
    styles_dir: str = "styles"
    skills_dir: str = "skills"
    output_dir: str = "out"


@dataclass
class Config:
    llm: LLMConfig = field(default_factory=LLMConfig)
    budget: BudgetConfig = field(default_factory=BudgetConfig)
    checkpoint: CheckpointConfig = field(default_factory=CheckpointConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)

    @classmethod
    def load(cls, path: Path | None = None) -> "Config":
        path = path or (ROOT / "config.yaml")
        if not path.is_file():
            return cls()
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return cls(
            llm=LLMConfig(**{k: v for k, v in (raw.get("llm") or {}).items() if k in LLMConfig.__dataclass_fields__}),
            budget=BudgetConfig(**{k: v for k, v in (raw.get("budget") or {}).items() if k in BudgetConfig.__dataclass_fields__}),
            checkpoint=CheckpointConfig(**{k: v for k, v in (raw.get("checkpoint") or {}).items() if k in CheckpointConfig.__dataclass_fields__}),
            output=OutputConfig(**{k: v for k, v in (raw.get("output") or {}).items() if k in OutputConfig.__dataclass_fields__}),
            paths=PathsConfig(**{k: v for k, v in (raw.get("paths") or {}).items() if k in PathsConfig.__dataclass_fields__}),
        )


def get_config() -> Config:
    return Config.load()