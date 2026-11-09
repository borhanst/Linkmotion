# Inspiration Library

Core skill: the agent's bank of deconstructed video references. Inspirations
are the INPUT to style work (playbooks, style-engine DNA) - separate from
output styles. Everything lives in the **standalone root folder
`/inspiration/`** and is **never pushed to git** (per user request; see
`.gitignore`).

## Library layout

```
inspiration/
    manifest.json   THE list file - the agent reads this FIRST
    <owner>/
        <slug>/
            inspiration.json   validated record (schemas/inspiration.json)
            profile.md         the deconstruction (technique to study, never copy)
            analysis.json      raw analysis output that produced this inspiration
            frames/            sampled reference frames (style analysis only)
```

Every user has MULTIPLE inspirations. One analyzed source can yield SEVERAL
different inspirations - e.g. from one channel analysis: a **visual** one
(framing, palette, motion), a **structure** one (hook -> story loop -> outro),
a **pacing** one, a **thumbnail** one - each with its own ratio (9:16 / 16:9 /
1:1) and tags.

## The manifest (read before styling anything)

`inspiration/manifest.json` lists EVERY inspiration across every user, flat,
with repo-root-relative `profile` / `frames` pointers. Each entry carries the
need selectors: `ratio`, `type`, `tags`, `best_for`, `linked_playbooks`.

Agent workflow:
1. READ `inspiration/manifest.json` first (or query
   `lib.inspiration.read_manifest()`).
2. Pick by need: ratio = the video's target ratio, type = what the stage
   styles (structure -> script, visual -> beats, thumbnail -> metadata).
3. Open the picked entry's `profile` and `linked_playbook` before styling.

Programmatic need-loading does the 1-2-3 for you:

```python
from lib.inspiration import load_for
picks = load_for(ratio="9:16", type="visual", best_for="ai-news-short")
for p in picks:
    profile = (p["folder"] + "/profile.md")   # read before styling
```

Scoring: exact `type` +3, exact `ratio` +3 (auto +1), `best_for` hit +2 each,
every shared `tag` +1, proven playbook +1.

CLI:

```bash
python -m ai_news_agent inspiration list --ratio 9:16
python -m lib.inspiration list --type structure --best-for ai-news-long --json
python -m lib.inspiration show worldofai-signal-cards --owner borhan
python -m lib.inspiration manifest      # rebuild the manifest list file
```

## Creating inspirations (4 source kinds)

```bash
# 1. One video link
python -m lib.inspiration analyze --kind video --ref "https://youtube.com/watch?v=..."
# 2. A channel link
python -m lib.inspiration analyze --kind channel --ref "https://youtube.com/@handle"
# 3. A raw local video
python -m lib.inspiration analyze --kind raw --ref path/to/clip.mp4 --count 6
# 4. A description (no source - the user describes the look/technique wanted)
python -m lib.inspiration analyze --kind description --ref "dark cards, red boxes..."
```

`analyze` returns the raw material ONLY. The agent then performs the
deconstruction: from the analysis output, decide the different inspiration
records to make and write each `profile.md` yourself (see
`inspiration/worldofai-channel-profile.md` as the template). Register one
record per derived inspiration:

```bash
python -m lib.inspiration create <name> --kind channel --ref <url> \
    --ratio 9:16 --type visual --tag <t1> --tag <t2> \
    --best-for ai-news-short --profile profile.md --frames frames/ --note "..."
```

(`create` rewrites `inspiration/manifest.json` automatically.)

Or split one analysis into several records in code:

```python
from lib.inspiration import create_split
create_split("WorldofAI", source_kind="channel", source_ref=url,
             analysis=analysis_dict, splits=[
    {"name": "worldofai visual system", "type": "visual", "ratio": "16:9",
     "tags": ["dark-stage", "evidence-cards"], "best_for": ["ai-news-long"]},
    {"name": "worldofai story loop", "type": "structure", "ratio": "16:9",
     "tags": ["hook", "story-loop", "outro-stack"], "best_for": ["ai-news-long"]},
])
```

Fields: `type` = full | structure | visual | pacing | hooks | thumbnail | tone.
`ratio` = 9:16 | 16:9 | 1:1 | 4:5 | auto ("auto" adapts to any project).
`best_for` = pipeline names (ai-news-short, ai-news-long, model-release) or
formats (short, long). `linked_playbooks` names a style playbook already
derived from this inspiration (e.g. insider-force-ceramic).

## When to load which

| Need | Load |
|---|---|
| Proposal stage, style direction | `load_for(best_for=<pipeline>)` top 2-3, read their profiles |
| Storyboard / script structure | `type="structure"` for the pipeline's ratio |
| Beat HTML / motion authoring | `type="visual"` for the project's ratio |
| Metadata stage (titles, thumbnail) | `type="thumbnail"` and/or `type="hooks"` |

## Rules

- INSPIRATION ONLY. Study technique; never reuse wording. Run
  `lib/originality.check()` on any derived title/script before presenting.
- `frames/` are for deconstruction - never ship them into a produced video.
- The folder is git-ignored: treat contents as local-only knowledge; do not
  reference inspiration paths from tracked files except `styles/README.md`
  and `styles/worldofai-signal.yaml` (full_profile pointer).
- New inspiration = new folder + `inspiration.json` (manifest rebuilds
  itself); never append to another user's bench (`owner` is the first path
  segment).
