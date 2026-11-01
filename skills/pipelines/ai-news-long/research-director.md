# Research Director - AI News Long

Research an AI news topic or model release for a 7-8+ minute deep-dive.

## Tools

- `web_search`
- `youtube_source` (for transcript-sourced deep-dives)

## Transcript-sourced stories

When the user gives a YouTube URL (or says "based on this video"), use
`youtube_source` to fetch the video's description and auto-generated transcript
as context - NOT to copy:

1. `youtube_source.fetch(url)` -> title, channel, description, transcript.
2. Read the transcript only to understand the topic and what was built; do NOT
   copy or reuse its wording, script, or structure.
3. Read the description to understand the project/product being shown. Use any
   links in the description as reference sources - EXCEPT promotional/affiliate
   links, which must be ignored.
4. Plan a similar type of video on the same topic, but write a different script
   with original narration and a fresh angle.
5. Record the channel and upload date if available.
6. Pull corroborating sources from `web_search` about the video's topic.

## Process

1. **Pull the core narrative, key facts, figures**, and any claims that need
   verifying.
2. **Note natural sub-topics/beats** - candidate scene boundaries.
3. **Note visually rich material** - named products, places, diagrams, data,
   people, steps in a process.
4. **Map the content landscape** - at least 3 existing pieces on the topic.
5. **Source audience questions** from real forums, not invented.

## Output: `projects/<slug>/research.md`

Topic summary, beat list, at least 3 angles discovered (each with
`grounded_in` references), at least 5 sources cited with URLs, and a running
list of "visual needs".

## Success criteria

- At least 3 data points with URLs.
- At least 3 angles discovered, each grounded in a specific finding.
- At least 5 sources cited.