"""Contract tests for AI-News-Agent artifacts and tool registry."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from lib.checkpoint import DecisionLog, Progress, init_progress
from lib.config import Config
from lib.pipeline_loader import PipelineManifest, load_pipeline
from lib.paths import ROOT
from lib.playbook_loader import list_playbooks, load_playbook
from tools.tool_registry import ToolRegistry


# --------------------------------------------------------------------------- #
# Pipeline manifests
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("name", ["ai-news-short", "ai-news-long", "model-release"])
def test_pipeline_manifest_loads(name: str) -> None:
    m = load_pipeline(name)
    assert m.name == name
    assert m.stages, f"{name} has no stages"
    assert m.orchestration.get("skill"), f"{name} has no orchestration skill"
    for s in m.stages:
        assert s.skill.startswith("pipelines/"), f"{name} stage {s.name} has bad skill path"
        assert s.produces, f"{name} stage {s.name} produces nothing"


def test_pipeline_stage_order() -> None:
    m = load_pipeline("ai-news-short")
    names = m.stage_names()
    assert names[0] == "research"
    assert names[-1] == "publish"
    assert len(names) == 7


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #

def test_config_loads() -> None:
    c = Config.load()
    assert c.output.default_fps == 30
    assert c.budget.mode in {"observe", "warn", "cap"}


# --------------------------------------------------------------------------- #
# Playbooks
# --------------------------------------------------------------------------- #

def test_playbooks_load() -> None:
    names = list_playbooks()
    assert "flat-motion-graphics" in names
    pb = load_playbook("flat-motion-graphics")
    assert pb["name"] == "flat-motion-graphics"
    assert "palette" in pb


# --------------------------------------------------------------------------- #
# Tool registry
# --------------------------------------------------------------------------- #

def test_registry_discovers_tools() -> None:
    r = ToolRegistry()
    discovered = r.discover()
    assert "web_search" in discovered
    assert "browser_capture" in discovered
    assert "tts" in discovered
    assert "video_compose" in discovered
    assert "metadata" in discovered
    catalog = r.capability_catalog()
    assert "web_search" in catalog
    assert "tts" in catalog


def test_registry_support_envelope() -> None:
    r = ToolRegistry()
    r.discover()
    env = r.support_envelope()
    assert env["tts"]["capability"] == "tts"
    assert env["video_compose"]["capability"] == "video_compose"


def test_tts_health() -> None:
    from tools.tts import TTSTool
    h = TTSTool().health()
    assert h["status"] in {"available", "unavailable", "degraded"}


def test_web_search_executes() -> None:
    from tools.web_search import WebSearchTool
    out = WebSearchTool().execute("OpenAI GPT-5 launch", num_results=3)
    assert out["ok"] is True
    assert isinstance(out["results"], list)


# --------------------------------------------------------------------------- #
# Checkpoint / decision log
# --------------------------------------------------------------------------- #

def test_init_progress_creates_dirs(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    # Re-point ROOT by monkeypatching lib.paths.ROOT is already imported; use
    # the project_slug_dir helper which reads ROOT at call time.
    from lib import paths as pmod
    monkeypatch.setattr(pmod, "ROOT", tmp_path)
    prog = init_progress("test-slug", "ai-news-short", "test topic")
    assert prog.path().is_file()
    assert (tmp_path / "projects" / "test-slug" / "audio").is_dir()
    assert (tmp_path / "projects" / "test-slug" / "assets" / "raw").is_dir()


def test_decision_log_append_and_summary(tmp_path: Path, monkeypatch) -> None:
    from lib import paths as pmod
    monkeypatch.setattr(pmod, "ROOT", tmp_path)
    dl = DecisionLog("test-slug")
    dl.log("angle_selection", "Story angle", "the drop",
           options_considered=["the drop", "the comparison"],
           rejected_because="most surprising")
    dl.log("render_runtime", "Composition engine", "remotion")
    entries = dl.all_entries()
    assert len(entries) == 2
    assert entries[0].category == "angle_selection"
    assert "remotion" in dl.summary()


def test_decision_log_changed_choice_appends(tmp_path: Path, monkeypatch) -> None:
    from lib import paths as pmod
    monkeypatch.setattr(pmod, "ROOT", tmp_path)
    dl = DecisionLog("test-slug")
    dl.log("voice_selection", "Narration TTS provider", "edge-tts",
           options_considered=["edge-tts"])
    # A changed mid-run choice appends a NEW entry reusing category+subject.
    dl.log("voice_selection", "Narration TTS provider", "openai-tts",
           options_considered=["edge-tts"],
           rejected_because="user requested premium voice")
    entries = dl.all_entries()
    assert len(entries) == 2
    assert entries[0].decision == "edge-tts"
    assert entries[1].decision == "openai-tts"
    assert entries[1].category == entries[0].category
    assert entries[1].subject == entries[0].subject

# --------------------------------------------------------------------------- #
# B-roll tool
# --------------------------------------------------------------------------- #

def test_broll_registers() -> None:
    from tools.tool_registry import ToolRegistry
    r = ToolRegistry()
    r.discover()
    assert "broll" in r._tools
    assert r.get("broll").capability == "broll"


def test_broll_health() -> None:
    from tools.broll import BrollTool
    assert BrollTool().health()["status"] == "available"


def test_broll_search_returns_results() -> None:
    from tools.broll import BrollTool
    out = BrollTool().execute("AI data center server room", num_results=4)
    assert out["ok"] is True
    assert isinstance(out["results"], list)
    assert out["count"] == len(out["results"])
    for r in out["results"]:
        assert r["kind"] in {"image", "video", "social", "user"}
        assert r["url"]


def test_broll_catalogs_user_files(tmp_path: Path) -> None:
    from tools.broll import BrollTool
    src = tmp_path / "shot.png"
    src.write_bytes(b"\x89PNG\r\n\x1a\n")
    out = BrollTool().catalog_user_files([str(src)], str(tmp_path / "out"))
    assert len(out) == 1
    assert out[0].kind == "user"
    assert out[0].source_url == "user-supplied"
    assert out[0].local_path
    assert Path(out[0].local_path).is_file()


# --------------------------------------------------------------------------- #
# YouTube source tool
# --------------------------------------------------------------------------- #

def test_youtube_source_registers() -> None:
    from tools.tool_registry import ToolRegistry
    r = ToolRegistry()
    r.discover()
    assert "youtube_source" in r._tools
    assert r.get("youtube_source").capability == "youtube_source"


def test_youtube_source_health() -> None:
    from tools.youtube_source import YouTubeSourceTool
    assert YouTubeSourceTool().health()["status"] == "available"


def test_youtube_source_extract_id() -> None:
    from tools.youtube_source import YouTubeSourceTool
    cases = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        # Any 11-char [A-Za-z0-9_-] string is accepted as a video ID, since
        # YouTube IDs are exactly 11 characters.
        ("dQw4w9WgXcZ", "dQw4w9WgXcZ"),
        ("way-too-short", ""),
        ("way_too_long_to_be_a_video_id", ""),
    ]
    for url, expected in cases:
        assert YouTubeSourceTool._extract_id(url) == expected, url


def test_youtube_source_schema_shape() -> None:
    from tools.youtube_source import YouTubeSourceTool
    out = YouTubeSourceTool().input_schema
    assert out["properties"]["url"]["type"] == "string"
    assert "url" in out["required"]


# --------------------------------------------------------------------------- #
# JSON Schema validation (lib.reviewer)
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("artifact", [
    "research_brief", "proposal", "script", "storyboard",
    "asset_manifest", "render_report", "publish_log", "broll",
])
def test_schema_file_exists(artifact: str) -> None:
    from lib.paths import schemas_dir
    assert (schemas_dir() / f"{artifact}.json").is_file(), f"missing schema: {artifact}.json"


@pytest.mark.parametrize("artifact", [
    "research_brief", "proposal", "script", "storyboard",
    "asset_manifest", "render_report", "publish_log", "broll",
])
def test_schema_is_valid_json_schema(artifact: str) -> None:
    from jsonschema import Draft202012Validator
    from lib.reviewer import schema_for
    Draft202012Validator.check_schema(schema_for(artifact))


def test_reviewer_passes_valid_proposal(tmp_path: Path, monkeypatch) -> None:
    from lib import paths as pmod
    monkeypatch.setattr(pmod, "ROOT", tmp_path)
    from lib.reviewer import Reviewer
    instance = {
        "concept_options": [{"concept_id": "c1", "angle": "the drop", "why": "x"}],
        "selected_concept": "c1",
        "target_duration_sec": 60,
        "approval": {"status": "approved"},
    }
    result = Reviewer("s").check("proposal", instance)
    assert not result.has_blocker(), result.summary()


def test_reviewer_blocks_bad_proposal(tmp_path: Path, monkeypatch) -> None:
    from lib import paths as pmod
    monkeypatch.setattr(pmod, "ROOT", tmp_path)
    from lib.reviewer import Reviewer
    instance = {
        "concept_options": [{"concept_id": "c1", "angle": "x"}],
        "selected_concept": "nope",
        "target_duration_sec": 60,
    }
    result = Reviewer("s").check("proposal", instance)
    assert result.has_blocker(), "expected a BLOCKER"


def test_reviewer_blocks_schema_failure(tmp_path: Path, monkeypatch) -> None:
    from lib import paths as pmod
    monkeypatch.setattr(pmod, "ROOT", tmp_path)
    from lib.reviewer import Reviewer
    # Missing required 'beats' + 'total_duration_sec'
    result = Reviewer("s").check("script", {"beats": []})
    assert result.has_blocker(), "expected schema BLOCKER"


def test_reviewer_writes_review_md(tmp_path: Path, monkeypatch) -> None:
    from lib import paths as pmod
    monkeypatch.setattr(pmod, "ROOT", tmp_path)
    from lib.reviewer import Reviewer
    instance = {
        "concept_options": [{"concept_id": "c1", "angle": "x"}],
        "selected_concept": "c1",
        "target_duration_sec": 60,
    }
    result = Reviewer("myslug").check("proposal", instance)
    out = result.write_md()
    assert out.is_file()
    text = out.read_text(encoding="utf-8")
    assert "Review - proposal" in text
    assert "[PASS]" in text


# --------------------------------------------------------------------------- #
# Dual-engine composition (Remotion + HyperFrames)
# --------------------------------------------------------------------------- #

def test_hyperframe_compose_registers() -> None:
    from tools.tool_registry import ToolRegistry
    r = ToolRegistry()
    r.discover()
    assert "video_compose_hyperframes" in r._tools
    assert r.get("video_compose_hyperframes").provider == "hyperframes"


def test_hyperframe_compose_health() -> None:
    from tools.hyperframe_compose import HyperFrameComposeTool
    assert HyperFrameComposeTool().health()["status"] in {"available", "unavailable", "degraded"}


def test_engine_selector_heuristics() -> None:
    from lib.engine_selector import CompositionEngine, recommend_engine, resolve_engine
    # Explicit override wins.
    assert resolve_engine({"type": "card", "engine": "hyperframes"}) == "hyperframes"
    assert resolve_engine({"type": "card", "engine": "remotion"}) == "remotion"
    # Heuristic fallback: web/media/social -> hyperframes, everything else -> remotion
    assert recommend_engine({"type": "web"}) == CompositionEngine.HYPERFRAMES.value
    assert recommend_engine({"type": "media"}) == CompositionEngine.HYPERFRAMES.value
    assert recommend_engine({"type": "social"}) == CompositionEngine.HYPERFRAMES.value
    assert recommend_engine({"type": "card"}) == CompositionEngine.REMOTION.value


def test_engine_selector_health() -> None:
    from lib.engine_selector import health
    h = health()
    assert "remotion" in h and "hyperframes" in h
    for v in h.values():
        assert "available" in v and "missing_dependencies" in v


def test_engine_selector_missing_source(tmp_path: Path, monkeypatch) -> None:
    from lib import paths as pmod
    monkeypatch.setattr(pmod, "ROOT", tmp_path)
    from lib.engine_selector import render_scene
    # No authored source file exists yet -> render fails cleanly with an error.
    out = render_scene({"id": "hook", "type": "card", "engine": "remotion"}, "myslug")
    assert out["ok"] is False
    assert "error" in out
    assert out["engine"] == "remotion"
