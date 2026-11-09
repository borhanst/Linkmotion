# Channel Profile: WorldofAI (@intheworldofai)

> **Purpose:** inspiration-only deconstruction for long-form production. Study the
> TECHNIQUE (structure, framing, pacing, visual system). **Never reuse wording** —
> run `lib/originality.check()` on any derived script and rewrite everything in our
> own voice. Profile built 2026-11-10 from `tools/channel_analysis` + transcript
> pulls + frame sampling (raw data: `/tmp/opencode/woa_*.json`).

## 1. Channel snapshot

| Metric | Value |
|---|---|
| Subscribers | 253K |
| Upload cadence | **~6.9 videos/week** (essentially daily) |
| Median duration | ~26 min |
| Duration range | 9 min (tutorials) → 46 min (news roundups) |
| Median views | ~106K; outlier: 329K ("HUGE GPT-7 BEL UPDATE!…") |
| Category | Science & Technology |
| Positioning | "Tips, tricks, guides using AI applications" — first-looks, rumors coverage, hands-on testing |

### Content formats (from latest 10 uploads)

| Format | Length | Recent example | Views |
|---|---|---|---|
| **Daily AI NEWS roundup** | 28–46 min | "NEW Claude Model Family LEAKED?! … AI NEWS" | 81K |
| **Quick-hit first look** | 10–15 min | "OpenAI's GPT-6.2 PREVIEW Is INSANE!…" | 53K |
| **"Fully Tested" deep dive** | 15–18 min | "QWEN 4 Preview IS INSANE!… (Fully Tested)" | 191K |
| **Comparison / showdown** | ~9 min | "I Tested 8 of the BEST AI Video Models!…" | 66K |
| **Sponsored tutorial** | ~9–12 min | "Grok Bot Is INSANE! AI Teammates… (Full Tutorial)" | 75K |

## 2. Script anatomy (transcript-verified)

### 2.1 Hook → CTA (news roundups, standard order)

1. **Cold open hook, no branding, no intro (0:00–1:30/2:00).** Teases *every* story
   in one rapid-fire block — "Starting off with X… Meanwhile OpenAI has… There's
   also… And here's where things get scary…" Ends with "**And there's so much
   more.**" The numbered list IS the hook: 6–10 teases, each 1–2 sentences.
2. **Mid-roll subscribe ask, ~90–120s in.** Exact formula (structure, not wording):
   - soft emotional appeal ("it would mean a lot / the world to me")
   - reason it helps ("helps me make videos for you guys day to day")
   - social proof + urgency ("the majority of you aren't subscribed")
   - combined ask (like + subscribe + bell)
3. **"Let's start things off with…"** → story block 1.

### 2.2 Story block (the ~2–4 min repeating loop)

Each story follows the same loop:
1. **Headline tease** ("potentially a new Fable 5.5 checkpoint…").
2. **Source of the leak/report** ("this new code name is listed as…", vertical
   screenshot of the finder's X post fills the screen).
3. **Interpretation + speculation:** what it means, how it compares to rival models.
4. **Community/creator voice:** quotes other X users' takes.
5. **Transition forward:** "Moving forward…", "But that's not all…", "And something
   else worth mentioning…"

### 2.3 Quick-hit format (e.g. GPT-6.2 preview, 12 min)

1. Hook = the discovery story itself: "Today while testing X, I noticed something
   interesting… which immediately led me to think…" (personal detective angle).
2. The verification method ("one suggested way to test this is simply asking the
   model…") — teaches the viewer a *technique they can try*.
3. **Subscribe ask at ~60–90s** (same formula, abbreviated), usually right before
   the demo segment ("sorry to interrupt, guys, but majority of you guys aren't
   actually subscribed").
4. Demo section = live screen share, several distinct tests (webdev prompt, game
   clone, 3D/Blender test), each with commentary.
5. Verdict + comparison against the current benchmark king ("on Opus 5.5's level,
   maybe even slightly better…").

### 2.4 Outro stack (惊人的 consistency — every video, verbatim structure)

Ends with, in this exact order:
1. Wrap line ("that's about it, guys, for today's video…")
2. Value promise ("hope you enjoyed it and got some sort of value")
3. Links promise ("I'll leave all the links that I use in today's video in the
   description below")
4. Like + subscribe + bell ask
5. **Ecosystem stack:** "take a look at the School community and the benchmark,
   take a look at our second channel, join the newsletter, join the Discord,
   follow me on Twitter"
6. "take a look at our previous videos"
7. **Motivational sign-off:** "have an amazing day, spread positivity, and I'll see
   you guys really shortly" (+ "Peace out, fellas" on some)
8. Monetization micro-CTAs (Super Thanks donation, Discord membership pitch) in a
   fixed slot *before* the final sign-off.

## 3. Tone of voice

- **First-person enthusiastic, conversational, breathless-optimistic.** Filled with
  superlatives: *insane, absolutely insane, crazy, nuts, honestly fascinating,
  mind-blowing, remarkable (used ~20+ times per video)*.
- **Audience address:** "guys" constantly; "you will see", "but you let me know what
  you guys think" — polls the audience verdict.
- **Rhetorical questions as transitions:** "which leads you to think, is this the
  Fable 5.5 or Opus 6 model?"
- **Speculation labeled honestly:** "reportedly", "rumored", "we don't actually
  know which model it is", "obviously not the exact game". Hype tone, but claims
  carry rumor-caveats.
- **Small imperfections admitted** during demos ("can't even exit the water which is
  one little small error… but aside from that everything seems proper") —
  credibility through candor.
- Sentence rhythm: short bursts + long compound run-ons; reads as energetic
  stream-of-consciousness but is clearly scripted (same outro verbatim each time).

## 4. Visual system (sampled frames)

| Element | Treatment |
|---|---|
| Base | **Dark near-black background** with soft blue/purple/orange gradients behind cards |
| Evidence cards | X posts / screenshots recreated as **styled dark cards** with the brand color of the company highlighted (orange = Anthropic, blue = OpenAI, violet = Alibaba), red rectangle annotation around the key line |
| Watermarks | "Tracked by @StatsWire • x.com/StatsWire" style attribution *inside* the card + tiny "New Model" badge |
| Tech diagrams | For infrastructure stories: full-screen dark animated diagrams (GPU racks, cold plates) with monospace labels + dashed callout lines |
| B-roll | Full-screen AI-generated game/demo footage with **subject label bottom-left in bold white** ("FABLE 5.5:", "Claude Opus 5.5") and **creator credit top-right** (@handle) |
| Coded screenshots | Config/diff screenshots on colored gradients, red/green diff lines, red-box highlight of the changed line |
| Opening | First story card appears within ~5 seconds — no logo animation, no channel intro |

## 5. Thumbnails (template system)

- Colored **border matching the company's brand color** (frame around whole thumb).
- Dark particle-wave background with glow, big **white neon-glowing headline**
  (product name), company **logo + blue verified check** top-left, small colored
  subtitle line above the headline. Extremely consistent template; only colors and
  words change. This builds channel recognition.

## 6. Titles

- 80–95 chars, **always one ALL-CAPS word** (100% of latest 30), most w/ a "?" or
  "!" twist, stacking 3–4 things ("…, & More! AI NEWS").
- Recurring format words: HUGE, LEAKED, INSANE, & More, AI NEWS, (Fully Tested),
  The ULTIMATE Showdown.

## 7. Demo-video technique (the "Fully Tested" videos — most relevant to us)

1. Multi-frontend test: same prompt thrown at 4+ different UIs/arenas.
2. **Live screen recordings** where the presenter plays *inside* the generated
   artifact (drives the game, opens water physics, finds caves) — narration reacts
   in real time: "let me just show you something. If I am to go into the water…"
3. Narration narrates *what appears on screen* ("You can see over here it has also
   added in different mobs, different tree types…") — screen and script are locked.
4. Comparison to the established benchmark ("something that kind of mimics what I
   was seeing with the early Opus or Fable models").
5. Honest flaw-spotting mid-demo.
6. Rumor-correction segment near the end adds trust ("I believe that is 100% a false
   rumor…").

## 8. Twitter/X posts & screenshots

- Source-of-truth habit: every story is anchored to **one visible artifact** — an X
  post by the finder, a config file diff, a benchmark listing, a news quote
  (CNBC-style cards for mainstream coverage).
- X posts are shown as both raw vertical screenshots and re-styled dark cards with
  highlight annotations.
- Their own X account is part of the outro CTA stack; community X posts become the
  B-roll (with credit).

## 9. Mapping to our long-form pipeline (`ai-news-long`)

- **Research:** one primary visible artifact per story (our `web_search.fetch` +
  `browser_capture` of the actual source satisfies their "show the receipt" rule).
- **Script:** adopt their skeleton — rapid-fire multi-tease hook → mid-roll ask at
  ~90s → story loop (artifact → interpretation → speculation → transition) →
  outro stack. Rewrite all language; our tone can be calmer but must keep
  first-person energy + audience address + rhetorical-question transitions.
- **Storyboard:** dark cards in brand color per company, red-box annotation keys,
  full-screen B-roll with bold bottom-left subject label and top-right credit,
  animated diagrams over monospace labels for infra stories.
- **Compose/HTML beats:** the news video of theirs is effectively our beat system —
  a "card reveal" beat, a "zoom to highlight" beat, a "B-roll full-screen" beat. Our
  `lib/captions.py` chunks handle their caption style gap (they don't burn captions;
  we should — it's a differentiator).
- **Publish:** title in their DNA (one CAPS keyword, 3–4 stacked topics, "?" or
  "!") but original; thumbnail = brand-colored border + glowing white headline
  template can be reproduced via `metadata` tool; outro links block + sign-off.

## 10. 7–8 min long-form template (structural, not worded)

| Beat | Time | Content |
|---|---|---|
| Hook | 0:00–0:35 | 3–5 teases in one breath, end with "and more" |
| CTA #1 | 0:35–0:50 | like+subscribe ask (helps channel + "so you stay updated") |
| Story loop ×3–5 | 0:50–6:30 | ~70–90s each: artifact on screen → what it means → limit/reasoning → transition |
| Q&A/value add | 6:30–7:10 | one honest caveat or mini-lesson, invite comment verdict |
| CTA #2 | 7:10–7:35 | links block + community stack + previous videos |
| Sign-off | 7:35–7:50 | gratitude + positivity sign-off + teases next upload |

Keep facts verifiable (golden rule: ground every claim in a page we fetched and
show), keep tone original, keep the *rhythm*, not the words.
