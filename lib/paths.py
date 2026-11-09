"""Project layout helpers - single source of truth for where things live."""

from __future__ import annotations

from pathlib import Path

# Project root is the directory that contains this file's grandparent.
ROOT: Path = Path(__file__).resolve().parent.parent


def project_root() -> Path:
    return ROOT


def pipeline_dir() -> Path:
    return ROOT / "pipeline_defs"


def projects_dir() -> Path:
    return ROOT / "projects"


def skills_dir() -> Path:
    return ROOT / "skills"


def styles_dir() -> Path:
    return ROOT / "styles"


def inspiration_dir(owner: str | None = None) -> Path:
    """Git-ignored inspiration bank root (or one user's bench)."""
    base = styles_dir() / "inspiration"
    return base / owner if owner else base


def schemas_dir() -> Path:
    return ROOT / "schemas"


def scripts_dir() -> Path:
    return ROOT / "scripts"


def out_dir() -> Path:
    return ROOT / "out"


def project_slug_dir(slug: str) -> Path:
    """One folder per produced video - everything about it lives here."""
    return projects_dir() / slug


def video_src_dir(slug: str) -> Path:
    return ROOT / "src" / "videos" / slug


def video_static_dir(slug: str) -> Path:
    return ROOT / "public" / "videos" / slug


def ensure_dirs() -> None:
    for d in (projects_dir(), out_dir(), schemas_dir(), scripts_dir()):
        d.mkdir(parents=True, exist_ok=True)