"""Theme-aware inline SVG diagrams for the Metronome Training page. Colours come from the .aim-figure
classes in aim.css, so each diagram follows the reader's scheme and picked colour. build.py splices
them into the page; call it rather than this module.
"""
import math
import sys
from pathlib import Path

# The kit sits a folder up, beside the other pages' figure code, and is not an installed package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from figure_kit import crosshair, lane_label, metadata, smooth, text  # noqa: E402

W = 600

# Beat: the same four targets shot two ways. Three of them sit in a cluster and one is far off, which
# is the arrangement that decides whether a fixed tempo is a fair ask. The beat hands every shot the
# same slice of time, so the cluster shots arrive early and wait, and the far one is fired at before
# the flick can land. The second lane fires on arrival instead, and its rhythm comes out uneven,
# which is the point.
BEAT_P = 0.85                                       # seconds between ticks
BEAT_N = 4
BEAT_T = BEAT_P * BEAT_N                            # one loop, one shot per tick
TICKS = [BEAT_P * (i + 0.55) for i in range(BEAT_N)]
TARGETS = [126, 172, 218, 520]
BEAT_X0 = 100
BEAT_LANE_H = 112
BEAT_TOP = 62
BEAT_FRAMES = 150
# Times are stretched from real ones, so the loop is followable rather than lifelike. What has to
# stay true is the ratio: a flick across the screen costs far more than one inside a cluster.
SLOW = 1.8
SETTLE = 0.08 * SLOW                                # the pause between arriving and being still
GAP = 0.04 * SLOW                                   # dead time after a shot, before the next flick
HIT = 9.0                                           # how close to the centre still counts as a hit


def flick_time(distance: float) -> float:
    """Roughly how long a flick of this length takes. Aiming time grows with the log of the distance,
    so the far target costs more than twice what a step inside the cluster does."""
    return SLOW * (0.05 + 0.10 * math.log2(abs(distance) / 12 + 1))


def position(segments: list[tuple[float, float, float, float]], t: float) -> float:
    """Where the crosshair is at time t, given the flicks it has made."""
    x = float(BEAT_X0)
    for start, end, from_x, to_x in segments:
        if t <= start:
            return x
        if t < end:
            return from_x + (to_x - from_x) * (t - start) / (end - start)
        x = to_x
    return x


def lane_run(paced: bool) -> tuple[list[float], list[tuple[float, float, bool]]]:
    """One lane: the crosshair's position every frame, and the shots it takes.

    A paced lane fires on its tick whether or not the crosshair has arrived. An unpaced lane fires
    once the flick has landed and settled, which takes as long as it takes.
    """
    segments: list[tuple[float, float, float, float]] = []
    shots: list[tuple[float, float, bool]] = []
    x, t = float(BEAT_X0), 0.0
    for index, target in enumerate(TARGETS):
        travel = flick_time(target - x)
        segments.append((t, t + travel, x, float(target)))
        arrival = t + travel
        fire = TICKS[index] if paced else arrival + SETTLE
        at = position(segments, fire)
        shots.append((fire, at, abs(at - target) <= HIT))
        x, t = float(target), max(fire, arrival) + GAP
    frames = [position(segments, i / BEAT_FRAMES * BEAT_T) for i in range(BEAT_FRAMES + 1)]
    return frames, shots


def travel_keyframes(name: str, frames: list[float]) -> str:
    last = len(frames) - 1
    parts = [f"{i / last * 100:.3g}%{{transform:translate({x - BEAT_X0:.1f}px,0)}}"
             for i, x in enumerate(frames)]
    return f"@keyframes {name}{{{''.join(parts)}}}"


def beat() -> str:
    lanes = [
        ("On the beat", "waits in the cluster, then runs out of time", "fig-loose-stroke", True),
        ("Beat as a reference", "ahead in the cluster, behind on the long flick",
         "fig-balanced-stroke", False),
    ]
    height = BEAT_TOP + BEAT_LANE_H * len(lanes) + 4
    css = ["@keyframes aimMetSweep{0%{transform:translate(0,0)}"
           f"100%{{transform:translate({W - 40 - BEAT_X0}px,0)}}}}",
           "@keyframes aimMetFlash{0%{opacity:0;transform:scale(0.3)}3%{opacity:1;transform:scale(1)}"
           "14%{opacity:0;transform:scale(2)}100%{opacity:0;transform:scale(2)}}",
           "@keyframes aimMetTick{0%{opacity:0.35;transform:scale(1)}3%{opacity:1;transform:scale(1.7)}"
           "12%{opacity:0.35;transform:scale(1)}100%{opacity:0.35;transform:scale(1)}}",
           f".aim-met-anim,.aim-met-shot{{animation-duration:{BEAT_T}s;"
           "animation-timing-function:linear;animation-iteration-count:infinite}"]
    # The strip stands a little taller than the beats need, so the count above each one has room
    # inside it rather than hanging over the edge.
    body = [f'<rect x="8" y="8" width="{W - 16}" height="46" rx="10" class="fig-panel"/>',
            text(20, 34, "Beat", "fig-muted", "start", 13, 600, middle=True)]
    # The strip along the top is time, not space: each tick is one beat of the metronome.
    strip_x0, strip_x1 = BEAT_X0, W - 40
    for index, tick in enumerate(TICKS):
        tx = strip_x0 + (tick / BEAT_T) * (strip_x1 - strip_x0)
        body.append(f'<circle cx="{tx:.1f}" cy="39" r="5" class="fig-ink-fill aim-met-anim" '
                    f'style="animation-name:aimMetTick;animation-delay:{tick - BEAT_T:.3f}s;'
                    f'transform-origin:{tx:.1f}px 39px;opacity:0.35"/>')
        body.append(text(tx, 22, str(index + 1), "fig-muted", "middle", 11, 600, middle=True))
    body.append(f'<g class="aim-met-anim" style="animation-name:aimMetSweep">'
                f'<path d="M{strip_x0} 14V50" class="fig-accent-stroke" stroke-width="2"/></g>')
    for index, (name, note, stroke, paced) in enumerate(lanes):
        top = BEAT_TOP + BEAT_LANE_H * index
        y = top + 74
        frames, shots = lane_run(paced)
        css.append(travel_keyframes(f"aimMetLane{index}", frames))
        body.append(f'<rect x="8" y="{top}" width="{W - 16}" height="{BEAT_LANE_H - 10}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(24, top + 28, name, note))
        body.append(f'<path d="M{BEAT_X0 - 20} {y}H{W - 24}" class="fig-grid-stroke" stroke-width="1" '
                    'stroke-dasharray="2 6"/>')
        for target in TARGETS:
            body.append(f'<circle cx="{target}" cy="{y}" r="11" class="fig-target"/>')
        for fire, at, hit in shots:
            mark = "fig-balanced-stroke" if hit else "fig-tense-stroke"
            body.append(f'<circle cx="{at:.1f}" cy="{y}" r="13" class="{mark} aim-met-shot" fill="none" '
                        f'stroke-width="2.6" style="animation-name:aimMetFlash;'
                        f'animation-delay:{fire - BEAT_T:.3f}s;transform-origin:{at:.1f}px {y}px;'
                        'opacity:0"/>')
            if not hit:
                body.append(f'<path d="M{at - 6:.1f} {y - 6}l12 12M{at + 6:.1f} {y - 6}l-12 12" '
                            f'class="fig-tense-stroke aim-met-shot" stroke-width="2.6" '
                            f'style="animation-name:aimMetFlash;animation-delay:{fire - BEAT_T:.3f}s;'
                            f'transform-origin:{at:.1f}px {y}px;opacity:0"/>')
        body.append(f'<g class="aim-met-anim" style="animation-name:aimMetLane{index}">'
                    f'{crosshair(stroke, BEAT_X0, y)}</g>')
    # Readers who ask for less motion get the frame just after the far shot, where the lanes differ
    # most, with every shot mark left showing so the whole run is readable at once.
    css.append("@media (prefers-reduced-motion:reduce){.aim-met-anim{animation-play-state:paused;"
               f"animation-delay:-{BEAT_T - TICKS[-1] - 0.05:.2f}s!important}}"
               ".aim-met-shot{animation:none!important;opacity:1!important}}")
    return (f'<svg viewBox="0 0 {W} {height}" class="fig-fit" role="img" aria-labelledby="fig-beat-title">'
            '<title id="fig-beat-title">Four targets, three of them clustered and one far away, shot '
            'twice against a steady beat. On the beat: the crosshair reaches each clustered target early '
            'and waits for the tick, then the far target is fired at before the flick arrives, and '
            'missed. Beat as a reference: each shot goes when the crosshair lands, running ahead of the beat '
            'inside the cluster and behind it on the long flick, and all four hit.</title>' + metadata() +
            f'<style>{"".join(css)}</style>' + "".join(body) + "</svg>")


# Ramp: accuracy against tempo. The curve is flat while the tempo is inside what you can already do,
# bends at your own pace, and falls away once the beat is asking for flicks you cannot land. The band
# just above your pace is the only part with evidence behind it; the far right is where a tempo chosen
# for ambition puts you.
# The plot's own box, and the figure's, which is taller: the tempo axis and its name sit under it.
RAMP_W, RAMP_H = 600, 314
RAMP_X0, RAMP_X1 = 72, 560
RAMP_Y0, RAMP_Y1 = 44, 228
RAMP_LO, RAMP_HI = 60, 240      # BPM at each end of the axis
RAMP_OWN = 132                  # the reader's own pace, marked on the axis
# What a paced run's accuracy tells you to do next. Above the first, the beat is still inside what
# you can do; between the two, it is the tempo worth working on; below the second, it is asking for
# misses rather than teaching anything.
RAMP_RAISE, RAMP_STAY = 0.90, 0.80
RAMP_T = 7.0
RAMP_FRAMES = 120


def ramp_x(bpm: float) -> float:
    return RAMP_X0 + (bpm - RAMP_LO) / (RAMP_HI - RAMP_LO) * (RAMP_X1 - RAMP_X0)


def ramp_accuracy(bpm: float) -> float:
    """Accuracy at a tempo, as 0 to 1. Flat below your pace, then falling ever faster above it."""
    if bpm <= RAMP_OWN:
        return 0.97 - 0.0002 * (RAMP_OWN - bpm)
    over = (bpm - RAMP_OWN) / (RAMP_HI - RAMP_OWN)
    return max(0.12, 0.97 - 0.85 * over ** 1.9)


def ramp_y(accuracy: float) -> float:
    return RAMP_Y1 - accuracy * (RAMP_Y1 - RAMP_Y0)


def ramp_cross(accuracy: float) -> int:
    """The first tempo whose accuracy falls below this line."""
    return next((bpm for bpm in range(RAMP_LO, RAMP_HI + 1) if ramp_accuracy(bpm) < accuracy), RAMP_HI)


def ramp() -> str:
    curve = [(ramp_x(RAMP_LO + i), ramp_y(ramp_accuracy(RAMP_LO + i)))
             for i in range(RAMP_HI - RAMP_LO + 1)]
    path = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in curve)
    # Where the curve leaves each band is where the advice changes, so the figure finds those two
    # tempos rather than marking a fixed step above your pace.
    raise_to, work_to = ramp_cross(RAMP_RAISE), ramp_cross(RAMP_STAY)
    frames = [RAMP_LO + (RAMP_HI - RAMP_LO) * i / RAMP_FRAMES for i in range(RAMP_FRAMES + 1)]
    steps = "".join(
        f"{i / RAMP_FRAMES * 50:.3g}%{{transform:translate({ramp_x(bpm):.1f}px,"
        f"{ramp_y(ramp_accuracy(bpm)):.1f}px)}}" for i, bpm in enumerate(frames))
    css = [f"@keyframes aimRampRide{{{steps}"
           f"50%{{transform:translate({ramp_x(RAMP_HI):.1f}px,{ramp_y(ramp_accuracy(RAMP_HI)):.1f}px)}}"
           f"100%{{transform:translate({ramp_x(RAMP_LO):.1f}px,{ramp_y(ramp_accuracy(RAMP_LO)):.1f}px)}}}}",
           f".aim-ramp-anim{{animation-duration:{RAMP_T}s;animation-timing-function:linear;"
           "animation-iteration-count:infinite}",
           "@media (prefers-reduced-motion:reduce){.aim-ramp-anim{animation-play-state:paused;"
           f"animation-delay:-{RAMP_T * 0.30:.2f}s!important}}}}"]
    body = [f'<rect x="8" y="8" width="{RAMP_W - 16}" height="{RAMP_H - 16}" rx="12" class="fig-panel"/>']
    # One band per verdict, read off the accuracy axis rather than off the tempo.
    # The bottom band is the tall one, and the curve falls through the right of it, so its label goes
    # to the left where there is nothing. The other two are clear on the right.
    for low, high, fill, label, side in (
            (RAMP_RAISE, 1.0, "fig-balanced-fill", "90%+  raise the beat", "end"),
            (RAMP_STAY, RAMP_RAISE, "fig-target", "80%+  stay here", "end"),
            (0.0, RAMP_STAY, "fig-tense-fill", "under 80%  lower it", "start")):
        top, bottom = ramp_y(high), ramp_y(low)
        body.append(f'<rect x="{RAMP_X0}" y="{top:.1f}" width="{RAMP_X1 - RAMP_X0}" '
                    f'height="{bottom - top:.1f}" class="{fill}" opacity="0.14"/>')
        edge = RAMP_X0 + 12 if side == "start" else RAMP_X1 - 10
        body.append(text(edge, (top + bottom) / 2, label, "fig-muted", side, 12, 700, middle=True))
    for accuracy in (0.5, RAMP_STAY, RAMP_RAISE, 1.0):
        y = ramp_y(accuracy)
        body.append(f'<path d="M{RAMP_X0} {y:.1f}H{RAMP_X1}" class="fig-grid-stroke" stroke-width="1" '
                    'stroke-dasharray="2 6"/>')
        body.append(text(RAMP_X0 - 12, y + 5, f"{round(accuracy * 100)}%", "fig-muted", "end", 12, 500))
    body.append(f'<path d="M{RAMP_X0} {RAMP_Y1}H{RAMP_X1}" class="fig-grid-stroke" stroke-width="1.5"/>')
    body.append(f'<path d="{path}" class="fig-ink-stroke" stroke-width="3" fill="none" '
                'stroke-linejoin="round"/>')
    body.append(f'<path d="M{ramp_x(RAMP_OWN):.1f} {RAMP_Y0 - 8}V{RAMP_Y1 + 8}" '
                'class="fig-balanced-stroke" stroke-width="2" stroke-dasharray="5 4"/>')
    body.append(text(24, 28, "Accuracy", "fig-muted", "start", 13, 600))
    body.append(text(ramp_x(RAMP_OWN), RAMP_Y0 - 16, "your own pace", "fig-balanced-fill", "middle", 13, 700))
    # The tempos where a run lands in the middle band: the span worth working on, walled off so the
    # reader can read it off the tempo axis as well as off the accuracy one.
    for edge in (raise_to, work_to):
        body.append(f'<path d="M{ramp_x(edge):.1f} {RAMP_Y0 - 8}V{RAMP_Y1 + 8}" class="fig-ink-stroke" '
                    'stroke-width="2" stroke-dasharray="5 4" opacity="0.7"/>')
    body.append(text((ramp_x(raise_to) + ramp_x(work_to)) / 2, RAMP_Y1 + 24, "work here", "fig-ink",
                     "middle", 13, 700))
    for bpm in (60, 100, 140, 180, 220):
        body.append(text(ramp_x(bpm), RAMP_Y1 + 44, str(bpm), "fig-muted", "middle", 12, 500))
    body.append(text((RAMP_X0 + RAMP_X1) / 2, RAMP_Y1 + 68, "Beats per minute (BPM)", "fig-muted",
                     "middle", 13, 600))
    body.append('<g class="aim-ramp-anim" style="animation-name:aimRampRide">'
                '<circle cx="0" cy="0" r="8" class="fig-accent-fill"/></g>')
    return (f'<svg viewBox="0 0 {RAMP_W} {RAMP_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-ramp-title">'
            '<title id="fig-ramp-title">Accuracy plotted against tempo. The line is flat while the beat '
            'asks for no more than you already do, and falls away above your own pace, slowly at first '
            'and then steeply. Three bands across the chart say what to do with a paced run: above 90 '
            'percent raise the beat, between 80 and 90 stay where you are and work, under 80 lower it. '
            'Two dashed lines across the chart wall off the tempos that land in the middle band.</title>' + metadata() +
            f'<style>{"".join(css)}</style>' + "".join(body) + "</svg>")


# Settle: one shot, drawn as time rather than space. A shot is a flick, the moment spent confirming
# the crosshair is on the target, and any micro-corrections in between. The metronome's case is that
# the second bar is mostly micro, and that a beat cuts it off. The case against is that on a far
# target one of those micros is what makes the shot land at all.
SET_W, SET_H = 600, 232
SET_X0, SET_X1 = 150, 560
SET_T = 4.2
SET_SCALE = 0.62                       # seconds of shot per full width of the bar
SET_CUT = 0.31                         # where the beat falls: halfway through the first micro
SET_ROWS = [
    ("Commit", "the beat arrives, the shot goes", [
        ("Flick", 0.17, "fig-ink-fill", 0.7),
        ("Confirm", 0.09, "fig-balanced-fill", 0.8),
        ("½", 0.05, "fig-tense-fill", 0.75),
    ]),
    ("Fine-tune", "micro, confirm, micro again", [
        ("Flick", 0.17, "fig-ink-fill", 0.7),
        ("Confirm", 0.09, "fig-balanced-fill", 0.8),
        ("Micro", 0.10, "fig-tense-fill", 0.75),
        ("Confirm", 0.09, "fig-balanced-fill", 0.8),
        ("Micro", 0.09, "fig-tense-fill", 0.75),
    ]),
]


def settle() -> str:
    span = SET_X1 - SET_X0
    css = [f"@keyframes aimSetSweep{{0%{{transform:translate(0,0)}}"
           f"82%{{transform:translate({span}px,0)}}100%{{transform:translate({span}px,0)}}}}",
           f".aim-set-anim{{animation-duration:{SET_T}s;animation-timing-function:linear;"
           "animation-iteration-count:infinite}",
           "@media (prefers-reduced-motion:reduce){.aim-set-anim{animation-play-state:paused;"
           f"animation-delay:-{SET_T * 0.82 * SET_CUT / SET_SCALE:.2f}s!important}}}}"]
    body = [f'<rect x="8" y="8" width="{SET_W - 16}" height="{SET_H - 16}" rx="12" class="fig-panel"/>']
    for index, (name, note, parts) in enumerate(SET_ROWS):
        top = 52 + index * 84
        y = top + 24
        body.append(lane_label(24, top - 4, name, ""))
        body.append(text(24, top + 16, note, "fig-muted", "start", 13, 500))
        x = float(SET_X0)
        total = 0.0
        for label, seconds, fill, opacity in parts:
            width = seconds / SET_SCALE * span
            body.append(f'<rect x="{x:.1f}" y="{y}" width="{width - 3:.1f}" height="30" rx="6" '
                        f'class="{fill}" opacity="{opacity}"/>')
            # A label sits inside its block with room to spare, or it does not go in at all: text that
            # runs into the rounded edge reads as a mistake. Bold display glyphs run about 0.62em.
            for size in (12, 11, 10):
                if len(label) * size * 0.62 + 14 <= width:
                    body.append(text(x + width / 2 - 1.5, y + 15, label, "fig-surface", "middle",
                                     size, 700, middle=True))
                    break
            x += width
            total += seconds
        # Where the bar ends is where the trigger is pulled, marked rather than animated: two moving
        # things in one figure and the eye has nowhere to rest.
        body.append(f'<path d="M{x + 3:.1f} {y - 5}v40" class="fig-accent-stroke" stroke-width="3"/>')
        body.append(text(x + 14, y + 20, f"{round(total * 1000)} ms", "fig-muted", "start", 13, 600))
    # Where a beat set for the committed shot actually lands on the fine-tuned one: half a confirm
    # and half a micro past the flick, which is just as the second bar starts correcting.
    cut = SET_X0 + (SET_CUT / SET_SCALE) * span
    body.append(f'<path d="M{cut:.1f} 40V{SET_H - 30}" class="fig-tense-stroke" stroke-width="2" '
                'stroke-dasharray="5 4"/>')
    body.append(text(cut + 6, 36, "the beat", "fig-tense-fill", "start", 13, 700))
    body.append(f'<g class="aim-set-anim" style="animation-name:aimSetSweep">'
                f'<path d="M{SET_X0} 62V{SET_H - 34}" class="fig-ink-stroke" stroke-width="1.5" '
                'opacity="0.35"/></g>')
    body.append(text(SET_X0, SET_H - 12, "one shot, start to trigger", "fig-muted", "start", 13, 600))
    return (f'<svg viewBox="0 0 {SET_W} {SET_H}" class="fig-fit" role="img" aria-labelledby="fig-settle-title">'
            '<title id="fig-settle-title">One shot drawn as a bar of time. On the first bar the beat '
            'arrives partway through the first micro-correction and the trigger goes at 310 '
            'milliseconds. The second bar keeps correcting instead, taking 510 milliseconds for the same '
            'shot. A dashed line marks where the beat falls across both.</title>'
            + metadata() + f'<style>{"".join(css)}</style>' + "".join(body) + "</svg>")


# Tension: five ways to spend one shot, on one shared clock. What the hand chooses is how much of the
# time goes into the flick and how much into fixing it afterwards. A tight hand throws the flick out
# fast and pays for the overshoot; a loose one crawls out and has nothing left to correct with. The
# beat is fixed, so two of these are still correcting when it arrives.
TEN_W = 600
TEN_LANE_H = 96
TEN_TOP = 10
TEN_X0, TEN_TARGET = 96, 400          # where the crosshair starts, and where the target sits
TEN_BAR_X1 = 560
TEN_BEAT = 0.30                       # the beat, in seconds of shot
TEN_WINDOW = 0.44                     # how much of the clock the bars span
TEN_PLAY = 2.0                        # seconds on screen per TEN_BEAT of shot, since 300 ms is a blur
TEN_T = 3.6                           # one loop: the slowest shot, then a pause
TEN_FRAMES = 180
# Each half of a shot is coloured by its speed, the way the rest of the site colours tension: red for
# fast, blue for slow, green for the balanced one in the middle.
TEN_FAST, TEN_EVEN, TEN_SLOW = "tense", "balanced", "loose"
# name, note, flick seconds, micro seconds, where the flick leaves the crosshair, where it stops,
# and the speed of each half.
TEN_LANES = [
    ("Fast, fast", "no time to fix the overshoot", 0.09, 0.06, 1.10, 1.04, TEN_FAST, TEN_FAST),
    ("Fast, slow", "overshoots, then pays it back", 0.09, 0.21, 1.12, 1.0, TEN_FAST, TEN_SLOW),
    ("Balanced", "one motion, short correction", 0.17, 0.13, 0.99, 1.0, TEN_EVEN, TEN_EVEN),
    ("Slow, fast", "arrives short, snaps on", 0.24, 0.06, 0.88, 1.0, TEN_SLOW, TEN_FAST),
    ("Slow, slow", "cut off short by the tick", 0.24, 0.18, 0.88, 1.0, TEN_SLOW, TEN_SLOW),
]


def ten_crosshair(x: float, y: float) -> str:
    """The lane's crosshair, drawn in whatever colour its group carries, so it can change mid-shot."""
    r = 8
    return (f'<circle cx="{x}" cy="{y}" r="{r}" stroke="currentColor" stroke-width="2.2" fill="none"/>'
            f'<path d="M{x - r - 5} {y}H{x - r + 4}M{x + r - 4} {y}H{x + r + 5}'
            f'M{x} {y - r - 5}V{y - r + 4}M{x} {y + r - 4}V{y + r + 5}" stroke="currentColor" '
            'stroke-width="2.2" fill="none"/>')
HIT = 0.02                            # how close to the target still counts, as a share of the distance


def ten_travel(flick: float, micro: float, peak: float, end: float, t: float) -> float:
    """How much of the distance is covered at t seconds, for one hand's flick and micro.

    A hand that rushes its micro-correction runs out of correction before it runs out of error, so
    `end` is where it actually stops rather than on the target.
    """
    if t <= 0:
        return 0.0
    if t < flick:
        return peak * smooth(t / flick)
    if t < flick + micro:
        return peak + (end - peak) * smooth((t - flick) / micro)
    return end


def tension() -> str:
    height = TEN_TOP + TEN_LANE_H * len(TEN_LANES) + 34
    span = TEN_TARGET - TEN_X0
    bar_w = TEN_BAR_X1 - TEN_X0
    per_second = bar_w / TEN_WINDOW
    beat_x = TEN_X0 + TEN_BEAT * per_second
    css = ["@keyframes aimTenFlash{0%{opacity:0;transform:scale(0.3)}4%{opacity:1;transform:scale(1)}"
           "20%{opacity:0;transform:scale(2)}100%{opacity:0;transform:scale(2)}}",
           f".aim-ten-anim,.aim-ten-shot{{animation-duration:{TEN_T}s;animation-timing-function:linear;"
           "animation-iteration-count:infinite}"]
    body = []
    for index, (name, note, flick, micro, peak, end, flick_speed, micro_speed) in enumerate(TEN_LANES):
        top = TEN_TOP + TEN_LANE_H * index
        y = top + 40
        # The shot goes when the hand is finished, or when the beat says so, whichever comes first.
        fire = min(flick + micro, TEN_BEAT)
        at = ten_travel(flick, micro, peak, end, fire)
        hit = abs(at - 1.0) <= HIT
        # The clock runs at TEN_PLAY seconds per TEN_BEAT of shot, so every lane shares one speed.
        scale = TEN_PLAY / TEN_BEAT
        frames = [ten_travel(flick, micro, peak, end, frame / TEN_FRAMES * TEN_T / scale) * span
                  for frame in range(TEN_FRAMES + 1)]
        css.append(f"@keyframes aimTenLane{index}{{" + "".join(
            f"{i / TEN_FRAMES * 100:.3g}%{{transform:translate({dx:.1f}px,0)}}"
            for i, dx in enumerate(frames)) + "}")
        body.append(f'<rect x="8" y="{top}" width="{TEN_W - 16}" height="{TEN_LANE_H - 10}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(24, top + 24, name, note))
        body.append(f'<path d="M{TEN_X0 - 16} {y}H{TEN_TARGET + 34}" class="fig-grid-stroke" '
                    'stroke-width="1" stroke-dasharray="2 6"/>')
        body.append(f'<circle cx="{TEN_TARGET}" cy="{y}" r="10" class="fig-target"/>')
        mark = "fig-balanced-stroke" if hit else "fig-tense-stroke"
        shot_x = TEN_X0 + at * span
        body.append(f'<circle cx="{shot_x:.1f}" cy="{y}" r="12" class="{mark} aim-ten-shot" fill="none" '
                    f'stroke-width="2.4" style="animation-name:aimTenFlash;'
                    f'animation-delay:{fire * scale - TEN_T:.3f}s;transform-origin:{shot_x:.1f}px {y}px;'
                    'opacity:0"/>')
        if not hit:
            body.append(f'<path d="M{shot_x - 5:.1f} {y - 5}l10 10M{shot_x + 5:.1f} {y - 5}l-10 10" '
                        f'class="fig-tense-stroke aim-ten-shot" stroke-width="2.4" '
                        f'style="animation-name:aimTenFlash;animation-delay:{fire * scale - TEN_T:.3f}s;'
                        f'transform-origin:{shot_x:.1f}px {y}px;opacity:0"/>')
        # The crosshair carries the colour of the half it is in: the transform rides the outer group
        # and the colour the inner one, so the two animations do not fight over one style.
        handover = flick * scale / TEN_T * 100
        css.append(f"@keyframes aimTenColour{index}{{0%{{color:var(--aim-{flick_speed})}}"
                   f"{handover:.3g}%{{color:var(--aim-{flick_speed})}}"
                   f"{handover + 0.01:.3g}%{{color:var(--aim-{micro_speed})}}"
                   f"100%{{color:var(--aim-{micro_speed})}}}}")
        body.append(f'<g class="aim-ten-anim" style="animation-name:aimTenLane{index}">'
                    f'<g class="aim-ten-anim" style="animation-name:aimTenColour{index}">'
                    f'{ten_crosshair(TEN_X0, y)}</g></g>')
        # The same clock under every lane: the flick, then the micro that pays for it.
        bar_y = top + TEN_LANE_H - 32
        for width, cls, opacity, label in (
                (flick * per_second, f"fig-{flick_speed}-fill", 0.85, "Flick"),
                (micro * per_second, f"fig-{micro_speed}-fill", 0.85, "Micro")):
            body.append(f'<rect x="{TEN_X0 + (0 if label == "Flick" else flick * per_second):.1f}" '
                        f'y="{bar_y}" width="{width - 2:.1f}" height="15" rx="7" class="{cls}" '
                        f'opacity="{opacity}"/>')
        if flick * per_second > 52:
            body.append(text(TEN_X0 + flick * per_second / 2 - 1, bar_y + 8, "Flick",
                             "fig-surface", "middle", 11, 700, middle=True))
        if micro * per_second > 52:
            body.append(text(TEN_X0 + (flick + micro / 2) * per_second - 1, bar_y + 8, "Micro",
                             "fig-surface", "middle", 11, 700, middle=True))
        # The number is what that hand's shot costs, which is not always when the trigger went: a hand
        # still correcting at the beat needs longer than the beat gives it.
        body.append(text(TEN_X0 + (flick + micro) * per_second + 10, bar_y + 12,
                         f"{round((flick + micro) * 1000)} ms",
                         "fig-muted" if hit else "fig-tense-fill", "start", 12, 600))
        # The beat, drawn across the clock only: the track above it is distance, not time.
        body.append(f'<path d="M{beat_x:.1f} {bar_y - 7}v29" class="fig-tense-stroke" stroke-width="2" '
                    'stroke-dasharray="4 3"/>')
    body.append(text(beat_x, height - 14, "the beat", "fig-tense-fill", "middle", 13, 700))
    body.append(text(TEN_X0, height - 14, "one shot, start to trigger", "fig-muted", "start", 13, 600))
    css.append("@media (prefers-reduced-motion:reduce){.aim-ten-anim{animation-play-state:paused;"
               f"animation-delay:-{TEN_PLAY:.2f}s!important}}"
               ".aim-ten-shot{animation:none!important;opacity:1!important}}")
    return (f'<svg viewBox="0 0 {TEN_W} {height}" class="fig-fit" role="img" '
            'aria-labelledby="fig-tension-title">'
            '<title id="fig-tension-title">One flick to one target, made five ways, against a fixed '
            'beat. A fast flick with a fast correction lands early and waits. A fast flick with a slow '
            'correction overshoots and spends the rest of the time crawling back. A balanced hand takes '
            'one motion and a short correction. A slow flick falls short and snaps on at the end. A slow '
            'flick with a slow correction is still correcting when the beat arrives. The clock under '
            'each lane shows where that hand spent its time.</title>' + metadata() +
            f'<style>{"".join(css)}</style>' + "".join(body) + "</svg>")
