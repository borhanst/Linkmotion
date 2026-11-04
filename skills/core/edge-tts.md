# edge-tts Narration

Core skill: male-voice narration per beat with word-level timestamps.

## When to use

Generating narration for every beat of a video. Per-beat audio files make it
possible to resync/regenerate a single beat later without re-cutting the whole
video.

## Setup

```bash
pip install edge-tts
edge-tts --list-voices | grep -i male
```

## Recipe

Use the `tts` tool (`tools/tts.py`) rather than calling the CLI by hand. It
streams through the edge-tts library with `boundary="WordBoundary"`, so the
returned `words` carry true per-word start/end offsets, and falls back to the
CLI + SRT when the library is missing.

```python
from tools.tts import TTSTool
r = TTSTool().synthesize(
    "Anthropic renamed its Max 20x plan to Ultra.",
    "projects/<slug>/audio/beat-1.mp3")
# r.words -> [{"word": "Anthropic", "start": 0.1, "end": 0.738}, ...]
```

CLI equivalent (chunk-level cues only - no true word timestamps):

```bash
edge-tts \
  --voice en-US-GuyNeural \
  --text "$(cat projects/<slug>/beat-1-narration.txt)" \
  --write-media projects/<slug>/audio/beat-1.mp3 \
  --write-subtitles projects/<slug>/audio/beat-1.srt
```

## After generation

Measure the real duration with `ffprobe` and write it back as
`actual_duration_sec`. Scene length in Remotion must be driven by the real
audio length, not an earlier estimate.

## Word-level timestamps

`TTSTool.synthesize().words` holds one entry per spoken word with its real
boundary: `{"word": "...", "start": 1.2, "end": 3.4}`. Feed them to the caption
choreography in `lib/captions.py` to show 1-2 words at a time, animated in/out
exactly on the spoken beat (see `skills/core/html-render.md` frames mode).

## Pronunciation

Write numbers and names as they should be *said*: "GPT five point five",
"forty times". Put the on-screen form in `caption` if it differs.

## Voice

Default male voice: `en-US-GuyNeural`. Keep the voice name configurable - do
not bake a specific voice into reusable components.