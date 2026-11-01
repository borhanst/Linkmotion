# AI News Agent - example video project

This folder is a fully-scaffolded example for the `ai-news-short` pipeline.
Every produced video gets its own folder like this.

## Layout

```
2026-10-gpt5-launch-short/
  progress.json       # stage + current beat tracker (single source of truth)
  research.md         # Stage 1 output
  proposal.json       # Stage 2 output
  script.json         # Stage 3 output
  storyboard.json     # Stage 4 output
  assets/
    manifest.json     # Stage 5 output
    raw/
      web/            # page captures
  audio/
    beat-1.mp3        # edge-tts narration per beat
    beat-1.srt        # word-level timestamps
  metadata/
    titles.md         # Stage 7 output
    description.md
    tags.json
    thumbnail/
  review-research.md
  review-proposal.md
  ...
  decision_log.jsonl  # append-only audit trail
```

## Resume

Read `progress.json` first. It says which stage and which beat is in flight.