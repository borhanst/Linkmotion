# Asset Director - AI News Long

Generate narration per scene + page captures.

## Input

`projects/<slug>/storyboard.json`, `projects/<slug>/script.json`

## Tools

Required: `tts`. Optional: `browser_capture`.

## Process

1. **Generate narration per scene** (not one giant file) with edge-tts.
2. **Measure real duration** with ffprobe -> `actual_duration_sec`.
3. **Capture page footage** for every `web` scene.
4. **Build `assets/manifest.json`** - one entry per asset with source, path,
   license note, and which scenes use it.

## Output: `projects/<slug>/assets/manifest.json`

## Rules

- Only generate the voiceover for the scene currently being built unless the
  user explicitly asks to batch-generate all narration.
- All file paths resolve to existing files.

## Success criteria

- Schema-valid asset manifest.
- Every scene has an audio file.
- Word-level timestamps present.