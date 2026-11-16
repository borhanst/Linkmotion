# Script Director - AI News Short

Write the narration for a 45-75s Short. One idea, delivered fast.

## Input

`projects/<slug>/proposal.json`, `projects/<slug>/research.md`

## Tools

None required.

## Process

1. **Hook in the first 2 seconds** - a number or a claim, not "hello everyone".
2. **The hook is a full summary of the whole video, completed in under 45
   seconds.** Compress the entire arc into the opening: what just happened ->
   what it is -> the key specs/numbers -> an honest verdict tease -> what proof
   this video shows (tests, demo, benchmark). By the time the hook ends the
   viewer already knows the outcome and why they should keep watching. No
   greeting, no preamble, no "in this video".
3. **2-4 quick delivery beats** - the proof, the explanation, the twist
   (the hook promised these; now show them in full).
4. **Payoff / punchline / key takeaway.**
5. **Loop-friendly last beat** - matching color/composition so a viewer who
   reaches the end and the video loops doesn't feel a hard seam.

## Structure

| Beat | Purpose | ~sec |
|---|---|---|
| 1 | Hook - full-video summary: claim + what it is + key numbers + verdict tease + proof preview | 30-40 (MUST finish < 45) |
| 2 | What it is - the primary source | 6-10 |
| 3 | How / why it works | 8-12 |
| 4 | Catch / limits | 6-10 |
| 5 | Verdict + loop | 6-10 |

The hook may span beats 1-2 as one continuous summary; whatever the beat
count, the summary itself must be fully delivered before the 45-second mark.

## Rules

- 35-150 words total at ~140-150 wpm. The hook summary alone is the majority
  of the script - front-load it.
- One idea per beat, 15-30 words each; the hook summary beats chain together
  as one continuous breath.
- Every sentence has something happening on screen - the hook must cut fast:
  announcement post -> logo -> demo screenshot -> benchmark, no static card
  lingering.
- Say numbers as spoken ("GPT five point five"); on-screen form in `caption`.
- No recap beat, no subscribe-ask scene, no multi-section arc.
- Write the narration in the voice of the channel - conversational, concrete.
- Hook voice pattern (model this): open with the news as fact ("Looks like
  <team> just shipped <thing>"), compress the specs into one flowing sentence,
  then an honest-verdict tease ("I don't want to lie to you - I was slightly
  disappointed"), then the proof preview ("I had early access, re-ran my
  tests").

## Output: `projects/<slug>/script.json`

```json
[
  {"beat": 1, "title": "Hook - full summary", "narration": "...", "est_duration_sec": 35, "purpose": "hook"},
  {"beat": 2, "title": "What it is", "narration": "...", "est_duration_sec": 8, "purpose": "delivery"}
]
```

## Success criteria

- 3-6 beats.
- `total_duration_sec` inside 45-75.
- Hook in the first 2 seconds AND the full-video summary delivered before 45s.