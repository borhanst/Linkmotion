# B-roll / Media Acquisition - Status

## Done
- `tools/broll.py` - `BrollTool`: web image/video search, social-post capture,
  demo-clip download, user-file catalog. Registers as capability `broll`.
- `skills/creative/broll-planning.md` - planning skill: stock-vs-generated
  decision matrix, query construction with POV keywords, evaluation scoring,
  failure escalation.
- `schemas/broll.json` - artifact schema (query, results, kind, license_note).
- `tools/tool_registry.py` - auto-discovers `broll` (no manual registration).
- `pipeline_defs/*.yaml` - `broll` added to research + assets `tools_available`
  in all 3 manifests (ai-news-short, ai-news-long, model-release).
- `skills/INDEX.md` - broll-planning row added.
- `tests/test_contracts.py` - 3 new broll tests (register, health, search,
  user-file catalog).
- `BROLL_STATUS.md` - this file.

## Verified
- `python -m ai_news_agent preflight` -> 6 tools, all `available`.
- `pytest tests/` -> **17 passed**.

## Design notes
- No stock-library APIs (Pexels/Pixabay). All media comes from:
  1. Web image/video search (`broll` image/video)
  2. Social-media posts + screenshots (`broll` social + `browser_capture`)
  3. Demo clips referenced by docs/articles (`broll` video +
     `browser_capture`)
  4. User-supplied files (`broll` user files)
- Every acquired asset records `source_url` + `license_note`; nothing is
  claimed royalty-free without checking the page it came from.
- Evaluation scoring 1-5; threshold 3+. Below 3 -> refine query, switch source
  type, use user files, or build a generated visual.

## Not yet wired
- Stage-director skills don't yet reference `broll` explicitly. Add a
  "B-roll acquisition" subsection to each pipeline's `asset-director.md` when
  a real production runs.