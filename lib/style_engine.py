"""Per-video Style DNA engine.

Every video gets its OWN visual identity. Palette, typography pairing, motion
motif, background system, caption choreography and transition language are
generated here - deterministically seeded by the slug, but pushed away from
recently-used genes by a uniqueness ledger (styles/style_history.jsonl) so two
projects never look alike.

Usage:
    from lib.style_engine import ensure_style, generate_style
    spec = ensure_style("2026-11-foo-short", "topic ...", source_mood="tech")

Outputs (per project):
    projects/<slug>/style/design-system.md   - the spec + rationale
    projects/<slug>/style/tokens.css         - CSS variables + fonts + motif CSS
    projects/<slug>/style/style-card.html    - one-page preview of the kit
    projects/<slug>/src/html/_kit/*.html     - themed component kit clones

The compose stage clones components from the kit instead of the shared
components/html/ templates, so each video's suite is fully themed.
"""

from __future__ import annotations

import hashlib
import json
import random
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from lib.paths import ROOT, project_slug_dir

STYLES_DIR = ROOT / "styles"
LEDGER_PATH = STYLES_DIR / "style_history.jsonl"

# --------------------------------------------------------------------------- #
# Gene catalogs - curated by design, weighted for uniqueness at generation
# --------------------------------------------------------------------------- #

PALETTES: dict[str, dict[str, Any]] = {
    "aurora-dark": {
        "bg": "#07090F", "surface": "#0E1420", "text": "#F4F7FB", "muted": "#8CA0BC",
        "accent": "#34D399", "accent2": "#38BDF8", "contrast": "flashing on dark",
        "bg_gradient": ["#07090F", "#0A1B1A"], "rule": "high-contrast emerald/sky on near-black",
    },
    "ember-heat": {
        "bg": "#170A08", "surface": "#241110", "text": "#FFF4EC", "muted": "#C79B8C",
        "accent": "#FF4D3D", "accent2": "#FFB020", "contrast": "warm",
        "bg_gradient": ["#170A08", "#1F1216"], "rule": "molten orange primary on charcoal",
    },
    "cyber-paper": {
        "bg": "#F6F4EF", "surface": "#FFFFFF", "text": "#17130E", "muted": "#6E6659",
        "accent": "#E2451D", "accent2": "#1A9E8F", "contrast": "light editorial",
        "bg_gradient": ["#F6F4EF", "#EFEAE0"], "rule": "warm paper with vermilion ink accents",
    },
    "deep-ocean": {
        "bg": "#03121F", "surface": "#0B1E33", "text": "#EAF6FF", "muted": "#7FA6C4",
        "accent": "#00C2FF", "accent2": "#65FBD2", "contrast": "cool glowing",
        "bg_gradient": ["#03121F", "#062033"], "rule": "bioluminescent cyan/teal on deep navy",
    },
    "violet-noir": {
        "bg": "#0B0817", "surface": "#151026", "text": "#F5F2FF", "muted": "#9D93BE",
        "accent": "#8B5CF6", "accent2": "#F472B6", "contrast": "lux dark",
        "bg_gradient": ["#0B0817", "#160E2B"], "rule": "violet primary, pink support, deep night bg",
    },
    "sand-editorial": {
        "bg": "#FAF6EE", "surface": "#FFFFFF", "text": "#1E1B16", "muted": "#786E60",
        "accent": "#C2410C", "accent2": "#0F766E", "contrast": "warm magazine",
        "bg_gradient": ["#FAF6EE", "#F2EBDD"], "rule": "magazine paper, burnt sienna + teal accents",
    },
    "mint-lab": {
        "bg": "#EAF7F1", "surface": "#FFFFFF", "text": "#052E22", "muted": "#5B8F7D",
        "accent": "#0D9488", "accent2": "#F59E0B", "contrast": "clean light",
        "bg_gradient": ["#EAF7F1", "#DDF0E8"], "rule": "clinical mint white-lab with amber pop",
    },
    "mono-swiss": {
        "bg": "#FFFFFF", "surface": "#F4F4F4", "text": "#111111", "muted": "#6B6B6B",
        "accent": "#EC3E36", "accent2": "#111111", "contrast": "hard poster",
        "bg_gradient": ["#FFFFFF", "#F7F7F7"], "rule": "single-red Helvetica poster, huge scale",
    },
    "blueprint-tech": {
        "bg": "#06264C", "surface": "#0A3263", "text": "#E8F2FF", "muted": "#8FB6E0",
        "accent": "#9AD1FF", "accent2": "#FFD166", "contrast": "technical",
        "bg_gradient": ["#06264C", "#0A3263"], "rule": "drafting-blue with sky lines + amber markers",
    },
    "grape-pop": {
        "bg": "#1A1026", "surface": "#28183C", "text": "#F7F1FF", "muted": "#A89BC7",
        "accent": "#A855F7", "accent2": "#7DD3FC", "contrast": "playful dark",
        "bg_gradient": ["#1A1026", "#221436"], "rule": "grape purple youth brand with sky accents",
    },
}

TYPOGRAPHY: dict[str, dict[str, str]] = {
    "grotesk-modern": {
        "display": "Space Grotesk", "ui": "Inter",
        "cdn": "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;600;800&display=swap",
    },
    "sora-round": {
        "display": "Sora", "ui": "Manrope",
        "cdn": "https://fonts.googleapis.com/css2?family=Sora:wght@600;800&family=Manrope:wght@400;700&display=swap",
    },
    "editorial-serif": {
        "display": "Playfair Display", "ui": "Source Sans 3",
        "cdn": "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Sans+3:wght@400;700&display=swap",
    },
    "poster-heavy": {
        "display": "Archivo Black", "ui": "Inter Tight",
        "cdn": "https://fonts.googleapis.com/css2?family=Archivo+Black&family=Inter+Tight:wght@400;700&display=swap",
    },
    "warm-serif": {
        "display": "Fraunces", "ui": "Inter",
        "cdn": "https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700;9..144,900&family=Inter:wght@400;600&display=swap",
    },
    "wide-future": {
        "display": "Unbounded", "ui": "Inter",
        "cdn": "https://fonts.googleapis.com/css2?family=Unbounded:wght@500;800&family=Inter:wght@400;600&display=swap",
    },
    "instrument-mag": {
        "display": "Instrument Serif", "ui": "Instrument Sans",
        "cdn": "https://fonts.googleapis.com/css2?family=Instrument+Serif&family=Instrument+Sans:wght@400;700&display=swap",
    },
    "bricolage-mix": {
        "display": "Bricolage Grotesque", "ui": "Inter",
        "cdn": "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=Inter:wght@400;600&display=swap",
    },
}

MOTIFS: dict[str, dict[str, str]] = {
    "mesh-blob": {"desc": "blurred color blobs drifting behind content (dark or light)", "tone": "soft organic"},
    "grid-terminal": {"desc": "perspective grid + scanline + mono labels (dev/tech feel)", "tone": "technical"},
    "glass-layers": {"desc": "stacked frosted translucent cards with depth blur", "tone": "sleek product"},
    "neo-brutalist": {"desc": "thick borders, hard offset shadows, rotated chips, raw blocks", "tone": "loud poster"},
    "paper-ink": {"desc": "paper texture, ink strokes and hand-drawn underlines", "tone": "handcrafted"},
    "particle-links": {"desc": "rising dots connected by faint lines (tech constellation)", "tone": "networked"},
    "iso-stacks": {"desc": "isometric stacked planes with accent edge lines", "tone": "diagrammatic"},
    "gradient-swim": {"desc": "one giant animated conic/linear gradient slowly swimming", "tone": "gradient-forward"},
}

EASINGS: dict[str, dict[str, str]] = {
    "spring-pop":    {"gsap": "back.out(1.7)", "note": "default spring; elements overshoot then settle"},
    "elastic-juice": {"gsap": "elastic.out(1, 0.6)", "note": "bouncy elastic entrances for chips/cards"},
    "snappy-pro":    {"gsap": "power3.out", "note": "fast confident decel, editorial restraint"},
    "soft-drift":    {"gsap": "power2.inOut", "note": "slow two-way ease for background, snappy for fg"},
    "bounce-cheer":  {"gsap": "bounce.out", "note": "playful bounce for badges/stickers"},
}

CAPTION_STYLES: dict[str, dict[str, str]] = {
    "word-chunk": {"ui": "1-2 giant words center screen, pop in/out", "note": "best for Shorts"},
    "bottom-bar": {"ui": "phrase bar at safe-zone bottom, slides per phrase", "note": "16:9 friendly"},
    "karaoke-highlight": {"ui": "full sentence with active word color-swept", "note": "readalong feel"},
    "badge-tag": {"ui": "small boxed tags popping near speaker points", "note": "minimal narration"},
}

TRANSITIONS: dict[str, dict[str, str]] = {
    "accent-wipe":   {"ui": "accent-color panel wipes L->R covering scene change", "note": "clean rhythm"},
    "zoom-punch":    {"ui": "scene scales 1->1.06 with motion blur into next", "note": "energy hit"},
    "slide-stack":   {"ui": "next scene card slides over previous like a deck", "note": "material feel"},
    "morph-dot":     {"ui": "a circle expands from a point into the next scene bg", "note": "organic"},
}

# --------------------------------------------------------------------------- #
# Ledger - anti-repetition
# --------------------------------------------------------------------------- #

GENE_AXES = ("palette", "typography", "motif", "easing", "caption", "transition")


@dataclass
class StyleSpec:
    slug: str
    topic: str = ""
    palette: str = ""
    typography: str = ""
    motif: str = ""
    easing: str = ""
    caption: str = ""
    transition: str = ""
    colors: dict[str, str] = field(default_factory=dict)
    fonts: dict[str, str] = field(default_factory=dict)
    seed: int = 0
    created_at: str = ""

    def signature(self) -> str:
        return "|".join(
            getattr(self, axis) for axis in GENE_AXES
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_ledger() -> dict[str, dict[str, int]]:
    if not LEDGER_PATH.is_file():
        return {}
    ledger: dict[str, dict[str, int]] = {}
    for line in LEDGER_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        genes = d.get("genes", {})
        for axis, value in genes.items():
            ledger.setdefault(axis, {})
            ledger[axis][value] = ledger[axis].get(value, 0) + 1
    return ledger


def _append_ledger(spec: StyleSpec) -> None:
    STYLES_DIR.mkdir(parents=True, exist_ok=True)
    with LEDGER_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "slug": spec.slug,
            "genes": {axis: getattr(spec, axis) for axis in GENE_AXES},
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }, ensure_ascii=False) + "\n")


def _spec_path(slug: str) -> Path:
    return project_slug_dir(slug) / "style" / "spec.json"


def _save_spec(spec: StyleSpec) -> None:
    p = _spec_path(spec.slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(spec.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")


def _load_spec(slug: str) -> StyleSpec | None:
    """Load a previously persisted spec, validating its genes still exist."""
    p = _spec_path(slug)
    if not p.is_file():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    # drop unknown xyz fields, validate gene values against the catalogs
    kwargs = {
        k: d.get(k, "") for k in
        ("slug", "topic", "palette", "typography", "motif", "easing", "caption", "transition")
    }
    catalogs = {
        "palette": PALETTES, "typography": TYPOGRAPHY, "motif": MOTIFS,
        "easing": EASINGS, "caption": CAPTION_STYLES, "transition": TRANSITIONS,
    }
    for axis, catalog in catalogs.items():
        if kwargs[axis] not in catalog:
            return None                      # stale spec -> regenerate
    # rebuild colors/fonts from the catalogs (single source of truth)
    spec = StyleSpec(
        seed=d.get("seed", 0), created_at=d.get("created_at", ""), colors=d.get("colors", {}),
        fonts={**d.get("fonts", {})}, **kwargs)
    return spec


def _pick_unique(catalog: dict, ledger_axis: dict, rng: random.Random) -> str:
    """Weight each gene by 1/(1+prior uses) - least-used genes are most likely."""
    names = sorted(catalog)
    weights = [1.0 / (1.0 + ledger_axis.get(n, 0)) for n in names]
    return rng.choices(names, weights=weights, k=1)[0]


# --------------------------------------------------------------------------- #
# Generation
# --------------------------------------------------------------------------- #

def generate_style(slug: str, topic: str = "") -> StyleSpec:
    """Generate a unique StyleSpec for this slug (ledger-aware, seeded)."""
    seed = int(hashlib.sha1(slug.encode("utf-8")).hexdigest()[:8], 16) % 1_000_000
    rng = random.Random(seed)
    ledger = _load_ledger()

    spec = StyleSpec(
        slug=slug,
        topic=topic,
        seed=seed,
        palette=_pick_unique(PALETTES, ledger.get("palette", {}), rng),
        typography=_pick_unique(TYPOGRAPHY, ledger.get("typography", {}), rng),
        motif=_pick_unique(MOTIFS, ledger.get("motif", {}), rng),
        easing=_pick_unique(EASINGS, ledger.get("easing", {}), rng),
        caption=_pick_unique(CAPTION_STYLES, ledger.get("caption", {}), rng),
        transition=_pick_unique(TRANSITIONS, ledger.get("transition", {}), rng),
    )

    pal = PALETTES[spec.palette]
    spec.colors = {k: pal[k] for k in ("bg", "surface", "text", "muted", "accent", "accent2")}
    fonts = TYPOGRAPHY[spec.typography]
    spec.fonts = {"display": fonts["display"], "ui": fonts["ui"], "cdn": fonts["cdn"]}
    return spec


# --------------------------------------------------------------------------- #
# Artifact writers
# --------------------------------------------------------------------------- #

# CSS to render the chosen background motif. Applied via body::before layers.
_MOTIF_CSS: dict[str, str] = {
    "mesh-blob": """
      .motif { position:fixed; inset:0; overflow:hidden; z-index:0; pointer-events:none; }
      .motif::before, .motif::after {
        content:""; position:absolute; width:60vmax; height:60vmax; border-radius:50%;
        filter:blur(12vmin); opacity:.32;
      }
      .motif::before { background:var(--accent);  top:-25vmax; left:-20vmax; }
      .motif::after  { background:var(--accent2); bottom:-25vmax; right:-20vmax; }
    """,
    "grid-terminal": """
      .motif { position:fixed; inset:0; z-index:0; pointer-events:none;
        background-image:
          linear-gradient(var(--grid-line) 1px, transparent 1px),
          linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
        background-size: 56px 56px;
        -webkit-mask-image: radial-gradient(ellipse at 50% 40%, #000 30%, transparent 75%);
                mask-image: radial-gradient(ellipse at 50% 40%, #000 30%, transparent 75%);
      }
      .motif::after { content:""; position:absolute; inset:0;
        background:repeating-linear-gradient(0deg, transparent 0 6px, rgba(0,0,0,.16) 6px 7px);
        opacity:.18; }
    """,
    "glass-layers": """
      .motif { position:fixed; inset:0; z-index:0; pointer-events:none; }
      .motif::before { content:""; position:absolute; inset:-5%;
        background: linear-gradient(135deg, var(--accent) 0%, transparent 55%),
                    linear-gradient(315deg, var(--accent2) 0%, transparent 45%);
        opacity:.14; }
      .glass { background: color-mix(in srgb, var(--surface) 62%, transparent);
        backdrop-filter: blur(22px); border:1px solid color-mix(in srgb, var(--text) 14%, transparent);
        border-radius: var(--radius); }
    """,
    "neo-brutalist": """
      .motif { position:fixed; inset:0; z-index:0; pointer-events:none;
        background: repeating-linear-gradient(45deg, transparent 0 180px, color-mix(in srgb, var(--accent) 7%, transparent) 180px 360px); }
      .card-brutal { border: 4px solid var(--text); box-shadow: 10px 10px 0 var(--accent);
        border-radius: 0; background: var(--surface); }
      .chip-brutal { border: 3px solid var(--text); box-shadow: 5px 5px 0 var(--accent2); }
    """,
    "paper-ink": """
      .motif { position:fixed; inset:0; z-index:0; pointer-events:none; opacity:.5;
        background:
          radial-gradient(circle at 20% 30%, transparent 0 2px, var(--graindot) 2px 2.6px),
          radial-gradient(circle at 70% 60%, transparent 0 2px, var(--graindot) 2px 2.6px),
          radial-gradient(circle at 40% 80%, transparent 0 2px, var(--graindot) 2px 2.6px);
        background-size: 90px 90px, 120px 120px, 150px 150px; }
      .ink-underline { background-image: linear-gradient(90deg, var(--accent), var(--accent));
        background-repeat:no-repeat; background-size:100% 10px; background-position:0 92%; }
    """,
    "particle-links": """
      .motif { position:fixed; inset:0; z-index:0; pointer-events:none; }
      .motif i { position:absolute; width:6px; height:6px; border-radius:50%;
        background:var(--accent); opacity:.5; box-shadow:0 0 12px 4px color-mix(in srgb, var(--accent) 45%, transparent); }
    """,
    "iso-stacks": """
      .motif { position:fixed; inset:0; z-index:0; pointer-events:none; overflow:hidden; }
      .motif .plane { position:absolute; width:120vmax; height:120vmax;
        background:var(--accent); transform:rotateX(62deg) rotateZ(-45deg) translateZ(-12vmax);
        transform-origin:50% 50%; opacity:.10; }
      .motif .plane + .plane { background:var(--accent2); opacity:.07; translate:0 0 8vmax; }
    """,
    "gradient-swim": """
      .motif { position:fixed; inset:-20%; z-index:0; pointer-events:none;
        background: conic-gradient(from 210deg at 60% 40%,
          var(--bg), var(--accent) 25%, var(--accent2) 50%, var(--bg) 75%);
        filter: blur(90px) saturate(1.3); opacity:.30;
        transform: rotate(0.001deg); will-change: transform; }
    """,
}

_CDN_FONT_INJECT = (
    "  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">\n"
    "  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>\n"
)


def tokens_css(spec: StyleSpec, viewport: tuple[int, int] = (1080, 1920)) -> str:
    pal = PALETTES[spec.palette]
    dark = pal["bg"][1] < "#8"[1]  # cheap lightness proxy for grain color choice
    grain = "rgba(20,16,10,.16)" if not dark else "rgba(255,255,255,.07)"
    grid = "color-mix(in srgb, var(--accent) 18%, transparent)"
    w, h = viewport
    motif_css = _MOTIF_CSS[spec.motif]
    return f'''/* Style DNA - auto-generated by lib/style_engine.py for {spec.slug}
   signature: {spec.signature()}
   motif: {spec.motif} | easing: {spec.easing} | caption: {spec.caption} | transition: {spec.transition} */
@import url("{spec.fonts["cdn"]}");

:root {{
  --bg: {pal["bg"]};
  --bg-grad-1: {pal["bg_gradient"][0]};
  --bg-grad-2: {pal["bg_gradient"][1]};
  --surface: {pal["surface"]};
  --text: {pal["text"]};
  --muted: {pal["muted"]};
  --accent: {pal["accent"]};
  --accent2: {pal["accent2"]};
  --font-display: "{spec.fonts["display"]}", system-ui, sans-serif;
  --font-ui: "{spec.fonts["ui"]}", system-ui, sans-serif;
  --radius: 20px;
  --graindot: {grain};
  --grid-line: {grid};
}}

html, body {{ width:{w}px; height:{h}px; margin:0; padding:0; overflow:hidden;
  background:linear-gradient(160deg, var(--bg-grad-1), var(--bg-grad-2));
  color:var(--text); font-family:var(--font-ui); -webkit-font-smoothing:antialiased; }}

h1,h2,h3,.display {{ font-family:var(--font-display); }}

/* film grain + vignette */
.stage::after {{ content:""; position:absolute; inset:0; pointer-events:none; z-index:2;
  background:radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,.38) 130%); }}

/* ---- chosen motif: {spec.motif} ---- */{motif_css}
'''


KIT_DIR_NAME = "src/html/_kit"


def kit_component_prefs(spec: StyleSpec) -> dict[str, str]:
    """Per-component GSAP entrance prefs derived from the easing gene."""
    e = EASINGS[spec.easing]["gsap"]
    return {
        "entrance_ease": e,
        "drift_ease": "sine.inOut",
        "caption_ease": e,
    }


def ensure_style(slug: str, topic: str = "", viewport: tuple[int, int] = (1080, 1920)) -> dict[str, Any]:
    """Generate (or reuse) the project's style DNA and write all artifacts.

    Idempotent: the chosen StyleSpec is persisted to style/spec.json on first
    run and reused thereafter, so re-running never mutates a project's look.
    """
    spec = _load_spec(slug)
    if spec is None:
        spec = generate_style(slug, topic)
        _save_spec(spec)
    pr = project_slug_dir(slug)
    style_dir = pr / "style"
    style_dir.mkdir(parents=True, exist_ok=True)

    tokens = style_dir / "tokens.css"
    if not tokens.is_file():
        tokens.write_text(tokens_css(spec, viewport), encoding="utf-8")

    design_md = style_dir / "design-system.md"
    if not design_md.is_file():
        design_md.write_text(design_doc(spec), encoding="utf-8")

    style_card = style_dir / "style-card.html"
    if not style_card.is_file():
        style_card.write_text(style_card_html(spec, slug), encoding="utf-8")

    # Clone the shared component kit into the project, themed via tokens.css
    kit_src = ROOT / "components" / "html" / "kit"
    kit_dst = pr / KIT_DIR_NAME
    kit_dst.mkdir(parents=True, exist_ok=True)
    cloned: list[str] = []
    for tpl in sorted(kit_src.glob("*.html")):
        dest = kit_dst / tpl.name
        if not dest.is_file():
            dest.write_text(tpl.read_text(encoding="utf-8"), encoding="utf-8")
            cloned.append(dest.name)

    _append_ledger(spec)

    return {
        "spec": spec.to_dict(),
        "signature": spec.signature(),
        "tokens_css": str(tokens),
        "design_system_md": str(design_md),
        "style_card": str(style_card),
        "kit_cloned": cloned,
        "kit_dir": str(kit_dst),
    }


def design_doc(spec: StyleSpec) -> str:
    pal, fam, motif = PALETTES[spec.palette], TYPOGRAPHY[spec.typography], MOTIFS[spec.motif]
    return f"""# Style DNA - {spec.slug}

Generated by `lib/style_engine.py` (seed {spec.seed}).
Signature (recorded in the uniqueness ledger): `{spec.signature()}`

## Palette - {spec.palette}
> {pal["rule"]}
| token | hex |
|---|---|
| bg | {pal["bg"]} |
| surface | {pal["surface"]} |
| text | {pal["text"]} |
| muted | {pal["muted"]} |
| accent | {pal["accent"]} |
| accent2 | {pal["accent2"]} |

## Typography - {spec.typography}
- Display: **{fam["display"]}** (headlines, numbers)
- UI: **{fam["ui"]}** (body, captions, labels)

## Motion motif - {spec.motif}
> {motif["desc"]} ({motif["tone"]})

## Easing family - {spec.easing}
> {EASINGS[spec.easing]["note"]} (GSAP default: `{EASINGS[spec.easing]["gsap"]}`)

## Caption style - {spec.caption}
> {CAPTION_STYLES[spec.caption]["ui"]} - {CAPTION_STYLES[spec.caption]["note"]}

## Transition language - {spec.transition}
> {TRANSITIONS[spec.transition]["ui"]} - {TRANSITIONS[spec.transition]["note"]}

## Changes over time
Append-only: if the design changes mid-run, log a decision entry and append a
new StyleSpec via `generate_style` with `force=True`-style reseed - never edit
this file silently.
"""


def style_card_html(spec: StyleSpec, slug: str) -> str:
    """One-page preview: every kit component in the video's theme."""
    e = EASINGS[spec.easing]["gsap"]
    w, h = 1080, 1920
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Style Card - {slug}</title>
{_CDN_FONT_INJECT}
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<link rel="stylesheet" href="tokens.css">
<style>
  .stage {{ position:relative; z-index:1; width:{w}px; height:{h}px; padding:80px 70px; }}
  .lbl {{ font-size:26px; letter-spacing:.28em; text-transform:uppercase; color:var(--muted);
          margin:64px 0 22px; }}
  .lbl:first-child {{ margin-top:0; }}
  .kicker {{ font-size:30px; font-weight:700; letter-spacing:.22em; text-transform:uppercase; color:var(--accent2); }}
  .title {{ font-size:96px; font-weight:800; line-height:1.04; margin:18px 0 20px; }}
  .title .hl {{ color:var(--accent); }}
  .subtitle {{ font-size:38px; color:var(--muted); }}
  .stat-num {{ font-size:150px; font-weight:900; font-family:var(--font-display);
               color:var(--accent); opacity:0; font-variant-numeric:tabular-nums; }}
  .stat-lbl {{ font-size:32px; color:var(--muted); }}
  .bullets li {{ list-style:none; font-size:40px; font-weight:600; padding:16px 0;
                 display:flex; gap:20px; align-items:center; }}
  .bullets i {{ width:14px; height:14px; border-radius:50%; background:var(--accent2); display:inline-block; }}
  .panel {{ font-size:40px; padding:56px 30px; text-align:center; font-weight:800; opacity:0; }}
  .bar-wrap {{ display:flex; gap:34px; align-items:flex-end; height:400px; margin-top:70px; }}
  .bar {{ flex:1; border-radius:12px 12px 0 0; background:var(--accent2); opacity:.35; }}
  .bar.win {{ background:var(--accent); opacity:1; }}
  .badge {{ display:inline-block; font-size:26px; font-weight:800; padding:14px 26px;
            border-radius:999px; background:var(--accent); color:var(--bg); }}
</style>
</head>
<body>
  <div class="motif"><i></i><i></i><i></i><i></i><i></i><i></i></div>
  <div class="stage">
    <div class="lbl">01 · Hook card</div>
    <div class="kicker">STYLE CARD</div>
    <h1 class="title">Every video<br>gets its own <span class="hl">visual DNA</span></h1>
    <p class="subtitle">palette · typography · motif · easing · captions · transitions</p>

    <div class="lbl">02 · Stat count-up</div>
    <div class="stat-num" id="stat">0</div>
    <div class="stat-lbl">possible style combinations</div>

    <div class="lbl">03 · Bullet reveal</div>
    <ul class="bullets">
      <li><i></i>palette &amp; typography pair</li>
      <li><i></i>background motion motif</li>
      <li><i></i>caption choreography</li>
    </ul>

    <div class="lbl">04 · Compare split</div>
    <div>
      <div class="panel" style="background:var(--surface)">BEFORE</div>
      <div class="panel" style="background:var(--accent); color:var(--bg)">AFTER</div>
    </div>

    <div class="lbl">05 · Chart bars</div>
    <div class="bar-wrap">
      <div class="bar" data-h="55%"></div>
      <div class="bar" data-h="70%"></div>
      <div class="bar win" data-h="100%"></div>
      <div class="bar" data-h="40%"></div>
    </div>

    <div style="margin-top:80px">
      <span class="badge" id="badge">UNIQUE BY DESIGN</span>
    </div>
  </div>

<script>
  // Entrance language: {EASINGS[spec.easing]["note"]} -> all entrances use "{e}"
  gsap.from(".kicker", {{ duration:.5, opacity:0, y:24, ease:"{e}" }});
  gsap.from(".title",  {{ duration:.8, opacity:0, y:60, ease:"{e}" }});
  gsap.from(".subtitle", {{ duration:.6, opacity:0, y:24, delay:.45, ease:"{e}" }});

  // Stat count-up
  const target = 256000;
  const countObj = {{ v:0 }};
  gsap.set("#stat", {{ opacity:1 }});
  gsap.to(countObj, {{ v:target, duration:1.8, delay:.9, ease:"power2.out",
    onUpdate: () => document.getElementById("stat").textContent =
      Math.round(countObj.v).toLocaleString("en-US") }});

  // Bullets stagger
  gsap.from(".bullets li", {{ duration:.5, opacity:0, x:-40, stagger:.16, delay:1.4, ease:"{e}" }});

  // Panels
  gsap.to(".panel", {{ duration:.5, opacity:1, stagger:.2, delay:2.0, ease:"{e}" }});

  // Bars: height spring into dataset targets
  document.querySelectorAll(".bar").forEach(b => b.style.height = "0");
  gsap.to(".bar", {{ duration:.9, height:(i, el) => el.dataset.h,
    ease:"power3.out", delay:2.4 }});

  // Badge
  gsap.from("#badge", {{ duration:.6, opacity:0, scale:.6, ease:"{e}", delay:3.0 }});

  // Motif: gentle perpetual drift (never fully static)
  gsap.to(".motif", {{ duration:9, scale:1.06, yoyo:true, repeat:-1, ease:"sine.inOut" }});
  gsap.to(".motif i", {{ duration:7, y:-160, stagger:1.2, repeat:-1, ease:"none",
    opacity:.15, startAt:{{ y:250 }} }});
</script>
</body>
</html>'''
