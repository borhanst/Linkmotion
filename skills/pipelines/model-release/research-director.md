# Research Director - Model Release

Research a new LLM / model release. Verify against primary sources.

## Tools

- `web_search`
- `twitter_post` (see "The lab's X announcement post" below)
- `youtube_source` (for transcript-sourced announcements)

## Transcript-sourced stories

When the user gives a YouTube URL (e.g. a recorded announcement talk), use
`youtube_source` to fetch the video's description and auto-generated transcript
as context - NOT to copy:

1. `youtube_source.fetch(url)` -> title, channel, description, transcript.
2. Read the transcript only to understand the topic and what was announced; do
   NOT copy or reuse its wording, script, or structure.
3. Read the description to understand the project/product being shown. Use any
   links in the description as reference sources - EXCEPT promotional/affiliate
   links, which must be ignored.
4. Plan a similar type of video on the same topic, but write a different script
   with original narration and a fresh angle.
5. Record the channel and upload date if available.
6. Pull corroborating sources from `web_search` about the video's topic.

## Process

1. **Find the lab's announcement post** - the primary source.
2. **Find the lab's X announcement post** - officially announced model releases
   almost always have a first-party post from the lab or CEO/researcher account.
   Search `site:x.com/<lab-handle> <model name>`, then fetch it:
   ```bash
   python -m tools.twitter_post "https://x.com/<author>/status/<id>" --screenshot
   ```
   Quote capability claims, dates, and links from the tweet text exactly as
   written and cite the tweet URL. The `--screenshot` PNG (official embed
   widget) is an authentic on-screen proof visual. If the tweet and blog post
   disagree, the blog/model card wins — record the discrepancy.
3. **Find the model card / system card / docs.**
4. **Find the pricing page.**
5. **Find a benchmarks table** (in the post or card). Flag vendor-reported vs independent.
6. **Record the publication date.** Say it in the video (`created_at` from the
   X post is exact when `TWITTER_BEARER_TOKEN` is set).
7. **Spell the model name exactly** as on the page.

## Pages, in priority order

announcement post -> model card -> pricing page -> benchmarks table -> (optional)
Hugging Face page, API docs "models" page, credible third-party review.

## Output: `projects/<slug>/research.md`

```markdown
# Research - <slug>

## Primary source
- URL: <announcement post>
- Title:
- Publication date:

## Official X post
- URL: <x.com/<author>/status/<id>, or "not found">
- Author/handle:
- Publication date: <created_at from twitter_post, or "unknown">
- Screenshot: <out/twitter_posts/... .png path, or "not captured">

## Model
- Name (exactly as on the page):
- Lab:
- Model string / identifier:

## Data points (verified)
1. <headline claim> - <URL>
2. <context window / modality / agentic capability> - <URL>
3. <benchmark score> - <URL>  [vendor-reported | independent]
4. <pricing> - <URL>

## Corroborating sources
- <URL>

## Visual needs
- announcement post (scroll + select headline)
- benchmarks table (spotlight)
- pricing row (spotlight)
- model identifier (select from docs)
```

## Success criteria

- At least 3 data points with URLs.
- `primary_source` set.
- Official X announcement post fetched and cited (or a research note explaining
  why none exists).
- `model_name` spelled exactly as on the page.
- Publication date recorded.