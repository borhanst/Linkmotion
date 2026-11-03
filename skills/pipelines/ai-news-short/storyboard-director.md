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

## Design system application (storyboard stage)
Apply the approved `design_system` from `proposal.md` to every scene so the video looks like one cohesive brand piece.

1. **Background**: set each scene's bg to `design_system.dark_bg` (or brand-approved variant). Add an animated mesh-gradient using the brand's primary + secondary colors as blurred blobs.
2. **Logo**: place the official brand logo SVG (from `design_system.logo_svg_url`) in the hook and verdict scenes. Size it small and tasteful — a watermark, not a dominant block.
3. **Colors**: use `primary_color` for headlines and key numbers, `secondary_color` for accents/glows, `accent_color` for CTAs and secondary highlights. Keep body text neutral (`#CBD5E1` / `#FFFFFF`).
4. **Typography**: use `typography_display` for big headlines (kicker/title), `typography_ui` for captions and small text. Match the brand's font weights.
5. **Motion**: use `design_system.motion_style` for GSAP easing — `spring`/`elastic` = `back.out`/`elastic.out`; `linear`/`bounce` = `power3.out`/`bounce.out`. Never mix easing styles across beats.
6. **Visual elements**: add brand-appropriate icons (chart bars, meter fills, checkmarks, pill badges) rendered in the brand's accent colors. Every number spoken must appear on screen in the brand palette.
7. **Verify against research.md**: every color/font/motion choice must trace back to the researched brand assets, not invented.

- Every anchor verbatim from inspect output.
- Verdict card has `footer` with sources + date.