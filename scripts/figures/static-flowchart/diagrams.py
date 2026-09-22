"""Theme-aware inline SVG diagrams for the Weakness Targeted Static Flowchart article. Colours come
from the .aim-figure classes in aim.css, so each diagram follows the reader's scheme and picked
colour. build.py splices them into the page; call it rather than this module.

Each figure lives in its own module here rather than in one file, which is where the metronome page
keeps its four. Five figures with their own geometry constants, keyframe names and helpers share a
namespace badly, and the split keeps each one's constants next to the drawing that uses them. The
keyframe prefixes are what actually matter: every name a figure emits is global once the page is
rendered, so they are kept apart by hand as aimSym, aimOvr, aimDrg, aimRte and aimGrp.
"""
import sys
from pathlib import Path

# The kit sits a folder up, beside the other pages' figure code, and is not an installed package.
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

from _dragflick import dragflick  # noqa: E402,F401
from _grouping import grouping  # noqa: E402,F401
from _overflick import overflick  # noqa: E402,F401
from _route import route  # noqa: E402,F401
from _symptoms import symptoms  # noqa: E402,F401

__all__ = ["symptoms", "overflick", "dragflick", "route", "grouping"]
