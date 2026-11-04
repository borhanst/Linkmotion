# Research & Design: YouTube → Twitter → Plan

## Purpose
Teach the agent how to take a YouTube URL, extract its description, find any Twitter links mentioned, fetch those Twitter posts, and produce a video production plan grounded in both sources.

## Input
- A YouTube URL (or "based on this video: <URL>")
- Optional: specific Twitter handle or tweet ID to focus on

## Step 1 — Fetch the YouTube video description
Use the `youtube_source` tool to pull the video's metadata:

```bash
python -m tools.youtube_source "https://www.youtube.com/watch?v=EXAMPLE"
```

The tool returns:
- `title`: video title
- `channel`: channel name
- `description`: full video description (may contain Twitter/X links)
- `transcript`: auto-generated transcript (often empty keyless)
- `thumbnail`: video thumbnail URL

> **Important**: The transcript and description may be empty without a `youtube_data_v3_api_key`. Do not depend on them being present.

## Step 2 — Extract Twitter/X links from the description
Search the `description` field for any `x.com` or `twitter.com` URLs. Common patterns:
- `https://x.com/.../status/...`
- `https://twitter.com/.../status/...`
- `@username` handles mentioned in the text

If one or more Twitter links are found, proceed to Step 3. If none are found, fall back to Step 4 (general web search for related topics).

## Step 3 — Fetch the Twitter post(s)
For each Twitter link extracted, use the `twitter_post` tool:

```bash
python -m tools.twitter_post "https://x.com/nasa/status/2116263878807998722"
```

The tool returns a structured `TwitterPost` with:
- `author_screen_name`
- `tweet_id`
- `created_at` (if `TWITTER_BEARER_TOKEN` is set)
- `text`
- `media_urls` (image/video URLs)
- `retweet_count`, `favorite_count`, `quote_count` (with bearer token)
- `url`

The tool also produces two artifacts:
- `out/twitter_posts/<author>_<tweet_id>.html` — self-contained design card HTML
- `out/twitter_posts/<author>_<tweet_id>.png` — 640×640 PNG of the card

**Screenshot note**: The PNG captures the **official Twitter embed widget** (widgets.js rendering the real tweet UI — avatar, verified badge, fonts, counts) inside headless Chromium, so it reads as authentic Twitter in the video. If the widget cannot render (offline/blocked), the tool falls back to a faithful recreation of the post's design card. Check `screenshot_method` in the output: `twitter_widget` = real UI, `playwright_card` = recreation.

> **Enrichment**: Set `TWITTER_BEARER_TOKEN` in `.env` to get timestamps and counts. Without it, the tool still works keyless via oEmbed + page metadata.

## Step 4 — Produce a video production plan
Using the YouTube video context + Twitter post data, create a plan in the `research.md` format (see `skills/pipelines/ai-news-short/research-director.md`). The plan must include:

### Primary source
- YouTube video URL
- Twitter post URL

### Core claim
- One sentence summarizing the hook/angle the video will hang on.

### Data points (verified)
1. <fact from YouTube description> - <YouTube URL>
2. <fact from Twitter post text> - <Twitter URL>

> If `TWITTER_BEARER_TOKEN` is set, also record:
- `created_at` (publication date)
- `retweet_count`, `favorite_count`, `quote_count`

### Corroborating sources
- 2-3 `web_search` results about the topic (e.g., "new GPT release", "Claude Code architecture", etc.)

### Visual needs
- What pages, tables, code, or screenshots must we capture?
- Twitter card image (`media_urls[0]`) as a reference visual
- YouTube thumbnail as reference
- Any on-screen charts, code snippets, or UI elements discussed

### Brand & design system research (before writing script)
> Before writing a script or choosing a concept, research the brand's actual visual identity so the video looks natural and professional — not a generic template slapped with a logo (see `skills/pipelines/ai-news-short/research-director.md` § "Brand & Design System Research").

Extract:
- Brand logo SVG URL (from YouTube channel art, Twitter profile, or web search)
- Primary/secondary/accent hex colors
- Display/UI typography
- Motion style (spring/elastic/linear/bounce)

### Output: `projects/<slug>/research.md`
```markdown
# Research - <slug>

## Primary source
- URL: <YouTube URL>
- URL: <Twitter post URL>
- Title: <YouTube title>
- Publication date: <from Twitter if available, else "unknown>

## Core claim
<one sentence>

## Data points (verified)
1. <fact from YouTube description> - <YouTube URL>
2. <fact from Twitter post text> - <Twitter URL>

## Corroborating sources
- <web_search URL 1>
- <web_search URL 2>
- <web_search URL 3>

## Visual needs
- Twitter card image: <media_urls[0]>
- YouTube thumbnail: <thumbnail URL>
- <other visual elements>

## Brand & design system
- brand: <inferred from channel/twitter handle>
- logo_svg_url: <or "not found">
- primary_color: <hex or "not found">
- secondary_color: <hex or "not found">
- accent_color: <hex or "not found">
- typography_display: <font name or "not found">
- typography_ui: <font name or "not found">
- motion_style: <spring | elastic | linear | bounce | "not found">
```

## Failure modes & mitigations
| Situation | Mitigation |
|---|---|
| YouTube description empty (no `youtube_data_v3_api_key`) | Fall back to `web_search` for the video topic; use the video title as the primary source |
| No Twitter links in description | Use `web_search` to find 2-3 authoritative sources on the topic; skip the Twitter-specific sections |
| `TWITTER_BEARER_TOKEN` not set, counts/dates missing | Accept that `created_at`, `retweet_count`, etc. will be absent; still capture the tweet text and media |
| x.com blocks raw-page screenshot | `twitter_post` renders the official embed widget (real tweet UI); if that fails it falls back to a card recreation — check `screenshot_method` in the output |
| Multiple Twitter links found | Process the first one (or ask the user which to prioritize); log all found URLs in the research notes |

## Example workflow
```bash
# 1. Fetch YouTube description
python -m tools.youtube_source "https://www.youtube.com/watch?v=abc123"

# 2. Spot a Twitter link in the description, e.g.:
#   "Check out this post https://x.com/guardian/status/1234567890"

# 3. Fetch the Twitter post
python -m tools.twitter_post "https://x.com/guardian/status/1234567890"

# 4. Produce research.md manually or via the agent's planner
#    referencing both the YouTube video and the Twitter post
```
