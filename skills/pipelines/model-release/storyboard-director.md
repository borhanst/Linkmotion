# Storyboard Director - Model Release

Plan visuals for a 60-120s model-release explainer.

## Input

`projects/<slug>/script.json`, `projects/<slug>/research.md`

## Tools

- `browser_capture`

## Process

1. **Inspect every page** you'll show BEFORE writing anchors.
2. **Copy anchors verbatim** from inspect output. Never invent.
3. **Watch for** cookie walls, login walls, bot checks. Don't bypass - switch to
   another source or a text-only card.
4. **Use the model-release playbook** (from `web-explainer-video-animation`):

| # | Scene | What happens |
|---|---|---|
| 1 | hook card | "[Model] just dropped" + date + one headline capability |
| 2 | announcement | url = post. `select` the lab's own headline claim sentence (attribute it) |
| 3 | what's new | 2-3 capabilities: `scroll` + `select` the phrase for each |
| 4 | benchmarks | `spotlight` the results table, then `select` 1-2 cells you discuss |
| 5 | pricing & availability | pricing page: `spotlight` the row for the new model |
| 6 | how to try it / model string | docs page `select` the model identifier |
| 7 | verdict card | 3 bullets - best for / watch out for / how it compares. `footer`: sources + date |

5. **Aspect ratio** matches the proposal (16:9 default, 9:16 for a Shorts variant).

## Output: `projects/<slug>/storyboard.json`

```json
{"settings": {"color_scheme": "dark", "voice": {"edge": "en-US-GuyNeural"},
               "output_size": [1920, 1080]},
 "scenes": [
   {"id": "hook", "type": "card", "kicker": "Just dropped", "title": "GPT-5",
    "subtitle": "OpenAI, October 2026", "narration": "..."},
   {"id": "announcement", "url": "https://openai.com/news/gpt-5", "narration": "...",
    "actions": [{"do": "scroll", "to": "heading:Highlights"},
                {"do": "select", "text": "exact text from the page", "when": "the phrase"}]},
   {"id": "verdict", "type": "card", "title": "Verdict",
    "bullets": ["best for ...", "watch out for ...", "vs GPT-4.1 ..."],
    "footer": "Sources: openai.com/news/gpt-5, October 2026"}
 ]}
```

## Success criteria

- Schema-valid storyboard.
- At least 3 scene types used.
- Verdict card has `footer` with sources + date.
- Benchmarks table spotlighted; vendor vs independent flagged on screen.
- Pricing row spotlighted; units named.