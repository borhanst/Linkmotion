"""Style DNA engine contracts: uniqueness, determinism, artifact generation."""

import json
from pathlib import Path

import pytest

from lib.style_engine import LEDGER_PATH, GENE_AXES, generate_style, ensure_style


@pytest.fixture()
def clean_ledger(tmp_path):
    """Point the ledger at a temp file so tests don't pollute production state."""
    import lib.style_engine as se
    real = se.LEDGER_PATH
    se.LEDGER_PATH = tmp_path / "style_history.jsonl"
    yield se.LEDGER_PATH
    se.LEDGER_PATH = real


def test_signature_is_complete(clean_ledger):
    spec = generate_style("test-sig-video", "topic")
    for axis in GENE_AXES:
        assert getattr(spec, axis), f"axis {axis} empty"


def test_deterministic_per_slug(clean_ledger):
    a = generate_style("deterministic-slug", "topic")
    b = generate_style("deterministic-slug", "topic")
    assert a.signature() == b.signature()


def test_ledger_pushes_different_videos_apart(clean_ledger):
    seen = set()
    for i in range(6):
        spec = generate_style(f"uniqueness-probe-{i}", "topic")
        # with the ledger active, full signatures must not repeat
        assert spec.signature() not in seen, f"repeat signature at probe {i}"
        seen.add(spec.signature())


def test_ensure_style_writes_artifacts(tmp_path, clean_ledger):
    import lib.style_engine as se
    from lib.paths import project_slug_dir

    slug = "artifact-check-video"
    result = se.ensure_style(slug, "some topic")

    pr = project_slug_dir(slug)
    tokens = Path(result["tokens_css"])
    card = Path(result["style_card"])
    doc = Path(result["design_system_md"])
    kit = Path(result["kit_dir"])

    assert tokens.is_file() and "--accent:" in tokens.read_text(encoding="utf-8")
    assert card.is_file() and "tokens.css" in card.read_text(encoding="utf-8")
    assert doc.is_file() and result["signature"] in doc.read_text(encoding="utf-8")
    assert kit.is_dir() and len(result["kit_cloned"]) >= 5

    # idempotent re-run
    again = se.ensure_style(slug, "some topic")
    assert again["signature"] == result["signature"]

    # ledger recorded this run
    lines = [json.loads(x) for x in clean_ledger.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert any(e["slug"] == slug for e in lines)

    # cleanup generated project
    import shutil
    shutil.rmtree(pr, ignore_errors=True)


def test_tokens_css_bakes_motif(clean_ledger):
    import lib.style_engine as se
    spec = se.generate_style("tokens-check-video", "t")
    css = se.tokens_css(spec)
    motif = spec.motif
    assert motif in css                                     # motif named
    for token in ("--bg", "--surface", "--accent", "--accent2", "--font-display"):
        assert token in css
