"""The chart's purple clouds: what the player actually sees from their own chair.

A symptom is not a diagnosis. The issue renderer draws the same peak/brake/jitter/shot numbers and
says what is wrong with them; this one only shows what the motion looked like and stops. That is why
nothing here takes a tension colour and nothing is marked as the fault: one accent for the crosshair,
one key colour for the target, muted ink for everything else. Colour that picked a culprit would be
the diagnosis leaking in, and identical colour is also what forces a reader to compare shape.

Every drawing runs on one clock and leaves a ghost dot at each equal tick of it. The dots crowd where
the hand was slow and string out where it was fast, so a still frame of any of these still says what
happened. That device is the whole argument of the family: the reader reads speed off spacing rather
than off a label.

Two layouts come out of the same machinery, because four of these nodes are not faults at all.

one flick   the five nodes that describe a single motion to a single target. Geometry is entirely
            params: peak is how far it goes, brake picks the leg structure, jitter is the wobble
            near the end, shot is where in the travel the trigger went.
a wall      the three nodes about clusters and pathing, which describe something to do rather than
            something that went wrong. They need several targets and an order, so the point sets
            live in WALLS below. Dwell time shows as piled-up dots at each target.

Namespace: every keyframe name starts aimSym2 and carries the node key, because 48 of these figures
render onto one page and a shared keyframe name would silently retime someone else's drawing.
"""
import math
import sys
from collections.abc import Sequence
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))
sys.path.insert(0, str(_HERE))
from figure_kit import crosshair, keyframes, lane_label, metadata, smooth, text  # noqa: E402
from nodes import Node, by_kind  # noqa: E402

W = 600
H = 180
DUR = 3.8                              # one loop, the same for all eight so the page reads as a set
PAUSE = 0.42                           # the frame a reader who asked for less motion is left on
FRAMES = 42                            # samples in a one-flick travel, kept low for page weight
FRAMES_B = 34                          # a wall's path is hops and holds, so it needs fewer
LIFT = 8                               # how far off the track a trail dot sits

# A short unique tail for every keyframe name this file emits. Forty-eight figures land on one page,
# so a name has to carry the node; it does not have to carry the node's spelling.
TAGS: dict[str, str] = {n.key: f"s{i}" for i, n in enumerate(by_kind("symptom"))}

X0, TARGET_X = 92, 470                 # one flick: where the crosshair starts and the target sits
TRACK_Y = 106
DOTS_A = 18
DOTS_B = 20
ENTRY = (44.0, 110.0)                  # a wall: where the crosshair comes in from
DWELL = 1.2                            # a wall: rest at a target, in the same units as a hop

Point = tuple[float, float]
Leg = tuple[float, float]

# A wall's targets, the order the crosshair takes them in, whether that order is numbered, and
# whether a ring closes round whatever is left at the end.
WALLS: dict[str, tuple[list[Point], list[int], bool, bool]] = {
    "sc-cluster-approach": ([(96.0, 126.0), (134.0, 84.0), (176.0, 118.0),
                             (428.0, 92.0), (468.0, 134.0), (512.0, 100.0)],
                            [0, 1, 2, 3, 4, 5], False, False),
    "sc-target-priorities": ([(108.0, 134.0), (180.0, 82.0), (262.0, 126.0),
                              (344.0, 80.0), (420.0, 132.0), (506.0, 90.0)],
                             [0, 2, 4, 5, 3, 1], True, False),
    # The close trio sits high enough that the ring drawn round it clears the caption line.
    "sc-create-clusters": ([(96.0, 86.0), (206.0, 140.0), (330.0, 78.0),
                            (438.0, 96.0), (472.0, 120.0), (504.0, 90.0)],
                           [0, 1, 2, 3, 4, 5], False, True),
}

# The one line under each drawing, and the sentence the screen reader gets. Both are written from
# the chair: what appeared, in what order, with no word for why.
WORDS: dict[str, tuple[str, str]] = {
    "sc-push-flick-speed": (
        "the first move covers nearly all of it",
        "The crosshair leaves fast. Its trail dots are strung far apart across the first stretch "
        "and bunch up at the target, where it sits still for the rest of the loop before the shot "
        "goes."),
    "sc-smooth-means-pacing": (
        "an even drag the whole way, which is what gets called smooth",
        "The crosshair covers the distance in even steps instead of one burst, so its trail dots "
        "sit at almost equal spacing all the way across and the last stretch is a crawl. The shot "
        "goes only once it has stopped."),
    "sc-clicking-too-fast": (
        "the shot mark lands before the crosshair does",
        "The shot mark appears while the crosshair is still running and still short of the target. "
        "Only afterwards does the crosshair arrive, and nothing in the loop waits to see whether "
        "the shot landed."),
    "sc-crosshair-lingers": (
        "it stops a little short and stays there",
        "The crosshair slows early and finishes its travel just short of the target, then holds "
        "there. Its trail dots crowd into that last short stretch, and the shot goes from where it "
        "stopped rather than from the target."),
    "sc-wider-flicks-ruin-pacing": (
        "the wide one runs long, and the clock keeps running",
        "On a wide flick the crosshair carries out past the target and has to come back, so its "
        "trail loops out above the line and returns below it. Most of the loop goes on that return, "
        "and the shot waits for it."),
    "sc-cluster-approach": (
        "a group cleared, one crossing, then the next group",
        "Six targets in two groups. The crosshair clears the near group in short hops, makes one "
        "long crossing, and clears the far group the same way. Each target dims as it is taken, and "
        "the trail dots spread out only across the crossing."),
    "sc-target-priorities": (
        "the order they were taken in, numbered as it goes",
        "Six scattered targets, numbered in the order the crosshair takes them: out along the low "
        "row first and back across the high one, rather than left to right. Each target dims as it "
        "is taken."),
    "sc-create-clusters": (
        "the loose ones first, so what is left sits close",
        "Six targets, three loose and three sitting close together. The crosshair takes the loose "
        "ones first, a ring closes round the three that are left, and those fall in three short "
        "hops."),
}

TAIL = " Every dot is one tick of one clock, so where the dots crowd the crosshair was slow."
CAPTION = "Dots are equal ticks of one clock. They crowd where the hand was slow."


def _n(v: float) -> str:
    """One decimal, with the pointless .0 dropped. Forty-eight figures share a page, so the digits
    that say nothing are worth removing."""
    s = f"{v:.1f}"
    return "0" if s in ("0.0", "-0.0") else (s[:-2] if s.endswith(".0") else s)


def _seed(key: str) -> int:
    """A stable seed from the node key. Python's own hash is salted per process, so a figure built
    from it would differ between builds."""
    n = 2166136261
    for ch in key:
        n = (n * 16777619 + ord(ch)) % 4294967296
    return n


def _legs(peak: float, brake: str) -> list[Leg]:
    """Where the crosshair should be, as a share of the distance, and when, as a share of the loop.

    brake is the whole difference between these drawings. early spends most of the loop on the last
    sliver of the distance; late arrives in one leg and corrects any overshoot cleanly; none arrives
    the same way but never finishes taking the overshoot back.
    """
    if brake == "early":
        return [(0.16, 0.64 * peak), (0.36, 0.85 * peak), (0.62, 0.95 * peak), (0.9, peak)]
    if brake == "none":
        legs = [(0.3, peak)]
        if peak > 1.0:
            legs.append((0.74, 1.0 + (peak - 1.0) * 0.35))
        return legs
    legs = [(0.28, peak)]
    if peak > 1.0:
        legs.append((0.52, 1.0))
    return legs


def _travel(legs: Sequence[Leg], u: float) -> float:
    """How much of the distance is covered at u. Eased inside each leg, held after the last one."""
    start_u, start_p = 0.0, 0.0
    for end_u, end_p in legs:
        if u < end_u:
            return start_p + (end_p - start_p) * smooth((u - start_u) / (end_u - start_u))
        start_u, start_p = end_u, end_p
    return start_p


def _shake(seed: int, jitter: float, u: float) -> Point:
    """The wobble a reader sees once the crosshair is near. Two sines rather than fresh noise per
    frame, so the trail and the animation agree and the keyframes stay compressible."""
    if jitter <= 0.0:
        return 0.0, 0.0
    a = (seed % 97) / 97 * 6.2832
    b = (seed // 97 % 89) / 89 * 6.2832
    amp = jitter * 7.0 * smooth((u - 0.18) / 0.34)
    return amp * 0.45 * math.sin(u * 47 + b), amp * math.sin(u * 31 + a)


def _reveal(name: str, at: float) -> str:
    """A mark rather than a mover: nothing, then the mark, held to the end of the loop."""
    return (f"@keyframes {name}{{0%{{opacity:0}}{at * 100:.4g}%{{opacity:0}}"
            f"{(at + 0.005) * 100:.4g}%{{opacity:1}}100%{{opacity:1}}}}")


def _dim(name: str, at: float) -> str:
    """A target going quiet as the crosshair reaches it."""
    return (f"@keyframes {name}{{0%{{opacity:1}}{at * 100:.4g}%{{opacity:1}}"
            f"{(at + 0.005) * 100:.4g}%{{opacity:.26}}100%{{opacity:.26}}}}")


def _anim(name: str) -> str:
    """The only thing an animated element needs of its own. The clock is shared: all eight of these
    run the same loop at the same phase, so duration and delay belong in the class."""
    return f'style="animation-name:{name}"'


def _dots(points: Sequence[Point]) -> str:
    """The travelled path: a faint line, then one dot per tick. Opacity rides on the group, since a
    per-circle attribute repeated twenty times is most of a kilobyte for nothing."""
    line = "M" + "L".join(f"{_n(x)} {_n(y)}" for x, y in points)
    dots = "".join(f'<circle cx="{_n(x)}" cy="{_n(y)}" r="2.2"/>' for x, y in points[1:])
    return (f'<path d="{line}" class="fig-accent-stroke" stroke-width="1.5" fill="none" '
            f'opacity=".28" stroke-linejoin="round"/>'
            f'<g class="fig-accent-fill" opacity=".5">{dots}</g>')


def _frame(key: str, body: str, clause: str, css: Sequence[str]) -> str:
    """The wrapper every one of these shares: the panel, the clock rules, the pause, the title."""
    rules = ("".join(css)
             + f".aim-sym2-run,.aim-sym2-take,.aim-sym2-mark{{animation-duration:{DUR}s;"
               "animation-timing-function:linear;animation-iteration-count:infinite;"
               f"animation-delay:-{DUR * PAUSE:.3g}s}}"
               "@media(prefers-reduced-motion:reduce){.aim-sym2-run,.aim-sym2-take"
               "{animation-play-state:paused}"
               ".aim-sym2-mark{animation:none!important;opacity:1!important}}")
    return (f'<svg viewBox="0 0 {W} {H}" class="fig-fit" role="img" aria-labelledby="fig-{key}-title">'
            f'<title id="fig-{key}-title">{clause}{TAIL}</title>' + metadata()
            + f"<style>{rules}</style>"
            f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" class="fig-panel"/>'
            + body + text(22, 170, CAPTION, "fig-muted fig-caption", "start", 12, 600) + "</svg>")


def _one_flick(node: Node) -> str:
    """One motion to one target, with the trigger marked wherever in the travel it went."""
    note, clause = WORDS[node.key]
    peak = float(node.params["peak"])
    jitter = float(node.params["jitter"])
    shot = float(node.params["shot"])
    legs = _legs(peak, str(node.params["brake"]))
    seed = _seed(node.key)
    span = float(TARGET_X - X0)
    tag = TAGS[node.key]
    run, mark = f"aimSym2Run{tag}", f"aimSym2Shot{tag}"
    moves: list[Point] = []
    for step in range(FRAMES + 1):
        u = step / FRAMES
        jx, jy = _shake(seed, jitter, u)
        moves.append((_travel(legs, u) * span + jx, jy))
    # A settled shot waits for the motion to finish, wherever that left the crosshair. An early one
    # goes at its share of the travel, which is the only thing there is to see about it.
    if shot >= 1.0:
        fire = min(0.96, legs[-1][0] + 0.08)
    else:
        want = shot * _travel(legs, 1.0)
        fire = next((s / FRAMES for s in range(FRAMES + 1)
                     if _travel(legs, s / FRAMES) >= want - 1e-9), 1.0)
    shot_x = X0 + _travel(legs, fire) * span
    trail: list[Point] = [(float(X0), TRACK_Y - LIFT)]
    previous = 0.0
    for step in range(1, DOTS_A + 1):
        u = step / DOTS_A
        share = _travel(legs, u)
        jx, jy = _shake(seed, jitter, u)
        lift = LIFT if share < previous - 1e-6 else -LIFT
        trail.append((X0 + share * span + jx, TRACK_Y + lift + jy))
        previous = share
    css = [keyframes(run, moves, lambda p: f"translate({_n(p[0])}px,{_n(p[1])}px)"),
           _reveal(mark, fire)]
    body = (lane_label(22, 28, node.label)
            + text(22, 47, note, "fig-muted fig-note", "start", 13, 500)
            + f'<path d="M{X0 - 20} {TRACK_Y}H540" class="fig-grid-stroke" stroke-width="1" '
              'stroke-dasharray="2 6"/>'
              f'<path d="M{X0} {TRACK_Y - 9}v18" class="fig-grid-stroke" stroke-width="1.5"/>'
            + _dots(trail)
            + f'<circle cx="{TARGET_X}" cy="{TRACK_Y}" r="10" class="fig-target"/>'
            + f'<g class="aim-sym2-mark" {_anim(mark)} opacity="0">'
              f'<circle cx="{_n(shot_x)}" cy="{TRACK_Y}" r="15" class="fig-ink-stroke" fill="none" '
              'stroke-width="2.4"/>'
              f'<path d="M{_n(shot_x)} {TRACK_Y + 15}v9" class="fig-ink-stroke" stroke-width="2.4"/>'
            + text(shot_x, TRACK_Y + 38, "shot", "fig-muted", "middle", 12, 600) + "</g>"
            + f'<g class="aim-sym2-run" {_anim(run)}>'
            + crosshair("fig-accent-stroke", X0, TRACK_Y) + "</g>")
    return _frame(node.key, body, clause, css)


def _wall(node: Node) -> str:
    """Several targets and an order through them: the three nodes that describe something to do."""
    note, clause = WORDS[node.key]
    points, order, numbered, ringed = WALLS[node.key]
    route: list[Point] = [ENTRY] + [points[i] for i in order]
    # A longer hop takes longer, but not in proportion: a flick twice as wide is nowhere near twice
    # the time. The square root is what puts the dots where a reader expects to find them.
    hops = [0.55 + math.dist(route[i - 1], route[i]) ** 0.5 / 6.0 for i in range(1, len(route))]
    total = sum(hops) + DWELL * len(hops) + 1.4
    segments: list[tuple[float, float, Point, Point]] = []
    takes: list[float] = []
    clock = 0.0
    for index, hop in enumerate(hops):
        start = clock / total
        clock += hop
        segments.append((start, clock / total, route[index], route[index + 1]))
        takes.append(clock / total)
        clock += DWELL

    def at(u: float) -> Point:
        for start, end, (x0, y0), (x1, y1) in segments:
            if u < end:
                if u <= start:
                    return x0, y0
                e = smooth((u - start) / (end - start))
                return x0 + (x1 - x0) * e, y0 + (y1 - y0) * e
        return route[-1]

    tag = TAGS[node.key]
    run = f"aimSym2Run{tag}"
    ox, oy = ENTRY
    moves = [(lambda p: (p[0] - ox, p[1] - oy))(at(s / FRAMES_B)) for s in range(FRAMES_B + 1)]
    # Whole pixels here. A hop is tens of pixels long and the easing shows in the spacing, not in
    # the tenths, so the decimal places are pure page weight.
    css = [keyframes(run, moves, lambda p: f"translate({p[0]:.0f}px,{p[1]:.0f}px)")]
    marks: list[str] = []
    numbers: list[str] = []
    for slot, target in enumerate(order):
        name = f"aimSym2Take{slot}{tag}"
        css.append(_dim(name, takes[slot]))
        x, y = points[target]
        marks.append(f'<circle cx="{_n(x)}" cy="{_n(y)}" r="9" class="fig-target aim-sym2-take" '
                     f"{_anim(name)}/>")
        if numbered:
            numbers.append(f'<text x="{_n(x + 13)}" y="{_n(y - 11)}">{slot + 1}</text>')
    if numbers:
        # One group carries the styling the six labels share, rather than six copies of it.
        marks.append(f'<g class="fig-muted" font-size="12" font-weight="700">{"".join(numbers)}</g>')
    if ringed:
        group = [points[i] for i in order[-3:]]
        cx = sum(p[0] for p in group) / 3
        cy = sum(p[1] for p in group) / 3
        radius = max(math.dist((cx, cy), p) for p in group) + 15
        name = f"aimSym2Ring{tag}"
        css.append(_reveal(name, takes[len(order) - 4]))
        # No word inside the ring. The note above already says what it is, and a label here would
        # be the figure telling the reader what to make of its own drawing.
        marks.append(f'<g class="aim-sym2-mark" {_anim(name)} opacity="0">'
                     f'<circle cx="{_n(cx)}" cy="{_n(cy)}" r="{_n(radius)}" class="fig-muted-stroke" '
                     'fill="none" stroke-width="1.6" stroke-dasharray="4 5"/></g>')
    trail = [at(step / DOTS_B) for step in range(DOTS_B + 1)]
    body = (lane_label(22, 28, node.label)
            + text(22, 47, note, "fig-muted fig-note", "start", 13, 500)
            + _dots(trail) + "".join(marks)
            + f'<g class="aim-sym2-run" {_anim(run)}>'
            + crosshair("fig-accent-stroke", ox, oy) + "</g>")
    return _frame(node.key, body, clause, css)


def render(node: Node) -> str:
    """One symptom, drawn as what the player saw and nothing more."""
    return _wall(node) if node.key in WALLS else _one_flick(node)
