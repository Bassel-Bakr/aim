"""The chart's eleven practice results, each drawn as two runs of the same reach on one clock.

A result node is a statistic, and a statistic is the easy thing to draw badly: a bar that grows to a
length only asserts the number, and freezing it loses nothing. So nothing here grows to a number.
Each figure runs the same reach twice on one shared clock, once the way the node is there to fix and
once the way it ends up, and the reader watches the second run finish while the first is still
working. What separates the two runs is the metric itself, so the metric decides what moves: an
overshoot sails past and walks back, a stall stops dead, a path length crosses the cluster twice.

Under each pair is the clock. A shot plants a mark on it at the moment it goes, above the line for
the first run and below for the second, and a shutter the colour of the page hides the marks until
the clock reaches them. That shutter rides the same keyframe as the clock's own dot, so the whole
reveal costs one animation, and the marks themselves are static: asked for less motion, the figure
hides the shutter, shows every mark and freezes both crosshairs on the frame where they are furthest
apart.

The before and after numbers in nodes.py are illustrative parameters, not measurements, so they are
never printed. They set how long a run takes and how badly it wastes its time, and nothing else.

Forty-eight of these figures share one page, so every keyframe name and class carries a short digest
of the node's key. figure_kit.keyframes() is not used: it wants one value per frame at a fixed rate,
and a fixed rate either segments the flick or spends a kilobyte on a pause. The stops here are
thinned against a straight line instead, which costs nothing where nothing is happening.
"""
import hashlib
import math
import sys
from collections.abc import Callable
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _path in (str(HERE.parent), str(HERE)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from figure_kit import crosshair, lane_label, metadata, smooth, text  # noqa: E402
from nodes import Node  # noqa: E402

W = 600
H = 194
X0 = 92.0                            # where both runs start
XT = 452.0                           # the lone target, for the metrics that have one
LANE_Y = (78.0, 124.0)               # the worse run, then the better one
STRIP_Y = 164.0                      # the clock under them
STRIP_X0, STRIP_X1 = 92.0, 556.0
SWEEP = STRIP_X1 - STRIP_X0
T = 4.8                              # one loop
RUN = 3.7                            # the part of the loop the clock spans; the rest is a rest
SAMPLES = 132                        # how finely a run is worked out before its stops are thinned
EPS = 2.0                            # how far a thinned stop may sit off the true path, in pixels
REACH = 40                           # how many samples one thinned stop may stand in for

# What the upper and lower runs are doing, for the figure's own description. Each metric moves
# differently, so each gets its own pair of phrases rather than a shared "better" and "worse".
STORY: dict[str, tuple[str, str]] = {
    "overshoot": ("sails past the target and walks back to it",
                  "stops where the target is"),
    "braking distance": ("starts slowing far out and crawls the shaded last stretch",
                         "brakes late, over a short stretch"),
    "initial flick speed": ("leaves softly and takes most of the lane to get going",
                            "breaks away hard and is most of the way there early"),
    "shake near the target": ("arrives and shakes around the target before it settles",
                              "arrives and holds still"),
    "confirm lag": ("lands, then hovers over the target before the shot goes",
                    "confirms as it lands and fires on arrival"),
    "gap between shots": ("parks on each target and waits there before the next flick",
                          "leaves again as soon as the shot has gone"),
    "dead time between targets": ("crawls from one target to the next",
                                  "crosses between them without slowing"),
    "pace drift": ("lets each interval run longer than the one before it",
                   "holds every interval the same length"),
    "wasted movement": ("bows away from the straight line and hooks back onto the target",
                        "stays on the line"),
    "stalls per run": ("stops dead several times on the way",
                       "crosses in one motion"),
    "path length": ("crosses the cluster back and forth",
                    "chains the nearest target each time"),
}


def tag(key: str) -> str:
    """A short digest of the node's key, so 48 figures on one page cannot share a keyframe name."""
    return hashlib.blake2s(key.encode(), digest_size=3).hexdigest()


def noise(key: str, count: int) -> list[float]:
    """A deterministic stream of 0-to-1 values, seeded from the node's key and nothing else."""
    state = int.from_bytes(hashlib.blake2s(key.encode(), digest_size=4).digest(), "big")
    out: list[float] = []
    for _ in range(count):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        out.append(state / 0x7FFFFFFF)
    return out


def leg(u: float, start: float, dur: float) -> float:
    """Eased progress through one sub-motion, 0 before it begins and 1 once it is over."""
    if dur <= 0:
        return 1.0 if u >= start else 0.0
    return smooth((u - start) / dur)


def chain(points: list[tuple[float, float]], t0: float, hops: list[float],
          gaps: list[float]) -> tuple[Callable[[float], tuple[float, float]], list[float]]:
    """A run that visits points in order: one eased hop each, then a pause, and a shot on arrival."""
    legs: list[tuple[float, float, tuple[float, float], tuple[float, float]]] = []
    shots: list[float] = []
    t = t0
    for i in range(1, len(points)):
        legs.append((t, hops[i - 1], points[i - 1], points[i]))
        t += hops[i - 1]
        shots.append(t + 0.02)
        t += gaps[i - 1]

    def pos(u: float) -> tuple[float, float]:
        x, y = points[0]
        for start, dur, a, b in legs:
            if u <= start:
                return x, y
            p = smooth((u - start) / dur) if dur > 0 else 1.0
            x, y = a[0] + (b[0] - a[0]) * p, a[1] + (b[1] - a[1]) * p
        return x, y

    return pos, shots


def scene(metric: str, key: str) -> list[tuple[float, float]]:
    """Where the targets sit, as x and an offset from the lane's line. Both runs share them."""
    if metric == "gap between shots":
        return [(188.0, 0.0), (320.0, 0.0), (452.0, 0.0)]
    if metric == "dead time between targets":
        return [(196.0, 0.0), (268.0, 0.0), (452.0, 0.0)]
    if metric == "pace drift":
        return [(190.0, 0.0), (277.0, 0.0), (364.0, 0.0), (452.0, 0.0)]
    if metric == "path length":
        r = noise(key, 8)
        return [(172.0 + i * 88.0 + (r[i] - 0.5) * 44.0, (r[i + 4] - 0.5) * 34.0) for i in range(4)]
    return [(XT, 0.0)]


def routes(points: list[tuple[float, float]], start: tuple[float, float]
           ) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    """The wandering order and the chained one: nearest target each time, and a crossing zigzag."""
    good: list[tuple[float, float]] = []
    left = list(points)
    cur = start
    while left:
        nxt = min(left, key=lambda p: math.dist(p, cur))
        good.append(nxt)
        left.remove(nxt)
        cur = nxt
    bad = [good[2], good[0], good[3], good[1]]
    return bad, good


def motion(metric: str, m: float, targets: list[tuple[float, float]], key: str, worse: bool
           ) -> tuple[Callable[[float], tuple[float, float]], list[float],
                      tuple[float, float] | None]:
    """One run: where the crosshair is across the clock, when its shots go, and any region the
    metric wants shaded behind it. `m` is the node's own parameter, lower being better."""
    span = XT - X0
    if metric == "overshoot":
        out, back = 0.20, 0.10 + 0.58 * m
        peak = 1.0 + 0.55 * m

        def over_pos(u: float) -> tuple[float, float]:
            return X0 + span * (peak * leg(u, 0.05, out)
                                + (1.0 - peak) * leg(u, 0.05 + out, back)), 0.0
        return over_pos, [0.05 + out + back + 0.04], None
    if metric == "braking distance":
        brake = 0.14 + 0.52 * m
        fast, slow = 0.16, 0.12 + 0.72 * m

        def brake_pos(u: float) -> tuple[float, float]:
            return X0 + span * ((1.0 - brake) * leg(u, 0.05, fast)
                                + brake * leg(u, 0.05 + fast, slow)), 0.0
        return brake_pos, [0.05 + fast + slow + 0.04], (X0 + span * (1.0 - brake), XT)
    if metric == "initial flick speed":
        # Both hands leave on the same beat. What differs is how hard, so the shape of the ramp is
        # the whole figure: an explosive start covers most of the distance early and eases in, a
        # soft one dawdles out of the gate and is still travelling when the other has arrived.
        # A departure delay would draw reaction time, which is a different fault.
        start, fly = 0.08, 0.30 + 0.34 * m
        punch = 0.45 + 1.70 * m          # under 1 leaves hard, over 1 leaves soft

        def speed_pos(u: float) -> tuple[float, float]:
            if u <= start:
                return X0, 0.0
            return X0 + span * min(1.0, ((u - start) / fly) ** punch), 0.0
        return speed_pos, [start + fly + 0.04], None
    if metric == "shake near the target":
        fly = 0.22
        amp, dur = 2.0 + 13.0 * m, 0.10 + 0.70 * m
        phase = noise(key, 1)[0] * 6.283

        def shake_pos(u: float) -> tuple[float, float]:
            base = X0 + span * leg(u, 0.05, fly)
            p = (u - 0.05 - fly) / dur
            if 0.0 <= p <= 1.0:
                k = amp * (1.0 - p)
                a = p * 5.5 * 6.283
                return base + k * math.sin(a), k * 0.75 * math.sin(a * 1.4 + phase)
            return base, 0.0
        return shake_pos, [0.05 + fly + dur + 0.03], None
    if metric == "confirm lag":
        fly, lag = 0.22, 0.04 + 0.60 * m

        def confirm_pos(u: float) -> tuple[float, float]:
            base = X0 + span * leg(u, 0.05, fly)
            p = (u - 0.05 - fly) / lag
            if 0.0 <= p <= 1.0:
                k = (1.0 + 8.0 * m) * math.sin(p * 9.42) * (1.0 - p)
                return base + k, k * 0.8
            return base, 0.0
        return confirm_pos, [0.05 + fly + lag], None
    if metric == "wasted movement":
        dur = 0.18 + 0.70 * m
        bow, over = 3.0 + 26.0 * m, 0.05 * m
        peak = 1.0 + over

        def wasted_pos(u: float) -> tuple[float, float]:
            a = leg(u, 0.05, dur * 0.76)
            b = leg(u, 0.05 + dur * 0.76, dur * 0.34)
            q = 0.76 * a + 0.24 * b
            return (X0 + span * (peak * a + (1.0 - peak) * b),
                    -bow * math.sin(math.pi * q) ** 1.15)
        return wasted_pos, [0.05 + dur * 1.10 + 0.03], None
    if metric == "stalls per run":
        n = max(1, round(4.6 * m))
        hold, move = 0.05 + 0.10 * m, 0.28
        stops = [(X0, 0.0)] + [(X0 + span * (i + 1) / (n + 1), 0.0) for i in range(n + 1)]
        pos, shots = chain(stops, 0.04, [move / (n + 1)] * (n + 1), [hold] * (n + 1))
        return pos, shots[-1:], None
    if metric == "gap between shots":
        pos, shots = chain([(X0, 0.0)] + targets, 0.04, [0.11] * 3, [0.03 + 0.34 * m] * 3)
        return pos, shots, None
    if metric == "dead time between targets":
        pos, shots = chain([(X0, 0.0)] + targets, 0.04, [0.09 + 0.26 * m] * 3, [0.025] * 3)
        return pos, shots, None
    if metric == "pace drift":
        gaps = [0.035 * (1.0 + 3.2 * m * i) for i in range(4)]
        pos, shots = chain([(X0, 0.0)] + targets, 0.04, [0.09] * 4, gaps)
        return pos, shots, None
    # path length: the order is the argument, and the node's own parameter sets the clock it costs.
    bad, good = routes(targets, (X0, 0.0))
    stops = [(X0, 0.0)] + (bad if worse else good)
    lengths = [math.dist(stops[i], stops[i + 1]) for i in range(len(stops) - 1)]
    budget = 0.05 + 0.78 * m
    hops = [budget * d / sum(lengths) for d in lengths]
    pos, shots = chain(stops, 0.04, hops, [0.02] * len(hops))
    return pos, shots, None


def thin(pts: list[tuple[float, float, float]], eps: float) -> list[tuple[float, float, float]]:
    """Keep only the stops a straight line between neighbours cannot stand in for. A pause collapses
    to two stops and a constant-speed flick to two, while a curve keeps as many as it needs."""
    kept = [pts[0]]
    i, n = 0, len(pts)
    while i < n - 1:
        best, j = i + 1, i + 1
        while j < n and j - i <= REACH:
            ax, ay, bx, by = pts[i][1], pts[i][2], pts[j][1], pts[j][2]
            ok = True
            for k in range(i + 1, j):
                f = (pts[k][0] - pts[i][0]) / (pts[j][0] - pts[i][0])
                if (abs(ax + (bx - ax) * f - pts[k][1]) > eps
                        or abs(ay + (by - ay) * f - pts[k][2]) > eps):
                    ok = False
                    break
            if not ok:
                break
            best, j = j, j + 1
        kept.append(pts[best])
        i = best
    return kept


def move(x: float, dy: float, planar: bool) -> str:
    """One stop's transform. A run that never leaves its line writes the shorter one-axis form, and
    a run that does keeps both axes on every stop so the browser has one function list to tween."""
    ax, ay = int(round(x - X0)), int(round(dy))
    return f"translate({ax}px,{ay}px)" if planar else f"translateX({ax}px)"


def render(node: Node) -> str:
    key = node.key
    h = tag(key)
    metric = str(node.params["metric"])
    targets = scene(metric, key)
    body = [f'<rect x="8" y="8" width="{W - 16}" height="140" rx="12" class="fig-panel"/>',
            lane_label(22, 32, node.label, metric)]
    marks: list[str] = []
    css: list[str] = []
    dense: list[list[tuple[float, float, float]]] = []
    for index, (worse, value, side) in enumerate(
            ((True, node.params["before"], "before"), (False, node.params["after"], "after"))):
        y = LANE_Y[index]
        hue = "fig-tense" if worse else "fig-balanced"
        pos, shots, band = motion(metric, float(value), targets, key, worse)
        # The straight line from start to target, which for the two metrics that leave it is also
        # the shortest route the run could have taken.
        if metric == "path length":
            route = [(X0, 0.0)] + (routes(targets, (X0, 0.0))[0 if worse else 1])
            body.append('<path d="M' + "L".join(f"{px:.0f} {y + py:.0f}" for px, py in route)
                        + f'" class="{hue}-stroke" stroke-width="1.6" fill="none" opacity="0.32" '
                        'stroke-linejoin="round"/>')
        else:
            body.append(f'<path d="M{X0 - 14:.0f} {y:.0f}H{XT + 22:.0f}" class="fig-grid-stroke" '
                        'stroke-width="1" stroke-dasharray="2 6"/>')
        if band is not None:
            body.append(f'<rect x="{band[0]:.0f}" y="{y - 13:.0f}" width="{band[1] - band[0]:.0f}" '
                        f'height="26" rx="4" class="{hue}-fill" opacity="0.14"/>')
        # The targets go inside one group per lane so the class is written once rather than per dot;
        # forty-eight figures on a page make that worth the extra element.
        body.append('<g class="fig-target">' + "".join(
            f'<circle cx="{tx:.0f}" cy="{y + ty:.0f}" r="9"/>' for tx, ty in targets) + "</g>")
        body.append(text(22, y, side, f"{hue}-fill", "start", 12, 700, middle=True))
        pts = [(j / SAMPLES, *pos(j / SAMPLES)) for j in range(SAMPLES + 1)]
        dense.append(pts)
        kept = thin(pts, EPS)
        planar = any(abs(p[2]) >= 0.6 for p in kept)
        stops = [f"{u * RUN / T * 100:.3g}%{{transform:{move(px, py, planar)}}}"
                 for u, px, py in kept]
        stops.append(f"100%{{transform:{move(kept[-1][1], kept[-1][2], planar)}}}")
        css.append(f"@keyframes aimRes{h}{'AB'[index]}{{{''.join(stops)}}}")
        body.append(f'<g class="aim-res-{h}" style="animation-name:aimRes{h}{"AB"[index]}">'
                    f'{crosshair(f"{hue}-stroke", X0, y)}</g>')
        # A shot is an event in time, so it is marked on the clock rather than on the lane: above
        # the line for the run being fixed, below it for the one that comes out of practice. One
        # run's marks are one path, since they never differ in anything but where they sit.
        top = STRIP_Y - 9 if worse else STRIP_Y
        ticks = "".join(f"M{STRIP_X0 + min(max(s, 0.0), 1.0) * SWEEP:.0f} {top:.0f}v9"
                        for s in shots)
        marks.append(f'<path d="{ticks}" class="{hue}-stroke" stroke-width="2.6"/>')
    # The frame where the two runs are furthest apart, which is the one a reader who wants no motion
    # is left looking at.
    far = max(range(SAMPLES + 1),
              key=lambda j: math.dist(dense[0][j][1:], dense[1][j][1:]))
    body.extend(marks)
    # The shutter is the page's own colour and hides each mark until the clock reaches it. It rides
    # the clock's keyframe, so the reveal and the dot cost one animation between them, and it runs
    # off the side of the figure where there is no panel behind it to give it away.
    body.append(f'<rect x="{STRIP_X0 - 2:.0f}" y="{STRIP_Y - 12:.0f}" width="470" height="24" '
                f'class="fig-surface aim-res-{h} aim-res-{h}-s" '
                f'style="animation-name:aimRes{h}S"/>')
    body.append(f'<path d="M{STRIP_X0:.0f} {STRIP_Y:.0f}H{STRIP_X1:.0f}" class="fig-grid-stroke" '
                'stroke-width="2"/>')
    body.append(f'<g class="aim-res-{h}" style="animation-name:aimRes{h}S">'
                f'<circle cx="{STRIP_X0:.0f}" cy="{STRIP_Y:.0f}" r="4" class="fig-ink-fill"/></g>')
    body.append(text(STRIP_X0, 188, "one clock, both runs", "fig-muted", "start", 12, 600))
    css.append(f"@keyframes aimRes{h}S{{0%{{transform:translateX(0px)}}"
               f"{RUN / T * 100:.4g}%{{transform:translateX({SWEEP:.0f}px)}}"
               f"100%{{transform:translateX({SWEEP:.0f}px)}}}}")
    css.append(f".aim-res-{h}{{animation-duration:{T}s;animation-timing-function:linear;"
               "animation-iteration-count:infinite}")
    css.append("@media (prefers-reduced-motion:reduce){"
               f".aim-res-{h}{{animation-play-state:paused;"
               f"animation-delay:-{far / SAMPLES * RUN:.2f}s!important}}"
               f".aim-res-{h}-s{{opacity:0}}}}")
    bad, good = STORY[metric]
    return (f'<svg viewBox="0 0 {W} {H}" class="fig-fit" role="img" '
            f'aria-labelledby="fig-{key}-title">'
            f'<title id="fig-{key}-title">{node.label}, drawn as the same reach run twice on one '
            f'clock. The upper run {bad}. The lower run {good}. The marks on the clock below are '
            'when each run takes its shots, planted as the clock passes them, so the lower row is '
            'already finished while the upper run is still working.</title>'
            + metadata() + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")
