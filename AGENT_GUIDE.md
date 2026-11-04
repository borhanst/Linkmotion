# AGENT_GUIDE - Routing Rules for AI-News-Agent

Read this file **before** responding to any user message. This file contains the
routing rules that determine your first action. All instructions live here.

## Rule Zero - All production goes through a pipeline

Every video request, however small, routes through a pipeline manifest in
`pipeline_defs/`. Never hand-write a scene, never call a tool without reading
its skill first.

## First action by message type

| User message | Your first action |
|---|---|
| Vague / exploratory / "what can you do?" | Run `skills/meta/onboarding.md` (preflight + classify + starter prompts) |
| Specific request to make a video (e.g. "Make a 60s Short about GPT-5") | Skip onboarding. Go to **Pipeline selection** below. |
| "Make a Short / reel" about one AI news story | Pipeline: `ai-news-short` |
| "Make a long-form / deep-dive / roundup" (7-8 min) | Pipeline: `ai-news-long` |
| "Make an explainer for a new model / LLM release" | Pipeline: `model-release` |
| "Make a video based on this YouTube URL" | Pipeline: `ai-news-short` (or `ai-news-long` if they want long-form). Use `youtube_source` in research. |
| "Make a video from this blog / article / URL" | Same 3 pipelines by length. Research normalizes ANY source: `web_search.fetch` the URL, extract claims, verify with corroborating search. The user requirement is that **every video has a unique style** - see `skills/core/style-engine.md`. |
| "Make a video about <topic>" (no URL) | Same pipelines. Research builds the source base from `web_search` + `broll`. |
| "Help me fix / review / debug the codebase" | Treat as engineering task, not a production run. |
| "Add a tool / skill / pipeline" | Treat as engineering task. See `skills/INDEX.md` for conventions. |

## Pipeline selection

```bash
python -m ai_news_agent pipelines     # list available manifests
python -m ai_news_agent preflight    # confirm tools are available
```

Then init the project:

```bash
python -m ai_news_agent init <slug> <pipeline> "<topic>" [source_url]
```

Slug: kebab-case, e.g. `2026-10-gpt5-launch-short`.

## Standard production flow

1. Read the pipeline manifest (`pipeline_defs/<pipeline>.yaml`).
2. Run preflight.
3. For **each stage** in order, read
   `skills/pipelines/<pipeline>/<stage>-director.md` **BEFORE** doing work.
4. At the **proposal** stage, generate the video's unique style via
   `lib/style_engine.ensure_style()` (see `skills/core/style-engine.md`) and
   show the rendered style card for approval with the proposal.
5. After each stage, run `skills/meta/reviewer.md` and write
   `projects/<slug>/review-<stage>.md` via `lib/reviewer.py`.
6. Checkpoint state (`projects/<slug>/progress.json`) after every stage.
7. Ask the user when `human_approval_default: true` for that stage.

## Where the instructions live

| Concern | File |
|---|---|
| This routing guide | `AGENT_GUIDE.md` (this file) |
| Agent persona + golden rules | `.kilo/agent/pipeline-director.md` |
| `/ai-news` command | `.kilo/commands/ai-news.md` |
| First-interaction flow | `skills/meta/onboarding.md` |
| Self-review protocol | `skills/meta/reviewer.md` |
| Checkpoint protocol | `skills/meta/checkpoint-protocol.md` |
| Tool registry | `tools/tool_registry.py` (query at runtime) |
| Skill index | `skills/INDEX.md` |

## Golden rules

- Build ONE scene/beat at a time. Preview before the next.
- Always check before you build, never guess from memory.
- Reuse existing components; never duplicate silently.
- Ground every claim in a page we actually fetched and showed.
- Never invent anchors - copy them verbatim from inspect output.
- The `decision_log` is append-only; a changed choice appends a new entry.