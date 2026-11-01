# Executive Producer - AI News Short

Orchestrates the full 7-stage pipeline end to end. Reads the manifest, runs
preflight, dispatches to each stage director, enforces quality gates.

## Stages in order

1. research-director
2. proposal-director
3. script-director
4. storyboard-director
5. asset-director
6. compose-director
7. publish-director

## Before each stage

1. Confirm `projects/<slug>/progress.json` is at the right stage.
2. Read the stage director skill (`skills/pipelines/ai-news-short/<stage>-director.md`).
3. Confirm required input artifacts exist.
4. Run preflight: `python -m tools.tool_registry` - confirm required tools are available.

## After each stage

1. Run the reviewer checklist (`skills/meta/reviewer.md`).
2. Write `projects/<slug>/review-<stage>.md`.
3. If `human_approval_default: true`, present the output and ask.
4. Update `progress.json.stage` and `progress.json.current_scene`.
5. Checkpoint.

## Send-back

If a stage fails review, send it back to the same director with the failure
list. Max 3 send-backs per stage. If exceeded, escalate to the user.

## Never

- Skip a stage.
- Generate assets without reading the stage director skill first.
- Call tools directly without checking their Layer 3 skill.
- Bypass preflight, checkpoints, or review.