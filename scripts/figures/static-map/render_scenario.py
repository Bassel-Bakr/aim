"""The scenario nodes of the static clicking chart, drawn as a wall rather than as a lane.

The other four renderers draw one crosshair crossing one horizontal lane, because what they are
about is the shape of a single motion. A scenario is not a motion. It is a layout: how many targets
the wall holds, how far apart they sit, how big they are, and whether they group. So this renderer
looks at the wall head-on and lets the layout carry the figure.

The crosshair takes the targets in a fixed order and the last leg returns to the first, so every
figure is one closed tour. An earlier version sent the crosshair back to a resting point between
targets, which drew every layout as a star: six dashed spokes from one spot said far more about the
resting point than about the wall. A tour says what the layout actually costs to clear.

What the parameters do to the drawing
-------------------------------------
targets  how many marks go on the wall, laid out on a jittered grid so no two overlap.
spread   how much of the wall the layout uses. Narrow keeps it near the middle, wide runs the
         drawing out to both edges, which is also how long each leg of the tour is.
size     the radius of a mark.
cluster  what the tour is teaching. A clustered layout is drawn tight and sits off to one side, its
         route short, dense and solid: the path between targets is the lesson. An unclustered one is
         spread, and its route is drawn dashed over real distance, because there the lesson is the
         flick that crosses the gap rather than the order they come in.

No scenario name appears here, in any form a reader could see. The article's argument is that those
names rot and that a generated figure is the worst place to bury one, so the figure's own title id
is built from the shape - target count, size, spread and whether it clusters - which is both unique
across these nodes and still true after a rename. That is a deliberate departure from the
`fig-<node.key>-title` convention the other renderers follow, and the only one: one node's key
carried a scenario name, and putting the key in the DOM would have published it.

Every name this file writes into a page is namespaced `Scn`/`scn` and carries that shape code, since
48 of these figures share one page and one CSS scope. A keyframe or class name repeated across two
nodes would silently drive both from whichever definition the browser saw last.
"""
import math
import random
import sys
from collections.abc import Sequence
from pathlib import Path

_HERE = Path(__file__).resolve().parent
for _dir in (str(_HERE.parent), str(_HERE)):
    if _dir not in sys.path:
        sys.path.insert(0, _dir)

from figure_kit import crosshair, keyframes, lane_label, metadata, smooth  # noqa: E402
from nodes import Node  # noqa: E402

Point = tuple[float, float]

W = 600
H = 184
# The wall, seen head-on. Everything else is placed inside it.
WALL = (12, 34, 576, 138)
CX = 300.0
CY = 103.0
# The box the layout may use, centred in the wall. Narrower than the wall so a large mark near the
# edge still has air around it.
FIELD_W = 520.0
FIELD_H = 96.0

# Half the width and height each spread is allowed to ask for. The layout may use less when the
# marks are too few to fill it, and is clamped when it asks for more than the field.
SPREAD: dict[str, tuple[float, float]] = {
    "narrow": (82.0, 30.0),
    "mid": (180.0, 44.0),
    "wide": (256.0, 52.0),
}
SIZE: dict[str, float] = {"small": 7.0, "mid": 12.0, "large": 17.0}
# A cluster is the same targets pulled together, so it takes the spread it was given and tightens
# it rather than having a spread of its own.
TIGHTEN = 0.62
# Fraction of a leg spent stopped at its end: the beat where the shot happens.
DWELL = 0.22
COUNT = ("no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
SIZE_WORD = {"small": "small", "mid": "mid-sized", "large": "large"}
SPREAD_WORD = {
    "narrow": "close together near the middle of the wall",
    "mid": "spaced across the middle of the wall",
    "wide": "spread wide across the whole wall",
}


def _num(value: float) -> str:
    """One decimal at most, and no trailing zero. Forty-eight figures share a page, so a digit
    nobody can see is a digit worth not sending."""
    out = f"{value:.1f}"
    if out.endswith(".0"):
        out = out[:-2]
    return "0" if out == "-0" else out


def _px(value: float) -> str:
    """A whole pixel. Keyframes are most of a figure's weight and the crosshair is 16px across, so a
    tenth of a pixel per frame buys nothing and costs four characters sixty times over."""
    return "0" if -0.5 < value < 0.5 else f"{value:.0f}"


def _code(node: Node) -> str:
    """The node's shape as a short token: count, size, spread, and clustered or spread out. Unique
    across these nodes, and unlike the key it names no scenario."""
    p = node.params
    return (f"{int(p['targets'])}{str(p['size'])[0]}{str(p['spread'])[0]}"
            f"{'c' if p['cluster'] else 's'}")


def _room(start: float, delta: float, centre: float, size: float) -> float:
    """How much of a move the field has room for, as a fraction of it."""
    if not delta:
        return 1.0
    edge = centre + size / 2 if delta > 0 else centre - size / 2
    return max(0.0, (edge - start) / delta)


def _layout(node: Node) -> list[Point]:
    """Where the marks go: a jittered grid, seeded from the node's key so a rebuild never reshuffles
    it. The grid is what keeps nine small targets from landing on top of each other; the jitter is
    what keeps them from reading as a spreadsheet. Cells are never smaller than a mark plus its
    breathing room, so a dense layout grows its box rather than overlapping inside it."""
    p = node.params
    count = int(p["targets"])
    radius = SIZE[str(p["size"])]
    half_w, half_h = SPREAD[str(p["spread"])]
    rng = random.Random(node.key)
    # A cluster is a blob, so it wants a squarish grid. A spread layout is a wall, so it wants a
    # wide one.
    if p["cluster"]:
        cols = max(1, math.ceil(math.sqrt(count)))
        half_w, half_h = half_w * TIGHTEN, half_h * TIGHTEN
    else:
        cols = max(1, min(count, math.ceil(math.sqrt(count * 2.2))))
    rows = math.ceil(count / cols)
    floor = 2 * radius + 12
    cell_w = min(max(2 * half_w / cols, floor), FIELD_W / cols)
    cell_h = min(max(2 * half_h / rows, floor), FIELD_H / rows)
    # A cluster sits somewhere on the wall rather than dead centre, which is what makes it a cluster
    # and not simply a small layout.
    shift = (rng.uniform(-1.0, 1.0) * (FIELD_W - cell_w * cols) / 2 * 0.55
             if p["cluster"] else 0.0)
    left = CX - cell_w * cols / 2 + shift
    top = CY - cell_h * rows / 2
    # Jitter stays under two fifths of the slack in a cell, so neighbouring marks cannot meet.
    jitter_x = max(0.0, 0.4 * (cell_w - 2 * radius - 8))
    jitter_y = max(0.0, 0.4 * (cell_h - 2 * radius - 8))
    out: list[Point] = []
    for cell in sorted(rng.sample(range(cols * rows), count)):
        col, row = cell % cols, cell // cols
        out.append((left + (col + 0.5) * cell_w + rng.uniform(-jitter_x, jitter_x),
                    top + (row + 0.5) * cell_h + rng.uniform(-jitter_y, jitter_y)))
    return out


def _away(node: Node, target: Point) -> Point:
    """Where the crosshair is dragged to when there is only one target, and so no tour to take.

    One target has nothing to be spread apart from, so spread becomes what it does mean here: how
    far the crosshair is pulled off before it has to come back. It leaves at an angle rather than
    straight along an axis, because a flick nobody has to move two ways is not the one these
    scenarios ask for."""
    rng = random.Random(node.key + "away")
    # Measured off the horizontal, and shallow: the wall is six times wider than the field is tall,
    # so a steep flick runs out of room and arrives as a nudge.
    angle = math.radians(rng.uniform(12.0, 32.0))
    reach = 78.0 + SPREAD[str(node.params["spread"])][0] * 0.45
    rise = math.sin(angle) * reach * rng.choice((-1.0, 1.0))
    seeded = rng.choice((-1.0, 1.0))
    # Both ways along the wall, and whichever the field has more room for wins. The move is scaled
    # to fit rather than clipped per axis, so what gets shorter is the flick, not its direction.
    options = []
    for side in (seeded, -seeded):
        run = math.cos(angle) * reach * side
        fit = min(1.0, _room(target[0], run, CX, FIELD_W), _room(target[1], rise, CY, FIELD_H))
        options.append((target[0] + run * fit, target[1] + rise * fit))
    return max(options, key=lambda p: math.dist(p, target))


def _tour(points: Sequence[Point]) -> list[Point]:
    """A fixed order through every target, closing back on the first.

    Nearest neighbour from the leftmost target, then 2-opt until nothing improves. Nearest neighbour
    alone leaves the closing leg to sweep back across everything it skipped; 2-opt is what takes
    those crossings out, since a tour whose legs cross is always beaten by the tour that uncrosses
    them. No randomness, so the order is the same on every machine."""
    order = [min(points)]
    remaining = [p for p in points if p != order[0]]
    while remaining:
        here = order[-1]
        nearest = min(remaining, key=lambda p: (p[0] - here[0]) ** 2 + (p[1] - here[1]) ** 2)
        remaining.remove(nearest)
        order.append(nearest)
    count = len(order)
    improving = count > 3
    while improving:
        improving = False
        for i in range(count - 1):
            for j in range(i + 2, count if i else count - 1):
                a, b, c, d = order[i], order[i + 1], order[j], order[(j + 1) % count]
                swapped = math.dist(a, c) + math.dist(b, d)
                if swapped < math.dist(a, b) + math.dist(c, d) - 1e-9:
                    order[i + 1:j + 1] = order[i + 1:j + 1][::-1]
                    improving = True
    return order


def _run(stops: Sequence[Point], frames: int) -> tuple[list[Point], list[float]]:
    """Offsets from the first stop, one per frame, and the moment each leg lands.

    Every leg takes the same share of the cycle: it eases across, then holds for DWELL. Holding is
    what makes a flick read as a flick rather than as a lap, and the hold frames cost nothing once
    `keyframes` drops the ones that repeat."""
    legs = len(stops) - 1
    origin = stops[0]
    out: list[Point] = []
    for index in range(frames + 1):
        along = min(index / frames * legs, legs - 1e-9)
        leg = int(along)
        eased = smooth(min(1.0, (along - leg) / (1.0 - DWELL)))
        (ax, ay), (bx, by) = stops[leg], stops[leg + 1]
        out.append((ax + (bx - ax) * eased - origin[0], ay + (by - ay) * eased - origin[1]))
    return out, [(leg + 1.0 - DWELL) / legs for leg in range(legs)]


def _title(node: Node) -> str:
    """What the figure shows, for a reader who cannot see it. The layout, then the path."""
    p = node.params
    count = int(p["targets"])
    noun = "target" if count == 1 else "targets"
    head = (f"A wall with {COUNT[count]} {SIZE_WORD[str(p['size'])]} {noun}, "
            f"{SPREAD_WORD[str(p['spread'])]}.")
    if count == 1:
        return (f"{head} The crosshair is pulled off the target and flicks back onto it, over and "
                "over.")
    if p["cluster"]:
        return (f"{head} The targets sit together in one group and the crosshair works through "
                "them along a short closed route, so what the figure shows is the path rather than "
                "any one flick.")
    return (f"{head} The crosshair takes them in a fixed order, one long flick to the next, and "
            "the last leg carries it back to the first target so the run loops.")


def render(node: Node) -> str:
    """One scenario node as a wall of targets and the tour a crosshair takes through them."""
    p = node.params
    code = _code(node)
    cls = f"aim-scn-{code}"
    kf = f"aimScn{code}"
    tid = f"fig-sc-scen-{code}-title"
    radius = SIZE[str(p["size"])]
    clustered = bool(p["cluster"])
    marks = _layout(node)
    if len(marks) == 1:
        # Nothing to tour. The loop is the crosshair leaving the target and having to find it again.
        route = [marks[0], _away(node, marks[0])]
        stops = [marks[0], route[1], marks[0]]
        lands = [1]
    else:
        # The tour starts on its own last target, so the first leg lands on the first target and
        # every target gets an arrival. Start and end are the same point: the loop closes.
        route = _tour(marks)
        stops = [route[-1]] + route
        lands = list(range(len(route)))
    legs = len(stops) - 1
    span = sum(math.dist(stops[i], stops[i + 1]) for i in range(legs)) / legs
    # A long leg takes longer than a short one, so a wide layout reads as travel and a tight one as
    # pace, rather than both running at whatever speed fits the cycle.
    duration = round(min(7.0, max(2.2, 0.4 + legs * (0.28 + 0.0016 * span))), 2)
    # Five samples a leg, since the leg is a straight line and only its speed is being approximated,
    # and a floor so a figure with one flick in it still moves smoothly.
    frames = min(56, max(28, 5 * legs))
    offsets, arrivals = _run(stops, frames)

    x, y, wall_w, wall_h = WALL
    body = [f'<rect x="{x}" y="{y}" width="{wall_w}" height="{wall_h}" rx="12" class="fig-panel"/>']
    note = f"{int(p['targets'])} {p['size']}, {p['spread']}"
    body.append(lane_label(28, 24, str(node.label), note + (", tight" if clustered else "")))
    points = " ".join(f"{_num(px)} {_num(py)}" for px, py in route)
    # A clustered route is solid, because the route is the lesson. A spread one is dashed over its
    # much longer legs, because there the lesson is each flick and the gap it has to cross.
    dash = "" if clustered else ' stroke-dasharray="7 7"'
    shape = "polyline" if len(marks) == 1 else "polygon"
    body.append(f'<{shape} points="{points}" class="fig-accent-stroke" stroke-width="2.4" '
                f'fill="none" stroke-linejoin="round" stroke-linecap="round"{dash}/>')
    for point in route if len(marks) > 1 else marks:
        body.append(f'<circle cx="{_num(point[0])}" cy="{_num(point[1])}" r="{_num(radius)}" '
                    'class="fig-target"/>')
    for index, landing in enumerate(lands):
        # A target is marked the moment the crosshair reaches it and stays marked, so a late frame
        # shows how far around the tour the run is.
        point = route[index] if len(marks) > 1 else marks[0]
        # Close around the target: in a tight cluster of small marks a wider ring would meet its
        # neighbours and the layout would read as nine rings rather than nine targets on a route.
        body.append(f'<circle cx="{_num(point[0])}" cy="{_num(point[1])}" r="{_num(radius + 4.5)}" '
                    f'class="fig-accent-stroke {cls}-hit" '
                    f'style="animation-delay:{arrivals[landing] * duration:.2f}s"/>')
    # The crosshair is the reader's own position, so it goes on last and stays readable over a
    # target it has landed on.
    body.append(f'<g class="{cls}">{crosshair("fig-accent-stroke", *stops[0])}</g>')

    # Paused, the figure stops with the crosshair sat on the target that ends the longest leg of the
    # tour: the moment a reader most wants to look at, and the frame where a wide layout and a tight
    # one differ most. Every hit mark shows at once, so the whole tour is readable in that frame.
    longest = max(range(legs), key=lambda leg: math.dist(stops[leg], stops[leg + 1]))
    held = (arrivals[longest] + 0.4 * DWELL / legs) * duration
    css = [keyframes(kf, offsets, lambda pt: f"translate({_px(pt[0])}px,{_px(pt[1])}px)"),
           f".{cls}{{animation-name:{kf};animation-duration:{duration}s;"
           "animation-timing-function:linear;animation-iteration-count:infinite}",
           f"@keyframes {kf}Hit{{0%{{opacity:0}}3%{{opacity:1}}100%{{opacity:1}}}}",
           f".{cls}-hit{{opacity:0;stroke-width:2;fill:none;animation-name:{kf}Hit;"
           f"animation-duration:{duration}s;"
           "animation-timing-function:linear;animation-iteration-count:infinite}",
           f"@media (prefers-reduced-motion:reduce){{.{cls}{{animation-play-state:paused;"
           f"animation-delay:-{held:.2f}s!important}}"
           f".{cls}-hit{{opacity:1;animation:none!important}}}}"]
    return (f'<svg viewBox="0 0 {W} {H}" class="fig-fit" role="img" aria-labelledby="{tid}">'
            f'<title id="{tid}">{_title(node)}</title>' + metadata()
            + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")
