# Script Director - AI News Long

Write a 7-8+ minute narration broken into 12-20 scenes.

## Input

`projects/<slug>/proposal.json`, `projects/<slug>/research.md`

## Process

Target **minimum 7-8 minutes** (~1,000-1,200+ words at ~140-150 wpm - check
the actual draft's word count against runtime, don't assume). Break into scenes;
a scene is a self-contained beat, typically 20-45 seconds each.

## Standard long-form beats (in order)

hook (first 5-10s) -> **dedicated subscribe-ask scene** -> setup/context ->
3-5 main content sections (each its own scene cluster) -> recap -> CTA/outro.

## Early subscribe-ask scene

Right after the hook lands, insert one short dedicated scene (~5-10s) where the
narration directly asks the viewer to subscribe. Frame it around the honest
observation that most people watching will never come back:

- Acknowledge it plainly: most people watching haven't subscribed, and most
  are about to keep scrolling past channels they actually like.
- Make the ask concrete and quick: one sentence telling them to hit
  subscribe/the bell now.
- Keep it under ~2 short sentences of narration.
- Mark this scene `"purpose": "subscribe_ask"`.

## Rules

- Confirm the script with the user before moving to design - scripts are
  expensive to re-record.
- Enhancement cue density: 1 per 8-10 seconds.
- Open loops at section boundaries - tease a payoff a beat before delivering it.
- **Tone:** write the narration against `skills/creative/narration-tone.md`
  (energetic first-person VO + 4-slot subscribe-ask + outro ritual; wording
  must be ours - originality check applies).

## Output

`projects/<slug>/script.md` (human-readable, with scene headers) and
`projects/<slug>/script.json` (machine-readable: `scene`, `title`,
`narration`, `est_duration_sec`, `visual_elements`, `purpose`,
`engagement_overlay`).

## Success criteria

- 12-20 scenes.
- `total_duration_sec` >= 480.
- Subscribe-ask scene present with `purpose: "subscribe_ask"`.