# Publish Director - Model Release

Generate the YouTube upload package and mark the video done.

## Input

`projects/<slug>/render_report.json`, `projects/<slug>/storyboard.json`

## Tools

- `metadata`

## Process

1. **Keyword research first.** Search the web for how people phrase searches
   around this model. Favor real search phrasing.
2. **Write 5-8 title options** to `projects/<slug>/metadata/titles.md`.
   Front-load the **exact model name**; first ~40-50 characters should stand
   alone. Mark one recommended.
3. **Write the description** to `projects/<slug>/metadata/description.md`.
   First 1-2 lines = strongest keyword summary. Include the date, lab, model
   string, and sources. Hashtags at the bottom.
4. **Write tags** to `projects/<slug>/metadata/tags.json`.
5. **Thumbnail** - render 1280x720 (or 1080x1920 for Shorts), 2-3 variants.
6. **Update `progress.json.stage` to `"done"`**.

## Output: `projects/<slug>/publish_log.json`

## Success criteria

- `publish_log` schema-valid.
- `titles.md`, `description.md`, `tags.json`, thumbnail present.
- Exact model name in the title.
- Date, lab, model string, and sources in the description.