"""AI-News-Agent core infrastructure."""

from lib.checkpoint import DecisionEntry, DecisionLog, Progress, init_progress
from lib.config import Config, get_config
from lib.paths import ROOT, project_root, project_slug_dir
from lib.pipeline_loader import PipelineManifest, StageDef, load_pipeline

__all__ = [
    "ROOT", "project_root", "project_slug_dir",
    "Config", "get_config",
    "PipelineManifest", "StageDef", "load_pipeline",
    "Progress", "DecisionLog", "DecisionEntry", "init_progress",
]