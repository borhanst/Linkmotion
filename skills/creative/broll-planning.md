# B-Roll Planning

How to plan supplementary footage (B-roll) from a script, decide what to source
where, and evaluate results. No stock-library APIs - everything comes from the
web, docs/articles, social posts, demo clips, or user-supplied files.

## When to Use

Planning visual assets for a video and need supplementary footage to accompany
narration, establish context, repetition, or add visual variety.

## Where B-roll Comes From

| Source | Use | Tool |
|---|---|---|
| Web image search | topic establishing shots, objects, environments | `broll` (image) |
| Social posts / screenshots | what people say, real reactions | `broll` (social) + `browser_capture` |
| Docs / articles | demo clips, product footage referenced in source | `broll` (video) + `browser_capture` |
| User-supplied files | branded assets, owned footage, screenshots | `broll` (user files) |

**Rule of thumb:** If the scene needs to look *real*, find it on the web or use
user files. If it needs to look *specific to your concept*, generate or build it.

## Extracting B-Roll Needs from a Script

Walk the script beat by beat. For each beat ask:

1. What is the narrator talking about? The subject suggests the visual.
2. Is there an enhancement cue? The script writer may have embedded
   `[B-ROLL: ...]` cues.
3. Does this beat reference something concrete? "servers in a data center" ->
   web image search for server rooms.
4. Does this beat explain an abstract concept? Build a diagram, don't search.
5. How long is the beat? Determines clip duration needed.

## Constructing Effective Web Search Queries

1. Be specific but not too specific. "aerial city skyline sunset" works.
2. Use 2-4 keywords. More words = fewer results.
3. Lead with the subject. "ocean waves" not "beautiful calm serene ocean waves".
4. Add a POV keyword: aerial, drone, close-up, macro, timelapse, slow motion.
5. Try synonyms on failure. "programmer coding" -> "developer laptop".

## Evaluating Results

Score each result 1-5:
- 5: perfect match, use immediately
- 4: good match, minor crop or trim needed
- 3: acceptable, would benefit from color grading
- 2: marginal - try different keywords first
- 1: wrong - doesn't match at all

**Threshold:** use results scoring 3+. Below 3, refine the query or switch source.

## POV Keywords

Add a POV keyword to every query. Adding POV often unlocks better matches than
refining the subject. A wrong-POV match is harder to fix than a wrong color grade.

| Scene Type | Query Template | Example |
|---|---|---|
| Establishing | `[place] [time of day] [POV]` | "tokyo skyline night drone" |
| Activity | `[person] [action] [POV]` | "scientist microscope OTS" |
| Object | `[object] [style] [POV]` | "circuit board macro top-down" |
| Nature | `[element] [quality] [POV]` | "ocean waves aerial drone" |
| Abstract motion | `[movement] [style] [POV]` | "light trails timelapse locked-off" |
| Workplace | `[setting] [activity] [POV]` | "modern office meeting handheld" |

## Failure Escalation

When web search fails (no results or all score below 3):
1. Retry with different keywords - synonyms, broader terms, different angles.
2. Try the other source type (image -> social -> video).
3. Fall back to user-supplied files if the user has them.
4. Last resort: build a generated/abstract visual.

## Integration with the Asset Pipeline

Every acquired B-roll asset gets an entry in `assets/manifest.json`:
```json
{"id": "broll-server-room", "type": "image", "source": "web-search",
 "url": "https://...", "license_note": "verify on page before use",
 "used_in_beats": [3]}
```
Record source URL and license note for each. Never claim a result is
royalty-free without checking the page it came from.