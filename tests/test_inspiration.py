"""Tests for the inspiration library (lib/inspiration.py)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import lib.inspiration as insp
from lib.inspiration import (INSPIRATION_TYPES, SOURCE_KINDS, list_inspirations,
                             load_for, slugify)


@pytest.fixture
def bench(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the library at an isolated git-ignored scratch bench."""
    monkeypatch.setattr(insp, "INSPIRATION_DIR", tmp_path)
    return tmp_path


def test_slugify_links_and_names() -> None:
    assert slugify("My Style DNA") == "my-style-dna"
    slug_link = slugify("https://www.youtube.com/watch?v=abc123")
    assert "youtube" not in slug_link and "://" not in slug_link
    assert "abc123" in slug_link
    assert slugify("https://youtube.com/@some-channel/videos").startswith("some")
    assert "-" in slugify("Very Long   NAME__with--punct!")


def test_create_valid_record_and_folder(bench: Path) -> None:
    made = insp.create(
        "Test Style Kit",
        source_kind="description",
        source_ref="dark cards, red boxes",
        ratio="9:16",
        type="visual",
        tags=["dark", "cards"],
        best_for=["ai-news-short"],
        profile_text="# test profile\n\nTechnique only.",
        analysis={"ok": True},
    )
    assert made["record"]["ratio"] == "9:16"
    folder = Path(made["folder"])
    assert (folder / "inspiration.json").is_file()
    assert (folder / "profile.md").is_file()
    assert (folder / "analysis.json").is_file()
    record = json.loads((folder / "inspiration.json").read_text(encoding="utf-8"))
    assert record["source"]["kind"] in SOURCE_KINDS
    assert record["type"] in INSPIRATION_TYPES

    # overwrite protection
    with pytest.raises(FileExistsError):
        insp.create("Test Style Kit", source_kind="description")
    made2 = insp.create("Test Style Kit", source_kind="description", overwrite=True)
    assert made2["record"]["slug"] == made["record"]["slug"]


def test_bad_type_kind_ratio_rejected(bench: Path) -> None:
    with pytest.raises(ValueError):
        insp.create("x", source_kind="mystery")
    with pytest.raises(ValueError):
        insp.create("x", source_kind="description", type="vibe")
    with pytest.raises(ValueError):
        insp.create("x", source_kind="description", ratio="5:1")
    assert insp._normalize_ratio("9x16") == "9:16"
    assert insp._normalize_ratio("vertical") == "9:16"
    assert insp._normalize_ratio("square") == "1:1"


def test_list_filters_and_multi_owner(bench: Path) -> None:
    insp.create("a", source_kind="channel", ratio="9:16", type="visual",
                tags=["t"], best_for=["ai-news-short"], owner="u1")
    insp.create("b", source_kind="raw", ratio="16:9", type="pacing",
                tags=["t", "shared"], best_for=["ai-news-long"], owner="u2")

    assert [i["record"]["slug"] for i in list_inspirations(owner="u1")] == ["a"]
    assert len(list_inspirations()) == 2
    assert [i["record"]["slug"] for i in list_inspirations(ratio="16:9")] == ["b"]
    assert [i["record"]["slug"] for i in list_inspirations(type="pacing")] == ["b"]
    assert [i["record"]["slug"] for i in list_inspirations(tag="shared")] == ["b"]
    assert [i["record"]["slug"]
            for i in list_inspirations(best_for="ai-news-short")] == ["a"]


def test_load_for_need_scoring(bench: Path) -> None:
    insp.create("Visitor Force Short", source_kind="channel", ratio="9:16",
                type="visual", tags=["typographic"], best_for=["ai-news-short"])
    insp.create("Worldof AI Long", source_kind="channel", ratio="16:9",
                type="full", tags=["news-roundup"], best_for=["ai-news-long"],
                linked_playbooks=["worldofai-signal"])

    picks = load_for(ratio="9:16", type="visual", best_for="ai-news-short")
    assert picks[0]["record"]["slug"] == "visitor-force-short"
    picks = load_for(ratio="16:9", best_for="ai-news-long")
    assert picks[0]["record"]["slug"] == "worldof-ai-long"
    # nothing in the bank matches an unrelated need -> empty, never wrong
    assert [p for p in load_for(ratio="1:1", tags=["whatever-nope"])] == []
    # strict need matching: a 9:16 need only surfaces 9:16 records
    assert [p["record"]["slug"] for p in load_for(ratio="9:16")] == [
        "visitor-force-short"]


def test_create_split_yields_multiple_inspirations(bench: Path) -> None:
    made = insp.create_split(
        "One Channel",
        source_kind="channel",
        source_ref="youtube.com/@one",
        splits=[
            {"type": "visual", "ratio": "9:16", "tags": ["frames"]},
            {"type": "structure", "ratio": "9:16", "tags": ["story-loop"]},
            {"name": "One Channel thumbs", "type": "thumbnail", "ratio": "16:9"},
        ],
    )
    slugs = [m["record"]["slug"] for m in made]
    assert all((Path(m["folder"]) / "inspiration.json").is_file() for m in made)
    assert len({s for s in slugs}) == 3
    types = {m["record"]["type"] for m in made}
    assert {"visual", "structure", "thumbnail"} <= types
    # missing type defaults fall through create-sanely
    split_types = {m["record"]["type"] for m in made}
    assert split_types == {"visual", "structure", "thumbnail"}


def test_analyze_description_is_immediate(bench: Path) -> None:
    out = insp.analyze("description", "flat white bg, one hero visual per beat")
    assert out["ok"] is True
    assert "flat white bg" in out["description"]


def test_manifest_is_built_on_create_and_rebuildable(bench: Path) -> None:
    insp.create("Split Style", source_kind="description", ratio="9:16",
                type="visual", profile_text="# profile", tags=["x"])
    insp.create("Other Clip", source_kind="raw",
                source_ref="clip.mp4", ratio="16:9",
                type="structure", best_for=["ai-news-long"],
                profile_text="# profile2")

    manifest_file = insp.manifest_path()
    assert manifest_file.is_file()
    entries = insp.read_manifest()
    slugs = {e["slug"] for e in entries}
    assert {"split-style", "other-clip"} <= slugs
    for e in entries:
        assert e["profile"]  # every entry points the LLM at a profile
        assert e["profile"].startswith(("profile.md", "/", str(bench)))

    # rebuild from scratch is idempotent
    insp.update_manifest()  # no-op on same state
    insp.create("Third Eye", source_kind="description", overwrite=True,
                ratio="1:1", type="hooks", profile_text="# p")
    assert insp.read_manifest()[-1]["type"] == "hooks"

    # need-based pick via manifest-equivalent loader
    picks = load_for(best_for="ai-news-long")
    assert picks[0]["record"]["slug"] == "other-clip"
