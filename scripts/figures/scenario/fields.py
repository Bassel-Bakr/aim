"""A figure per editor field.

The section needs one illustration for every option in every tab, which is several hundred. Writing
each one by hand is not the job: almost all of them are the same handful of shapes, differing only
in labels and in which direction the effect runs. This module holds the shapes, and each tab file
holds a one-line spec per field.

A card is deliberately small. Thirty of them sit on one page, so each gets a strip rather than a
panel: the field's name, what it does in the editor's own words, and a pair of states with the
difference animated between them.

Kinds, chosen by what the field actually varies:

    toggle   off against on, for a checkbox
    speed    slow against fast, for anything measured per second
    reach    short against long, for a distance or a height
    delay    immediate against delayed, for a time in seconds
    count    few against many, for an integer
    angle    narrow against wide, for degrees

Several fields are not horizontal at all, and drawing them on a left-to-right track says the wrong
thing. These have their own shapes:

    jump     an arc off a floor line, for jump height and jump count
    crouch   a body shrinking against its standing outline, for crouch height and rate
    fly      free vertical drift with no floor, for flight and jetpacks
    fall     descent rate against a floor, for gravity and terminal velocity
    air      steering sideways while falling, for air control
    bounce   an approach to a wall that either stops or rebounds
    crouchrate  the same duck at two speeds, for the animation rate
    land     a landing followed by a slowed crawl, for the landing penalty
    scatter  shots landing around a crosshair, for spread and its shape
    burst    rounds leaving per press, for bullets per click and burst fire
    climb    a crosshair rising off its resting line, for recoil
    zoom     a target growing as the view narrows, for aim down sights

Abstract motion is only honest where the field really is a magnitude along one axis. Everything
else draws the thing itself, and those shapes live in shapes.py.

A kind may carry an "-inv" suffix. By default the right-hand cell shows more of the effect, because
the right-hand cell is the higher value. Several fields run the other way: raising Let Off Friction
shortens the slide, and raising Walking Acceleration removes the delay. Those are marked inverted,
so the right-hand cell shows less, and the cell stops contradicting its own label.
"""
import math
import random
from collections.abc import Sequence

import shapes
import shapes_ai
import shapes_ammo
import shapes_life
import shapes_lock
import shapes_body
import shapes_aim
import shapes_hit
import shapes_more
import shapes_move
import shapes_score
import shapes_time
from figure_kit import crosshair, keyframes, metadata, smooth, text

W = 760
H = 160
T = 4.0
FRAMES = 36
# Each card is two demonstration cells side by side, with the field's name and note to their left.
LABEL_W = 268
CELL_W = 232
CELL_X = (LABEL_W, LABEL_W + CELL_W + 14)

# A field: its name, the editor's description, the kind of demonstration, and the two state labels.
# An optional sixth entry names what the thing being drawn actually is. The magnitude kinds used to
# draw a target for everything, which is wrong for a reload timer, a decal or a round of ammo.
Field = tuple[str, str, str, str, str] | tuple[str, str, str, str, str, str]

SHAPE_MODULES = (shapes, shapes_more, shapes_ai, shapes_hit, shapes_score,
                 shapes_aim, shapes_time, shapes_move, shapes_body,
                 shapes_ammo, shapes_lock, shapes_life)
GLYPHS = ("target", "round", "spark", "decal", "box", "bar", "mark")


def glyph(name: str, cx: float, cy: float) -> str:
    """The marker a magnitude kind slides, sized so any of them reads at strip scale."""
    if name == "round":
        return (f'<rect x="{cx - 3.5}" y="{cy - 8}" width="7" height="16" rx="3" '
                'class="fig-accent-fill"/>')
    if name == "spark":
        rays = "".join(f'M{cx} {cy}l{9 * math.cos(i * 1.0472):.1f} '
                       f'{9 * math.sin(i * 1.0472):.1f}' for i in range(6))
        return (f'<path d="{rays}" class="fig-accent-stroke" stroke-width="2.4" '
                'stroke-linecap="round"/>')
    if name == "decal":
        return (f'<circle cx="{cx}" cy="{cy}" r="9" class="fig-muted-stroke" stroke-width="2.4" '
                'fill="none"/>')
    if name == "box":
        return (f'<rect x="{cx - 9}" y="{cy - 9}" width="18" height="18" rx="3" '
                'class="fig-cool-fill"/>')
    if name == "bar":
        return (f'<rect x="{cx - 14}" y="{cy - 6}" width="28" height="12" rx="4" '
                'class="fig-accent-fill"/>')
    if name == "mark":
        return (f'<path d="M{cx - 7} {cy - 7}l14 14M{cx + 7} {cy - 7}l-14 14" '
                'class="fig-muted-stroke" stroke-width="2.6" stroke-linecap="round"/>')
    return f'<circle cx="{cx}" cy="{cy}" r="10" class="fig-target"/>'


def _cell(x: float) -> str:
    return (f'<rect x="{x}" y="34" width="{CELL_W}" height="{H - 58}" rx="8" '
            'class="fig-panel"/>')


def _track(x: float, y: float) -> str:
    return (f'<path d="M{x + 26} {y}H{x + CELL_W - 26}" class="fig-grid-stroke" '
            'stroke-width="2" stroke-dasharray="5 5" opacity="0.6"/>')


def _states(x: float, label: str) -> str:
    return text(x + CELL_W / 2, H - 8, label, "fig-muted", size=11, weight=600)


def card(index: int, field: Field, slug: str = "fld") -> tuple[str, list[str]]:
    """One field's strip: name and note on the left, two animated states on the right.

    `slug` has to be the sheet's own, because the class names and keyframe names below are
    global to the page. Several sheets sit on one page, so numbering from zero in each of them
    made every sheet overwrite the last one's rules.
    """
    name, note, kind, low, high = field[:5]
    mark = field[5] if len(field) > 5 else "target"
    invert = kind.endswith("-inv")
    kind = kind[:-4] if invert else kind
    uid = f"{slug}{index}"
    body = [text(12, 54, name, "fig-ink", anchor="start", size=14, weight=700)]
    # The note wraps by hand: there is no text flow in SVG, and these run to two lines.
    words, line, lines = note.split(), "", []
    for word in words:
        if len(line) + len(word) > 32:
            lines.append(line.strip())
            line = ""
        line += word + " "
    lines.append(line.strip())
    # Four lines: the editor's own wording runs long, and cutting it mid-sentence is
    # worse than a taller strip.
    for order, part in enumerate(lines[:4]):
        body.append(text(12, 72 + order * 16, part, "fig-muted", anchor="start", size=11,
                         weight=500))
    css: list[str] = []
    for side, (x, label) in enumerate(zip(CELL_X, (low, high))):
        body.append(_cell(x))
        body.append(_states(x, label))
        cy = 76
        # "strong" is the cell showing more of the effect, which is the right-hand one unless the
        # field runs backwards.
        strong = (side == 0) if invert else (side == 1)
        if kind == "toggle":
            body.append(_track(x, cy))
            if strong:
                frames = [(0.0, -26 * abs(math.sin(i / FRAMES * 3.14159)))
                          for i in range(FRAMES + 1)]
            else:
                frames = [(0.0, 0.0)] * (FRAMES + 1)
            opacity = ' opacity="0.45"' if not strong else ""
            body.append(f'<g class="aim-{uid}-{side}"{opacity}>'
                        f'{glyph(mark, x + CELL_W / 2, cy)}</g>')
            css.append(keyframes(f"aim{uid}k{side}", frames,
                                 lambda p: f"translate(0,{p[1]:.1f}px)"))
            css.append(f".aim-{uid}-{side}{{animation-name:aim{uid}k{side};"
                       f"animation-duration:{T}s;animation-timing-function:linear;"
                       "animation-iteration-count:infinite}")
        elif kind in ("speed", "reach", "angle"):
            span = 34.0 if not strong else 78.0
            body.append(_track(x, cy))
            frames = [(span * (2 * smooth(min(1.0, i / FRAMES * 2)) - 1) if i <= FRAMES / 2
                       else span * (1 - 2 * smooth(min(1.0, (i / FRAMES - 0.5) * 2))), 0.0)
                      for i in range(FRAMES + 1)]
            body.append(f'<g class="aim-{uid}-{side}">'
                        f'{glyph(mark, x + CELL_W / 2, cy)}</g>')
            css.append(keyframes(f"aim{uid}k{side}", frames,
                                 lambda p: f"translate({p[0]:.1f}px,0)"))
            dur = T if kind != "speed" else (T if not strong else T * 0.45)
            css.append(f".aim-{uid}-{side}{{animation-name:aim{uid}k{side};"
                       f"animation-duration:{dur}s;animation-timing-function:linear;"
                       "animation-iteration-count:infinite}")
        elif kind == "delay":
            body.append(_track(x, cy))
            wait = 0.0 if not strong else 0.45
            frames = []
            for i in range(FRAMES + 1):
                u = i / FRAMES
                pos = -62.0 if u < wait else -62 + 124 * smooth((u - wait) / (1 - wait))
                frames.append((pos, 0.0))
            body.append(f'<g class="aim-{uid}-{side}">'
                        f'{glyph(mark, x + CELL_W / 2, cy)}</g>')
            css.append(keyframes(f"aim{uid}k{side}", frames,
                                 lambda p: f"translate({p[0]:.1f}px,0)"))
            css.append(f".aim-{uid}-{side}{{animation-name:aim{uid}k{side};"
                       f"animation-duration:{T}s;animation-timing-function:linear;"
                       "animation-iteration-count:infinite}")
        elif kind in ("jump", "crouch", "crouchrate", "fly", "fall", "air", "bounce", "land"):
            mid = x + CELL_W / 2
            floor = cy + 26
            if kind != "fly":
                body.append(f'<path d="M{x + 22} {floor}H{x + CELL_W - 22}" '
                            'class="fig-grid-stroke" stroke-width="2.4"/>')
            if kind in ("crouch", "crouchrate"):
                # The standing outline stays so the duck is measurable against it. `duck`, not
                # `low`: `low` is already this card's left-hand state label.
                tall = 44.0
                # crouchrate holds the depth still and varies only how fast the duck happens,
                # which is what the rate field actually changes.
                duck = 0.42 if kind == "crouchrate" else (0.78 if not strong else 0.42)
                beat = (T * 1.6 if not strong else T * 0.7) if kind == "crouchrate" else T
                body.append(f'<rect x="{mid - 13}" y="{floor - tall}" width="26" '
                            f'height="{tall}" rx="6" class="fig-grid-stroke" stroke-width="1.6" '
                            'stroke-dasharray="4 4" fill="none"/>')
                body.append(f'<rect x="{mid - 11}" y="{floor - tall + 2}" width="22" '
                            f'height="{tall - 2}" rx="5" '
                            f'class="fig-target aim-{uid}-{side}"/>')
                css.append(f"@keyframes aim{uid}c{side}{{0%{{transform:scaleY(1)}}"
                           f"30%{{transform:scaleY({duck})}}70%{{transform:scaleY({duck})}}"
                           "100%{transform:scaleY(1)}}")
                css.append(f".aim-{uid}-{side}{{transform-box:fill-box;"
                           "transform-origin:center bottom;"
                           f"animation-name:aim{uid}c{side};animation-duration:{beat}s;"
                           "animation-timing-function:linear;"
                           "animation-iteration-count:infinite}")
                continue
            if kind == "jump":
                height = 22.0 if not strong else 46.0
                frames = [(0.0, -height * abs(math.sin(i / FRAMES * 3.14159)))
                          for i in range(FRAMES + 1)]
            elif kind == "fly":
                lift = 12.0 if not strong else 40.0
                frames = [(0.0, -lift * (0.5 + 0.5 * math.sin(i / FRAMES * 6.28318)))
                          for i in range(FRAMES + 1)]
            elif kind == "fall":
                drop = 0.5 if not strong else 1.0
                frames = [(0.0, -48 + 48 * min(1.0, (i / FRAMES) / drop))
                          for i in range(FRAMES + 1)]
            elif kind == "air":
                sway = 4.0 if not strong else 40.0
                frames = [(sway * (i / FRAMES), -48 + 48 * (i / FRAMES))
                          for i in range(FRAMES + 1)]
            elif kind == "land":
                # Down to the floor, then a crawl whose slowness is the penalty.
                crawl = 46.0 if not strong else 12.0
                frames = []
                for i in range(FRAMES + 1):
                    u = i / FRAMES
                    if u < 0.4:
                        frames.append((-40.0, -46 + 46 * smooth(u / 0.4)))
                    else:
                        frames.append((-40 + crawl * smooth((u - 0.4) / 0.6), 0.0))
            else:
                wall = mid + 52
                body.append(f'<rect x="{wall}" y="{floor - 54}" width="10" height="54" '
                            'class="fig-grid-fill"/>')
                frames = []
                for i in range(FRAMES + 1):
                    u = i / FRAMES
                    out = -46 + 92 * smooth(min(1.0, u / 0.5))
                    if strong and u > 0.5:
                        out = 46 - 92 * smooth((u - 0.5) / 0.5)
                    frames.append((out, 0.0))
            body.append(f'<g class="aim-{uid}-{side}">'
                        f'<circle cx="{mid}" cy="{floor - 11}" r="10" class="fig-target"/></g>')
            css.append(keyframes(f"aim{uid}v{side}", frames,
                                 lambda p: f"translate({p[0]:.1f}px,{p[1]:.1f}px)"))
            css.append(f".aim-{uid}-{side}{{animation-name:aim{uid}v{side};"
                       f"animation-duration:{T}s;animation-timing-function:linear;"
                       "animation-iteration-count:infinite}")
        elif any(kind in m.KINDS for m in SHAPE_MODULES):
            module = next(m for m in SHAPE_MODULES if kind in m.KINDS)
            parts, rules = module.draw(kind, index, uid, side, strong, x + CELL_W / 2, cy)
            # A shape captions its own cell, and the field names that state again underneath. When
            # the two come out identical the reader gets the same words twice, stacked. The label
            # is the one that stays, because it is the field's own wording.
            body += [part for part in parts if f">{label}</text>" not in part]
            css += rules
        elif kind in ("scatter", "burst", "climb", "zoom"):
            mid = x + CELL_W / 2
            if kind == "scatter":
                spread = 12.0 if not strong else 34.0
                rng = random.Random(index * 31 + side)
                body.append(f'<circle cx="{mid}" cy="{cy}" r="{spread:.0f}" '
                            'class="fig-grid-stroke" stroke-width="1.6" stroke-dasharray="4 4" '
                            'fill="none"/>')
                for shot in range(7):
                    angle = rng.uniform(0, 6.28318)
                    dist = spread * (rng.random() ** 0.5)
                    body.append(f'<circle cx="{mid + dist * math.cos(angle):.1f}" '
                                f'cy="{cy + dist * math.sin(angle):.1f}" r="4" '
                                f'class="fig-target aim-{uid}-{side}" '
                                f'style="animation-delay:{shot * 0.09:.2f}s"/>')
                body.append(crosshair("fig-ink-stroke", mid, cy))
                css.append(f"@keyframes aim{uid}s{side}{{0%{{opacity:0}}6%{{opacity:1}}"
                           "72%{opacity:1}80%{opacity:0}100%{opacity:0}}")
                css.append(f".aim-{uid}-{side}{{opacity:0;animation-name:aim{uid}s{side};"
                           f"animation-duration:{T}s;animation-iteration-count:infinite}}")
            elif kind == "burst":
                rounds = 1 if not strong else 3
                for shot in range(rounds):
                    body.append(f'<circle cx="{mid - 46}" cy="{cy}" r="5" '
                                f'class="fig-accent-fill aim-{uid}-{side}" '
                                f'style="animation-delay:{shot * 0.22:.2f}s"/>')
                body.append(crosshair("fig-ink-stroke", mid - 58, cy))
                body.append(f'<circle cx="{mid + 58}" cy="{cy}" r="14" class="fig-target"/>')
                css.append(f"@keyframes aim{uid}b{side}{{0%{{opacity:0;transform:translate(0,0)}}"
                           "6%{opacity:1;transform:translate(0,0)}"
                           "54%{opacity:1;transform:translate(90px,0)}"
                           "60%{opacity:0;transform:translate(90px,0)}"
                           "100%{opacity:0;transform:translate(90px,0)}}")
                css.append(f".aim-{uid}-{side}{{opacity:0;animation-name:aim{uid}b{side};"
                           f"animation-duration:{T}s;animation-timing-function:linear;"
                           "animation-iteration-count:infinite}")
            elif kind == "climb":
                rise = 14.0 if not strong else 40.0
                body.append(f'<path d="M{mid - 60} {cy + 18}H{mid + 60}" '
                            'class="fig-grid-stroke" stroke-width="2" stroke-dasharray="5 5"/>')
                body.append(f'<g class="aim-{uid}-{side}">'
                            f'{crosshair("fig-ink-stroke", mid, cy + 18)}</g>')
                frames = [(0.0, -rise * min(1.0, (i / FRAMES) / 0.55))
                          for i in range(FRAMES + 1)]
                css.append(keyframes(f"aim{uid}r{side}", frames,
                                     lambda p: f"translate(0,{p[1]:.1f}px)"))
                css.append(f".aim-{uid}-{side}{{animation-name:aim{uid}r{side};"
                           f"animation-duration:{T}s;animation-timing-function:linear;"
                           "animation-iteration-count:infinite}")
            else:
                small, big = 13.0, 30.0
                body.append(f'<circle cx="{mid}" cy="{cy}" r="{small if not strong else big}" '
                            f'class="fig-target aim-{uid}-{side}"/>')
                body.append(crosshair("fig-ink-stroke", mid, cy))
                css.append(f"@keyframes aim{uid}z{side}{{0%{{opacity:0.55}}20%{{opacity:1}}"
                           "100%{opacity:1}}")
                css.append(f".aim-{uid}-{side}{{animation-name:aim{uid}z{side};"
                           f"animation-duration:{T}s;animation-iteration-count:infinite}}")
        elif kind == "count":
            pips = 2 if not strong else 5
            for pip in range(pips):
                px = x + CELL_W / 2 - (pips - 1) * 15 + pip * 30
                body.append(f'<g class="aim-{uid}-{side}" '
                            f'style="animation-delay:{pip * 0.16:.2f}s">'
                            f'{glyph(mark, px, cy)}</g>')
            css.append(f"@keyframes aim{uid}p{side}{{0%{{opacity:0.2}}10%{{opacity:1}}"
                       "100%{opacity:1}}")
            css.append(f".aim-{uid}-{side}{{opacity:0.2;animation-name:aim{uid}p{side};"
                       f"animation-duration:{T}s;animation-iteration-count:infinite}}")
    css.append(f"@media (prefers-reduced-motion:reduce){{[class*='aim-{uid}-']{{"
               f"animation-play-state:paused;animation-delay:-{T * 0.3:.2f}s!important;"
               "opacity:1}}")
    return "".join(body), css


def sheet(slug: str, title: str, note: str, fields: Sequence[Field]) -> str:
    """All of a tab's fields as one tall figure, one strip per field."""
    height = 52 + len(fields) * H
    body = [text(12, 26, title, "fig-ink", anchor="start", size=16, weight=700),
            text(12, 44, note, "fig-muted", anchor="start", size=12, weight=500)]
    css: list[str] = []
    for index, field in enumerate(fields):
        strip, rules = card(index, field, slug)
        body.append(f'<g transform="translate(0,{52 + index * H})">{strip}</g>')
        css += rules
    return (f'<svg viewBox="0 0 {W} {height}" class="fig-fit" role="img" '
            f'aria-labelledby="fig-{slug}-title"><title id="fig-{slug}-title">'
            f'{title}. One strip per field, each naming the setting, describing it, and '
            'demonstrating a low and a high state side by side.</title>' + metadata()
            + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")
