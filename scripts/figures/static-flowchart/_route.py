"""One walk through the chart the page reproduces further down, drawn in this site's own language.

The source chart holds roughly forty-five nodes and colour-codes five kinds of them. This figure
draws one path of five, and carries the kind in the *shape* rather than in the colour: a cloud for
the symptom, a diamond for the issue, a rounded box for the technique, a plain box for the scenario
and a double-edged box for the result. That is deliberate. The palette here has no purple and no
orange, and blue already means something fixed in these figures, so borrowing it for a "result"
node on a page about clicking tension would say the wrong thing. Colour is left to carry meaning:
red on the issue, green on the technique, the key wash on the thing aimed at, ink on the rest.

The reveal is staggered on purpose. A reader who watches one connector draw and one node land learns
the order to read the real chart in, which is the only thing this figure is trying to teach.
"""
import sys
from pathlib import Path

# The kit sits a folder up, beside the other pages' figure code, and is not an installed package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figure_kit import lane_label, metadata, smooth, text  # noqa: E402

W = 760
H = 532
CX = 380.0
# One full pass and then a hold, so the finished path stays on screen long enough to read before it
# clears. The last node lands at 4.7s, which leaves 2.3s of stillness.
T = 7.0
STEP = 1.05                                         # between one node arriving and the next
RISE = 0.5                                          # how long a node takes to fade and lift in
DRAW = 0.42                                         # how long the connector above it takes to draw
LIFT = 12.0                                         # how far below its place a node starts
FRAMES = 8                                          # eased frames in the fade
DRAW_FRAMES = 6                                     # eased frames in the draw
RECT_W = 356.0                                      # the three boxes, near enough the cloud's width
GAP = 30.0                                          # a node's bottom to the next node's top
LINE = 20.0                                         # the drawn part of a connector, before its head
LABEL_X = 172.0                                     # where the kind of node is named, right-aligned
GLOSS_X = 588.0                                     # where the question it answers sits, left-aligned
PANEL_TOP = 46.0
PANEL_BOTTOM = 514.0

# top, height, kind, what the node says, the question it answers. The content is the article's own
# example: an overflick, the cause it points to, the fix, a scenario given by its shape rather than
# by a name that will rot, and what the fix should show up as.
ROWS: tuple[tuple[float, float, str, str, str], ...] = (
    (62.0, 68.0, "Symptom", "it sails past the target", "what you saw"),
    (160.0, 84.0, "Issue", "braking too late", "what it points to"),
    (274.0, 54.0, "Technique", "commit and stop", "what to change"),
    (358.0, 54.0, "Scenario", "one wall · two targets · short travel", "what to play"),
    (442.0, 54.0, "Result", "fewer corrections", "what to expect"),
)


def cloud(top: float) -> str:
    """The symptom node: a flat-bottomed puff of elliptical arcs, all swept the same way round.

    Three bumps over the top and three under the bottom, so the middle of the lower edge is the low
    point of a bump rather than the cusp between two, and the connector leaves from the outline
    instead of from inside it."""
    xs, yt = CX - 164, top + 22
    return (f'<path d="M{xs} {yt}a 52 22 0 0 1 104 0a 60 22 0 0 1 120 0a 52 22 0 0 1 104 0'
            'a 16 15 0 0 1 0 30a 55 16 0 0 1 -110 0a 54 16 0 0 1 -108 0a 55 16 0 0 1 -110 0'
            'a 16 15 0 0 1 0 -30Z" class="fig-panel fig-muted-stroke" stroke-width="2"/>')


def diamond(top: float, h: float) -> str:
    """The issue node. Red, because this is the thing that is wrong, and the one place on the path
    where the reader is being told a cause rather than shown a fact."""
    cy = top + h / 2
    return (f'<path d="M{CX} {top}L{CX + 150} {cy}L{CX} {top + h}L{CX - 150} {cy}Z" '
            'class="fig-panel fig-tense-stroke" stroke-width="2.4"/>')


def rounded(top: float, h: float) -> str:
    """The technique node. Green, and rounded far enough that it cannot be mistaken for the plain
    box under it at a glance."""
    return (f'<rect x="{CX - RECT_W / 2}" y="{top}" width="{RECT_W}" height="{h}" rx="26" '
            'class="fig-panel fig-balanced-stroke" stroke-width="2.4"/>')


def plain(top: float, h: float) -> str:
    """The scenario node: the only filled shape on the path, in the key wash used everywhere else on
    this site for the thing being aimed at."""
    return (f'<rect x="{CX - RECT_W / 2}" y="{top}" width="{RECT_W}" height="{h}" '
            'class="fig-target"/>')


def doubled(top: float, h: float) -> str:
    """The result node. A plain box with a second edge inside it, which is the usual way a chart
    marks the end of a path, and the only thing separating it from the scenario box above."""
    return (f'<rect x="{CX - RECT_W / 2}" y="{top}" width="{RECT_W}" height="{h}" '
            'class="fig-panel fig-ink-stroke" stroke-width="2"/>'
            f'<rect x="{CX - RECT_W / 2 + 5}" y="{top + 5}" width="{RECT_W - 10}" '
            f'height="{h - 10}" class="fig-ink-stroke" fill="none" stroke-width="1.4"/>')


def shape(index: int, top: float, h: float) -> str:
    """The outline for one step, which is what tells the reader which kind of node it is."""
    if index == 0:
        return cloud(top)
    if index == 1:
        return diamond(top, h)
    if index == 2:
        return rounded(top, h)
    if index == 3:
        return plain(top, h)
    return doubled(top, h)


def content(index: int, top: float, h: float, label: str) -> str:
    """The line inside a node, in the ink that goes with its outline. Text takes the darker ink of
    its hue, which is what the -ink variants in aim.css exist for."""
    if index == 0:
        return text(CX, top + 37, label, "fig-ink", size=16, weight=700, middle=True)
    cy = top + h / 2
    if index == 1:
        return text(CX, cy, label, "fig-tense-fill", size=16, weight=700, middle=True)
    if index == 2:
        return text(CX, cy, label, "fig-balanced-fill", size=16, weight=700, middle=True)
    if index == 3:
        return text(CX, cy, label, "fig-key-text", size=15, weight=700, middle=True)
    return text(CX, cy, label, "fig-ink", size=16, weight=700, middle=True)


def connector(bottom: float) -> tuple[str, str]:
    """One arrow between two nodes: a stub that draws itself in, and a head that arrives once the
    stub has finished. The head is a drawn triangle rather than a marker, because a marker is not
    clipped by the dash that does the drawing and would sit there waiting from the first frame.

    Both come back unclosed, since the caller is the one that knows when this arrow is due."""
    line = (f'<path d="M{CX} {bottom}V{bottom + LINE}" class="fig-grid-stroke aim-rte-line" '
            f'stroke-width="2" stroke-dasharray="{LINE:.0f}"')
    head = (f'<path d="M{CX - 6} {bottom + LINE - 1}L{CX + 6} {bottom + LINE - 1}'
            f'L{CX} {bottom + GAP}Z" class="fig-grid-fill aim-rte-head"')
    return line, head


def fade() -> str:
    """The arrival of one node: from low and invisible to placed and solid, eased in the values
    because the timing function stays linear across this whole figure."""
    span = RISE / T * 100
    parts = []
    for i in range(FRAMES + 1):
        eased = smooth(i / FRAMES)
        parts.append(f"{i / FRAMES * span:.4g}%{{opacity:{eased:.3f};"
                     f"transform:translate(0px,{LIFT * (1 - eased):.2f}px)}}")
    parts.append("100%{opacity:1;transform:translate(0px,0px)}")
    return "@keyframes aimRteIn{" + "".join(parts) + "}"


def draw() -> str:
    """The connector drawing itself, as a dash offset walking to zero."""
    span = DRAW / T * 100
    parts = []
    for i in range(DRAW_FRAMES + 1):
        eased = smooth(i / DRAW_FRAMES)
        parts.append(f"{i / DRAW_FRAMES * span:.4g}%{{stroke-dashoffset:{LINE * (1 - eased):.2f}}}")
    parts.append("100%{stroke-dashoffset:0}")
    return "@keyframes aimRteDraw{" + "".join(parts) + "}"


def arrowhead() -> str:
    """The head, held back until the stub it caps has finished drawing."""
    span = DRAW / T * 100
    return (f"@keyframes aimRteHead{{0%{{opacity:0}}{span * 0.94:.4g}%{{opacity:0}}"
            f"{span * 1.06:.4g}%{{opacity:1}}100%{{opacity:1}}}}")


def route() -> str:
    body = [f'<rect x="12" y="{PANEL_TOP}" width="736" height="{PANEL_BOTTOM - PANEL_TOP}" rx="12" '
            'class="fig-panel"/>',
            lane_label(32, 30, "One walk through the chart", "five kinds of node, five shapes")]
    css = [fade(), draw(), arrowhead(),
           ".aim-rte-in,.aim-rte-line,.aim-rte-head{animation-timing-function:linear;"
           f"animation-iteration-count:infinite;animation-duration:{T}s}}",
           ".aim-rte-in{opacity:0;animation-name:aimRteIn}",
           f".aim-rte-line{{stroke-dashoffset:{LINE:.0f};animation-name:aimRteDraw}}",
           ".aim-rte-head{opacity:0;animation-name:aimRteHead}"]
    # The connectors go down first, so a node that arrives on top of one covers its last pixel
    # rather than being crossed by it.
    for index in range(1, len(ROWS)):
        bottom = ROWS[index - 1][0] + ROWS[index - 1][1]
        line, head = connector(bottom)
        delay = f' style="animation-delay:{index * STEP - DRAW:.2f}s"/>'
        body.append(line + delay)
        body.append(head + delay)
    for index, (top, h, kind, label, gloss) in enumerate(ROWS):
        cy = top + h / 2
        body.append(f'<g class="aim-rte-in" style="animation-delay:{index * STEP:.2f}s">'
                    + shape(index, top, h)
                    + content(index, top, h, label)
                    # The kind of node is named beside it, so the shapes need no separate legend.
                    + text(LABEL_X, cy, kind, "fig-ink", anchor="end", size=15, weight=700,
                           middle=True)
                    + text(GLOSS_X, cy, gloss, "fig-muted", anchor="start", size=13, weight=500,
                           middle=True)
                    + "</g>")
    # Asked for less motion, the figure is simply the whole path at rest, which is what a reader
    # wanting to study the shapes rather than the order would want anyway.
    css.append("@media (prefers-reduced-motion:reduce){.aim-rte-in,.aim-rte-line,.aim-rte-head"
               "{opacity:1;stroke-dashoffset:0;transform:none;animation:none!important}}")
    return (f'<svg viewBox="0 0 {W} {H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-route-title"><title id="fig-route-title">One path through a '
            'diagnostic chart, built up a step at a time from the top down. A cloud arrives first, '
            'naming the symptom: the crosshair sails past the target. An arrow draws downward from '
            'it and a red diamond arrives, naming the issue it points to, braking too late. A '
            'second arrow draws and a green rounded box arrives with the technique to change, '
            'commit and stop. A third arrow draws and a filled box arrives describing the scenario '
            'to play by its shape rather than by a name: one wall, two targets, short travel. A '
            'fourth arrow draws and a box with a double edge arrives with the result to expect, '
            'fewer corrections. Each of the five nodes has a different outline, so the kind of node '
            'can be read from its shape rather than from its colour. The path then clears and '
            'builds again.</title>' + metadata() + f"<style>{''.join(css)}</style>"
            + "".join(body) + "</svg>")
