# Publish Director - AI News Short

Generate the YouTube upload package and mark the video done.

## Input

`projects/<slug>/render_report.json`, `projects/<slug>/storyboard.json`

## Tools

- `metadata`

## Process

1. **Keyword research first.** Search the web for how people actually phrase
   searches around this topic. Favor real search phrasing over a cleverer
   synonym.
2. **Write 5-8 title options** to `projects/<slug>/metadata/titles.md`.
   Vary the angle: direct benefit, curiosity gap, number/list, how-to,
   question, bold claim. Mark one as recommended. Front-load the primary
   keyword; first ~40-50 characters should stand alone.
3. **Write the description** to `projects/<slug>/metadata/description.md`.
   First 1-2 lines = strongest keyword summary. Keep it brief for Shorts.
   Include hashtags at the bottom.
4. **Write tags** to `projects/<slug>/metadata/tags.json`. Always include
   `#Shorts` among the hashtags.
5. **Thumbnail** - optional for Shorts unless the user asks. If wanted, render
   1080x1920 stills from the storyboard's verdict beat.
6. **Update `progress.json.stage` to `"done"`**.

## Output: `projects/<slug>/publish_log.json`

```json
{"slug": "...", "titles": ["..."], "tags": {"tags": [...], "hashtags": [...]},
 "description": "...", "thumbnail": "", "ok": true}
```

## Success criteria

- `publish_log` schema-valid.
- `titles.md`, `description.md`, `tags.json` present.
- `#Shorts` in hashtags.