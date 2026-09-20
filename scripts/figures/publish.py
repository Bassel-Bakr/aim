"""Write generated figures to docs/figures, where the aim_figures extension picks them up.

A generator used to rewrite its SVG inside the page, which made every regeneration churn the whole
page and buried the prose. Now it writes one file per figure and the page keeps a marker line.

A figure no page asks for is an error rather than a stray file: the marker and the generator have
to agree, or a renamed figure leaves an orphan on disk and a hole in the page.
"""
import re
from pathlib import Path

from names import published

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
FIGURES = DOCS / "figures"


def _markers() -> dict[str, Path]:
    """Every figure the pages ask for, and which page asks."""
    found: dict[str, Path] = {}
    for page in DOCS.rglob("*.md"):
        for name in re.findall(r"<!--\s*aim:figure\s+([A-Za-z0-9_-]+)\s*-->",
                               page.read_text(encoding="utf-8")):
            found[name] = page
    return found


def publish(figures: dict[str, str]) -> None:
    """Write each figure under its published name, after checking a page asks for it."""
    FIGURES.mkdir(parents=True, exist_ok=True)
    wanted = _markers()
    named = {published(name): svg for name, svg in figures.items()}
    missing = sorted(set(named) - set(wanted))
    if missing:
        raise SystemExit("no page has a marker for: " + ", ".join(missing))
    for name, svg in named.items():
        (FIGURES / f"{name}.svg").write_text(svg.strip() + "\n", encoding="utf-8", newline="\n")
    print(f"{len(named)} figures written to {FIGURES.relative_to(ROOT)}")
