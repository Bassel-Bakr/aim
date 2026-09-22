"""The issue renderer: one lane per fault, drawn from the four numbers that separate the faults.

Fourteen of the chart's nodes are faults in one motion, and the chart states each of them as a
sentence. A sentence cannot show a fault that only exists in time, so each one is drawn as the same
shot fired badly: a crosshair leaves the start, the arm brakes somewhere, the crosshair shakes or
does not, and the trigger goes. What separates the fourteen is only where the flick stops, when the
braking starts, how much the hand shakes and how early the trigger goes, which is exactly what
nodes.py carries, so one drawing serves all fourteen and none of them can drift from the table.

Three things stay honest across the set. The furthest the crosshair gets is a trail under the track,
so an excursion is still readable after the crosshair has left it. Where the shot went is a ring or
a crossed ring at the position the crosshair actually held at the trigger, shake included, rather
than at the position the arm was aiming for. The bar under each lane is real time, one scale for all
fourteen, split into the flick, the braking and the settle, so a fault that costs time shows up as a
wider bar rather than as an adjective.

Everything this module emits is namespaced Iss and carries the node's own key, since all 48 figures
render onto one page and keyframe names are global on it.
"""
import math
import random
import sys
from pathlib import Path
from typing import Any

# Neither the kit a folder up nor the node table beside this file is an installed package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_kit import crosshair, keyframes, lane_label, metadata, smooth, text  # noqa: E402
from nodes import Node  # noqa: E402

W = 600
H = 164                                 # one of 48 figures on a page, so the lane stays shallow
X0, TARGET = 80, 420                    # where every flick starts, and where the target sits
SPAN = float(TARGET - X0)
TRACK_X1 = 560                          # the track runs past the furthest excursion any node makes
BAR_X1 = 496                            # the clock, leaving room for its total to the right of it
WINDOW = 0.32                           # seconds of shot per full width of that clock
TRACK_Y, BAR_Y = 82, 112
FRAMES = 42                             # enough to carry a shake; more would only cost page weight
LOOP = 3.4                              # one loop: the slowest shot, then a pause on the outcome
SCALE = 9.0                             # real flicks are a blur, so the clock is stretched once
HIT = 8.5                               # how near the target's centre a shot still counts, in px
SHAKE = 30.0                            # pixels of crosshair travel at jitter 1.0

# brake -> the drive's seconds, the share of the flick it covers, and the braking seconds. Late
# braking means a long fast drive and a short violent stop; early braking spends most of the shot
# decelerating; no braking means the drive covers the whole flick and ends dead.
PHASES: dict[str, tuple[float, float, float]] = {
    "late": (0.070, 0.86, 0.032),
    "early": (0.058, 0.44, 0.205),
    "none": (0.104, 1.00, 0.000),
}
NOTES: dict[str, str] = {
    "late": "brakes late",
    "early": "brakes far too early",
    "none": "does not slow at all",
}


def drive(u: float) -> float:
    """The flick's own profile: accelerate, then hold the speed. Nothing here decelerates, because
    deceleration is the phase after it and the whole set turns on when that phase starts."""
    a = 0.35
    u = max(0.0, min(1.0, u))
    return ((u * u) / (2 * a) if u < a else a / 2 + (u - a)) / (1 - a / 2)


def ease_out(u: float) -> float:
    """Braking: full speed at the start, stopped at the end."""
    u = max(0.0, min(1.0, u))
    return u * (2 - u)


def base(t: float, dt: float, share: float, bt: float, st: float, peak: float, rest: float) -> float:
    """How much of the start-to-target span is covered at t seconds of shot, shake aside."""
    if t <= 0:
        return 0.0
    if t < dt:
        return peak * share * drive(t / dt)
    if bt > 0 and t < dt + bt:
        return peak * (share + (1 - share) * ease_out((t - dt) / bt))
    if st > 0 and t < dt + bt + st:
        return peak + (rest - peak) * smooth((t - dt - bt) / st)
    return rest


def envelope(t: float, start: float, stop: float) -> float:
    """How much of the shake is running at t: it builds as the crosshair nears the target, holds
    through the trigger, and dies away after it. A hand does not start or stop shaking on a frame."""
    if t < start:
        return 0.0
    if t < start + 0.022:
        return (t - start) / 0.022
    if t <= stop:
        return 1.0
    if t < stop + 0.045:
        return 1.0 - (t - stop) / 0.045
    return 0.0


def bar_label(label: str, x: float, y: float, width: float, cls: str) -> str:
    """A block's name inside it, at the largest size that leaves room, or nothing. Text running into
    a rounded edge reads as a mistake. Bold display glyphs run about 0.62em."""
    for size in (11, 10):
        if len(label) * size * 0.62 + 12 <= width:
            return text(x, y, label, cls, "middle", size, 700, middle=True)
    return ""


def shot_mark(x: float, y: float, tone: str, hit: bool) -> str:
    """Where the shot landed: a ring round it if it went in, a cross through it if it did not."""
    if hit:
        return (f'<circle cx="{x:.4g}" cy="{y:.4g}" r="14" class="fig-balanced-stroke" fill="none" '
                'stroke-width="2.6"/>')
    return (f'<path d="M{x - 8.5:.4g} {y - 8.5:.4g}l17 17M{x + 8.5:.4g} {y - 8.5:.4g}l-17 17" '
            f'class="fig-{tone}-stroke" stroke-width="2.8" fill="none" stroke-linecap="round"/>')


def narrate(node: Node, peak: float, brake: str, jitter: float, shot: float, hit: bool,
            total: float) -> str:
    """The lane in words, for a reader who cannot see it move."""
    if peak > 1.03:
        reach = f"carries {round((peak - 1) * 100)} per cent of the distance past the target"
    elif peak < 0.97:
        reach = f"stalls {round((1 - peak) * 100)} per cent short of the target and never arrives"
    else:
        reach = "reaches the target"
    braking = {
        "late": "Braking starts late, close to the target, so hauling the crosshair back is the "
                "longest part of the shot.",
        "early": "Braking starts far out, so the last stretch is a crawl.",
        "none": "There is no braking at all: the motion runs at speed and stops dead, with no "
                "correction after it.",
    }[brake]
    if jitter >= 0.4:
        shake = "The crosshair shakes badly as it arrives."
    elif jitter > 0:
        shake = "The crosshair shakes a little as it arrives."
    else:
        shake = "The crosshair is steady."
    trigger = (f"The trigger goes at {round(shot * 100)} per cent of the shot, before the crosshair "
               "has settled." if shot < 1 else "The trigger goes once the motion is done.")
    landed = ("the shot lands on the target" if hit else "the shot misses")
    return (f"{node.label}. The crosshair leaves the start and {reach}. {braking} {shake} {trigger} "
            f"A faint trail shows how far it got, and a ring or a crossed ring marks where the shot "
            f"went: {landed}. The bar underneath is real time on one scale, split into the flick, "
            f"the braking and the settle, and this shot takes {round(total * 1000)} milliseconds "
            "from the start to the trigger.")


def render(node: Node) -> str:
    """One fault, drawn as the shot that produces it."""
    params: dict[str, Any] = node.params
    peak = float(params["peak"])
    brake = str(params["brake"])
    jitter = float(params["jitter"])
    shot = float(params["shot"])
    slug = node.key.replace("sc-", "", 1).replace("-", "_")
    # Too much of anything is a tense fault and too little a loose one, which is the split the
    # chart's own two branches make. A flick that reaches the target but fires early is rushing,
    # so it sits with the tense faults rather than getting a colour of its own.
    tone = "tense" if peak >= 1.0 else "loose"

    dt, share, bt = PHASES[brake]
    corrects = brake != "none" and peak > 1.0
    # A bigger overshoot costs more to undo, so the settle is not a constant.
    st = 0.030 + (0.22 * (peak - 1.0) if corrects else 0.0)
    rest = 1.0 if corrects else peak
    total = dt + bt + st

    step = LOOP / SCALE / FRAMES
    fire_frame = max(1, min(FRAMES, round(total * shot / step)))
    fire_t = fire_frame * step
    shake_from = dt                     # the shake belongs to the approach, not to the whole flick
    shake_to = max(fire_t, shake_from + 0.10)
    amp = jitter * SHAKE
    rng = random.Random(node.key)
    # The drawing picks the instant the trigger catches the shake at its worst and swinging away
    # from the target, which is the instant worth drawing: a shaking hand that fires does miss, and
    # a figure that happened to catch it swinging back would say the opposite. Where the arm is on
    # the target anyway, either way is the same miss, so the key picks one.
    aimed = X0 + base(fire_t, dt, share, bt, st, peak, rest) * SPAN
    away = 1.0 if aimed > TARGET + 0.5 else -1.0 if aimed < TARGET - 0.5 else rng.choice((1.0, -1.0))
    freq = 2.6 / max(shake_to - shake_from, 0.05)
    phase = away * math.pi / 2 - math.tau * freq * (fire_t - shake_from)
    freq_y, phase_y = freq * 1.35, rng.uniform(0.0, math.tau)

    def offsets(t: float) -> tuple[float, float]:
        x = base(t, dt, share, bt, st, peak, rest) * SPAN
        if amp <= 0:
            return x, 0.0
        env = amp * envelope(t, shake_from, shake_to)
        return (x + env * math.sin(math.tau * freq * (t - shake_from) + phase),
                env * 0.5 * math.sin(math.tau * freq_y * (t - shake_from) + phase_y))

    frames = [offsets(i * step) for i in range(FRAMES + 1)]
    fire_dx, fire_dy = frames[fire_frame]
    shot_x, shot_y = X0 + fire_dx, TRACK_Y + fire_dy
    hit = math.hypot(shot_x - TARGET, fire_dy) <= HIT
    far_x = X0 + peak * SPAN

    css = [f".aim-iss-t-{slug},.aim-iss-m-{slug}{{animation-duration:"
           f"{LOOP}s;animation-timing-function:linear;animation-iteration-count:infinite}}",
           keyframes(f"aimIssTravel_{slug}", frames,
                     lambda p: (f"translate({p[0]:.4g}px,{p[1]:.4g}px)" if abs(p[1]) >= 0.05
                                else f"translate({p[0]:.4g}px,0)")),
           f"@keyframes aimIssFire_{slug}{{0%,{fire_frame / FRAMES * 100:.4g}%{{opacity:0}}"
           f"{fire_frame / FRAMES * 100 + 2:.4g}%,100%{{opacity:1}}}}"]

    name = node.label.split(",")[0]
    note = NOTES[brake]
    if 20 + len(name) * 16 * 0.62 + len(note) * 13 * 0.56 + 10 > 560:
        note = ""
    body = [f'<rect x="8" y="6" width="{W - 16}" height="{H - 12}" rx="12" class="fig-panel"/>',
            lane_label(20, 28, name, note),
            f'<path d="M{X0 - 18} {TRACK_Y}H{TRACK_X1}" class="fig-grid-stroke" stroke-width="1" '
            'stroke-dasharray="2 6"/>',
            f'<path d="M{X0} {TRACK_Y - 14}v28" class="fig-grid-stroke" stroke-width="1.5"/>',
            f'<path d="M{X0} {TRACK_Y}H{far_x:.4g}" class="fig-{tone}-stroke" stroke-width="8" '
            'opacity="0.2" fill="none" stroke-linecap="round"/>',
            f'<circle cx="{TARGET}" cy="{TRACK_Y}" r="10" class="fig-target"/>']
    # The furthest point gets its own tick only where the crosshair later left it, which is the
    # corrected overshoot. Elsewhere the end of the trail already stands there.
    if peak - rest > 0.03:
        body.append(f'<path d="M{far_x:.4g} {TRACK_Y - 13}v26" class="fig-{tone}-stroke" '
                    'stroke-width="2" stroke-dasharray="4 3" opacity="0.75"/>')
    verdict = "sails past" if peak > 1.03 else ("never gets there" if peak < 0.97 else "")
    if verdict:
        body.append(text(far_x, TRACK_Y - 24, verdict, f"fig-{tone}-fill", "middle", 12, 700))
    body.append(f'<g class="aim-iss-m-{slug}" style="animation-name:aimIssFire_{slug};opacity:0">'
                f'{shot_mark(shot_x, shot_y, tone, hit)}</g>')
    body.append(f'<g class="aim-iss-t-{slug}" style="animation-name:aimIssTravel_{slug}">'
                f'{crosshair(f"fig-{tone}-stroke", X0, TRACK_Y)}</g>')

    # The clock: the same seconds-per-pixel under all fourteen lanes, so the wide bars are the
    # faults that cost time and the narrow ones are the faults that cost accuracy instead.
    per_second = (BAR_X1 - X0) / WINDOW
    cursor = float(X0)
    for width, label, fill, opacity, label_cls in (
            (dt * per_second, "Flick", "fig-ink-fill", 0.7, "fig-surface"),
            (bt * per_second, "Brake", f"fig-{tone}-fill", 1.0, "fig-surface"),
            (st * per_second, "Settle", f"fig-{tone}-fill", 0.45, "fig-ink")):
        if width <= 1:
            continue
        body.append(f'<rect x="{cursor:.4g}" y="{BAR_Y}" width="{width - 2:.4g}" height="14" rx="6" '
                    f'class="{fill}" opacity="{opacity}"/>')
        body.append(bar_label(label, cursor + width / 2 - 1, BAR_Y + 7, width, label_cls))
        cursor += width
    if shot < 1:
        body.append(f'<path d="M{X0 + fire_t * per_second:.4g} {BAR_Y - 5}v24" '
                    'class="fig-ink-stroke" stroke-width="2"/>')
    body.append(text(cursor + 9, BAR_Y + 11, f"{round(total * 1000)} ms", f"fig-{tone}-fill",
                     "start", 12, 600))

    caption = ("shakes badly as it arrives" if jitter >= 0.4 else
               "shakes as it arrives" if jitter > 0 else "steady as it arrives")
    outcome = ("shot lands" if hit else "shot misses long" if shot_x > TARGET else
               "shot misses short")
    if shot < 1:
        outcome = f"trigger at {round(shot * 100)}%, {outcome}"
    body.append(text(20, 148, caption, "fig-muted fig-caption", "start", 12, 600))
    body.append(text(W - 20, 148, outcome, "fig-muted fig-caption", "end", 12, 600))

    # Held at the furthest point of the flick, where the fault is widest apart from a shot that
    # lands, with the shot mark shown so the outcome is readable in that one frame.
    css.append(f"@media (prefers-reduced-motion:reduce){{.aim-iss-t-{slug}"
               f"{{animation-play-state:paused;"
               f"animation-delay:-{(dt + bt) * SCALE:.3g}s!important}}"
               f".aim-iss-m-{slug}{{animation:none!important;opacity:1!important}}}}")
    return (f'<svg viewBox="0 0 {W} {H}" class="fig-fit" role="img" '
            f'aria-labelledby="fig-{node.key}-title">'
            f'<title id="fig-{node.key}-title">'
            f'{narrate(node, peak, brake, jitter, shot, hit, total)}</title>' + metadata() +
            f'<style>{"".join(css)}</style>' + "".join(body) + "</svg>")
