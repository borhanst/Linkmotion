# Research Director - AI News Short

Research one AI news story or model release. Verify, don't guess.

## Input

Topic, URL, or vague description from the user.

## Tools

- `web_search` (required)
- `twitter_post` (required, see "Official X posts" below)
- `youtube_source` (optional, for transcript-sourced stories)

## Official X posts (first-party verification)

Most AI news is announced on X before (or instead of) a blog post. An official
post from the lab/company account is a **first-party primary source** — its text
and timestamp are more accurate than any third-party recap. Always research it:

1. **Find the post URL** with `web_search`, e.g. `site:x.com/<lab-handle> <topic>`
   or `"<topic>" site:x.com` (watch for reposts — prefer the lab's own account,
   the researcher who authored the work, or the official product account).
2. **Fetch it** with the `twitter_post` tool:
   ```bash
   python -m tools.twitter_post "https://x.com/<author>/status/<id>" --screenshot
   ```
   The tool works keyless via oEmbed; with `TWITTER_BEARER_TOKEN` set in `.env`
   it also returns `created_at`, retweet/like/reply/quote counts.
3. **Use it as verified data**: quote numbers, dates, and claims from the tweet
   text exactly as written, and cite the tweet URL for each. The `--screenshot`
   PNG (official embed widget) doubles as an on-screen proof visual.
4. Cross-check the tweet against the blog post / model card. If they disagree,
   the more primary page wins and you record the discrepancy in research notes.

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
   model card, pricing/docs page, official X announcement post, or arXiv/HF page.
   Never narrate a number,
   date, benchmark, or price you did not see on a page you are about to show.
2. **Fetch the official X post** (see "Official X posts" above) and treat its
   text + timestamp as first-party evidence.
3. **Find 2-3 corroborating sources.** Credible third-party coverage.
4. **Record the publication date.** Say it in the video ("announced October 2026").
5. **Extract the core claim.** One sentence the whole Short hangs on.
6. **Note the visual needs.** What pages, tables, code, or screenshots must we
   capture?

## Output: `projects/<slug>/research.md`

```markdown
# Research - <slug>

## Primary source
- URL:
- Title:
- Publication date:

## Official X post
- URL: <x.com/<author>/status/<id>, or "not found">
- Author/handle:
- Publication date: <created_at from twitter_post, or "unknown">
- Engagement: <retweets/likes/quotes if TWITTER_BEARER_TOKEN set>
- Screenshot: <out/twitter_posts/... .png path from --screenshot, or "not captured">

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
- Twitter card PNG: <official embed screenshot, doubles as on-screen proof>
```

## Success criteria

- At least 2 cited data points with URLs.
- `primary_source` set.
- Official X post fetched and cited (or a research note explaining why none
  exists for this story — e.g. pre-announcement leaks, no official account).

## Lessons learned (YouTube-source remakes)

When the user says "make a video based on this YouTube URL" and wants a **different script and visual**:

1. `youtube_source.fetch(url)` reliably returns `title`, `channel`, and `thumbnail`, but `transcript` and `description` are often **empty** (keyless oEmbed/timedtext endpoints are limited). Do not depend on the transcript.
2. Always supplement with `web_search` to find 2-3 corroborating sources and verify every number/date/price you will narrate. Ground claims in pages you actually capture (browser_capture).
3. Record the channel and upload date from the watch page/oEmbed; cite the primary source (lab blog / help center / pricing page) in research.md and the verdict footer.
4. Do not copy the source video's wording or structure. Write an original hook and angle; use the source only for topic discovery.

### Output (research.md) additions
- `primary_source`: the lab/help-center/pricing URL you will show on screen.
- `transcript_available`: boolean (true/false) — whether youtube_source returned a transcript.
- `supplement_sources`: 2-3 web_search URLs used to verify claims.
- Publication date recorded.

## Brand & Design System Research (before any video plan)

Before writing a script or choosing a concept, research the brand's actual visual identity so the video looks natural and professional — not a generic template slapped with a logo.

### 1. Find the brand's real design assets
- **Logo SVG**: Search the brand's site for an SVG logo (press kit, brand assets, footer, `brand.svg`, `logo.svg`, or GitHub org page). Prefer the official vector mark over a screenshot.
- **Color combination**: Extract the brand's primary/secondary/accent colors from its website CSS, press kit, or design tokens. Record them as hex values (e.g. Claude purple `#A855F7`, amber `#F59E0B`).
- **Typography**: Note the brand's display and UI fonts from its site (Inter, Space Grotesk, etc.) and whether it uses bold/heavy weights for headlines.
- **Motion style**: Look for the brand's existing video ads, product demos, or landing-page animations. Note easing (spring vs linear), transition types (slide, scale, fade), and whether it uses 3D, glassmorphism, or flat 2D.

### 2. What to capture in research.md
Add a `design_system` block:

```markdown
## Design System
- brand: <company name>
- logo_svg_url: <URL to official SVG logo, or "not found">
- primary_color: <hex>
- secondary_color: <hex>
- accent_color: <hex>
- dark_bg: <hex for video background>
- typography_display: <font name>
- typography_ui: <font name>
- motion_style: <spring | elastic | linear | bounce>
- reference_urls: [<brand site>, <press kit>, <brand video>]
- visual_elements: [<icon set>, <chart style>, <card treatment>]
```

### 3. Rules for professional look
- **Use the actual brand logo SVG**, never a low-res PNG screenshot or a hand-drawn substitute.
- **Use the brand's real hex colors** for backgrounds, accents, and text — do not invent a palette.
- **Match the brand's motion language**: if the brand uses springy bouncy UI, use `back.out`/`elastic` GSAP easing; if it uses clean corporate fades, use `power3.out` with opacity only.
- **One dominant brand color + one accent**, never a rainbow. Keep the rest dark/neutral so the brand color pops.
- **Safe zones**: keep essential text inside the center 80% horizontally and clear of the bottom ~15-20% (Shorts UI overlays).