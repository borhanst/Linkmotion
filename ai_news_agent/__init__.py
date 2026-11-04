"""AI-News-Agent CLI package.

Instruction-driven video production system orchestrator entry points:

    python -m ai_news_agent preflight                      # tool health
    python -m ai_news_agent pipelines                      # list manifests
    python -m ai_news_agent init <slug> <pipeline> "<topic>" [source_url]

The AI agent IS the orchestrator; this package only exposes the thin CLI the
routing guide (AGENT_GUIDE.md) and Makefile depend on. All production logic
lives in lib/ (loaders, checkpoint, reviewer, engine_selector) and tools/.
"""

__version__ = "1.0"
