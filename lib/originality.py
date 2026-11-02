"""Originality guard - idea mining is inspiration-only.

Channel/video analysis feeds a CHANNEL PROFILE or mined VIDEO IDEAS. Ideas may
borrow TECHNIQUE (structure, hook style, framing, format, pacing) from a
source - never content, wording, or the source's own angle re-told.

This module scores overlap between a derived idea and the source material
(title + description + transcript). Word-shingle Jaccard + containment give a
cheap, deterministic plagiarism signal; the recommended policy:

- pass: containment < IDEAS_MAX_CONTAINMENT and jaccard < IDEAS_MAX_JACCARD
- fail: regenerate the idea from scratch (do not just re-word it)

A failed check is recorded in the project decision_log; never present an idea
that failed unless the regenerated version passes.
"""

from __future__ import annotations

import json
import re
from typing import Any

# Policy defaults. Tune per-pipeline in a manifest if needed.
IDEAS_MAX_JACCARD = 0.30
IDEAS_MAX_CONTAINMENT = 0.30
SHINGLE_N = 3

_WORD_RX = re.compile(r"[a-z0-9']+")


def tokens(text: str) -> list[str]:
    """Lowercased content tokens."""
    return _WORD_RX.findall(text.lower())


def shingles(text: str, n: int = SHINGLE_N) -> set[str]:
    """Set of n-word shingles."""
    tk = tokens(text)
    if len(tk) < n:
        return {" ".join(tk)} if tk else set()
    return {" ".join(tk[i:i + n]) for i in range(len(tk) - n + 1)}


def jaccard(candidate: str, source: str, n: int = SHINGLE_N) -> float:
    """|A & B| / |A | B| over n-word shingles (0.0 = disjoint)."""
    a, b = shingles(candidate, n), shingles(source, n)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def containment(candidate: str, source: str, n: int = SHINGLE_N) -> float:
    """|A & B| / min(|A|, |B|) - how much of the smaller text is covered by the
    other. Catches 'reordered transcript' ideas even when they add novelty."""
    if not candidate.strip():
        return 0.0
    a, b = shingles(candidate, n), shingles(source, n)
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def check(candidate: str, sources: list[str],
          max_jaccard: float = IDEAS_MAX_JACCARD,
          max_containment: float = IDEAS_MAX_CONTAINMENT) -> dict[str, Any]:
    """Score one derived idea against all source material.

    Returns a structured verdict; IDEA-MINING pipelines must run this and not
    present an idea whose `passed` is False.
    """
    per_source: list[dict[str, Any]] = []
    worst_j = worst_c = 0.0
    for i, src in enumerate(sources):
        if not src or not src.strip():
            continue
        j = jaccard(candidate, src)
        c = containment(candidate, src)
        worst_j, worst_c = max(worst_j, j), max(worst_c, c)
        per_source.append({"source_index": i, "jaccard": round(j, 4),
                           "containment": round(c, 4)})
    passed = worst_j < max_jaccard and worst_c < max_containment
    return {
        "passed": passed,
        "max_jaccard": worst_j,
        "max_containment": worst_c,
        "thresholds": {"jaccard": max_jaccard, "containment": max_containment},
        "per_source": per_source,
    }


def check_field(flat_fields: list[str], sources: list[str], **kw: Any) -> dict[str, Any]:
    """Check several fields of one idea (title, hook, outline, script) jointly."""
    return check(" ".join(f for f in flat_fields if f), sources, **kw)


def _main() -> None:  # pragma: no cover
    import sys
    a = sys.argv[1:]
    if len(a) < 2:
        print("usage: python -m lib.originality <candidate_text_file_or_text> <source_file_1> [source_file_2 ...]")
        return
    candidate = a[0]
    if len(a) > 2 or candidate.endswith(".txt") or candidate.endswith(".md"):
        candidate = open(candidate, encoding="utf-8").read()
    sources = [open(p, encoding="utf-8").read() for p in a[1:]]
    print(json.dumps(check(candidate, sources), indent=2))


if __name__ == "__main__":  # pragma: no cover
    _main()
