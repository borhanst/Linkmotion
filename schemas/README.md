# JSON Schemas for AI-News-Agent artifacts.

Schemas live in this directory as real JSON Schema files. Each is referenced by
the pipeline manifests and enforced by the reviewer skill (`skills/meta/reviewer.md`).

Validate with the helper in `lib/reviewer.py`:

```python
from lib.reviewer import validate_artifact
validate_artifact("research_brief", instance)  # raises ValidationError on failure
```

Or directly:

```bash
python -c "import json, jsonschema; jsonschema.validate(instance, schema)"
```

| Artifact | Schema file | Stage | Required fields |
|---|---|---|---|
| research_brief | `research_brief.json` | research | `primary_source`, `data_points` (>=2) |
| proposal | `proposal.json` | proposal | `concept_options` (>=1), `selected_concept`, `target_duration_sec` |
| script | `script.json` | script | `beats` (>=1), `total_duration_sec` |
| storyboard | `storyboard.json` | storyboard | `settings`, `scenes` (>=3) |
| asset_manifest | `asset_manifest.json` | assets | `assets` (>=1, each needs `id`/`type`/`path`) |
| render_report | `render_report.json` | compose | `out_mp4`, `ok` |
| publish_log | `publish_log.json` | publish | `titles` (>=1), `tags` |
| broll | `broll.json` | assets (broll) | `query`, `results` |

Cross-field rules that JSON Schema cannot express (e.g. `selected_concept` must
reference a valid `concept_id`, every beat must have an audio file) are checked
by the reviewer's semantic checks in `lib/reviewer.py`.