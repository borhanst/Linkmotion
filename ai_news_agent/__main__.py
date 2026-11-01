"""AI-News-Agent CLI entry point.

Usage:
  python -m ai_news_agent                # help
  python -m ai_news_agent preflight     # tool registry + capability menu
  python -m ai_news_agent pipelines     # list pipeline manifests
  python -m ai_news_agent init <slug> <pipeline> "<topic>" [source_url]
"""

from ai_news_agent import main

if __name__ == "__main__":
    raise SystemExit(main())