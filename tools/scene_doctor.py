"""Scene doctor: catch broken beat HTML BEFORE rendering.

Checks the failure modes that historically caused user-visible defects and
cost re-render rounds:

1. tokens.css reachable from the HTML's directory AND :root vars present
   (symptom when broken: white background, fallback fonts, invisible accents)
2. every <img> src resolves to an existing file
   (symptom: empty browser frames, missing captures)
3. GSAP loaded + a drivable timeline exists
   (symptom: frames mode errors, or everything stuck at CSS opacity:0)
4. elements pre-hidden with CSS opacity:0 must be revealed by a
   .to(opacity:1) tween - a .from(opacity:0) tween on a CSS-hidden element
   animates 0 -> 0 and the element never appears
5. burned caption chunks anchored to one line (position:absolute + translateX)
   (symptom: caption "paragraph" stacking at different heights)

Usage:
    python -m tools.scene_doctor projects/<slug>/src/html/beat-1/index.html
    python -m tools.scene_doctor projects/<slug>/src/html/   # whole dir

Exit code 1 on any FAIL.

Add a check for every new failure mode the moment it costs a re-render.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _resolve(href: str, html_path: Path) -> Path | None:
    """Resolve a relative href against the HTML file's directory, then repo root."""
    if not href or href.startswith(("http://", "https://", "data:", "//")):
        return None
    p = (html_path.parent / href).resolve()
    if p.is_file():
        return p
    alt = (ROOT / href).resolve()
    return alt if alt.is_file() else None


def doctor(html_path: str | Path) -> tuple[list[str], int]:
    """Return (report lines, fail count) for one beat HTML."""
    hp = Path(html_path).resolve()
    lines: list[str] = []
    fails = 0

    def add(status: str, msg: str) -> None:
        nonlocal fails
        if status == "FAIL":
            fails += 1
        lines.append(f"[{status}] {msg}")

    if not hp.is_file():
        return [f"[FAIL] html not found: {hp}"], 1
    html = hp.read_text(encoding="utf-8")

    # 1) local stylesheets resolve + define :root vars
    links = re.findall(r'<link[^>]*rel="stylesheet"[^>]*href="([^"]+)"', html)
    for href in links:
        if href.startswith(("http://", "https://", "//")):
            add("PASS", f"CDN stylesheet: {href.split('/')[-1][:40]}")
            continue
        tgt = _resolve(href, hp)
        if tgt is None:
            add("FAIL", f"stylesheet not reachable: {href} "
                        f"(beat dirs need ../../../ to reach projects/<slug>/...)")
            continue
        css = tgt.read_text(encoding="utf-8", errors="ignore")
        if "--accent" in css and ":root" in css:
            add("PASS", f"stylesheet OK: {href}")
        else:
            add("WARN", f"stylesheet reachable but looks tokenless: {href}")
    if not links:
        add("WARN", "no local stylesheet linked - theme will not apply")

    # 2) images resolve
    imgs = re.findall(r'<img[^>]*src="([^"]+)"', html)
    for src in imgs:
        if src.startswith(("http://", "https://", "//")):
            add("WARN", f"remote image (networkidle + determinism risk): {src[:60]}")
        elif _resolve(src, hp) is not None:
            add("PASS", f"image OK: {src.split('/')[-1]}")
        else:
            add("FAIL", f"image NOT FOUND: {src} "
                        f"(404 renders as an empty hole in the scene)")

    # 3) gsap present + timeline
    if "gsap.min.js" in html or "gsap" in html:
        add("PASS", "GSAP referenced")
    else:
        add("FAIL", "no GSAP - frames mode cannot drive the page")
    if re.search(r"gsap\.timeline\(\)", html):
        add("PASS", "gsap.timeline() found")
    else:
        add("WARN", "no gsap.timeline() - nothing to drive?")

    # 4) CSS opacity:0 elements must be revealed with .to(opacity:1)
    hidden = {}
    for m in re.finditer(r'([.#][\w.#:\s>+()-]*?)\{([^}]*)\}', html):
        if re.search(r'(?<![\w-])opacity:\s*0\s*(;|})', m.group(2)):
            for cls in re.findall(r'\.([\w-]+)', m.group(1)):
                hidden.setdefault(cls, m.group(0)[:60])
    to_t, from_t = set(), set()
    for m in re.finditer(r'\.(to|from)\(\s*"([^"]+)"[^)]*?opacity:\s*(1|0)\b', html, re.DOTALL):
        bucket = to_t if m.group(3) == "1" else from_t
        # tween targets may be classes or ids; a hidden selector is covered
        # when any of its classes, or the id it is addressed by, appears
        bucket.update(c.lstrip(".") for c in re.findall(r'\.([\w-]+)', m.group(2)))
        bucket.update(re.findall(r'#([\w-]+)', m.group(2)))
    for cls, css_snip in sorted(hidden.items()):
        if cls in to_t:
            add("PASS", f".{cls} pre-hidden, revealed via .to(opacity:1)")
        elif cls in from_t:
            add("FAIL", f".{cls} pre-hidden in CSS but revealed via .from(opacity:0) "
                        f"-> animates 0 to 0, never appears. "
                        f"Remove opacity:0 from the CSS or switch the tween to .to(opacity:1)")
        else:
            add("WARN", f".{cls} pre-hidden in CSS with no opacity reveal tween found")

    # 5) burned captions anchored to one line
    if "cap-track" in html:
        if re.search(r'\.cap-track \.cap-chunk \{[^}]*position:\s*absolute', html, re.DOTALL):
            add("PASS", "caption chunks anchored (absolute, single line)")
        else:
            add("FAIL", "caption chunks are inline-blocks -> they stack like a "
                        "paragraph at different heights. Re-burn after the "
                        "lib/captions.py fix or add the .cap-chunk anchor override.")
        # override must precede the caption script for gsap transform parsing
        style_end = html.find("</style>", html.find("cap-chunk { position:absolute")) \
            if "cap-chunk { position:absolute" in html else -1
        script_pos = html.find("<script>", html.find("CAPTION-TRACK"))
        if style_end != -1 and script_pos != -1 and style_end > script_pos:
            add("FAIL", "caption anchor override comes AFTER the caption script - "
                        "gsap parses transforms before the CSS applies and drops "
                        "translateX(-50%). Move the override into <head>.")

    return lines, fails


def _iter_targets(target: str) -> list[Path]:
    p = Path(target)
    if p.is_dir():
        return sorted(p.glob("*/index.html")) or sorted(p.glob("*.html"))
    return [p]


def main(argv: list[str] | None = None) -> int:  # pragma: no cover
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print(__doc__)
        return 2
    total_fails = 0
    for tgt in args:
        for hp in _iter_targets(tgt):
            lines, fails = doctor(hp)
            print(f"--- {hp}")
            for ln in lines:
                print(" ", ln)
            total_fails += fails
    print(f"\nscene_doctor: {total_fails} FAIL(s)")
    return 1 if total_fails else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
