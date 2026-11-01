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

Parse the `.srt` into word entries: `{"word": "...", "start": 1.2, "end": 3.4}`.
Use these to sync on-screen captions and element entrances to the actual
spoken words.

## Pronunciation

Write numbers and names as they should be *said*: "GPT five point five",
"forty times". Put the on-screen form in `caption` if it differs.

## Voice

Default male voice: `en-US-GuyNeural`. Keep the voice name configurable - do
not bake a specific voice into reusable components.