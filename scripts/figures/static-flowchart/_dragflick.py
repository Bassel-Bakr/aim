"""Drag-flick: what a shot fired mid-motion costs, drawn as a length rather than a wait.

The counter-intuitive part of a dragging flick is that the wait between pressing the button and the
shot resolving is not what hurts. That wait is the same however the hand moves. What changes is how
much ground the crosshair covers while it passes, and that turns a fixed wait into a distance on
screen. Three passes over one target, at three hand speeds, share one window and come out with three
different gaps.

No duration is named anywhere in the figure, and none should be added: the page cites no measurement
for it, and the drawing only has to show the mechanism.
"""
import sys
from pathlib import Path
from collections.abc import Sequence

# The kit sits a folder up, beside the other pages' figure code, and is not an installed package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from figure_kit import crosshair, keyframes, lane_label, metadata, smooth, text  # noqa: E402

W = 600

# The lane, repeated once per hand speed. Each row is its own region: a track in space on top, and a
# button strip in time underneath, kept apart so neither is read in the other's units.
ROW_TOP = 8
ROW_H = 130
PANEL_H = 122
LABEL_DY = 22                      # lane name and note, baseline inside the panel
TRACK_DY = 56                      # the line the crosshair rides
BRACKET_DY = 84                    # the gap between where it was aimed and where it landed
STRIP_DY = 98                      # top of the button strip
STRIP_H = 13
TRACK_X0, TRACK_X1 = 56, 528
TX, TR = 364, 22                   # the target, and its radius: the aim point is its centre
SX0, SX1 = 104, 234                # the button strip runs between these, the same in every row

# One clock for every row, in seconds on screen. The press is simultaneous across the three passes,
# so the three windows fill together and their sameness needs no label to carry it.
T = 7.40
FRAMES = 185
DT = T / FRAMES
RAMP_UP, RAMP_DOWN = 0.48, 0.56    # the hand getting under way, and coasting to a stop afterwards
PRESS = 5.00
LAT = 0.40                         # press to registration: deliberately unlabelled, and identical
REG = PRESS + LAT
PRESS_F = round(PRESS / DT)
REG_F = round(REG / DT)
# name, note, when the hand sets off, how far the shot drifts, the outcome, and whether it still hit.
# The drift is the speed times the window, so choosing it here is choosing the hand's speed.
PASSES: Sequence[tuple[str, str, float, float, str, bool]] = [
    ("Slow", "hardly moves while the shot resolves", 0.40, 11.0, "gap, still on", True),
    ("Faster", "the same wait, more ground covered", 1.60, 22.0, "gap, on the rim", True),
    ("Fastest", "same wait again, the shot lands past the target", 2.92, 53.0,
     "gap, off the target", False),
]
HEIGHT = ROW_TOP + ROW_H * len(PASSES) + 28


def pct(seconds: float) -> str:
    return f"{seconds / T * 100:.4g}"


def speed(launch: float, peak: float, t: float) -> float:
    """How fast the hand is moving at t. It eases up to its cruising speed, holds that speed across
    the target and right through the window, then eases back down once the shot has registered.
    Holding the speed flat across the window is the whole claim: the drift is speed times wait."""
    if t <= launch:
        return 0.0
    if t < launch + RAMP_UP:
        return peak * smooth((t - launch) / RAMP_UP)
    if t < REG:
        return peak
    if t < REG + RAMP_DOWN:
        return peak * (1.0 - smooth((t - REG) / RAMP_DOWN))
    return 0.0


def sweep(launch: float, peak: float) -> list[float]:
    """Ground covered by the end of each frame, integrated rather than sampled, so the eased ramps
    keep their shape instead of being stepped through."""
    steps = 8
    covered, run = [0.0], 0.0
    for frame in range(FRAMES):
        for sub in range(steps):
            run += speed(launch, peak, (frame + (sub + 0.5) / steps) * DT) * DT / steps
        covered.append(run)
    return covered


def dragflick() -> str:
    css = [".aim-drg-anim,.aim-drg-mark{animation-duration:" + f"{T}s;"
           "animation-timing-function:linear;animation-iteration-count:infinite}",
           # The button, held from the press until the shot resolves. Identical in all three rows,
           # and it snaps back rather than draining, so the reset is not a fourth moving thing.
           "@keyframes aimDrgWindow{0%{transform:scaleX(0)}"
           f"{pct(PRESS)}%{{transform:scaleX(0)}}{pct(REG)}%{{transform:scaleX(1)}}"
           "99%{transform:scaleX(1)}99.4%{transform:scaleX(0)}100%{transform:scaleX(0)}}",
           # Where the shot went, revealed when it registers and left standing for the rest of the
           # loop, so all three gaps can be compared against each other rather than remembered.
           "@keyframes aimDrgMark{0%{opacity:0}" + f"{pct(REG)}%{{opacity:0}}"
           f"{pct(REG + 0.19)}%{{opacity:1}}95%{{opacity:1}}99%{{opacity:0}}100%{{opacity:0}}}}"]
    body: list[str] = []
    for index, (name, note, launch, gap, outcome, hit) in enumerate(PASSES):
        top = ROW_TOP + ROW_H * index
        y = top + TRACK_DY
        by = top + BRACKET_DY
        covered = sweep(launch, gap / LAT)
        # Every pass crosses the target's centre at the same instant, so the start of its sweep is
        # wherever that leaves it. A faster hand simply came from further away.
        start = TX - covered[PRESS_F]
        landing = start + covered[REG_F]
        rest = start + covered[-1]
        css.append(keyframes(f"aimDrgSweep{index}", covered, lambda d: f"translate({d:.1f}px,0)"))
        body.append(f'<rect x="8" y="{top}" width="{W - 16}" height="{PANEL_H}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(24, top + LABEL_DY, name, note))
        body.append(f'<path d="M{TRACK_X0} {y}H{TRACK_X1}" class="fig-grid-stroke" stroke-width="1" '
                    'stroke-dasharray="2 6"/>')
        # The stretch this hand actually covered, from where it set off to where it coasted to rest.
        # Its length is the speed, read off the picture rather than asserted in a label.
        body.append(f'<path d="M{start:.1f} {y}H{rest:.1f}" class="fig-muted-stroke" stroke-width="2" '
                    'opacity="0.4"/>')
        body.append(f'<path d="M{start:.1f} {y - 7}v14" class="fig-muted-stroke" stroke-width="2" '
                    'opacity="0.55"/>')
        body.append(f'<circle cx="{TX}" cy="{y}" r="{TR}" class="fig-target"/>')
        # The aim point, carried down to the bracket so the gap has something to start from.
        body.append(f'<path d="M{TX} {y - TR - 8}V{by}" class="fig-ink-stroke" stroke-width="1.5" '
                    'stroke-dasharray="4 4" opacity="0.45"/>')
        if index == 0:
            body.append(text(TX, y - TR - 12, "aimed", "fig-muted", "middle", 12, 600))
        # The verdict is a colour and the mechanism is a length, so the bracket carries both: the
        # three of them are read against each other for size, and only the last one is red.
        stroke = "fig-balanced-stroke" if hit else "fig-tense-stroke"
        ink = "fig-balanced-fill" if hit else "fig-tense-fill"
        body.append(f'<circle cx="{landing:.1f}" cy="{y}" r="11" class="{stroke} aim-drg-mark" '
                    'fill="none" stroke-width="2.6" style="animation-name:aimDrgMark" opacity="0"/>')
        body.append(f'<path d="M{TX} {by - 6}V{by + 6}M{TX} {by}H{landing:.1f}'
                    f'M{landing:.1f} {by - 6}V{by + 6}" class="{stroke} aim-drg-mark" '
                    'stroke-width="2.2" fill="none" style="animation-name:aimDrgMark" opacity="0"/>')
        body.append(f'<g class="aim-drg-mark" style="animation-name:aimDrgMark" opacity="0">'
                    + text(landing + 10, by + 4, outcome, ink, "start", 12, 700) + '</g>')
        # The button strip: time, not space, which is why it keeps its own band and its own ticks.
        # Its two ends are named in every row rather than once, since the reader's whole job here is
        # to notice that the three of them are the same length.
        strip_y = top + STRIP_DY
        mid = strip_y + STRIP_H / 2
        body.append(text(SX0 - 8, mid, "press", "fig-muted", "end", 12, 600, middle=True))
        body.append(text(SX1 + 8, mid, "shot registers", "fig-muted", "start", 12, 600, middle=True))
        body.append(f'<rect x="{SX0}" y="{strip_y}" width="{SX1 - SX0}" height="{STRIP_H}" rx="6" '
                    'class="fig-grid-fill" opacity="0.35"/>')
        body.append(f'<rect x="{SX0}" y="{strip_y}" width="{SX1 - SX0}" height="{STRIP_H}" rx="6" '
                    f'class="fig-accent-fill aim-drg-anim" style="animation-name:aimDrgWindow;'
                    f'transform-origin:{SX0}px {strip_y + STRIP_H / 2}px;transform:scaleX(0)"/>')
        for edge in (SX0, SX1):
            body.append(f'<path d="M{edge} {strip_y - 4}v{STRIP_H + 8}" class="fig-muted-stroke" '
                        'stroke-width="1.5" opacity="0.6"/>')
        # The crosshair rides on top of its own marks, so at the moment of registration it is sitting
        # exactly on the ring it just put there. It stays ink rather than taking a colour: in the
        # light scheme the accent and the tense red are the same hue, and a red crosshair sitting
        # inside a red miss ring is one mark too many to tell apart.
        body.append(f'<g class="aim-drg-anim" style="animation-name:aimDrgSweep{index}">'
                    f'{crosshair("fig-ink-stroke", start, y)}</g>')
    body.append(text(24, HEIGHT - 12, "The button is held the same span in all three. Only the "
                     "distance changes.", "fig-muted", "start", 13, 600))
    # Less motion gets the frame the whole figure is about: the instant each shot registers, where
    # the gap between the aim point and the landing point is at its widest in every row.
    css.append("@media (prefers-reduced-motion:reduce){.aim-drg-anim{animation-play-state:paused;"
               f"animation-delay:-{REG:.2f}s!important}}"
               ".aim-drg-mark{animation:none!important;opacity:1!important}}")
    return (f'<svg viewBox="0 0 {W} {HEIGHT}" class="fig-fit" role="img" '
            'aria-labelledby="fig-dragflick-title">'
            '<title id="fig-dragflick-title">One target crossed three times, by a slow hand, a faster '
            'one and a fastest one. In each pass the crosshair sweeps across the target and the button '
            'goes down while it is still travelling, rather than after it has settled. The strip under '
            'each lane is the mouse button, held from the press until the shot registers, and it is the '
            'same length in all three passes. Because the crosshair keeps moving through that window, '
            'the shot lands where the crosshair was when it registered rather than where it was aimed, '
            'and a bracket under each lane measures the gap between the two. The slow pass leaves a gap '
            'narrow enough that the shot is still on the target, the faster pass leaves one that puts '
            'the shot on the rim, and the fastest pass leaves a gap wider than the target, so the shot '
            'lands clear of it and is marked as a miss. The wait never changes across the three; only '
            'the distance it costs does.</title>' + metadata() +
            f'<style>{"".join(css)}</style>' + "".join(body) + "</svg>")
