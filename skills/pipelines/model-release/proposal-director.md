# Proposal Director - Model Release

Turn the model-release research into a concept + production plan.

## Input

`projects/<slug>/research.md`

## Process

1. **Pick the angle.** Options: "it just dropped", "here's what actually
   changed", "is it worth your money", "how it compares to the last version".
   Pick the single sharpest; offer 2-3 differentiated options.
2. **Production plan.** Beats, scene types, assets, duration target (60-120s),
   render runtime.
3. **Cost estimate.** Zero-key by default.
4. **Log decisions.**

## Output: `projects/<slug>/proposal.json`

```json
{"slug": "...", "pipeline": "model-release", "format": "short",
 "model_name": "GPT-5", "lab": "OpenAI",
 "concept_options": [{"concept_id": "c1", "angle": "...", "why": "..."}],
 "selected_concept": "c1",
 "target_duration_sec": 90,
 "production_plan": {"beats": 7, "scene_types": ["card","web","card"], "render_runtime": "remotion"},
 "cost_estimate": {"total_usd": 0.0, "line_items": []},
 "approval": {"status": "pending"}}
```

## Decision log

- `angle_selection` - chosen angle + alternatives.
- `render_runtime` - "remotion".

## Success criteria

- At least 1 concept option.
- `selected_concept` references a valid `concept_id`.
- Duration inside 60-120s.