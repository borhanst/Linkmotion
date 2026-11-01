# AGENTS.md - OpenCode

This project is **AI-News-Agent**, an OpenMontage-style, instruction-driven
video production system for AI news / LLM model releases.

## Mandatory first read

Before responding to ANY user message, read `AGENT_GUIDE.md` in the project
root. It contains the routing rules that determine your first action.
Skipping it will cause you to take the wrong action.

```text
AGENT_GUIDE.md  <- routing rules (read first)
AGENTS.md       <- this file's pointer
```

## What this project does

The AI agent IS the orchestrator. There is no code orchestrator. You read
instruction files (pipeline manifests + stage director skills + meta skills)
and drive the pipeline using Python tools.

```bash
python -m ai_news_agent preflight    # see which tools are available
python -m ai_news_agent pipelines    # list pipeline manifests
python -m ai_news_agent init <slug> <pipeline> "<topic>" [url]
```

## Pipelines

| Pipeline | Manifest | Best For |
|---|---|---|
| AI News Short | `pipeline_defs/ai-news-short.yaml` | 45-75s vertical Short about one AI news story |
| AI News Long | `pipeline_defs/ai-news-long.yaml` | 7-8 min long-form deep-dive / roundup |
| Model Release | `pipeline_defs/model-release.yaml` | 60-120s new LLM/model announcement explainer |

## Standard production flow

1. Read the pipeline manifest.
2. Run preflight.
3. For each stage, read `skills/pipelines/<pipeline>/<stage>-director.md`
   BEFORE doing work.
4. After each stage, run `skills/meta/reviewer.md` and write
   `projects/<slug>/review-<stage>.md` via `lib/reviewer.py`.
5. Checkpoint state (`projects/<slug>/progress.json`) after every stage.
6. Ask the user when `human_approval_default: true` for that stage.

## Golden rules

- Build ONE scene/beat at a time. Preview before the next.
- Always check before you build, never guess from memory.
- Reuse existing components; never duplicate silently.
- Ground every claim in a page we actually fetched and showed.
- Never invent anchors - copy them verbatim from inspect output.
- The `decision_log` is append-only; a changed choice appends a new entry.

## Composition engines

Each scene picks **Remotion** (React) or **HyperFrames** (HTML). The LLM
decides per scene; `lib/engine_selector.py` provides the decision framework,
heuristic fallback, and a single `render_scene()` entry point. All authored
scene code lives under `projects/<slug>/src/<engine>/<scene-id>/` - nothing is
global. Load the engine's official skill before writing scene code
(`remotion-best-practices`, `hyperframes`).

## Where instructions live

| Concern | File |
|---|---|
| Routing rules | `AGENT_GUIDE.md` |
| Agent persona + golden rules | `.opencode/agent/pipeline-director.md` |
| First-interaction flow | `skills/meta/onboarding.md` |
| Self-review protocol | `skills/meta/reviewer.md` |
| Checkpoint protocol | `skills/meta/checkpoint-protocol.md` |
| Tool registry | `tools/tool_registry.py` (query at runtime) |
| Skill index | `skills/INDEX.md` |