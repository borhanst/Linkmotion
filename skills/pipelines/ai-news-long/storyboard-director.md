# Storyboard Director - AI News Long

Plan visuals for every scene of a 7-8+ minute video.

## Input

`projects/<slug>/script.json`, `projects/<slug>/research.md`

## Tools

- `browser_capture`

## Process

1. **Inspect every page** you'll show BEFORE writing anchors.
2. **Copy anchors verbatim** from inspect output.
3. **Plan per-scene visuals**: background, foreground elements (rule of thirds),
   camera/motion, on-screen text and entrance timing, transition in/out.
4. **Palette & gradient** - chosen to fit the topic, not a generic default.
   One dominant color, 1-2 supporting tones, one accent.
5. **Subscribe-ask scene** - large/centered subscribe button or bell, held for
   the scene's full ~5-10 seconds.
6. **Engagement overlays** - pick 2-3 scenes total (not every scene), clearly
   after and separate from the subscribe-ask scene. Corner popup, ~3-4s window,
   spring pop-in, colors from the palette.
7. **Pacing** - pattern interrupt roughly every 10-20 seconds.

## Output: `projects/<slug>/design.md` + `projects/<slug>/storyboard.json`

Design file: palette (exact hex), per-scene visual plan, motion picks from the
repo's Motion graphics system, transition picks (chapter wipe 12f, within
chapter mask-slice 8f, into outro fade-to-ink 20f - never a default crossfade).

## Success criteria

- Full script duration covered, no gaps.
- Visual variety: no 3+ consecutive scenes of same type.
- Every anchor verbatim from inspect output.
- Subscribe-ask scene present.
- 2-3 engagement overlays placed after the subscribe-ask scene.