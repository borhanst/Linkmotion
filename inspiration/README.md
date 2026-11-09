# Inspiration Bank (git-ignored)

Standalone per-user reference library at the project root - **never pushed to
git** (see `.gitignore`).

```
manifest.json            THE list file: read this FIRST to pick by need
<owner>/<slug>/          one inspiration = record + profile (+ analysis, frames)
```

Ideas live here; rendered styles (playbooks `styles/*.yaml`) stay tracked, but
the deconstructions they came from do not.

## Sources

| kind | example |
|---|---|
| video | a YouTube video URL |
| channel | a YouTube channel URL |
| raw | a local video file (frame-sampled) |
| description | free text describing the look/technique wanted |

One analysis can produce several inspirations (different `type` and / or
different `ratio`). Every create rewrites `manifest.json`; load what a stage
needs with `lib.inspiration.load_for()`.

Agent docs: `skills/core/inspiration.md`.
