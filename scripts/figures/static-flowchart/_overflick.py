"""The overflick figure: one target, three arms, and the two ways of missing it that the chart
treats as one.

The chart this page is about routes an overflick to two causes, too much tension and too little, and
that split is the part worth keeping. What it gets wrong is the second branch. A relaxed arm does not
sail past the target; the page the wiki cites has it lagging behind one, so the loose lane here
decelerates far too early and is still short when the shot goes. Drawing it overshooting would draw
the opposite of what the article argues.

Everything the module emits is namespaced Ovr, since five figures share one rendered page and
keyframe names are global on it.
"""
import sys
from pathlib import Path

# The kit sits a folder up, beside the other pages' figure code, and is not an installed package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from figure_kit import crosshair, keyframes, lane_label, metadata, smooth, text  # noqa: E402

W = 600
OVR_LANE_H = 140
OVR_TOP = 8
OVR_X0, OVR_TARGET = 84, 440            # where every flick starts, and where the target sits
OVR_TRACK_X1 = 540                      # the track runs past the furthest excursion
OVR_BAR_X1 = 512                        # the clock under each lane, leaving room for its total
OVR_WINDOW = 0.36                       # seconds of shot per full width of that clock
OVR_FRAMES = 160
# Real flicks are over in a few hundred milliseconds, which is a blur. The clock is stretched by a
# fixed factor, so the three lanes keep their true ratios and stay followable.
OVR_SCALE = 9.0
OVR_T = 4.2                             # one loop: the slowest shot, then a pause on the outcome
OVR_HIT = 0.02                          # how close to the target still counts, as a share of the span
# The frame the whole argument lives in: the tense arm is at the far end of its overshoot while the
# loose arm has barely left the start. Readers who ask for less motion are held here.
OVR_PAUSE = 0.078

# name, note, tone, flick seconds, where the flick leaves the crosshair, correction seconds, where it
# is when the trigger goes, and the word for what happened, as a share of the start-to-target span.
OVR_LANES: list[tuple[str, str, str, float, float, float, float, str]] = [
    ("Too much tension", "brakes late, then hauls it back", "tense",
     0.075, 1.24, 0.185, 1.10, "sails past"),
    ("Too little tension", "slows far too early, drags in short", "loose",
     0.185, 0.78, 0.150, 0.88, "never gets there"),
    ("Balanced", "one motion, lands and stops", "balanced",
     0.135, 1.02, 0.048, 1.00, ""),
]


def travel(flick: float, peak: float, corr: float, end: float, t: float) -> float:
    """How much of the start-to-target span is covered at t seconds of shot.

    Two phases, each eased at both ends: the flick out to wherever the arm's braking leaves it, then
    the correction towards the target. An arm that is still correcting when the trigger goes stops at
    `end` rather than on the target, which is what both failing lanes do.
    """
    if t <= 0:
        return 0.0
    if t < flick:
        return peak * smooth(t / flick)
    if t < flick + corr:
        return peak + (end - peak) * smooth((t - flick) / corr)
    return end


def lane_offsets(flick: float, peak: float, corr: float, end: float, span: float) -> list[float]:
    """The crosshair's offset from the start, one value per frame of the loop."""
    return [travel(flick, peak, corr, end, frame / OVR_FRAMES * OVR_T / OVR_SCALE) * span
            for frame in range(OVR_FRAMES + 1)]


def mark_keyframes(name: str, at: float) -> str:
    """A shot mark appearing at `at` percent of the loop and staying put for the rest of it.

    It is revealed rather than moved: the lane already has one moving thing in it, and the reader is
    meant to be able to compare the three outcomes at the end of the loop without chasing anything.
    """
    return (f"@keyframes {name}{{0%{{opacity:0;transform:scale(0.35)}}"
            f"{at:.3g}%{{opacity:0;transform:scale(0.35)}}"
            f"{at + 2.2:.3g}%{{opacity:1;transform:scale(1.3)}}"
            f"{at + 5:.3g}%{{opacity:1;transform:scale(1)}}"
            "100%{opacity:1;transform:scale(1)}}")


def inside(label: str, x: float, y: float, width: float) -> str:
    """A label inside a bar, at the largest size that leaves room to spare, or nothing at all. Text
    running into a rounded edge reads as a mistake. Bold display glyphs run about 0.62em."""
    for size in (12, 11, 10):
        if len(label) * size * 0.62 + 14 <= width:
            return text(x, y, label, "fig-surface", "middle", size, 700, middle=True)
    return ""


def shot_mark(x: float, y: float, tone: str, hit: bool) -> str:
    """Where the shot landed: a ring round it if it went in, a cross through it if it did not.

    Both sit where the crosshair comes to rest, so the ring is drawn wide enough to clear it and the
    cross wide enough to strike right through it.
    """
    if hit:
        return (f'<circle cx="{x:.1f}" cy="{y}" r="15" class="fig-{tone}-stroke" fill="none" '
                'stroke-width="2.8"/>')
    return (f'<path d="M{x - 9.2:.1f} {y - 9.2}l18.4 18.4M{x + 9.2:.1f} {y - 9.2}l-18.4 18.4" '
            f'class="fig-{tone}-stroke" stroke-width="3" fill="none" stroke-linecap="round"/>')


def overflick() -> str:
    """Three arms, one target: a tense overshoot, a loose lag, and a flick that lands."""
    height = OVR_TOP + OVR_LANE_H * len(OVR_LANES) + 30
    span = float(OVR_TARGET - OVR_X0)
    per_second = (OVR_BAR_X1 - OVR_X0) / OVR_WINDOW
    css = [f".aim-ovr-anim,.aim-ovr-mark{{animation-duration:{OVR_T}s;"
           "animation-timing-function:linear;animation-iteration-count:infinite}"]
    body: list[str] = []
    for index, (name, note, tone, flick, peak, corr, end, verdict) in enumerate(OVR_LANES):
        top = OVR_TOP + OVR_LANE_H * index
        y = top + 76
        bar_y = top + 104
        fire = flick + corr
        hit = abs(end - 1.0) <= OVR_HIT
        # The furthest the crosshair ever gets. For the tense arm that is past the target, for the
        # loose one it is short of it, and the trail keeps both visible once the crosshair has moved.
        far = max(peak, end)
        far_x = OVR_X0 + far * span
        shot_x = OVR_X0 + end * span
        css.append(keyframes(f"aimOvrLane{index}",
                             lane_offsets(flick, peak, corr, end, span),
                             lambda dx: f"translate({dx:.1f}px,0)"))
        css.append(mark_keyframes(f"aimOvrMark{index}", fire * OVR_SCALE / OVR_T * 100))
        body.append(f'<rect x="8" y="{top}" width="{W - 16}" height="{OVR_LANE_H - 10}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(24, top + 26, name, note))
        body.append(f'<path d="M{OVR_X0 - 18} {y}H{OVR_TRACK_X1}" class="fig-grid-stroke" '
                    'stroke-width="1" stroke-dasharray="2 6"/>')
        body.append(f'<path d="M{OVR_X0} {y - 15}v30" class="fig-grid-stroke" stroke-width="1.5"/>')
        # The trail: everything this arm covered, laid down under the track so the excursion reads
        # even after the crosshair has come back off it.
        body.append(f'<path d="M{OVR_X0} {y}H{far_x:.1f}" class="fig-{tone}-stroke" stroke-width="8" '
                    'opacity="0.2" fill="none" stroke-linecap="round"/>')
        # The far point gets its own tick only where the shot did not go, which is the tense arm: on
        # the other two the shot mark already stands at the end of the trail.
        if far - end > 0.03:
            body.append(f'<path d="M{far_x:.1f} {y - 14}v28" class="fig-{tone}-stroke" '
                        'stroke-width="2" stroke-dasharray="4 3" opacity="0.75"/>')
        body.append(f'<circle cx="{OVR_TARGET}" cy="{y}" r="11" class="fig-target"/>')
        if verdict:
            body.append(text(far_x, y - 22, verdict, f"fig-{tone}-fill", "middle", 12, 700))
        body.append(f'<g class="aim-ovr-mark" style="animation-name:aimOvrMark{index};'
                    f'transform-origin:{shot_x:.1f}px {y}px;opacity:0">'
                    f'{shot_mark(shot_x, y, "balanced" if hit else tone, hit)}</g>')
        body.append(f'<g class="aim-ovr-anim" style="animation-name:aimOvrLane{index}">'
                    f'{crosshair(f"fig-{tone}-stroke", OVR_X0, y)}</g>')
        # The same clock under every lane: the flick, then what fixing it cost. The second block is
        # the one to read, since it is the only part the three arms spend differently on purpose.
        flick_w = flick * per_second
        corr_w = corr * per_second
        # Both blocks are dark enough to carry a label in the page background's own colour, which is
        # what the 7:1 a label is held to needs: a paler wash leaves the text at graphic contrast.
        body.append(f'<rect x="{OVR_X0}" y="{bar_y}" width="{flick_w - 2:.1f}" height="16" rx="7" '
                    'class="fig-ink-fill" opacity="0.7"/>')
        body.append(f'<rect x="{OVR_X0 + flick_w:.1f}" y="{bar_y}" width="{corr_w - 2:.1f}" '
                    f'height="16" rx="7" class="fig-{tone}-fill"/>')
        body.append(inside("Flick", OVR_X0 + flick_w / 2 - 1, bar_y + 8, flick_w))
        body.append(inside("Correction", OVR_X0 + flick_w + corr_w / 2 - 1, bar_y + 8, corr_w))
        body.append(text(OVR_X0 + (flick + corr) * per_second + 10, bar_y + 12,
                         f"{round(fire * 1000)} ms", f"fig-{tone}-fill", "start", 12, 600))
    body.append(text(OVR_X0, height - 12, "one flick, start to trigger", "fig-muted", "start", 13, 600))
    body.append(text(W - 24, height - 12, "same target, same distance", "fig-muted", "end", 13, 600))
    # Held at the top of the tense arm's overshoot, where the three lanes are furthest apart, with
    # every shot mark showing so the outcomes are readable in the one frame.
    css.append("@media (prefers-reduced-motion:reduce){.aim-ovr-anim{animation-play-state:paused;"
               f"animation-delay:-{OVR_PAUSE * OVR_SCALE:.2f}s!important}}"
               ".aim-ovr-mark{animation:none!important;opacity:1!important}}")
    return (f'<svg viewBox="0 0 {W} {height}" class="fig-fit" role="img" '
            'aria-labelledby="fig-overflick-title">'
            '<title id="fig-overflick-title">One target at one distance, flicked to three ways at '
            'once. The tense arm throws the crosshair out fastest and brakes too late: it sails well '
            'past the target, hauls back, and the shot goes while it is still long. The loose arm '
            'fails the other way round, slowing far too early and dragging the last stretch at a '
            'crawl, so the trigger goes with the crosshair still short of the target, which it never '
            'reaches at all. The balanced arm travels once, settles on the target and stops there. A '
            'faint trail behind each crosshair keeps the furthest point it got to visible after it '
            'has moved on, and a ring or a crossed ring marks where each shot landed. The bar under '
            'each lane splits the shot into flick time and correction time, so what the two failures '
            'cost shows up as the longer second block.</title>' + metadata() +
            f'<style>{"".join(css)}</style>' + "".join(body) + "</svg>")
