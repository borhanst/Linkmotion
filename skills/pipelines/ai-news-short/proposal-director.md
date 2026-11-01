# Proposal Director - AI News Short

Turn the research brief into one sharp concept + production plan.

## Input

`projects/<slug>/research.md`

## Tools

None required (all local / free).

## Process

1. **Pick the single sharpest angle.** A Short has room for one idea, not a
   topic survey. From the research, choose the most surprising or most useful
   angle.
2. **Write the concept.** One sentence: the hook, the promise, the audience.
3. **Plan production.** Beats, scene types, assets needed, duration target
   (45-75s).
4. **Estimate cost.** Zero-key path by default. Itemize if any paid tool is used.
5. **Log decisions.** Append to `decision_log.jsonl`.

## Output: `projects/<slug>/proposal.json`

```json
{
  "slug": "...",
  "pipeline": "ai-news-short",
  "format": "short",
  "concept_id": "angle-1",
  "angle": "one sentence describing the sharpest angle",
  "target_duration_sec": 60,
  "concept_options": [
    {"concept_id": "angle-1", "angle": "...", "why": "..."},
    {"concept_id": "angle-2", "angle": "...", "why": "..."}
  ],
  "production_plan": {
    "beats": 5,
    "scene_types": ["card", "web", "card"],
    "assets": ["narration", "page captures"],
    "render_runtime": "remotion"
  },
  "cost_estimate": {"total_usd": 0.0, "line_items": []},
  "approval": {"status": "pending", "notes": ""}
}
```

## Decision log entries

- `category: "angle_selection"`, `subject: "Story angle"`, the chosen angle and
  the alternatives considered.
- `category: "render_runtime"`, `subject: "Composition engine"`, "remotion".

## Success criteria

- At least 1 concept option.
- `selected_concept` references a valid `concept_id`.
- Duration inside 45-75s.