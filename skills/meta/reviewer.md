# Reviewer

Self-review protocol after every stage. Run through this checklist before
presenting any stage output to the user.

## Implementation

The checks below are enforced by `lib/reviewer.py`. Use it rather than
hand-writing reviews:

```python
from lib.reviewer import Reviewer
result = Reviewer(slug).check(stage, artifact_dict)
result.write_md()   # -> projects/<slug>/review-<stage>.md
```

CLI:

```bash
python -m lib.reviewer <slug> <stage> <artifact.json>
```

Exit code 1 if any BLOCKER. JSON Schemas live in `schemas/` (real files, not
prose) and are loaded automatically by artifact name.

## Mandatory checks

1. **Schema valid** - every artifact passes its JSON Schema in `schemas/`.
   `lib/reviewer.Reviewer.check()` raises a BLOCKER on any schema failure.
2. **Sources real** - every claim has a URL we actually fetched and showed.
3. **Anchors verbatim** - every `select`/`spotlight` text was copied from
   `inspect_page.py` output, never invented.
4. **Numbers on screen** - every number spoken appears on screen when spoken.
5. **No fabricated demos** - terminal output, benchmark numbers, product UI,
   and API behavior are real or clearly labeled illustrative.
6. **Duration inside target** - measured with ffprobe, not estimated.
7. **Captions synced** - word-level timestamps drive on-screen text.
8. **Safe zones** - no key text outside platform safe margins.
9. **Audio clean** - no clipping, abrupt cuts, or distracting noise.
10. **Decision log current** - every meaningful choice is logged.

## Semantic checks (beyond JSON Schema)

`lib/reviewer.py` also runs cross-field checks that JSON Schema cannot express:

| Stage | Check |
|---|---|
| proposal | `selected_concept` references a valid `concept_id` |
| script | sum of `est_duration_sec` matches `total_duration_sec` |
| asset_manifest | every asset `path` resolves to an existing file |
| storyboard | >= 3 scene types; verdict card has `footer` with sources |
| publish_log | hashtags present |

Add new semantic checks as functions in the `_SEMANTIC_CHECKS` map.

## Severity

- **BLOCKER**: any check fails -> do not proceed. Fix and re-review.
- **WARN**: cosmetic or minor -> note it, proceed, fix in next stage.
- **NOTE**: informational -> record it.

## Output

Write the review to `projects/<slug>/review-<stage>.md` with one line per check:
`[PASS|WARN|NOTE|BLOCKER] <check> - <detail>`.