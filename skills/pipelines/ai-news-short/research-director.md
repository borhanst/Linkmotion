# Research Director - AI News Short

Research one AI news story or model release. Verify, don't guess.

## Input

Topic, URL, or vague description from the user.

## Tools

- `web_search` (required)
- `youtube_source` (optional, for transcript-sourced stories)

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
5. Record the channel and upload date if available (the transcript itself has no
   dates - check the page).
6. Pull 2-3 corroborating sources from `web_search` about the video's topic.

## Process

1. **Pick a primary source.** For AI news / model releases: the lab's blog post,
   model card, pricing/docs page, or arXiv/HF page. Never narrate a number,
   date, benchmark, or price you did not see on a page you are about to show.
2. **Find 2-3 corroborating sources.** Credible third-party coverage.
3. **Record the publication date.** Say it in the video ("announced October 2026").
4. **Extract the core claim.** One sentence the whole Short hangs on.
5. **Note the visual needs.** What pages, tables, code, or screenshots must we
   capture?

## Output: `projects/<slug>/research.md`

```markdown
# Research - <slug>

## Primary source
- URL:
- Title:
- Publication date:

## Core claim
<one sentence>

## Data points (verified)
1. <fact> - <URL>
2. <fact> - <URL>

## Corroborating sources
- <URL>
- <URL>

## Visual needs
- <page to capture>
- <table to spotlight>
```

## Success criteria

- At least 2 cited data points with URLs.
- `primary_source` set.
- Publication date recorded.