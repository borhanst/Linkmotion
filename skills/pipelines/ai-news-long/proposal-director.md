# Proposal Director - AI News Long

Turn the research brief into 3 differentiated concepts + production plan.

## Input

`projects/<slug>/research.md`

## Process

1. **Generate 3 genuinely different concepts** - different structure, hook,
   and audience. Each grounded in a specific research finding.
2. **Production plan** reflects real tool availability from preflight.
3. **Cost estimate** itemized and honest.
4. **Log decisions** to `decision_log.jsonl`.

## Output: `projects/<slug>/proposal.json`

```json
{"slug": "...", "pipeline": "ai-news-long", "format": "long",
 "concept_options": [{"concept_id": "c1", "angle": "...", "structure": "...", "audience": "...", "why": "..."}],
 "selected_concept": "c1",
 "target_duration_sec": 540,
 "production_plan": {"scenes": 16, "scene_types": ["card","web","media","social"], "render_runtime": "remotion"},
 "cost_estimate": {"total_usd": 0.0, "line_items": []},
 "approval": {"status": "pending"}}
```

## Decision log

- `angle_selection` - chosen angle + alternatives.
- `render_runtime` - "remotion".

## Success criteria

- At least 3 concept options, genuinely different.
- `selected_concept` references a valid `concept_id`.
- `approval.status` is "approved" or "approved_with_changes".