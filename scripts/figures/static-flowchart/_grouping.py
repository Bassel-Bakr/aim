"""The grouping figure for docs/articles/weakness-targeted-static-flowchart.md.

The page's last section says the thing worth watching is not the score. This figure is that sentence
run twice: two runs put the same nine shots on the same target on the same clock, and a ring around
the aim point resizes after every shot to follow how far the shots are sitting from the middle. One
ring never closes. The other does. The hit count, identical under both, is withheld until the very
end of the loop, so the reader has already seen the difference the number cannot carry.

The ring is the root-mean-square distance of the shots so far, which is a spread, not a containment
circle: outlying marks sit outside it on purpose, the same way they do on a trainer's grouping plot.
That is what lets it close as a run settles, instead of only ever growing.

Nothing here is measured. Nine shots and one hit count are the smallest schematic pair that makes
the comparison, and neither is a claim about any real scenario's scoring.
"""
import math
import random
import sys
from collections.abc import Sequence
from pathlib import Path

# The kit sits a folder up, beside the other pages' figure code, and is not an installed package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figure_kit import crosshair, keyframes, lane_label, metadata, smooth, text  # noqa: E402

GRP_W = 600
GRP_H = 326
GRP_T = 9.0                 # one loop, in seconds
GRP_PANEL_W = 282
GRP_CY = 148                # where both targets sit, so the eye compares at one height
GRP_TARGET_R = 70           # every shot lands inside this, or the runs would not share a hit count
GRP_FRAMES = 180            # samples of the ring's radius across the loop
# The loop, as fractions of it. The shots occupy the first half, the finished groupings hold through
# the third quarter, the count arrives last, and a blank beat at the end says a new run is starting.
GRP_SHOT_0 = 0.045
GRP_SHOT_GAP = 0.058
GRP_POP = 0.016             # how long a mark takes to appear
GRP_EASE = 0.035            # how long the ring takes to resize after a shot
GRP_SCORE_0 = 0.72
GRP_SCORE_1 = 0.76
GRP_CLEAR = 0.94
GRP_BLANK = 0.97

# Two runs, same count, same clock. What differs is only how far from the middle each shot lands:
# Run A scatters the whole way, Run B opens just as wide and then settles onto the aim point. The
# radii are written out rather than drawn from the seed, because the shape of each run is the
# argument; the seed only decides which way round the circle each shot falls.
GRP_RUNS: tuple[tuple[int, str, str, str, int, tuple[float, ...]], ...] = (
    (12, "a", "Run A", "the spread never settles", 17,
     (46.0, 58.0, 38.0, 62.0, 44.0, 55.0, 33.0, 60.0, 48.0)),
    (306, "b", "Run B", "the spread closes in", 53,
     (54.0, 47.0, 36.0, 24.0, 19.0, 14.0, 17.0, 12.0, 15.0)),
)
GRP_SHOTS = len(GRP_RUNS[0][5])
GRP_COUNT = f"{GRP_SHOTS} hits"


def shot_marks(seed: int, radii: Sequence[float]) -> list[tuple[float, float]]:
    """Where each shot lands, at the given distance from the aim point. The angle walks by roughly
    the golden angle with a seeded wobble, so consecutive shots never stack and a rebuild never
    reshuffles the figure."""
    rng = random.Random(seed)
    angle = rng.uniform(0.0, math.tau)
    out: list[tuple[float, float]] = []
    for radius in radii:
        angle += 2.39996 + rng.uniform(-0.45, 0.45)
        out.append((radius * math.cos(angle), radius * math.sin(angle)))
    return out


def spread_steps(radii: Sequence[float]) -> list[float]:
    """The ring's radius after each shot: the root-mean-square distance of the shots landed so far."""
    return [math.sqrt(sum(r * r for r in radii[:count]) / count)
            for count in range(1, len(radii) + 1)]


def ring_scale(steps: Sequence[float], frames: int) -> list[float]:
    """The ring's size across the loop, as a multiple of where it ends up.

    It holds between shots and eases between sizes, because a ring that snapped would read as a
    redraw rather than as a measurement being updated. Ending at one means the reduced-motion state
    needs no transform of its own: with the animation off, the circle is already its final size."""
    end = steps[-1]
    out: list[float] = []
    for frame in range(frames + 1):
        u = frame / frames
        value = steps[0]
        for index in range(1, len(steps)):
            start = GRP_SHOT_0 + index * GRP_SHOT_GAP
            if u >= start + GRP_EASE:
                value = steps[index]
            elif u > start:
                value = steps[index - 1] + (steps[index] - steps[index - 1]) * smooth(
                    (u - start) / GRP_EASE)
                break
            else:
                break
        out.append(value / end)
    return out


def mark_keyframes(order: int) -> str:
    """One mark's whole life. Every run's nth shot shares it, which is what puts both runs on the
    same clock and clears both panels at the same instant rather than in a stagger."""
    on = GRP_SHOT_0 + order * GRP_SHOT_GAP
    return (f"@keyframes aimGrpMark{order}{{0%{{opacity:0}}{on * 100:.4g}%{{opacity:0}}"
            f"{(on + GRP_POP) * 100:.4g}%{{opacity:1}}{GRP_CLEAR * 100:.4g}%{{opacity:1}}"
            f"{GRP_BLANK * 100:.4g}%{{opacity:0}}100%{{opacity:0}}}}")


def grouping() -> str:
    css = [mark_keyframes(order) for order in range(GRP_SHOTS)]
    # The ring waits for the first shot: before one has landed there is no spread to draw.
    css.append(f"@keyframes aimGrpRingFade{{0%{{opacity:0}}{GRP_SHOT_0 * 100:.4g}%{{opacity:0}}"
               f"{(GRP_SHOT_0 + GRP_POP) * 100:.4g}%{{opacity:1}}{GRP_CLEAR * 100:.4g}%{{opacity:1}}"
               f"{GRP_BLANK * 100:.4g}%{{opacity:0}}100%{{opacity:0}}}}")
    css.append(f"@keyframes aimGrpScore{{0%{{opacity:0}}{GRP_SCORE_0 * 100:.4g}%{{opacity:0}}"
               f"{GRP_SCORE_1 * 100:.4g}%{{opacity:1}}{GRP_CLEAR * 100:.4g}%{{opacity:1}}"
               f"{GRP_BLANK * 100:.4g}%{{opacity:0}}100%{{opacity:0}}}}")
    css.append(".aim-grp-mark,.aim-grp-score{opacity:0;animation-timing-function:linear;"
               f"animation-iteration-count:infinite;animation-duration:{GRP_T}s}}")
    css.append(".aim-grp-ring{opacity:0;animation-timing-function:linear;"
               f"animation-iteration-count:infinite;animation-duration:{GRP_T}s,{GRP_T}s}}")
    css.append(".aim-grp-score{animation-name:aimGrpScore}")
    for order in range(GRP_SHOTS):
        css.append(f".aim-grp-mark{order}{{animation-name:aimGrpMark{order}}}")
    body: list[str] = []
    for x, tag, name, note, seed, radii in GRP_RUNS:
        cx = x + GRP_PANEL_W / 2
        steps = spread_steps(radii)
        body.append(f'<rect x="{x}" y="40" width="{GRP_PANEL_W}" height="{GRP_H - 78}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 18, 28, name, note))
        # The target both runs shoot at, drawn the same size in both panels: every mark lands on it,
        # so the two runs really do share a hit count and differ only in spread.
        body.append(f'<circle cx="{cx}" cy="{GRP_CY}" r="{GRP_TARGET_R}" class="fig-target"/>')
        body.append(f'<circle cx="{cx}" cy="{GRP_CY}" r="{GRP_TARGET_R}" class="fig-grid-stroke" '
                    'stroke-width="2" fill="none"/>')
        # The aim point goes under the marks: shots that land on it have to cover it, not dodge it.
        body.append(crosshair("fig-muted-stroke", cx, GRP_CY))
        # Drawn at the size it ends the run at, then scaled to whatever the spread is so far. The
        # stroke is kept out of that scaling, or the ring would thin as it closed and read as fading.
        body.append(f'<circle cx="{cx}" cy="{GRP_CY}" r="{steps[-1]:.2f}" fill="none" '
                    'stroke-width="2.6" vector-effect="non-scaling-stroke" '
                    f'class="fig-accent-stroke aim-grp-ring aim-grp-ring-{tag}" '
                    f'style="transform-origin:{cx}px {GRP_CY}px"/>')
        for order, (dx, dy) in enumerate(shot_marks(seed, radii)):
            body.append(f'<circle cx="{cx + dx:.1f}" cy="{GRP_CY + dy:.1f}" r="4.6" '
                        f'class="fig-ink-fill aim-grp-mark aim-grp-mark{order}"/>')
        # The number arrives last and is the same under both, which is the whole argument.
        body.append(text(cx, 258, GRP_COUNT, "fig-accent-text aim-grp-score", size=18, weight=700))
        css.append(keyframes(f"aimGrpRing{tag.upper()}", ring_scale(steps, GRP_FRAMES),
                             lambda v: f"scale({v:.4f})"))
        css.append(f".aim-grp-ring-{tag}{{animation-name:aimGrpRingFade,aimGrpRing{tag.upper()}}}")
    body.append(text(GRP_W / 2, 312, "the same count, two runs that were nothing alike",
                     "fig-muted aim-grp-score", size=13, weight=500))
    # Readers who ask for less motion get both runs finished side by side, every shot on the target
    # and each ring at the size its run ended on, which is the comparison the figure exists to make.
    css.append("@media (prefers-reduced-motion:reduce){.aim-grp-mark,.aim-grp-ring,.aim-grp-score"
               "{opacity:1;animation:none!important}}")
    return (f'<svg viewBox="0 0 {GRP_W} {GRP_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-grouping-title"><title id="fig-grouping-title">Two panels, Run A '
            'and Run B, each putting the same nine shots on the same target on the same clock. The '
            'shots land one at a time, and a ring around the aim point resizes after every shot to '
            'follow how far from the middle the shots are sitting. In Run A the ring stays wide the '
            'whole way through, wobbling but never closing. In Run B the ring opens just as wide and '
            'then closes in as the later shots land near the aim point. Only once both runs have '
            'finished does the hit count appear under each of them, and it is the same number under '
            'both.</title>' + metadata() + f"<style>{''.join(css)}</style>" + "".join(body)
            + "</svg>")
