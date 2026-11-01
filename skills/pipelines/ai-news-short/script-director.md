# Script Director - AI News Short

Write the narration for a 45-75s Short. One idea, delivered fast.

## Input

`projects/<slug>/proposal.json`, `projects/<slug>/research.md`

## Tools

None required.

## Process

1. **Hook in the first 2 seconds.** A number or a claim, not "hello everyone".
2. **2-4 quick delivery beats** - the proof, the explanation, the twist.
3. **Payoff / punchline / key takeaway.**
4. **Loop-friendly last beat** - matching color/composition so a viewer who
   reaches the end and the video loops doesn't feel a hard seam.

## Structure

| Beat | Purpose | ~sec |
|---|---|---|
| 1 | Hook - the claim/number | 2 |
| 2 | What it is - the primary source | 6-10 |
| 3 | How / why it works | 8-12 |
| 4 | Catch / limits | 6-10 |
| 5 | Verdict + loop | 6-10 |

## Rules

- 35-150 words total at ~140-150 wpm.
- One idea per beat, 15-30 words each.
- Every sentence has something happening on screen.
- Say numbers as spoken ("GPT five point five"); on-screen form in `caption`.
- No recap beat, no subscribe-ask scene, no multi-section arc.
- Write the narration in the voice of the channel - conversational, concrete.

## Output: `projects/<slug>/script.json`

```json
[
  {"beat": 1, "title": "Hook", "narration": "...", "est_duration_sec": 2, "purpose": "hook"},
  {"beat": 2, "title": "What it is", "narration": "...", "est_duration_sec": 8, "purpose": "delivery"}
]
```

## Success criteria

- 3-6 beats.
- `total_duration_sec` inside 45-75.
- Hook in the first 2 seconds.