# Checkpoint Protocol

When and how to checkpoint state and request human approval.

## When to checkpoint

Checkpoint after every stage that has `checkpoint_required: true` in the
pipeline manifest. Also checkpoint before any paid or irreversible action.

## What to checkpoint

Write `projects/<slug>/progress.json`:

```json
{
  "slug": "...",
  "pipeline": "ai-news-short",
  "stage": "script",
  "current_scene": 0,
  "total_scenes": 6,
  "notes": "..."
}
```

Also write the stage's artifacts into `projects/<slug>/`.

## When to ask for approval

Ask when `human_approval_default: true` for that stage, or when a decision is
material (switch provider, switch model family, switch composition engine,
drop narration/music, change sample->batch).

## How to present

Show: what was produced, what decision is being asked, what the alternatives
are, and what happens next. One clear question.