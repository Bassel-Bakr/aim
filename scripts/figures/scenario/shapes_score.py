"""Shapes for the Edit Scenario window.

None of the profile shapes fit here. A scenario field is a rule or a number: what a run is worth,
when it stops, what the reader is shown while it runs, and whether anyone can find it afterwards.
A bot sliding along a track says none of that, so these draw a score, a clock, a search result.

The panel behind each cell runs from y 34 to y 136, so nothing may stray past cy - 42 or cy + 60.
"""
import math

from figure_kit import crosshair, keyframes, smooth, text

T = 4.0
FRAMES = 48
KINDS = ("worldscale", "timescale", "clockadd", "adaptmode", "fovclamp", "healthbar",
         "hitmarker", "hitsound", "predictor", "wintarget", "overdamage", "movescore",
         "findable", "difficulty", "thumbnail", "flick", "unpack",
         "paydamage", "payhit", "paykill", "paydirect", "paymidair", "paytime",
         "penaltydamage", "penaltydeath",
         "multaccuracy", "multsqrt", "multdamage", "multkill")

# Each payout draws the event it pays for, so five score fields do not share one picture.
EVENTS = {
    "paydamage": ("damage landed", 2, 14),
    "payhit": ("a hit", 1, 12),
    "paykill": ("a kill", 25, 150),
    "paydirect": ("a direct hit", 5, 40),
    "paymidair": ("a midair direct", 10, 90),
    "paytime": ("a second left", 1, 20),
}
LOSSES = {"penaltydamage": ("damage taken", 2, 20), "penaltydeath": ("a death", 10, 100)}
FACTORS = {
    "multaccuracy": ("accuracy", 0.62),
    "multsqrt": ("root accuracy", 0.79),
    "multdamage": ("damage efficiency", 0.58),
    "multkill": ("kill efficiency", 0.7),
}


def _float(uid: str, side: int, letter: str, up: float) -> list[str]:
    """A number drifting up or down off the thing it came from, then fading."""
    cls = f"aim-{uid}-{side}{letter}"
    return [f"@keyframes aim{uid}{letter}{side}{{0%{{opacity:0;transform:translate(0,0)}}"
            "18%{opacity:0}"
            f"24%{{opacity:1;transform:translate(0,0)}}"
            f"86%{{opacity:1;transform:translate(0,{up:.0f}px)}}"
            f"96%{{opacity:0;transform:translate(0,{up:.0f}px)}}"
            f"100%{{opacity:0;transform:translate(0,{up:.0f}px)}}}}",
            f".{cls}{{animation-name:aim{uid}{letter}{side};animation-duration:{T}s;"
            "animation-timing-function:linear;animation-iteration-count:infinite}"]


def _target(mid: float, cy: float, radius: float = 14.0) -> str:
    return f'<circle cx="{mid}" cy="{cy}" r="{radius}" class="fig-target"/>'


def draw(kind: str, index: int, uid: str, side: int, strong: bool,
         mid: float, cy: float) -> tuple[list[str], list[str]]:
    body: list[str] = []
    css: list[str] = []
    cls = f"aim-{uid}-{side}"

    if kind in EVENTS:
        # What the event is worth. The number is the point, so it is what moves.
        what, low, high = EVENTS[kind]
        pays = high if strong else low
        if kind == "paymidair":
            body.append(f'<path d="M{mid - 70} {cy + 26}H{mid + 70}" class="fig-grid-stroke" '
                        'stroke-width="2"/>')
            body.append(_target(mid - 28, cy - 14))
        elif kind == "paytime":
            body.append(f'<rect x="{mid - 62}" y="{cy - 8}" width="60" height="16" rx="5" '
                        'class="fig-grid-fill" opacity="0.5"/>')
            body.append(f'<rect x="{mid - 62}" y="{cy - 8}" width="24" height="16" rx="5" '
                        'class="fig-cool-fill"/>')
        elif kind == "paykill":
            body.append(f'<path d="M{mid - 38} {cy - 14}l20 20M{mid - 18} {cy - 14}l-20 20" '
                        'class="fig-muted-stroke" stroke-width="3" stroke-linecap="round"/>')
        else:
            body.append(_target(mid - 28, cy - 4))
        body.append(text(mid + 34, cy - 2, f"+{pays}", f"fig-accent-text {cls}a",
                         size=15, weight=700))
        css += _float(uid, side, "a", -18)
        body.append(text(mid, cy + 44, f"{what} pays {pays}", "fig-muted", size=10, weight=600))

    elif kind in LOSSES:
        what, low, high = LOSSES[kind]
        costs = high if strong else low
        if kind == "penaltydeath":
            body.append(f'<path d="M{mid - 38} {cy - 14}l20 20M{mid - 18} {cy - 14}l-20 20" '
                        'class="fig-muted-stroke" stroke-width="3" stroke-linecap="round"/>')
        else:
            body.append(crosshair("fig-ink-stroke", mid - 28, cy - 4))
        body.append(text(mid + 34, cy - 2, f"-{costs}", f"fig-tense-fill {cls}a",
                         size=15, weight=700))
        css += _float(uid, side, "a", 18)
        body.append(text(mid, cy + 44, f"{what} costs {costs}", "fig-muted",
                         size=10, weight=600))

    elif kind in FACTORS:
        # The subtotal the rest of the tab produced, and what this multiplier leaves of it.
        what, factor = FACTORS[kind]
        applied = factor if strong else 1.0
        body.append(f'<rect x="{mid - 74}" y="{cy - 20}" width="148" height="20" rx="5" '
                    'class="fig-grid-fill" opacity="0.45"/>')
        body.append(text(mid, cy - 6, "subtotal", "fig-muted", size=10, weight=600))
        body.append(f'<rect x="{mid - 74}" y="{cy + 6}" width="148" height="20" rx="5" '
                    f'class="fig-accent-fill {cls}" style="transform-box:fill-box;'
                    'transform-origin:left center"/>')
        css.append(f"@keyframes aim{uid}a{side}{{0%{{transform:scaleX(1)}}"
                   f"30%{{transform:scaleX({applied:.2f})}}"
                   f"100%{{transform:scaleX({applied:.2f})}}}}")
        css.append(f".{cls}{{animation-name:aim{uid}a{side};animation-duration:{T}s;"
                   "animation-iteration-count:infinite}")
        body.append(text(mid, cy + 46, "unchanged" if not strong
                         else f"{what} takes a cut", "fig-muted", size=10, weight=600))

    elif kind == "wintarget":
        goal = 0.45 if not strong else 0.88
        body.append(f'<rect x="{mid - 74}" y="{cy - 10}" width="148" height="22" rx="5" '
                    'class="fig-grid-fill" opacity="0.45"/>')
        body.append(f'<rect x="{mid - 74}" y="{cy - 10}" width="148" height="22" rx="5" '
                    f'class="fig-accent-fill {cls}" style="transform-box:fill-box;'
                    'transform-origin:left center"/>')
        css.append(keyframes(f"aim{uid}a{side}", [i / FRAMES for i in range(FRAMES + 1)],
                             lambda v: f"scaleX({max(0.02, v):.3f})"))
        css.append(f".{cls}{{animation-name:aim{uid}a{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")
        gx = mid - 74 + 148 * goal
        body.append(f'<path d="M{gx:.1f} {cy - 20}V{cy + 22}" class="fig-tense-stroke" '
                    'stroke-width="2.6"/>')
        body.append(text(mid, cy + 42, "reached early" if not strong else "a long way up",
                         "fig-muted", size=10, weight=600))

    elif kind == "overdamage":
        # A target with more damage on it than it needed. The question is whether the surplus is
        # paid for or thrown away.
        body.append(f'<rect x="{mid - 74}" y="{cy - 12}" width="100" height="22" rx="5" '
                    'class="fig-grid-fill" opacity="0.45"/>')
        body.append(text(mid - 24, cy + 3, "health", "fig-muted", size=10, weight=600))
        surplus = "fig-accent-fill" if strong else "fig-grid-fill"
        body.append(f'<rect x="{mid + 30}" y="{cy - 12}" width="44" height="22" rx="5" '
                    f'class="{surplus}" opacity="{0.9 if strong else 0.35}"/>')
        if not strong:
            body.append(f'<path d="M{mid + 32} {cy + 8}L{mid + 72} {cy - 10}" '
                        'class="fig-muted-stroke" stroke-width="2"/>')
        body.append(text(mid + 52, cy - 22, "surplus", "fig-muted", size=9, weight=600))
        body.append(text(mid, cy + 40, "the surplus pays" if strong else "the surplus is wasted",
                         "fig-muted", size=10, weight=600))

    elif kind == "movescore":
        body.append(f'<path d="M{mid - 74} {cy + 12}H{mid + 74}" class="fig-grid-stroke" '
                    'stroke-width="2"/>')
        body.append(f'<g class="{cls}">{crosshair("fig-ink-stroke", mid - 74, cy + 12)}</g>')
        css.append(keyframes(f"aim{uid}a{side}",
                             [(148 * i / FRAMES, 0.0) for i in range(FRAMES + 1)],
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".{cls}{{animation-name:aim{uid}a{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")
        if strong:
            for tick in range(4):
                tx = mid - 52 + tick * 36
                body.append(text(tx, cy - 16, "+1", "fig-accent-text", size=11, weight=700))
        body.append(text(mid, cy + 40, "distance pays" if strong else "moving pays nothing",
                         "fig-muted", size=10, weight=600))

    elif kind == "worldscale":
        # The same character in two sizes of room, which is what scaling the map does to the
        # distances you have to cover.
        room = 40.0 if not strong else 74.0
        body.append(f'<rect x="{mid - room}" y="{cy - room * 0.5}" width="{room * 2}" '
                    f'height="{room}" rx="6" class="fig-grid-stroke" stroke-width="2" '
                    'fill="none"/>')
        body.append(_target(mid, cy, 11))
        body.append(text(mid, cy + 46, "a small room" if not strong else "a large one",
                         "fig-muted", size=10, weight=600))

    elif kind in ("timescale", "clockadd"):
        # A clock, filled rather than marked with a line: at the reduced-motion freeze two bare
        # playheads a few pixels apart said nothing, and two fills of different length do.
        body.append(f'<rect x="{mid - 74}" y="{cy - 12}" width="148" height="24" rx="5" '
                    'class="fig-grid-fill" opacity="0.45"/>')
        if kind == "timescale":
            cycles = 1 if not strong else 2
            levels = [(i / FRAMES * cycles) % 1.0 for i in range(FRAMES + 1)]
            note = "the clock runs fast" if strong else "the clock runs normally"
            mark = "elapsed"
        else:
            # A countdown a kill puts time back into. The kill lands early, so the two cells have
            # already parted by the time the strip is frozen.
            levels = []
            for i in range(FRAMES + 1):
                u = i / FRAMES
                left = 1.0 - u
                if strong and u > 0.2:
                    left = min(1.0, left + 0.24)
                levels.append(left)
            note = "a kill buys time back" if strong else "the clock only falls"
            mark = "left"
        body.append(f'<rect x="{mid - 74}" y="{cy - 12}" width="148" height="24" rx="5" '
                    f'class="fig-cool-fill {cls}" style="transform-box:fill-box;'
                    'transform-origin:left center"/>')
        css.append(keyframes(f"aim{uid}a{side}", levels,
                             lambda v: f"scaleX({max(0.02, v):.3f})"))
        css.append(f".{cls}{{animation-name:aim{uid}a{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")
        body.append(text(mid, cy + 26, mark, "fig-muted", size=9, weight=600))
        body.append(text(mid, cy + 46, note, "fig-muted", size=10, weight=600))

    elif kind == "adaptmode":
        # Six runs against the bar they are being judged by. A fixed bar makes a rise mean
        # something; a bar that rises with you does not.
        runs = (0.35, 0.44, 0.4, 0.55, 0.62, 0.7)
        base = cy + 26
        for order, run in enumerate(runs):
            bx = mid - 72 + order * 25
            body.append(f'<rect x="{bx}" y="{base - 52 * run:.1f}" width="14" '
                        f'height="{52 * run:.1f}" rx="2" class="fig-cool-fill"/>')
        if strong:
            pts = " ".join(f"{mid - 72 + order * 25 + 7},{base - 52 * run - 8:.1f}"
                           for order, run in enumerate(runs))
        else:
            pts = f"{mid - 72},{base - 34} {mid + 72},{base - 34}"
        body.append(f'<polyline points="{pts}" class="fig-tense-stroke" stroke-width="2.4" '
                    'fill="none"/>')
        body.append(text(mid, cy + 48, "the bar rises too" if strong else "a fixed bar",
                         "fig-muted", size=10, weight=600))

    elif kind == "fovclamp":
        # The same target at two fields of view. Clamped, the two readers see the same drill.
        for lane, (dx, spread, radius) in enumerate(((-42, 26, 15), (42, 40, 9))):
            shown = radius if not strong else 13
            body.append(f'<path d="M{mid + dx} {cy + 30}L{mid + dx - spread} {cy - 24}'
                        f'L{mid + dx + spread} {cy - 24}Z" class="fig-grid-stroke" '
                        'stroke-width="1.6" stroke-dasharray="4 4" fill="none" opacity="0.7"/>')
            body.append(f'<circle cx="{mid + dx}" cy="{cy - 6}" r="{shown}" '
                        'class="fig-target"/>')
        body.append(text(mid, cy + 48, "the same size for both" if strong
                         else "a different drill each", "fig-muted", size=10, weight=600))

    elif kind in ("healthbar", "hitmarker", "hitsound", "predictor"):
        # Four different pieces of feedback, so four different pictures. Disabling one is not the
        # same as disabling another.
        if kind == "predictor":
            body.append(_target(mid - 20, cy - 4))
            if not strong:
                body.append(f'<circle cx="{mid + 34}" cy="{cy - 4}" r="13" '
                            'class="fig-cool-stroke" stroke-width="2" stroke-dasharray="4 4" '
                            'fill="none"/>')
                body.append(text(mid + 34, cy + 22, "lead", "fig-muted", size=9, weight=600))
            note = "no lead shown" if strong else "the lead is drawn"
        elif kind == "healthbar":
            body.append(_target(mid, cy + 2))
            if not strong:
                body.append(f'<rect x="{mid - 26}" y="{cy - 26}" width="52" height="8" rx="3" '
                            'class="fig-grid-fill"/>')
                body.append(f'<rect x="{mid - 26}" y="{cy - 26}" width="32" height="8" rx="3" '
                            'class="fig-accent-fill"/>')
            note = "no bar" if strong else "health is shown"
        elif kind == "hitmarker":
            body.append(_target(mid, cy))
            if not strong:
                body.append(f'<path d="M{mid - 20} {cy - 20}l10 10M{mid + 20} {cy - 20}l-10 10'
                            f'M{mid - 20} {cy + 20}l10 -10M{mid + 20} {cy + 20}l-10 -10" '
                            f'class="fig-tense-stroke {cls}" stroke-width="3" '
                            'stroke-linecap="round"/>')
                css.append(f"@keyframes aim{uid}a{side}{{0%{{opacity:0}}22%{{opacity:0}}"
                           "28%{opacity:1}70%{opacity:1}80%{opacity:0}100%{opacity:0}}")
                css.append(f".{cls}{{animation-name:aim{uid}a{side};animation-duration:{T}s;"
                           "animation-iteration-count:infinite}")
            note = "nothing marks the hit" if strong else "the hit is marked"
        else:
            body.append(_target(mid - 24, cy))
            if not strong:
                for ring in range(3):
                    body.append(f'<path d="M{mid + 6 + ring * 12} {cy - 12 - ring * 4}'
                                f'a{10 + ring * 6} {10 + ring * 6} 0 0 1 0 '
                                f'{24 + ring * 8}" class="fig-cool-stroke" stroke-width="2" '
                                'fill="none"/>')
            note = "silent" if strong else "the hit is heard"
        body.append(text(mid, cy + 44, note, "fig-muted", size=10, weight=600))

    elif kind == "findable":
        # A search result list, with this scenario in it or not.
        for row in range(3):
            ry = cy - 24 + row * 20
            mine = row == 1
            fill = "fig-accent-fill" if mine and strong else "fig-grid-fill"
            width = 132 if not (mine and not strong) else 0
            if width:
                body.append(f'<rect x="{mid - 66}" y="{ry}" width="{width}" height="14" rx="4" '
                            f'class="{fill}" opacity="{0.95 if mine and strong else 0.5}"/>')
        body.append(text(mid, cy + 44, "it turns up in search" if strong
                         else "nobody finds it", "fig-muted", size=10, weight=600))

    elif kind == "difficulty":
        filled = 2 if not strong else 5
        for pip in range(5):
            px = mid - 56 + pip * 28
            cls_pip = "fig-accent-fill" if pip < filled else "fig-grid-fill"
            body.append(f'<rect x="{px - 9}" y="{cy - 12}" width="18" height="24" rx="4" '
                        f'class="{cls_pip}" opacity="{1 if pip < filled else 0.45}"/>')
        body.append(text(mid, cy + 40, f"rated {filled} of 5", "fig-muted", size=10, weight=600))

    elif kind == "thumbnail":
        body.append(f'<rect x="{mid - 54}" y="{cy - 26}" width="108" height="56" rx="6" '
                    'class="fig-grid-fill" opacity="0.5"/>')
        if strong:
            body.append(f'<path d="M{mid - 44} {cy + 22}L{mid - 8} {cy - 12}L{mid + 14} '
                        f'{cy + 10}L{mid + 30} {cy - 4}L{mid + 44} {cy + 22}Z" '
                        'class="fig-cool-fill"/>')
            body.append(f'<circle cx="{mid + 28}" cy="{cy - 14}" r="6" '
                        'class="fig-accent-fill"/>')
        body.append(text(mid, cy + 48, "a picture" if strong else "an empty tile",
                         "fig-muted", size=10, weight=600))

    elif kind == "flick":
        body.append(_target(mid + 48, cy - 8, 13))
        frames = []
        for i in range(FRAMES + 1):
            u = i / FRAMES
            if strong:
                # One jump, then a hold: a flick is a single correction, not a follow. It has to
                # have landed by the freeze at 30%, or both cells show a crosshair in transit.
                moved = smooth(min(1.0, max(0.0, (u - 0.10) * 8)))
            else:
                moved = smooth(min(1.0, u * 0.9))
            frames.append((-48 + 96 * moved, 8 - 16 * moved))
        body.append(f'<g class="{cls}">{crosshair("fig-ink-stroke", mid, cy)}</g>')
        css.append(keyframes(f"aim{uid}a{side}", frames,
                             lambda p: f"translate({p[0]:.1f}px,{p[1]:.1f}px)"))
        css.append(f".{cls}{{animation-name:aim{uid}a{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")
        body.append(text(mid, cy + 44, "one snap" if strong else "a slide onto it",
                         "fig-muted", size=10, weight=600))

    else:
        # A packed scenario, and the profile files unpacking puts back on disk.
        body.append(f'<rect x="{mid - 70}" y="{cy - 20}" width="48" height="40" rx="5" '
                    'class="fig-grid-fill" opacity="0.6"/>')
        body.append(text(mid - 46, cy + 4, "pack", "fig-muted", size=9, weight=600))
        if strong:
            for order in range(3):
                fx = mid + 6 + order * 26
                body.append(f'<rect x="{fx - 9}" y="{cy - 16 + order * 2}" width="18" '
                            'height="26" rx="3" class="fig-cool-fill"/>')
            body.append(f'<path d="M{mid - 18} {cy}H{mid - 6}" class="fig-accent-stroke" '
                        'stroke-width="2.4"/>')
        body.append(text(mid, cy + 40, "profiles written out" if strong else "it stays packed",
                         "fig-muted", size=10, weight=600))

    return body, css
