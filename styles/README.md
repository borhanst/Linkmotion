# Style Playbooks for AI-News-Agent

Each playbook defines visual language: typography, color palette, motion
style, audio profile, and asset constraints. Validated against
`schemas/styles/playbook.schema.json`.

## clean-professional
Category: motion-graphics. Mood: polished, trustworthy.
Best for: corporate, educational, SaaS.

## flat-motion-graphics
Category: motion-graphics. Mood: energetic, bold.
Best for: social media, TikTok, startups.

## minimalist-diagram
Category: whiteboard. Mood: focused, technical.
Best for: technical deep-dives, architecture.

## premium-minimalist
Category: minimalist. Mood: calm, editorial.
Best for: investor updates, expert explainers, product narratives.

## insider-force-ceramic
Category: ceramic-diagram. Mood: clean, engineered, AI-premium.
Best for: AI news shorts, tool breakdowns, list formats.
User-approved reference style deconstructed from @InsiderForce (YouTube).
See `insider-force-ceramic.reference.md` + `inspiration/borhan/insiderforce-ceramic-diagram/frames/`
(six sampled reference frames). Layout grammar + blur-in motion stay fixed
per user request; accent hue varies per video for uniqueness-ledger.

## worldofai-signal
Category: signal-card. Mood: dark, glowing, energetic AI-newsroom hype.
Best for: ai-news-long, long-form roundups, model first-looks.
Reference style deconstructed from @intheworldofai (YouTube) on user request.
See `worldofai-signal.reference.md` + `inspiration/borhan/worldofai-signal-cards/frames/` and the full
channel profile in `inspiration/worldofai-channel-profile.md`.
Fixed identity: dark stage + dark evidence cards with red-box highlights,
brand-color-coded accents, labeled B-roll, fast open. Gradient hue pairing and
heavy card-type mix vary per video (uniqueness ledger). Pair narration with
`skills/creative/narration-tone.md` - originality rules apply to wording.

## Style inspirations (input bank)

`inspiration/` (git-ignored, standalone root folder) holds the deconstructed
references these playbooks came from - a per-user "inspiration bank" whose
`manifest.json` the agent reads first. New inspirations are
created from a video link, a channel link, a raw local video, or a plain
description (`skills/core/inspiration.md`), each file with its own ratio and
type, and are loaded at the proposal stage via `lib.inspiration.load_for()`.
The references above already exist there: `insider-force-ceramic` (9:16
visual) and `worldofai-signal` (16:9 full deconstruction).