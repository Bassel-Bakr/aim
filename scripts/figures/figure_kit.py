"""Pieces every page's diagrams need, so no two figure scripts disagree about them.

A page's own drawing code lives in its folder, next to the build.py that splices it into the page.
What sits here is only what more than one page uses: who made the diagrams, the authorship block that
travels inside a copied SVG, and the few primitives whose shape readers recognize across pages, such
as a crosshair or a lane's label.

Add something here once a second page needs it, not in advance.
"""
from collections.abc import Callable, Sequence
from typing import Any

AUTHOR = "Bassel Bakr"
SOURCE = "https://github.com/Bassel-Bakr/aim"
LICENSE = "https://creativecommons.org/licenses/by-sa/4.0/"


def metadata() -> str:
    """Authorship inside each SVG, so a copied diagram still names its author, source and licence."""
    return ('<metadata><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#">'
            f'<cc:Work rdf:about=""><dc:creator>{AUTHOR}</dc:creator><dc:source>{SOURCE}</dc:source>'
            f'<cc:license rdf:resource="{LICENSE}"/></cc:Work></rdf:RDF></metadata>')


def text(x: float, y: float, s: str, cls: str = "fig-ink", anchor: str = "middle",
         size: int = 15, weight: int = 600, middle: bool = False) -> str:
    """A line of text. With `middle`, y is the centre of the line rather than its baseline, which is
    what a label inside a box wants: eyeballing the baseline leaves it a pixel or two low."""
    baseline = ' dominant-baseline="central"' if middle else ""
    return (f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="{weight}"{baseline}>{s}</text>')


def smooth(u: float) -> float:
    """Smoothstep: 0 to 1 with both ends eased, for a value that starts and stops rather than jumps."""
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def keyframes(name: str, values: Sequence[Any], fmt: Callable[[Any], str],
              prop: str = "transform") -> str:
    """Keyframes from one value per frame, dropping any frame whose value matches both neighbours,
    since linear timing between equal values changes nothing."""
    text = [fmt(v) for v in values]
    last = len(text) - 1
    parts = [f"{i / last * 100:.4g}%{{{prop}:{v}}}" for i, v in enumerate(text)
             if i in (0, last) or not (text[i - 1] == v == text[i + 1])]
    return f"@keyframes {name}{{{''.join(parts)}}}"


def lane_label(x: float, y: float, name: str, note: str = "") -> str:
    """A lane's name and a short note on one line, top-left inside its panel. The fig-name and fig-note
    classes let aim.css enlarge them on phones, where a fitted diagram scales its text down. A lane
    whose panel is already crowded can leave the note out."""
    tail = (f'<tspan dx="10" font-size="13" font-weight="500" class="fig-muted fig-note">{note}</tspan>'
            if note else "")
    return (f'<text x="{x}" y="{y}"><tspan font-size="16" font-weight="700" class="fig-ink fig-name">{name}</tspan>'
            f'{tail}</text>')


def crosshair(cls: str, x: float, y: float) -> str:
    """A small tight crosshair: a ring with four ticks that cross it, drawn in the lane's tension
    colour. It has to read at a glance against a target dot, so it stays smaller than one."""
    r = 8
    return (f'<circle cx="{x}" cy="{y}" r="{r}" class="{cls}" stroke-width="2.2" fill="none"/>'
            f'<path d="M{x - r - 5} {y}H{x - r + 4}M{x + r - 4} {y}H{x + r + 5}'
            f'M{x} {y - r - 5}V{y - r + 4}M{x} {y + r - 4}V{y + r + 5}" class="{cls}" stroke-width="2.2"/>')
