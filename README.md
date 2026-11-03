# AI News Agent

The first open-source, instruction-driven video production system for **AI news
and LLM model releases**.

Turn your AI coding assistant into a full video production studio. Describe what
you want in plain language - the agent handles research, scripting, asset
generation, editing, and final composition.

## Install & Run

```bash
git clone <this-repo>
cd ai-news-agent
make setup
```

Open the project in your AI coding assistant and tell it what you want:

```
"Make a 60-second Short about the new GPT-5 release"
"Make a 7-minute deep-dive on how Claude Code works under the hood"
"Make a model-release explainer for the new Gemini Omni Flash"
```

## Pipelines

| Pipeline | Manifest | Best For |
|---|---|---|
| AI News Short | `pipeline_defs/ai-news-short.yaml` | 45-75s vertical Short/R reel about one AI news story |
| AI News Long | `pipeline_defs/ai-news-long.yaml` | 7-8 min long-form deep-dive / news roundup |
| Model Release | `pipeline_defs/model-release.yaml` | 60-120s new LLM/model announcement explainer |

## Architecture

```
AI-News-Agent/
├── tools/              # 6 registered production tools (the agent's hands)
│   ├── tool_registry.py     # auto-discovery, support envelope, capability families
│   ├── base_tool.py         # ToolContract: capability, provider, cost, tier, status
│   ├── web_search.py        # web search + fetch (research + verification)
│   ├── browser_capture.py   # Playwright screen recording of real pages
│   ├── tts.py               # edge-tts narration (male voice, word-level timestamps)
│   ├── video_compose.py     # Remotion render (React scene composition)
│   └── metadata.py          # titles / description / tags / thumbnail
├── lib/                # core infrastructure
│   ├── checkpoint.py        # resumable state + decision log
│   ├── config.py            # config.yaml loader
│   ├── pipeline_loader.py   # manifest loader
│   └── paths.py             # project layout
├── pipeline_defs/       # YAML pipeline manifests (the agent's playbook)
├── skills/             # Markdown skill files (the agent's knowledge)
│   ├── meta/               # onboarding, reviewer, checkpoint protocol, ...
│   ├── core/               # Remotion, edge-tts, Playwright, FFmpeg
│   ├── creative/           # storytelling, typography, captions, ...
│   └── pipelines/          # per-pipeline stage director skills
├── schemas/            # JSON Schemas (contract validation)
├── styles/             # visual style playbooks (YAML)
├── scripts/            # helper scripts
└── projects/           # one folder per produced video
```

## How It Works

OpenMontage uses an **agent-first architecture**. There is no code orchestrator.
Your AI coding assistant IS the orchestrator.

```
You: "Make a 60-second Short about the new GPT-5 release"
 |
 v
Agent reads pipeline manifest (YAML) -- stages, tools, review criteria, success gates
 |
 v
Agent reads stage director skill (Markdown) -- HOW to execute each stage
 |
 v
Agent calls Python tools -- capability discovery via the registry
 |
 v
Agent self-reviews using reviewer skill -- schema validation, quality checks
 |
 v
Agent checkpoints state (JSON) -- resumable, with decision log
 |
 v
Agent presents for your approval -- you stay in control at every creative decision
 |
 v
Render (Remotion) -- composition engine
 |
 v
Final video output + metadata package
```

## What You Get With Zero API Keys

Out of the box, `make setup` gives you:

| Capability | Tool | What It Does |
|---|---|---|
| Narration | edge-tts | Male-voice TTS with word-level timestamps |
| Browser capture | Playwright | Screen recording of real pages (scroll/select/spotlight) |
| Composition | Remotion | React-based programmatic video, captions, animations |
| Post-production | FFmpeg | Encoding, subtitle burn-in, audio mixing |
| Research | web_search | Live web search to ground every claim |
| Social post | twitter_post | Fetch a Twitter/X post URL into structured card data (same design card) and capture a high-resolution screenshot of that post's design card. Keyless: Twitter's oEmbed endpoint + page metadata. x.com blocks automated full-page screenshots, so the screenshot is a faithful Headless-Chromium render of the post's card design. |

## Contributing

See `CONTRIBUTING.md`.

## License

AGPL-3.0