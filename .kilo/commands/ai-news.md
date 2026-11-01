# /ai-news - produce an AI news / model-release video

Use this command when the user wants to make an AI news story or LLM model
release video through the pipeline.

## Workflow

1. **Read `AGENTS.md`** (already loaded) for routing rules.
2. **Run preflight**: `python -m ai_news_agent preflight`
3. **Pick the pipeline** from `pipeline_defs/`:
   - 45-75s vertical Short about one story -> `ai-news-short`
   - 7-8 min long-form deep-dive / roundup -> `ai-news-long`
   - 60-120s new LLM/model announcement -> `model-release`
4. **Init the project**: `python -m ai_news_agent init <slug> <pipeline> "<topic>" [url]`
5. **Execute stage by stage**: for each stage read
   `skills/pipelines/<pipeline>/<stage>-director.md` BEFORE doing work.
6. **After each stage**: run `skills/meta/reviewer.md`, write
   `projects/<slug>/review-<stage>.md`, checkpoint.
7. **Finish**: `projects/<slug>/publish_log.json` + `progress.json.stage = "done"`.

## Golden rules

- Build ONE scene/beat at a time. Preview before the next.
- Always check before you build, never guess from memory.
- Reuse existing components; never duplicate silently.
- Every claim grounded in a page we actually fetched and showed.
- Never invent anchors - copy them verbatim from `inspect_page.py` output.
- The `decision_log` is append-only; a changed choice appends a new entry.