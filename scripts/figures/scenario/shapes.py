"""Domain shapes for field strips.

fields.py owns the kinds that are honestly a magnitude along one axis: a dot further along a track
really does mean more speed, more reach, more delay. A third of the editor's fields are not that,
and drawing them as a dot on a track was noise wearing the costume of information.

These draw the thing itself instead. Each returns the strip's body and the CSS it needs, given the
cell's centre, the field's uid, which side of the card it is, and whether this is the cell showing
more of the effect.
"""
import math
import random

from figure_kit import crosshair, keyframes, smooth, text

T = 4.0
FRAMES = 36
KINDS = ("view", "head", "hitscan", "lock", "aircrouch", "pattern", "particle", "pass")


def draw(kind: str, index: int, uid: str, side: int, strong: bool,
         mid: float, cy: float) -> tuple[list[str], list[str]]:
    body: list[str] = []
    css: list[str] = []
    cls = f"aim-{uid}-{side}"

    if kind == "view":
        # A viewport, not a dot: the question is which camera you are behind.
        body.append(f'<rect x="{mid - 76}" y="{cy - 32}" width="152" height="76" rx="5" '
                    'class="fig-grid-stroke" stroke-width="1.6" fill="none"/>')
        body.append(f'<path d="M{mid - 74} {cy + 30}H{mid + 74}" class="fig-grid-stroke" '
                    'stroke-width="1.4" opacity="0.7"/>')
        if strong:
            body.append(f'<rect x="{mid - 9}" y="{cy - 2}" width="18" height="32" rx="7" '
                        'class="fig-target"/>')
            body.append(f'<circle cx="{mid}" cy="{cy - 11}" r="7" class="fig-target"/>')
        else:
            body.append(f'<path d="M{mid + 28} {cy + 30}L{mid + 58} {cy + 4}" '
                        'class="fig-muted-stroke" stroke-width="7" stroke-linecap="round" '
                        'opacity="0.85"/>')
        body.append(crosshair("fig-ink-stroke", mid, cy + 4))

    elif kind == "head":
        floor = cy + 34
        body.append(f'<rect x="{mid - 13}" y="{floor - 40}" width="26" height="40" rx="6" '
                    'class="fig-target"/>')
        if strong:
            body.append(f'<circle cx="{mid}" cy="{floor - 52}" r="11" class="fig-target"/>')
            body.append(f'<circle cx="{mid}" cy="{floor - 52}" r="17" '
                        'class="fig-accent-stroke" stroke-width="2" stroke-dasharray="4 3" '
                        'fill="none"/>')
        body.append(crosshair("fig-ink-stroke", mid + 36, floor - 52))

    elif kind == "hitscan":
        body.append(f'<circle cx="{mid + 54}" cy="{cy}" r="14" class="fig-target"/>')
        if strong:
            body.append(f'<circle cx="{mid - 54}" cy="{cy}" r="6" '
                        f'class="fig-accent-fill {cls}"/>')
            css.append(f"@keyframes aim{uid}h{side}{{0%{{transform:translate(0,0)}}"
                       "70%{transform:translate(108px,0)}100%{transform:translate(108px,0)}}")
            css.append(f".{cls}{{animation-name:aim{uid}h{side};animation-duration:{T}s;"
                       "animation-timing-function:linear;animation-iteration-count:infinite}")
        else:
            body.append(f'<path d="M{mid - 54} {cy}H{mid + 54}" '
                        f'class="fig-accent-stroke {cls}" stroke-width="3" '
                        'stroke-linecap="round"/>')
            css.append(f"@keyframes aim{uid}h{side}{{0%{{opacity:0}}8%{{opacity:1}}"
                       "34%{opacity:1}42%{opacity:0}100%{opacity:0}}")
            css.append(f".{cls}{{opacity:0;animation-name:aim{uid}h{side};"
                       f"animation-duration:{T}s;animation-iteration-count:infinite}}")
        body.append(crosshair("fig-ink-stroke", mid - 66, cy))

    elif kind == "lock":
        body.append(f'<circle cx="{mid + 40}" cy="{cy}" r="20" class="fig-target"/>')
        pull = 0.0 if not strong else 74.0
        frames = [(pull * smooth(min(1.0, (i / FRAMES) / 0.6)), 0.0) for i in range(FRAMES + 1)]
        body.append(f'<g class="{cls}">{crosshair("fig-ink-stroke", mid - 56, cy)}</g>')
        css.append(keyframes(f"aim{uid}l{side}", frames,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".{cls}{{animation-name:aim{uid}l{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")

    elif kind == "aircrouch":
        # No floor line at all: these fields are about what happens while airborne, and a ground
        # crouch under an airborne setting was simply wrong.
        tall, duck = 40.0, (1.0 if not strong else 0.5)
        body.append(f'<rect x="{mid - 13}" y="{cy - 22}" width="26" height="{tall}" rx="6" '
                    'class="fig-grid-stroke" stroke-width="1.6" stroke-dasharray="4 4" '
                    'fill="none"/>')
        body.append(f'<rect x="{mid - 11}" y="{cy - 20}" width="22" height="{tall - 4}" rx="5" '
                    f'class="fig-target {cls}"/>')
        body.append(f'<path d="M{mid - 36} {cy + 34}H{mid + 36}" class="fig-grid-stroke" '
                    'stroke-width="1.6" stroke-dasharray="3 5" opacity="0.45"/>')
        body.append(text(mid, cy + 50, "airborne", "fig-muted", size=10, weight=500))
        css.append(f"@keyframes aim{uid}a{side}{{0%{{transform:scaleY(1)}}"
                   f"34%{{transform:scaleY({duck})}}70%{{transform:scaleY({duck})}}"
                   "100%{transform:scaleY(1)}}")
        css.append(f".{cls}{{transform-box:fill-box;transform-origin:center bottom;"
                   f"animation-name:aim{uid}a{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")

    elif kind == "pattern":
        rng = random.Random(index * 17 + 3)
        spread = 30.0
        first = [(rng.uniform(-spread, spread), rng.uniform(-spread, spread)) for _ in range(6)]
        second = first if strong else [(rng.uniform(-spread, spread),
                                        rng.uniform(-spread, spread)) for _ in range(6)]
        for half, volley in enumerate((first, second)):
            for dx, dy in volley:
                body.append(f'<circle cx="{mid + dx:.1f}" cy="{cy + dy:.1f}" r="4" '
                            f'class="fig-target {cls}" '
                            f'style="animation-delay:{half * T / 2:.2f}s"/>')
        body.append(crosshair("fig-ink-stroke", mid, cy))
        css.append(f"@keyframes aim{uid}n{side}{{0%{{opacity:0}}5%{{opacity:1}}44%{{opacity:1}}"
                   "50%{opacity:0}100%{opacity:0}}")
        css.append(f".{cls}{{opacity:0;animation-name:aim{uid}n{side};"
                   f"animation-duration:{T}s;animation-iteration-count:infinite}}")

    elif kind == "particle":
        body.append(f'<rect x="{mid - 40}" y="{cy - 32}" width="14" height="64" '
                    'class="fig-grid-fill"/>')
        body.append(f'<path d="M{mid + 60} {cy}H{mid - 24}" class="fig-accent-stroke" '
                    'stroke-width="2.6" stroke-linecap="round" opacity="0.8"/>')
        if strong:
            for ray in range(6):
                angle = ray * 1.0472
                body.append(f'<path d="M{mid - 22} {cy}l{14 * math.cos(angle):.1f} '
                            f'{14 * math.sin(angle):.1f}" class="fig-accent-stroke {cls}" '
                            'stroke-width="2.4" stroke-linecap="round"/>')
            css.append(f"@keyframes aim{uid}f{side}{{0%{{opacity:0}}10%{{opacity:1}}"
                       "40%{opacity:0}100%{opacity:0}}")
            css.append(f".{cls}{{opacity:0;animation-name:aim{uid}f{side};"
                       f"animation-duration:{T}s;animation-iteration-count:infinite}}")

    else:
        gap = 30.0 if not strong else 7.0
        for slot in (-1, 1):
            body.append(f'<circle cx="{mid + slot * gap:.1f}" cy="{cy}" r="17" '
                        f'class="fig-target" opacity="{1 if slot < 0 else 0.6}"/>')
        body.append(text(mid, cy + 44, "they collide" if not strong else "they overlap",
                         "fig-muted", size=10, weight=500))

    return body, css
