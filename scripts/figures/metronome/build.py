"""Regenerates the figures on docs/articles/metronome-method.md.

    python scripts/figures/metronome/build.py

Each diagram is rewritten in place inside the page, matched by its <svg>'s aria-labelledby id, so
edit the drawing code in diagrams.py and never the SVG in the page. The page keeps whatever caption
sits under each figure.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PAGE = ROOT / "docs" / "articles" / "metronome-method.md"
sys.path.insert(0, str(HERE))
import diagrams as d  # noqa: E402


def main() -> None:
    text = PAGE.read_text(encoding="utf-8")
    for name, svg in (("settle", d.settle()), ("ramp", d.ramp()), ("beat", d.beat()),
                      ("tension", d.tension())):
        pattern = re.compile(r'<svg [^>]*aria-labelledby="fig-%s-title".*?</svg>' % name, re.S)
        text, count = pattern.subn(lambda _: svg, text)
        if count != 1:
            sys.exit(f"expected one fig-{name} diagram in {PAGE.name}, found {count}")
    PAGE.write_text(text, encoding="utf-8", newline="\n")
    print(f"diagrams written to {PAGE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
