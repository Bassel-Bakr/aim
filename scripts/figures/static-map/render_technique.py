"""The four green technique nodes: the only motions on the page that are being done right.

Everything else the static clicking chart names is a fault, a symptom, a drill or an outcome, so
these four are the reference the other forty-four are measured against. That sets the drawing's job:
they have to look calm. No overshoot, no shake, no cut-off correction, and nothing marked in the
tense red the issue figures use. One colour runs through all four, the balanced green.

What separates them is `phases` and `hold`, read together:

    phases 2 or 3   one arrival to one target, cut into that many named sub-motions. The crosshair
                    still makes a single eased move; the split is a reading of it, not a seam.
    phases 4        four flicks, one per target, and `hold` decides the rhythm between them.

    hold            how long the crosshair rests once it lands, 0 to 1. A node whose flicks come in
                    bursts spends nearly all of that budget on one gap and almost none on the rest,
                    which is what makes controlled bursts look nothing like continuous flicking
                    despite the two sharing a phase count.

Forty-eight of these figures render onto one page and CSS keyframe names are global to it, so every
name here carries the aimTec prefix and the node's own slug, and every class the aim-tec- prefix and
the node's key.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import NamedTuple

# The kit sits a folder up, beside the other pages' figure code, and is not an installed package.
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))
sys.path.insert(0, str(_HERE))
from figure_kit import crosshair, keyframes, lane_label, metadata, smooth, text  # noqa: E402
from nodes import Node  # noqa: E402

W = 600
H = 178
TRACK_X0, TRACK_X1 = 64, 566            # the rail the crosshair runs along
TRACK_Y = 96
LABEL_Y = 30                            # the node's own words
UPPER_Y = 62                            # brackets over the run, or the seamed comparison
PHASE_Y = 118                           # what each sub-motion or each flick is called
BAR_Y, BAR_H = 126, 16                  # the clock: the same loop drawn as time rather than space
BAR_X0, BAR_X1 = 76, 560
CAP_Y = 160
FRAMES = 38                             # samples of the crosshair's path, before equal ones are cut
GHOST_FRAMES = 22
# Stretched from real times: a flick is over in a couple of hundred milliseconds and a loop of those
# is a flicker. What has to stay true is the ratio between a long flick and a short one, and between
# a motion and a pause.
HOLD_SCALE = 1.1                        # seconds of rest at hold = 1
REPLAY = 0.38                           # the gap the crosshair is faded out for, so the loop replays
                                        # rather than teleporting home
BURST_LONG, BURST_SHORT = 3.2, 0.3      # what a bursting node does with its hold budget

# Where each node's targets sit. Distances are deliberately unequal: a run whose gaps are all the
# same would say the rhythm comes from a beat, which is the fault these nodes are the answer to.
STOPS: dict[str, list[float]] = {
    "sc-flick": [92, 470],
    "sc-fluid-transition": [92, 470],
    "sc-continuous-flicking": [96, 204, 474, 304, 544],
    "sc-controlled-bursts": [96, 172, 248, 440, 516],
}
# Which arrivals are followed by the long gap, by index. A node with none of these paces evenly.
LONG_GAP: dict[str, frozenset[int]] = {"sc-controlled-bursts": frozenset({1})}
# Brackets over the run, as (first stop, last stop) and the word for what they enclose.
BRACKETS: dict[str, list[tuple[int, int, str]]] = {
    "sc-flick": [(0, 1, "one motion")],
    "sc-continuous-flicking": [(0, 4, "one run, no stops")],
    "sc-controlled-bursts": [(0, 2, "burst"), (3, 4, "burst")],
}
# The faint comparison: where it stalls as a share of the distance, and what its three parts cost
# against the clean flick's one. Only the node whose whole point is the missing seam has one.
GHOST: dict[str, tuple[float, float, float, float]] = {
    "sc-fluid-transition": (0.62, 0.55, 0.38, 0.45),
}
# How a single arrival is cut up, as shares of its duration.
SPLIT: dict[int, tuple[tuple[float, ...], tuple[str, ...]]] = {
    2: ((0.66, 0.34), ("Flick", "Land")),
    3: ((0.50, 0.27, 0.23), ("Flick", "Blend", "Land")),
}
# A label with a comma in it splits into a name and a note on its own. The two without one need the
# split written out, and both are cut shorter than the node's words: fig-name and fig-note grow on a
# phone, where the figure itself has scaled down, and a label that fits here runs off the panel there.
WORDS: dict[str, tuple[str, str]] = {
    "sc-fluid-transition": ("Fluid transition", "no seam in the middle"),
    "sc-controlled-bursts": ("Controlled bursts", "fast inside, still between"),
}
CAPTION: dict[str, str] = {
    "sc-flick": "out, land, stop, and nothing after it",
    "sc-fluid-transition": "the faint trace is the same flick with a stop left in it",
    "sc-continuous-flicking": "the gaps are set by where the targets are, not by a beat",
    "sc-controlled-bursts": "two quick flicks, a pause the player chose, two more",
}
TITLE: dict[str, str] = {
    "sc-flick": "One flick to one target. The crosshair leaves fast, eases in and stops on the "
                "target. The clock below shows the motion, then the rest that follows it.",
    "sc-fluid-transition": "One flick, drawn as a flick, a blend and a landing that run into each "
                           "other with no seam. The faint trace above is the same flick with a stop "
                           "left in the middle of it, and arrives later for that.",
    "sc-continuous-flicking": "Four flicks across four targets at unequal distances. The crosshair "
                              "barely rests between them, and each gap lasts as long as its own "
                              "flick needs rather than as long as a beat allows.",
    "sc-controlled-bursts": "Four flicks in two bursts of two. Inside a burst the crosshair goes "
                            "straight from one target to the next. Between the bursts it sits still "
                            "on the target far longer than any of the flicks take.",
}


def num(value: float) -> str:
    """A coordinate, short. Forty-eight animated figures share one page, so trailing zeros cost."""
    out = f"{value:.1f}"
    return out[:-2] if out.endswith(".0") else out


def px(value: float) -> str:
    """A travel offset, to the pixel. Half a pixel of a crosshair's path is nobody's evidence, and
    whole numbers let the kit drop more of the frames that repeat."""
    return str(round(value))


def secs(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def ease(u: float) -> float:
    """How much of a flick is done at u of its time. Committed out of the gate, soft on arrival.

    Smoothstep alone is symmetric, which draws a hand that creeps away from the start. A real flick
    that lands is already most of the way there by halfway, so most of the weight sits on a curve
    that leaves at full speed and spends its time braking.
    """
    u = max(0.0, min(1.0, u))
    return smooth(u) * 0.42 + (1.0 - (1.0 - u) ** 2.4) * 0.58


def move_time(distance: float) -> float:
    """Roughly what a flick of this length costs on screen. Grows with the log of the distance, so a
    hop inside a cluster is cheap and crossing the wall is not, without being four times the wait."""
    return 0.22 + 0.26 * math.log2(abs(distance) / 40.0 + 1.0)


class Move(NamedTuple):
    t0: float
    t1: float
    x0: float
    x1: float


class Block(NamedTuple):
    """One stretch of the clock under the track: a motion, or a rest.

    A single arrival is one block however many sub-motions it is named in. Cutting it into three
    would draw two gaps, and the node with three of them is the one arguing that the flick and the
    landing have no gap between them. Where the parts hand over is marked on the rail instead.
    """
    t0: float
    t1: float
    rest: bool


class Run(NamedTuple):
    total: float                            # one loop, including the gap it replays over
    moves: list[Move]
    blocks: list[Block]
    arrivals: list[tuple[float, float]]     # when the crosshair lands, and where
    ghost: list[Move]
    pause: float                            # the frame reduced motion holds, as a share of total


def split_of(phases: int) -> tuple[tuple[float, ...], tuple[str, ...]]:
    known = SPLIT.get(phases)
    if known is not None:
        return known
    share = 1.0 / max(1, phases)
    return tuple([share] * phases), tuple(["Flick"] + ["Blend"] * (phases - 2) + ["Land"])[:phases]


def position(moves: list[Move], t: float) -> float:
    """Where the crosshair is at t. Between moves it is exactly where the last one left it."""
    x = moves[0].x0
    for move in moves:
        if t <= move.t0:
            return x
        if t < move.t1:
            return move.x0 + (move.x1 - move.x0) * ease((t - move.t0) / (move.t1 - move.t0))
        x = move.x1
    return x


def build_run(node: Node) -> Run:
    """The whole loop: every flick, every rest, and the frame worth freezing on."""
    stops = STOPS[node.key]
    peak = float(node.params["peak"])
    hold = float(node.params["hold"]) * HOLD_SCALE
    longs = LONG_GAP.get(node.key, frozenset())
    single = len(stops) == 2
    moves: list[Move] = []
    blocks: list[Block] = []
    arrivals: list[tuple[float, float]] = []
    t, x = 0.0, float(stops[0])
    for index, stop in enumerate(stops[1:]):
        # Where the flick actually leaves the crosshair. At peak 1 that is the target, which is what
        # every one of these four does; the term is here so the param drives the drawing.
        land = x + (stop - x) * peak
        span = move_time(land - x)
        moves.append(Move(t, t + span, x, land))
        blocks.append(Block(t, t + span, False))
        t += span
        arrivals.append((t, land))
        x = land
        last = index == len(stops) - 2
        if last:
            gap = hold
        elif index in longs:
            gap = hold * BURST_LONG
        elif longs:
            gap = hold * BURST_SHORT
        else:
            gap = hold
        blocks.append(Block(t, t + gap, True))
        t += gap
    ghost: list[Move] = []
    if node.key in GHOST:
        # The same flick with a stop left in it: out, stall, out again. It leaves when the clean one
        # does and arrives after it, which is the whole cost of the seam.
        seam, out, stall, back = GHOST[node.key]
        base = moves[0]
        span = base.t1 - base.t0
        mid = base.x0 + (base.x1 - base.x0) * seam
        ghost = [Move(0.0, span * out, base.x0, mid),
                 Move(span * (out + stall), span * (out + stall + back), mid, base.x1)]
        t = max(t, ghost[-1].t1 + hold)
        blocks[-1] = Block(blocks[-1].t0, t, True)
    # What a reader who asked for less motion is left looking at. Each node freezes where its own
    # point is most visible, never on an empty frame.
    if ghost:
        pause = (ghost[0].t1 + ghost[1].t0) / 2
    elif longs:
        rests = [b for b in blocks if b.rest]
        longest = max(rests, key=lambda b: b.t1 - b.t0)
        pause = (longest.t0 + longest.t1) / 2
    elif single:
        pause = arrivals[0][0] + 0.06
    else:
        longest_move = max(moves, key=lambda m: m.t1 - m.t0)
        pause = (longest_move.t0 + longest_move.t1) / 2
    total = t + REPLAY
    return Run(total, moves, blocks, arrivals, ghost, pause / total)


def words(node: Node) -> tuple[str, str]:
    """The node's own label as a name and a note. Most of these carry the comma to split on."""
    written = WORDS.get(node.key)
    if written is not None:
        return written
    name, _, note = node.label.partition(",")
    return name.strip(), note.strip()


def bracket(x0: float, x1: float, word: str) -> str:
    return (f'<path d="M{num(x0)} {UPPER_Y + 9}V{UPPER_Y}H{num(x1)}V{UPPER_Y + 9}" '
            'class="fig-grid-stroke" stroke-width="1.6" fill="none"/>'
            + text((x0 + x1) / 2, UPPER_Y - 7, word, "fig-muted fig-phase", "middle", 12, 600))


def render(node: Node) -> str:
    """One technique node as a self-contained animated SVG."""
    tag = node.key[3:]
    slug = "".join(part.capitalize() for part in tag.split("-"))
    stops = STOPS[node.key]
    run = build_run(node)
    total = run.total
    home = float(stops[0])
    anim, mark = f"aim-tec-{tag}", f"aim-tec-{tag}-m"
    css: list[str] = []
    body: list[str] = [f'<rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="12" '
                       'class="fig-panel"/>']
    name, note = words(node)
    body.append(lane_label(24, LABEL_Y, name, note))
    # The row above the track: what the run is grouped into, or the comparison it is being read
    # against. Never both, since two things there read as a second lane.
    if run.ghost:
        seam_x = run.ghost[0].x1
        body.append(f'<path d="M{TRACK_X0} {UPPER_Y}H{TRACK_X1}" class="fig-grid-stroke" '
                    'stroke-width="1" stroke-dasharray="2 6"/>')
        body.append(f'<circle cx="{num(run.ghost[-1].x1)}" cy="{UPPER_Y}" r="8" class="fig-target" '
                    'opacity="0.5"/>')
        body.append(f'<path d="M{num(seam_x)} {UPPER_Y - 11}v22" class="fig-grid-stroke" '
                    'stroke-width="1.8" stroke-dasharray="3 3"/>')
        body.append(text(seam_x, UPPER_Y - 17, "seam", "fig-muted fig-phase", "middle", 12, 600))
    else:
        marks = BRACKETS.get(node.key, [])
        for first, last, word in marks:
            body.append(bracket(stops[first], stops[last], word))
        if len(marks) > 1:
            # The gap between two brackets is the pause, and it is the whole difference between this
            # node and the one that flicks straight through.
            left, right = stops[marks[0][1]], stops[marks[1][0]]
            body.append(f'<path d="M{num(left)} {UPPER_Y}H{num(right)}" class="fig-grid-stroke" '
                        'stroke-width="1.6" stroke-dasharray="3 5"/>')
            body.append(text((left + right) / 2, UPPER_Y - 7, "pause", "fig-muted fig-phase",
                             "middle", 12, 600))
    body.append(f'<path d="M{TRACK_X0} {TRACK_Y}H{TRACK_X1}" class="fig-grid-stroke" '
                'stroke-width="1" stroke-dasharray="2 6"/>')
    body.append(f'<path d="M{num(home)} {TRACK_Y - 9}v18" class="fig-grid-stroke" stroke-width="2"/>')
    # Shapes that share every attribute but a coordinate go under one group and inherit the rest.
    # It is the same drawing, and on a page carrying forty-eight of these it is a page lighter.
    body.append('<g class="fig-target">'
                + "".join(f'<circle cx="{num(s)}" cy="{TRACK_Y}" r="11"/>' for s in stops[1:])
                + "</g>")
    # Naming the parts. A single arrival is named where each part happens in space, with a tick on
    # the rail at the handover; a run of flicks is numbered under its targets.
    labels: list[tuple[float, str]] = []
    if len(stops) == 2:
        base = run.moves[0]
        shares, names = split_of(int(node.params["phases"]))
        done, edge = 0.0, base.x0
        for share, word in zip(shares, names):
            done += share
            end = base.x0 + (base.x1 - base.x0) * ease(done)
            labels.append(((edge + end) / 2, word))
            if done < 0.999:
                body.append(f'<path d="M{num(end)} {TRACK_Y - 7}v14" class="fig-grid-stroke" '
                            'stroke-width="1.6"/>')
            edge = end
    else:
        labels = [(stop, str(i + 1)) for i, stop in enumerate(stops[1:])]
    body.append('<g class="fig-muted fig-phase" text-anchor="middle" font-size="11" '
                'font-weight="600">'
                + "".join(f'<text x="{num(x)}" y="{PHASE_Y}">{word}</text>' for x, word in labels)
                + "</g>")
    # The clock: the same loop as time. Solid where the crosshair moves, pale where it rests, and
    # bare rail for the gap the loop replays over.
    scale = (BAR_X1 - BAR_X0) / total
    body.append(f'<rect x="{BAR_X0}" y="{BAR_Y}" width="{BAR_X1 - BAR_X0}" height="{BAR_H}" '
                f'rx="{BAR_H // 2}" class="fig-grid-fill" opacity="0.16"/>')
    for rest, shade in ((False, "0.9"), (True, "0.32")):
        bars = "".join(
            f'<rect x="{num(BAR_X0 + b.t0 * scale)}" y="{BAR_Y}" '
            f'width="{num((b.t1 - b.t0) * scale - 1.5)}" height="{BAR_H}" rx="5"/>'
            for b in run.blocks if b.rest is rest and (b.t1 - b.t0) * scale > 2.7)
        if bars:
            body.append(f'<g class="fig-balanced-fill" opacity="{shade}">{bars}</g>')
    css.append(f"@keyframes aimTec{slug}Sweep{{0%{{transform:translate(0,0)}}"
               f"100%{{transform:translate({BAR_X1 - BAR_X0}px,0)}}}}")
    body.append(f'<g class="{anim}" style="animation-name:aimTec{slug}Sweep">'
                f'<path d="M{BAR_X0} {BAR_Y - 5}v{BAR_H + 10}" class="fig-ink-stroke" '
                'stroke-width="1.5" opacity="0.4"/></g>')
    body.append(text(BAR_X0, CAP_Y, CAPTION[node.key], "fig-muted fig-caption", "start", 12, 600))
    # Each landing, marked once as it happens. These are the figure's only transient marks, so a
    # reader who asked for less motion gets all of them showing at once instead.
    css.append(f"@keyframes aimTec{slug}Hit{{0%{{opacity:0;transform:scale(.35)}}"
               "4%{opacity:.95;transform:scale(1)}18%{opacity:0;transform:scale(1.85)}"
               "100%{opacity:0;transform:scale(1.85)}}")
    css.append(f".{mark}{{animation-name:aimTec{slug}Hit;fill:none;stroke-width:2.4;opacity:0}}")
    body.append('<g class="fig-balanced-stroke">' + "".join(
        f'<circle cx="{num(where)}" cy="{TRACK_Y}" r="15" class="{mark}" '
        f'style="animation-delay:{secs(when - total)}s;'
        f'transform-origin:{num(where)}px {TRACK_Y}px"/>'
        for when, where in run.arrivals) + "</g>")
    # The loop's own seam, hidden: the crosshair fades out on the last target and fades back in at
    # the start, so the replay never reads as a motion the hand made.
    lead = 0.12 / total * 100
    out = (total - REPLAY + 0.08) / total * 100
    gone = (total - REPLAY + 0.24) / total * 100
    css.append(f"@keyframes aimTec{slug}Fade{{0%{{opacity:0}}{lead:.3g}%{{opacity:1}}"
               f"{out:.3g}%{{opacity:1}}{gone:.3g}%{{opacity:0}}100%{{opacity:0}}}}")
    css.append(keyframes(f"aimTec{slug}Go",
                         [position(run.moves, i / FRAMES * total) - home for i in range(FRAMES + 1)],
                         lambda dx: f"translate({px(dx)}px,0)"))
    if run.ghost:
        css.append(keyframes(
            f"aimTec{slug}Ghost",
            [position(run.ghost, i / GHOST_FRAMES * total) - home for i in range(GHOST_FRAMES + 1)],
            lambda dx: f"translate({px(dx)}px,0)"))
        body.append(f'<g class="{anim}" style="animation-name:aimTec{slug}Fade">'
                    f'<g class="{anim}" style="animation-name:aimTec{slug}Ghost">'
                    f'<circle cx="{num(home)}" cy="{UPPER_Y}" r="6" class="fig-muted" '
                    'opacity="0.75"/></g></g>')
    # The transform rides the inner group and the opacity the outer one, so neither animation has to
    # carry the other's property.
    body.append(f'<g class="{anim}" style="animation-name:aimTec{slug}Fade">'
                f'<g class="{anim}" style="animation-name:aimTec{slug}Go">'
                f'{crosshair("fig-balanced-stroke", home, TRACK_Y)}</g></g>')
    css.append(f".{anim},.{mark}{{animation-duration:{secs(total)}s;"
               "animation-timing-function:linear;animation-iteration-count:infinite}")
    css.append(f"@media (prefers-reduced-motion:reduce){{.{anim}{{animation-play-state:paused;"
               f"animation-delay:-{secs(run.pause * total)}s!important}}"
               f".{mark}{{animation:none!important;opacity:1!important}}}}")
    return (f'<svg viewBox="0 0 {W} {H}" class="fig-fit" role="img" '
            f'aria-labelledby="fig-{node.key}-title">'
            f'<title id="fig-{node.key}-title">{TITLE[node.key]}</title>' + metadata()
            + f'<style>{"".join(css)}</style>' + "".join(body) + "</svg>")
