# Asset Director - AI News Short

Generate every asset the storyboard needs: narration, page captures.

## Input

`projects/<slug>/storyboard.json`, `projects/<slug>/script.json`

## Tools

Required: `tts`
Optional: `browser_capture`

## Process

1. **Generate narration per beat.** One mp3 + one srt per beat. Use
   `edge-tts --voice en-US-GuyNeural --write-media <beat>.mp3 --write-subtitles <beat>.srt`.
2. **Measure real duration.** `ffprobe` each mp3 and write
   `actual_duration_sec` back into the beat.
3. **Capture page footage** for every `web` scene. Store under
   `projects/<slug>/assets/raw/web/<site-slug>/`.
4. **Build `assets/manifest.json`** - one entry per asset with source, path,
   license note, and which beats use it.

## Output: `projects/<slug>/assets/manifest.json`

```json
{
  "assets": [
    {"id": "beat-1-mp3", "type": "audio", "path": "audio/beat-1.mp3",
     "source": "edge-tts", "voice": "en-US-GuyNeural",
     "duration_sec": 2.1, "used_in_beats": [1]},
    {"id": "openai-com-shots", "type": "image", "path": "assets/raw/web/openai.com/shot-1.png",
     "source": "playwright", "url": "https://openai.com/news/gpt-5",
     "license_note": "captured from a public page", "used_in_beats": [2]}
  ]
}
```

## Rules

- Narration covers every beat.
- Word-level timestamps present for every beat.
- All file paths resolve to existing files.
- Only generate the beat currently being built unless the user asks to batch.

## Success criteria

- Schema-valid asset manifest.
- Every beat has an audio file.
- Every `web` scene has captures.