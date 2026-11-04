"""Component kit templates for the Style DNA system.

Each template is a self-contained HTML file that reads its theme exclusively
from the project's generated `style/tokens.css` (path: ../../style/tokens.css
relative to projects/<slug>/src/html/_kit/ where ensure_style clones them).

Cloning: `lib/style_engine.ensure_style()` copies every kit/*.html into
projects/<slug>/src/html/_kit/. The compose stage then copies a kit component
into src/html/<beat>/index.html and edits ONLY the content (text, data) -
never the theme. This is how every video looks different while staying
consistent within itself.

Add new components here; they'll be cloned into all new projects.
"""
