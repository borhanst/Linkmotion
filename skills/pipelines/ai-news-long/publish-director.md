# Publish Director - AI News Long

Generate the full YouTube upload package and mark the video done.

## Input

`projects/<slug>/render_report.json`, `projects/<slug>/storyboard.json`

## Tools

- `metadata`

## Process

1. **Keyword research first.** Search the web for how people phrase searches
   around this topic.
2. **Write 5-8 title options** to `projects/<slug>/metadata/titles.md` - vary
   the angle (direct benefit, curiosity gap, number/list, how-to, question,
   bold claim). Mark one recommended. Front-load the primary keyword; first
   ~40-50 characters should stand alone; stay under ~60-70 total.
3. **Write the description** - first 1-2 lines = strongest keyword summary, then
   an expanded paragraph, then **chapter timestamps** matching actual scene
   boundaries from `scenes.json`, then links/CTA, then 3-8 hashtags at the
   bottom.
4. **Write tags** to `projects/<slug>/metadata/tags.json` - mix broad category
   tags, the specific topic phrase, and longer-tail phrases.
5. **Thumbnail** (long-form: required) - 1280x720, 3-6 words of bold text max,
   high contrast. Generate 2-3 variants. Reuse an existing icon/image
   component from this video's own `components/`.
6. **Update `progress.json.stage` to `"done"`**.

## Output: `projects/<slug>/publish_log.json`

## Success criteria

- `publish_log` schema-valid.
- `titles.md`, `description.md`, `tags.json`, thumbnail present.
- Chapter timestamps match scene boundaries.
- Hashtags at the bottom of the description.