# Script Director - Model Release

Write the narration for a 60-120s model-release explainer.

## Input

`projects/<slug>/proposal.json`, `projects/<slug>/research.md`

## Process

Target **60-120 seconds** (~140-150 wpm). 6-9 beats, each 8-15s.

## Standard beats (in order)

1. **Hook** - "[Model] just dropped" + date + one headline capability. First 5s.
2. **Announcement** - the lab's own headline claim, attributed ("Anthropic says...").
3. **What's new** - 2-3 capabilities: context window, modalities, agentic/coding, safety.
4. **Benchmarks** - spotlight the results table; say which benchmark and who ran it;
   flag vendor-reported unless independent.
5. **Pricing & availability** - spotlight the row; say units ("per million tokens"),
   where it's available (API, app, cloud).
6. **How to try it / model string** - select the model identifier from docs.
7. **Verdict** - 3 bullets: best for / watch out for / how it compares to the
   previous version. Footer: sources + date.

## Rules

- Model name spelled exactly as on the page.
- Every number visible on screen when spoken.
- Don't compare to competitors using numbers from different sources unless
  the page does.
- Say numbers as spoken ("GPT five point five", "forty times").
- One CTA at most, at the end.
- Vendor claims attributed; independent benchmarks flagged.

## Output: `projects/<slug>/script.json`

```json
[
  {"beat": 1, "title": "Hook", "narration": "...", "est_duration_sec": 5, "purpose": "hook"},
  {"beat": 2, "title": "Announcement", "narration": "...", "est_duration_sec": 12, "purpose": "delivery"}
]
```

## Success criteria

- 6-9 beats.
- `total_duration_sec` inside 60-120.
- Hook in the first 5 seconds.
- Vendor claims attributed.