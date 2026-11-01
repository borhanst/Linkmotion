# Remotion

Core skill: React-based programmatic video composition.

## When to use

Rendering scene components to MP4 with captions, animations, and narration
audio. Default composition engine for AI-News-Agent.

## Official skills (Layer 3)

Load these before writing scene code - they carry the correct API knowledge for
the installed version:

- `remotion-best-practices` - router; load this first, it dispatches to the rest
- `remotion-create` - creating a new Remotion project / composition
- `remotion-markup` - writing React markup (timing, sequencing, transitions,
  audio, captions, images, fonts, Lottie, effects, 3D, measuring)
- `remotion-render` - advanced rendering (transparent videos, Lambda, stills)
- `remotion-captions` - word-synced captions
- `remotion-multimedia` - trimming, cropping, metadata in-browser
- `remotion-interactivity` - Studio interactivity
- `remotion-studio` - preview workflow
- `remotion-docs` - search the Remotion docs

Do not write scene code from memory - the installed version may differ.

## Setup

```bash
npm install
npx remotion studio      # preview
npx remotion render src/Root.tsx <id> out.mp4
```

## Conventions

- One Remotion repo hosts many videos. Each video lives in
  `src/videos/<slug>/` with its own `index.tsx`, `scenes/`, `components/`.
- `src/Root.tsx` is a thin registry - one import + one line per video.
- Deleting a video = delete `src/videos/<slug>/`, `public/videos/<slug>/`,
  `projects/<slug>/`, and its one line in `Root.tsx`.
- Build ONE scene at a time. Preview before the next.
- `durationInFrames = actual_duration_sec * fps` (add a small pad).
- `<Audio src={staticFile(`videos/<slug>/audio/scene-N.mp3`)} />`.
- Motion: `src/common/motion.ts` is the one cross-video motion import.
- Determinism: every frame is a pure function of `useCurrentFrame()`. No
  wall-clock, no `requestAnimationFrame`, no CSS transitions, no `Date.now()`,
  no `Math.random()` (seeded PRNG only).

## Component reuse

Before authoring a scene from scratch, check the project's own components under
`projects/<slug>/src/remotion/<scene-id>/components/` and any shared
`components/`. Clone a fitting component and customize only what differs
(name/title/kicker, logo/brand, data from `research.md`, palette from the style
playbook). Never silently duplicate a component that already does the job.
Log the reuse to `projects/<slug>/engine_decisions.json`.

## Docs

Check `remotion.dev` for anything not verified against the installed version
before writing scene code.