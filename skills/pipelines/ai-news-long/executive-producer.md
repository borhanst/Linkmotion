# Executive Producer - AI News Long

Orchestrates the full 7-stage long-form pipeline. Reads the manifest, runs
preflight, dispatches to each stage director, enforces quality gates.

## Stages in order

1. research-director -> 2. proposal-director -> 3. script-director ->
4. storyboard-director -> 5. asset-director -> 6. compose-director ->
7. publish-director

## Before each stage

1. Confirm `projects/<slug>/progress.json` is at the right stage.
2. Read `skills/pipelines/ai-news-long/<stage>-director.md`.
3. Confirm required input artifacts exist.
4. Run preflight: `python -m tools.tool_registry`.

## After each stage

1. Run the reviewer checklist (`skills/meta/reviewer.md`).
2. Write `projects/<slug>/review-<stage>.md`.
3. If `human_approval_default: true`, present and ask.
4. Update `progress.json`.
5. Checkpoint.

## Never

Skip a stage. Generate assets without reading the stage director skill. Call
tools directly without checking their skill. Bypass preflight, checkpoints, or review.