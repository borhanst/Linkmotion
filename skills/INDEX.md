# AI News Agent - Skill Index

For the full agent onboarding guide, see `AGENTS.md` in the project root.

This file lists all available skills and documents the knowledge architecture.

## Knowledge Architecture

```
Layer 1: tools/tool_registry.py      "What tools exist and what they can do"
         tools/base_tool.py           Each tool declares: capability, provider,
                                       tier, status, dependencies, cost, agent_skills[]

        <- agent_skills[] points to <-

Layer 2: skills/                      "How AI-News-Agent uses these tools"
         Project-specific conventions: pipeline integration, artifact mappings,
         {core,creative,meta,pipelines}/ quality checklists

        <- references underlying tech in <-

Layer 3: .agents/skills/              "How the technology itself works"
         Generic API knowledge from skills.sh (installed skills) - correct
         import paths, code patterns, constraints, parameters - tech-agnostic
```

**How the agent uses this:**
1. The orchestrator queries Layer 1 (`python -m tools.tool_registry`) to see
   what's available.
2. Each tool's `agent_skills[]` field names the Layer 2 skills it relies on.
3. Layer 2 skills teach the agent AI-News-Agent conventions.
4. Layer 3 skills provide generic API knowledge, loaded on-demand.

## Capability Families

The registry is the single source of truth. Query it at runtime:

```bash
python -m tools.tool_registry
```

| Capability | Tool | Discovery |
|---|---|---|
| `web_search` | `web_search` | Web search + fetch for research/verification |
| `youtube_source` | `youtube_source` | YouTube oEmbed + auto-generated transcript (keyless) for transcript-sourced stories |
| `browser_capture` | `browser_capture` | Playwright screen recording of real pages |
| `broll` | `broll` | Web image/video search, social-post capture, demo clips, user files |
| `tts` | `tts` | edge-tts narration (male voice, word-level timestamps) |
| `video_compose` | `video_compose` | Remotion render |
| `metadata` | `metadata` | Titles / description / tags / thumbnail |

## Core Skills

| Skill | File | Trigger | Agent Skills (Layer 3) |
|-------|------|---------|----------------------|
| Remotion | `core/remotion.md` | React-based composition | `remotion-best-practices`, `remotion` |
| HyperFrames | `core/hyperframes.md` | HTML-based composition (alternative engine) | `hyperframes`, `hyperframes-html-authoring` |
| edge-tts | `core/edge-tts.md` | Male-voice narration, word timestamps | `remotion-video-common` |

## Engine selection

The compose stage picks **Remotion** or **HyperFrames** per scene. The LLM
decides; the framework in `lib/engine_selector.py` provides the decision rules,
a heuristic fallback, and a single `render_scene()` entry point. All authored
scene code lives under `projects/<slug>/src/<engine>/<scene-id>/` - nothing is
global.

| Engine | Authoring | When to use |
|---|---|---|
| Remotion | React component (`index.tsx`) | Bespoke programmatic UI, charts, long-form, motion graphics |
| HyperFrames | Plain HTML (`composition.html`) | Existing web material, templates, data-driven cards, GSAP/Lottie |

Default: Remotion. Switch to HyperFrames for `web`/`media`/`social` scenes or
any beat better expressed as HTML/CSS.

## Creative Skills

| Skill | File | Trigger |
|-------|------|---------|
| Storytelling | `creative/storytelling.md` | Narrative structure, hooks, pacing |
| B-Roll Planning | `creative/broll-planning.md` | Supplementary footage sourcing from web/social/user files |

## Pipeline Type Skills

| Skill | File | When to Use |
|---|---|---|
| AI News Short | `pipelines/ai-news-short/` | 45-75s vertical Short about one AI news story |
| AI News Long | `pipelines/ai-news-long/` | 7-8 min long-form deep-dive / roundup |
| Model Release | `pipelines/model-release/` | 60-120s new LLM/model announcement explainer |

## Meta Skills

| Skill | File | Purpose |
|-------|------|---------|
| Onboarding | `meta/onboarding.md` | First-interaction greeting, capability discovery, starter prompts |
| Reviewer | `meta/reviewer.md` | Self-review protocol after every stage |
| Checkpoint Protocol | `meta/checkpoint-protocol.md` | When/how to checkpoint and request human approval |

## Style Playbooks

Style playbooks (`styles/*.yaml`) define visual language, typography, motion,
audio, and asset constraints. Load via `lib/playbook_loader.py`.

| Playbook | Category | Mood | Best For |
|----------|----------|------|----------|
| `clean-professional` | motion-graphics | polished, trustworthy | Corporate, educational, SaaS |
| `flat-motion-graphics` | motion-graphics | energetic, bold | Social media, TikTok, startups |
| `minimalist-diagram` | whiteboard | focused, technical | Technical deep-dives, architecture |

## Adding New Tools

1. Place the tool in `tools/`.
2. Set `capability` and `provider` in the class definition.
3. The registry discovers tools automatically - no manual registration needed.
4. Attach relevant Layer 2 skills via `agent_skills[]`.
5. **No other files need updating.**