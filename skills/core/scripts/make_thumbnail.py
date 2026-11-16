#!/usr/bin/env python3
"""Generate one 1280x720 thumbnail in the "Receipts" layout.

Generic: content and palette come from CLI args / the target project's
style/tokens.css. See skills/core/thumbnail-style.md. Requires Pillow.
"""
import argparse
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
# Generic fallback only; projects should pass --tokens to use their own palette.
FALLBACK = {
    "bg": (26, 16, 38), "surface": (40, 24, 60), "text": (247, 241, 255),
    "muted": (168, 155, 199), "accent": (168, 85, 247), "accent2": (125, 211, 252),
}
TOKEN_KEYS = ("bg", "surface", "text", "muted", "accent", "accent2")


def load_palette(path: str | None) -> dict[str, tuple[int, int, int]]:
    palette = dict(FALLBACK)
    if not path:
        return palette
    css = Path(path).read_text(encoding="utf-8")
    for key in TOKEN_KEYS:
        m = re.search(rf"--{key}\s*:\s*#([0-9a-fA-F]{{6}})", css)
        if m:
            h = m.group(1)
            palette[key] = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    return palette


def font(size: int, display_path: str | None = None) -> ImageFont.FreeTypeFont:
    candidates = [display_path] if display_path else []
    candidates += [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for path in candidates:
        if path and Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def cover(img: Image.Image, fx: float, fy: float) -> Image.Image:
    iw, ih = img.size
    scale = max(W / iw, H / ih)
    img = img.resize((int(iw * scale), int(ih * scale)), Image.LANCZOS)
    nw, nh = img.size
    left, top = int((nw - W) * fx), int((nh - H) * fy)
    return img.crop((left, top, left + W, top + H)).convert("RGBA")


def overlay(bg: tuple[int, int, int]) -> Image.Image:
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for x in range(W):
        d.line([(x, 0), (x, H)], fill=(*bg, int(244 - 96 * (x / W))))
    return ov


def shadowed(d, xy, text, fnt, fill):
    x, y = xy
    d.text((x + 4, y + 5), text, font=fnt, fill=(0, 0, 0))
    d.text((x, y), text, font=fnt, fill=fill)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capture", required=True, help="project-approved image")
    p.add_argument("--title", required=True, help="model name / topic, 1 word")
    p.add_argument("--sub", required=True, help="2-4 word payoff")
    p.add_argument("--badge", required=True, help="one real number from the video")
    p.add_argument("--source-label", required=True, help="project source + date")
    p.add_argument("--tokens", help="path to the project's style/tokens.css")
    p.add_argument("--display-font", help="optional bold display font .ttf")
    p.add_argument("--focus-x", type=float, default=0.5)
    p.add_argument("--focus-y", type=float, default=0.5)
    p.add_argument("--out", required=True)
    a = p.parse_args()

    c = load_palette(a.tokens)
    base = Image.alpha_composite(cover(Image.open(a.capture), a.focus_x, a.focus_y),
                                 overlay(c["bg"]))
    d = ImageDraw.Draw(base)

    for y in range(156, 520):
        t = (y - 156) / 364
        col = tuple(int(c["accent"][i] * (1 - t) + c["accent2"][i] * t) for i in range(3))
        d.line([(72, y), (82, y)], fill=(*col, 255))

    f_title = font(112, a.display_font)
    f_sub = font(56, a.display_font)
    f_badge = font(44, a.display_font)
    f_small = font(22)
    shadowed(d, (104, 150), a.title, f_title, c["text"])
    shadowed(d, (108, 292), a.sub, f_sub, c["accent2"])

    bb = d.textbbox((0, 0), a.badge, font=f_badge)
    bw, bh = bb[2] - bb[0], bb[3] - bb[1]
    d.rounded_rectangle((92, 386, 124 + bw, 410 + bh), radius=16,
                        fill=c["surface"], outline=c["accent"], width=3)
    d.text((108, 396), a.badge, font=f_badge, fill=c["accent2"])
    d.text((104, H - 56), a.source_label, font=f_small, fill=c["muted"])

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(out, "PNG", optimize=True)
    print(f"wrote {out} ({W}x{H})")


if __name__ == "__main__":
    main()
