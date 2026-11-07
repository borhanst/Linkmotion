# Linkmotion

Linkmotion is an opinionated, instruction-driven workflow for producing short-form and long-form AI videos from a brief, URL, or topic. Instead of hard-coding a single pipeline, it gives an AI coding assistant a project structure, pipeline manifests, review checks, and tool registry so it can research, script, render, and checkpoint work end-to-end.

This repo is designed for:

- AI shorts and explainers
- model release explainers
- YouTube-style AI storytelling videos
- pipeline-driven production with human approval loops

## Key idea

The repo does not try to replace the agent. It gives the agent:

- a set of production tools
- a pipeline manifest describing stages and outputs
- skill files explaining how to perform each stage
- schemas for validating outputs
- checkpointing for resumable work

In other words: your AI assistant becomes an orchestrator for a video production pipeline.

Check out the workflow in action: ▶️ **[@therefactorengine](https://www.youtube.com/@therefactorengine)**

## What this repo contains

- `pipeline_defs/` — pipeline blueprints for different video types
- `tools/` — concrete production tools (search, capture, TTS, render, etc.)
- `lib/` — project setup, config, pipeline loading, checkpointing, and style logic
- `skills/` — authoring guidance and stage-by-stage instructions
- `schemas/` — JSON schema contracts for proposals, scripts, storyboards, report files
- `styles/` — visual identity and motion style definitions
- `projects/` — generated video workspaces, one folder per project
- `tests/` — repository validation tests

## Prerequisites

You need:

- Python 3.10+
- Git
- ffmpeg and ffprobe installed and on PATH
- A working AI coding assistant or terminal environment with access to the repo

For local render and browser workflows, the repo expects Python packages such as Playwright, edge-tts, pyyaml, and jsonschema. These are installed with the setup commands below.

## Quick start

Clone and set up the environment:

```bash
git clone <repo-url>
cd linkmotion
make setup
```

This creates a local virtual environment and installs the Python dependencies from `requirements.txt`.

If you want the dev environment too:

```bash
make install-dev
```

## Verify the repo is ready

Run the repo preflight check:

```bash
python -m ai_news_agent preflight
```

This checks external dependencies and the discovered tool registry. It also flags missing render or browser support.

List available pipelines:

```bash
python -m ai_news_agent pipelines
```

## Create a new project

Initialize a new project with a slug, pipeline, topic, and optional source URL:

```bash
python -m ai_news_agent init 2026-11-gpt5-short ai-news-short "GPT-5 launch coverage" "https://example.com/article"
```

This creates a new project folder under `projects/<slug>/` and writes progress/state files. Project names should be kebab-case.

## Available pipelines

The repo ships with several video production pipelines:

| Pipeline | Manifest | Best for |
|---|---|---|
| `ai-news-short` | `pipeline_defs/ai-news-short.yaml` | 45-75 second AI news short / vertical reel |
| `ai-news-long` | `pipeline_defs/ai-news-long.yaml` | 7-8 minute deep-dive or roundup |
| `model-release` | `pipeline_defs/model-release.yaml` | model / LLM release explainers |

You can inspect the pipeline config directly in `pipeline_defs/*.yaml` to see stages and requirements.

## Example video

Here's a full breakdown video produced with the `model-release` pipeline:

📺 **[Meituan's LongCat-2.5: This 1.6T AI Agent Beats GPT-5.5 — Full Breakdown](https://youtu.be/o-__tKpOhsU)**

## YouTube channel

More videos produced with this pipeline are on the channel:

▶️ **[@therefactorengine](https://www.youtube.com/@therefactorengine)**

## Standard workflow

The workflow is intentionally stage-based and review-heavy.

1. Read the pipeline manifest
2. Run preflight
3. For each stage, read the matching skill file before making changes
4. Generate or select a style for the video
5. Review the output and save a review artifact
6. Update checkpoint/progress state
7. Request approval when the stage requires it

The routing and stage guidance are defined in `AGENT_GUIDE.md`.

Example flow:

```bash
python -m ai_news_agent preflight
python -m ai_news_agent pipelines
python -m ai_news_agent init my-ai-news-short ai-news-short "Claude Code release analysis"
```

Then work inside `projects/my-ai-news-short/` and follow the stage instructions in `skills/pipelines/...`.

## Repo architecture

```text
.
├── AGENT_GUIDE.md              # routing and production workflow rules
├── AGENTS.md                  # high-level agent instructions
├── README.md                  # this file
├── Makefile                   # setup / preflight / test shortcuts
├── config.yaml                # default config for model/budget/output setup
├── requirements.txt           # runtime dependencies
├── requirements-dev.txt       # development dependencies
├── pipeline_defs/             # pipeline manifests
├── skills/                    # agent playbooks and stage instructions
├── tools/                     # tool implementations
├── lib/                       # core libraries
├── schemas/                   # JSON contracts
├── styles/                    # YAML style definitions
├── projects/                  # generated project workspaces
├── tests/                     # test suite
├── ai_news_agent/             # CLI entry point
└── out/                       # rendered output directory
```

## Tooling and capabilities

The repo auto-discovers tools via `tools/tool_registry.py`. This makes tool availability explicit and lets the agent adapt to what is installed.

Key capability families include:

- `web_search` — research + verification
- `youtube_source` — fetch and normalize YouTube source material
- `browser_capture` — Playwright-based page capture
- `broll` — image/video / social asset search and capture
- `tts` — edge-tts narration and word timing
- `sfx` — sound effects and audio polish
- `video_compose` — final render / composition
- `metadata` — title, description, tags, thumbnail metadata

## Project layout

Each video project is created under `projects/<slug>/` and usually includes:

- `proposal.json` — project brief / concept
- `research.md` or `research_brief.json` — research-backed notes
- `script.json` — narrative script
- `storyboard.json` — beat-by-beat visual plan
- `progress.json` — stage tracking and checkpoint state
- `decision_log.jsonl` — append-only log of decisions
- `review-*.md` — review notes generated for each stage
- `assets/`, `audio/`, `captures/`, `renders/`, `src/` — project output folders

The project folder is where the actual production work happens.

## Style system

The repo uses a style engine and YAML playbooks to create a unique visual identity per video. These lives under `styles/` and are associated with each pipeline.

The standard behavior is:

- generate a style identity for the project
- tailor the motion, typography, and look to the topic
- keep the style consistent across the script, storyboard, and composition stages

## Safety and review loops

This repo expects iterative review, not blind execution. Outputs are meant to be checked by the agent and by you.

Important patterns:

- every stage has review criteria
- progress is checkpointed in JSON
- decisions are logged append-only
- human approval is expected for creative gates
- quality reviews happen after each stage

See `AGENT_GUIDE.md` and the files under `skills/meta/` for the review/checkpoint protocol.

## Common commands

```bash
# install deps
make setup

# install dev deps
make install-dev

# verify tool availability
python -m ai_news_agent preflight

# list manifests
python -m ai_news_agent pipelines

# scaffold a project
python -m ai_news_agent init <slug> <pipeline> "<topic>" [source_url]

# run tests
make test

# compile check
make lint
```

## Typical usage examples

Short AI video:

```bash
python -m ai_news_agent init gpt5-launch ai-news-short "GPT-5 launch coverage"
```

Long AI analysis:

```bash
python -m ai_news_agent init claude-code-deep-dive ai-news-long "Claude Code internals explained"
```

Model release explainer:

```bash
python -m ai_news_agent init gemini-omni-flash model-release "Gemini Omni Flash release breakdown"
```

Then open the generated project and proceed stage by stage.

## Notes

- This repo is optimized for agent-driven production rather than manual scripting.
- It is best used with an AI coding assistant that can read pipeline manifests and skills and execute tools.
- The design philosophy is grounded claims, structured review, and resumable work.
- The repo prefers explicit checkpoints over implicit state.

## License

AGPL-3.0 — see [LICENSE](LICENSE) for the full text.

## Contributing

This project expects a pipeline-first convention. If you add new tools, skills, or pipeline stages, follow the patterns already used in `tools/`, `skills/`, and `pipeline_defs/` rather than creating ad hoc workflows.
