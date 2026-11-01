# Storyboard Director - AI News Short

Turn the script into a JSON storyboard the capture + render stages consume.

## Input

`projects/<slug>/script.json`, `projects/<slug>/research.md`

## Tools

- `browser_capture` (required for `web` scenes)

## Process

1. **Inspect every page you'll show** with `browser_capture` BEFORE writing
   anchors. View the screenshots - they are what the video will look like.
2. **Copy anchors verbatim** from the inspect output. Anchors that don't
   exist produce a warning and a missing highlight - never invent them.
3. **Watch for** cookie walls, login walls, bot checks
   (`http_status` 403/429). Don't bypass captchas or paywalls - switch to
   another source or a text-only card.
4. **Assign scene types.** Use the standard recipe: `card` opens and closes,
   `web` is the proof, `media` is the user's own image/video, `social` is what
   people say. Never more than two `web` scenes in a row.
5. **Plan 9:16 safe zones.** Keep essential text inside the center 80%
   horizontally and clear of the bottom ~15-20% and right-edge ~10-15%.

## Scene types

| Type | Use | Fields |
|---|---|---|
| `card` | hook, stat, bars, verdict | `kicker`, `title`, `subtitle`, `narration`, optionally `bullets` |
| `web` | real page walkthrough | `url`, `narration`, `actions[]` |
| `media` | user's own image/video | `src`, `kicker`, `narration` |
| `social` | what people say | `posts[]`, `narration` |

## Actions

`scroll` `select` `spotlight` `click` `type` `cursor` `clear` `wait` `press` `goto` `js`.
Targets: `text:...` · `heading:...` · `css:...`.
Timing: `"when": "<phrase from narration>"` fires as that word is spoken;
`"at": 2.5` = seconds into the scene.

## Output: `projects/<slug>/storyboard.json`

```json
{
  "settings": {"color_scheme": "dark", "voice": {"edge": "en-US-GuyNeural"},
               "viewport": [540, 960], "scale": 2, "output_size": [1080, 1920]},
  "scenes": [
    {"id": "hook", "type": "card", "kicker": "Breaking", "title": "GPT-5",
     "subtitle": "OpenAI just dropped it", "narration": "..."},
    {"id": "what", "url": "https://openai.com/news/gpt-5", "narration": "...",
     "actions": [{"do": "scroll", "to": "heading:Highlights"},
                 {"do": "select", "text": "exact text from the page", "when": "the phrase"}]},
    {"id": "verdict", "type": "card", "title": "Verdict", "bullets": ["..."],
     "footer": "Source: openai.com, October 2026"}
  ]
}
```

## Success criteria

- Schema-valid storyboard.
- At least 3 scene types used.
- Loop-friendly last beat.
- Every anchor verbatim from inspect output.
- Verdict card has `footer` with sources + date.