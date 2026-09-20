"""Regenerates the figures cited by docs/articles/metronome-method.md.

    python scripts/figures/metronome/build.py

Each figure is written to docs/figures, where the page's own marker line picks it up at build time.
Edit the drawing code in diagrams.py; the page keeps the caption under each figure.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import diagrams as d  # noqa: E402
from publish import publish  # noqa: E402


def main() -> None:
    publish({"settle": d.settle(), "ramp": d.ramp(), "beat": d.beat(), "tension": d.tension()})


if __name__ == "__main__":
    main()
