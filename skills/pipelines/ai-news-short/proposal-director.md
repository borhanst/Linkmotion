# Proposal Director - AI News Short

Turn the research brief into one sharp concept + production plan.

## Input

`projects/<slug>/research.md`

## Tools

None required (all local / free).

## Process

1. **Pick the single sharpest angle.** A Short has room for one idea, not a
   topic survey. From the research, choose the most surprising or most useful
   angle.
2. **Write the concept.** One sentence: the hook, the promise, the audience.
3. **Plan production.** Beats, scene types, assets needed, duration target
   (45-75s).
4. **Estimate cost.** Zero-key path by default. Itemize if any paid tool is used.
5. **Log decisions.** Append to `decision_log.jsonl`.

## Output: `projects/<slug>/proposal.json`

```json
{
  "slug": "...",
  "pipeline": "ai-news-short",
  "format": "short",
  "concept_id": "angle-1",
  "angle": "one sentence describing the sharpest angle",
  "target_duration_sec": 60,
  "concept_options": [
    {"concept_id": "angle-1", "angle": "...", "why": "..."},
    {"concept_id": "angle-2", "angle": "...", "why": "..."}
  ],
  "production_plan": {
    "beats": 5,
    "scene_types": ["card", "web", "card"],
    "assets": ["narration", "page captures"],
    "render_runtime": "remotion"
  },
  "cost_estimate": {"total_usd": 0.0, "line_items": []},
  "approval": {"status": "pending", "notes": ""}
}
```

## Decision log entries

- `category: "angle_selection"`, `subject: "Story angle"`, the chosen angle and
  the alternatives considered.
- `category: "render_runtime"`, `subject: "Composition engine"`, "remotion".

## Success criteria

- At least 1 concept option.

## Design system selection (concept stage)
Pick the visual system during proposal, not after scripting. Reference `research.md` → `design_system`.

1. **Confirm brand assets exist** — logo SVG URL, primary/secondary/accent hex colors, typography names. If the logo SVG is not found, plan a text-based wordmark using the brand's display font and colors instead of faking a logo.
2. **Choose motion style** from `design_system.motion_style` (spring/elastic/linear/bounce). This dictates GSAP easing in every beat.
3. **Record the palette** in `proposal.production_plan.design_system`:
   ```json
   "design_system": {
     "brand": "Anthropic",
     "logo_svg_url": "https://.../claude-logo.svg",
     "primary_color": "#A855F7",
     "secondary_color": "#F59E0B",
     "accent_color": "#06B6D4",
     "dark_bg": "#050508",
     "typography_display": "Inter",
     "typography_ui": "Inter",
     "motion_style": "spring"
   }
   ```
4. **Apply consistently**: every scene uses the same bg color, accent color, font family, and easing. Do not mix palettes across beats.
5. **Log the decision** in `decision_log.jsonl` with category `design_system`.

- `selected_concept` references a valid `concept_id`.
- Duration inside 45-75s.