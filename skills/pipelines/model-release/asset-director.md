# Asset Director - Model Release

Generate narration per beat + page captures.

## Input

`projects/<slug>/storyboard.json`, `projects/<slug>/script.json`

## Tools

Required: `tts`. Optional: `browser_capture`.

## Process

1. **Generate narration per beat** with edge-tts.
2. **Measure real duration** with ffprobe -> `actual_duration_sec`.
3. **Capture page footage** for every `web` scene. Store under
   `projects/<slug>/assets/raw/web/<site-slug>/`.
4. **Build `assets/manifest.json`** - one entry per asset with source, path,
   license note, and which beats use it.

## Output: `projects/<slug>/assets/manifest.json`

## Rules

- All file paths resolve to existing files.
- Word-level timestamps present for every beat.
- Only generate the beat currently being built unless the user asks to batch.

## Success criteria

- Schema-valid asset manifest.
- Every beat has an audio file.
- Every `web` scene has captures.