"""Symptoms: the three things worth watching for on a replay, drawn as motion and nothing else.

Each panel gets the same target, the same starting point and the same clock, so the only thing that
can differ between them is the shape of the motion. The trail behind each crosshair is sampled at
equal slices of that one clock, which is why the dots crowd where the hand was slow and spread where
it was fast: a still frame of the figure still says which symptom is which.

The figure names symptoms and stops there. What causes any of them is the route figure's job, so
nothing here takes a tension colour: all three crosshairs are the same accent, or the reader would
read a verdict off the palette rather than off the motion.
"""
import sys
from collections.abc import Sequence
from pathlib import Path

# The kit sits a folder up, beside the other pages' figure code, and is not an installed package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from figure_kit import crosshair, keyframes, lane_label, metadata, smooth, text  # noqa: E402

W = 600
SYM_TOP = 10
SYM_LANE_H = 122
SYM_FOOT = 34
SYM_X0, SYM_TARGET = 118, 466          # where every crosshair starts, and where every target sits
SYM_T = 3.6                            # one loop, shared by all three panels
SYM_FRAMES = 160                       # frames per lane in the travel keyframes
SYM_DOTS = 26                          # ticks of the shared clock left behind as a trail
SYM_LIFT = 9                           # how far off the track a trail dot sits
# The frame the figure holds on when the reader asks for less motion. It is the moment the first
# shot goes: by then the first panel is at the far end of its overshoot, the second is at the start
# of its crawl, and the third has already fired. One frame, three different places.
SYM_PAUSE = 0.26

# A leg is where the crosshair should be, as a share of the distance, and when it should be there,
# as a share of the loop. Easing inside each leg comes from smooth(), so the crosshair starts and
# stops rather than jumping between legs.
Leg = tuple[float, float]
# name, note, legs, and when the trigger goes.
SYM_LANES: list[tuple[str, str, list[Leg], float]] = [
    ("It sails past", "out past the target, then back",
     [(0.26, 1.16), (0.52, 1.00)], 0.60),
    ("It creeps in", "most of the way fast, the rest a crawl",
     [(0.20, 0.80), (0.38, 0.90), (0.62, 0.96), (0.90, 1.00)], 0.94),
    ("The shot goes early", "the trigger beats the crosshair",
     [(0.24, 0.92), (0.50, 1.00)], SYM_PAUSE),
]


def sym_travel(legs: Sequence[Leg], u: float) -> float:
    """How much of the distance is covered at u, as a share of one loop. Holds after the last leg."""
    start_u, start_p = 0.0, 0.0
    for end_u, end_p in legs:
        if u < end_u:
            return start_p + (end_p - start_p) * smooth((u - start_u) / (end_u - start_u))
        start_u, start_p = end_u, end_p
    return start_p


def sym_trail(legs: Sequence[Leg], y: float) -> str:
    """The travelled path: one dot per tick of the shared clock, plus a faint line through them.

    A dot sits above the track while the crosshair is running out and below it while it is coming
    back, so an excursion past the target closes into a loop rather than doubling back over itself.
    """
    span = SYM_TARGET - SYM_X0
    points: list[tuple[float, float]] = [(float(SYM_X0), y - SYM_LIFT)]
    previous = 0.0
    for step in range(1, SYM_DOTS + 1):
        share = sym_travel(legs, step / SYM_DOTS)
        lift = SYM_LIFT if share < previous - 1e-6 else -SYM_LIFT
        points.append((SYM_X0 + share * span, y + lift))
        previous = share
    line = "M" + "L".join(f"{x:.1f} {py:.1f}" for x, py in points)
    dots = "".join(f'<circle cx="{x:.1f}" cy="{py:.1f}" r="2.2" class="fig-accent-fill" opacity="0.5"/>'
                   for x, py in points[1:])
    return (f'<path d="{line}" class="fig-accent-stroke" stroke-width="1.5" fill="none" '
            f'opacity="0.3" stroke-linejoin="round"/>{dots}')


def sym_shot_keyframes(name: str, fire: float) -> str:
    """A mark rather than a mover: the shot appears at its moment and stays for the rest of the loop,
    so the panel keeps only one moving thing in it."""
    return (f"@keyframes {name}{{0%{{opacity:0}}{fire * 100:.4g}%{{opacity:0}}"
            f"{(fire + 0.004) * 100:.4g}%{{opacity:1}}100%{{opacity:1}}}}")


def symptoms() -> str:
    span = SYM_TARGET - SYM_X0
    height = SYM_TOP + SYM_LANE_H * len(SYM_LANES) + SYM_FOOT
    css = [f".aim-sym-anim,.aim-sym-shot{{animation-duration:{SYM_T}s;"
           "animation-timing-function:linear;animation-iteration-count:infinite}"]
    body: list[str] = []
    for index, (name, note, legs, fire) in enumerate(SYM_LANES):
        top = SYM_TOP + SYM_LANE_H * index
        y = top + 74
        frames = [sym_travel(legs, frame / SYM_FRAMES) * span for frame in range(SYM_FRAMES + 1)]
        css.append(keyframes(f"aimSymLane{index}", frames,
                             lambda dx: f"translate({dx:.1f}px,0)"))
        css.append(sym_shot_keyframes(f"aimSymShot{index}", fire))
        body.append(f'<rect x="8" y="{top}" width="{W - 16}" height="{SYM_LANE_H - 10}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(24, top + 26, name, note))
        body.append(f'<path d="M{SYM_X0 - 18} {y}H540" class="fig-grid-stroke" stroke-width="1" '
                    'stroke-dasharray="2 6"/>')
        body.append(sym_trail(legs, y))
        body.append(f'<circle cx="{SYM_TARGET}" cy="{y}" r="10" class="fig-target"/>')
        # Where the trigger went, which is the one thing the third panel does differently.
        shot_x = SYM_X0 + sym_travel(legs, fire) * span
        body.append(f'<g class="aim-sym-shot" style="animation-name:aimSymShot{index};opacity:0">'
                    f'<circle cx="{shot_x:.1f}" cy="{y}" r="15" class="fig-ink-stroke" fill="none" '
                    'stroke-width="2.4"/>'
                    f'<path d="M{shot_x:.1f} {y + 15}v9" class="fig-ink-stroke" stroke-width="2.4"/>'
                    f'{text(shot_x, top + 102, "shot", "fig-muted", "middle", 12, 600)}</g>')
        body.append(f'<g class="aim-sym-anim" style="animation-name:aimSymLane{index}">'
                    f'{crosshair("fig-accent-stroke", SYM_X0, y)}</g>')
    body.append(text(24, height - 14, "One clock for all three. The dots crowd where the crosshair "
                     "was slow.", "fig-muted", "start", 13, 600))
    # Less motion gets the frame the first shot goes on, with every shot mark left showing, since a
    # paused figure that hides two of its three marks says less than the running one.
    css.append("@media (prefers-reduced-motion:reduce){.aim-sym-anim{animation-play-state:paused;"
               f"animation-delay:-{SYM_T * SYM_PAUSE:.2f}s!important}}"
               ".aim-sym-shot{animation:none!important;opacity:1!important}}")
    return (f'<svg viewBox="0 0 {W} {height}" class="fig-fit" role="img" '
            'aria-labelledby="fig-symptoms-title">'
            '<title id="fig-symptoms-title">Three panels, each with the same target, the same '
            'starting point and the same clock, so only the shape of the motion can differ. In the '
            'first the crosshair flicks out past the target and comes back, and its trail loops out '
            'above the line and returns below it. In the second it covers most of the distance '
            'quickly and then inches the last short stretch, so its trail dots crowd together just '
            'short of the target. In the third the motion is ordinary but the shot mark falls early, '
            'while the crosshair is still short of the target and still settling. Every dot is one '
            'tick of the shared clock, so where the dots crowd the crosshair was slow.</title>'
            + metadata() + f'<style>{"".join(css)}</style>' + "".join(body) + "</svg>")
