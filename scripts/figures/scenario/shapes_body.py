"""Shapes for the character's hitboxes, eye line and spawn rules.

Ten fields here were a marker on a track. A hitbox is a thing you have to hit, a spawn box is an
area a target can appear in, and a spawn rule is a cone or a radius that refuses certain spots.
None of those is a magnitude along one axis, so none of them is drawn as one.

The panel behind each cell runs from y 34 to y 136, so nothing may stray past cy - 42 or cy + 60,
and every strip is frozen at 30% of its loop for readers with motion turned off.
"""
import math

from figure_kit import crosshair, keyframes, text

T = 4.0
FRAMES = 48
KINDS = ("boxheight", "boxwidth", "projheight", "projwidth", "eyeline", "targetscale",
         "spawnnear", "spawnfar", "spawnapart", "spawnangle", "spawnreach")

# The four hitbox fields: which dimension moves, and whether the projectile box is the subject.
BOXES = {
    "boxheight": ("tall", False, "a short box", "a tall one"),
    "boxwidth": ("wide", False, "a narrow box", "a wide one"),
    "projheight": ("tall", True, "a short second box", "a tall one"),
    "projwidth": ("wide", True, "a narrow second box", "a wide one"),
}


def draw(kind: str, index: int, uid: str, side: int, strong: bool,
         mid: float, cy: float) -> tuple[list[str], list[str]]:
    body: list[str] = []
    css: list[str] = []
    cls = f"aim-{uid}-{side}"

    if kind in BOXES:
        # A hitbox is the thing you have to hit, so the crosshair sweeps across it and the reader
        # sees how much of that sweep lands.
        axis, projectile, lownote, highnote = BOXES[kind]
        floor = cy + 30
        body.append(f'<path d="M{mid - 84} {floor}H{mid + 84}" class="fig-grid-stroke" '
                    'stroke-width="2"/>')
        tall = (30.0 if not strong else 56.0) if axis == "tall" else 46.0
        wide = (14.0 if not strong else 34.0) if axis == "wide" else 22.0
        if projectile:
            # The main box stays put, so the reader can see this is the second one.
            body.append(f'<rect x="{mid - 20}" y="{floor - 46}" width="40" height="46" rx="14" '
                        'class="fig-grid-stroke" stroke-width="1.6" stroke-dasharray="4 4" '
                        'fill="none" opacity="0.7"/>')
            body.append(text(mid - 46, floor - 40, "main", "fig-muted", size=8, weight=600))
        body.append(f'<rect x="{mid - wide:.0f}" y="{floor - tall:.0f}" '
                    f'width="{wide * 2:.0f}" height="{tall:.0f}" rx="{min(wide, 14):.0f}" '
                    f'class="fig-target"{" opacity=\'0.75\'" if projectile else ""}/>')
        body.append(f'<g class="{cls}">'
                    f'{crosshair("fig-ink-stroke", mid, floor - tall / 2)}</g>')
        css.append(keyframes(f"aim{uid}a{side}",
                             [(70 * math.sin(i / FRAMES * 6.28318), 0.0)
                              for i in range(FRAMES + 1)],
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".{cls}{{animation-name:aim{uid}a{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")
        body.append(text(mid, cy + 52, highnote if strong else lownote, "fig-muted",
                         size=10, weight=600))

    elif kind == "targetscale":
        # One multiplier over whatever size the character profile set, so the original is kept on
        # screen as the thing being multiplied.
        body.append(f'<circle cx="{mid}" cy="{cy - 4}" r="14" class="fig-grid-stroke" '
                    'stroke-width="1.6" stroke-dasharray="4 4" fill="none" opacity="0.7"/>')
        body.append(f'<circle cx="{mid}" cy="{cy - 4}" r="{14 if not strong else 30}" '
                    'class="fig-target" opacity="0.85"/>')
        body.append(text(mid, cy + 36, "as the profile set it" if not strong
                         else "scaled up from it", "fig-muted", size=10, weight=600))
        body.append(crosshair("fig-ink-stroke", mid - 64, cy - 4))

    elif kind == "eyeline":
        # Where the camera sits on the body, which decides what a target sees over cover.
        floor = cy + 30
        body.append(f'<path d="M{mid - 84} {floor}H{mid + 84}" class="fig-grid-stroke" '
                    'stroke-width="2"/>')
        body.append(f'<rect x="{mid - 22}" y="{floor - 52}" width="44" height="52" rx="14" '
                    'class="fig-target"/>')
        eye = floor - (18 if not strong else 44)
        body.append(f'<path d="M{mid - 40} {eye}H{mid + 62}" class="fig-cool-stroke" '
                    'stroke-width="2.4" stroke-dasharray="5 4"/>')
        body.append(f'<circle cx="{mid}" cy="{eye}" r="5" class="fig-cool-fill"/>')
        body.append(text(mid + 64, eye + 4, "eyes", "fig-muted", anchor="start",
                         size=8, weight=600))
        body.append(text(mid, cy + 52, "it sees from the chest" if not strong
                         else "it sees from the head", "fig-muted", size=10, weight=600))

    elif kind in ("spawnnear", "spawnfar"):
        # Seen from above: the box a target may appear in, with one corner pinned and the other
        # being the field. Widening it turns holding an angle into repositioning.
        anchor_x, anchor_y = mid - 62, cy + 26
        near = 22.0 if kind == "spawnfar" else (18.0 if not strong else 54.0)
        far = (120.0 if kind == "spawnfar" and strong else
               (58.0 if kind == "spawnfar" else 112.0))
        body.append(f'<path d="M{anchor_x - 8} {anchor_y}h16m-8 -8v16" '
                    'class="fig-grid-stroke" stroke-width="1.8"/>')
        body.append(text(anchor_x, anchor_y + 15, "anchor", "fig-muted", size=8, weight=600))
        body.append(f'<rect x="{anchor_x + near:.0f}" y="{anchor_y - 56:.0f}" '
                    f'width="{max(10.0, far - near):.0f}" height="48" rx="4" '
                    'class="fig-accent-fill" opacity="0.22"/>')
        body.append(f'<rect x="{anchor_x + near:.0f}" y="{anchor_y - 56:.0f}" '
                    f'width="{max(10.0, far - near):.0f}" height="48" rx="4" '
                    'class="fig-accent-stroke" stroke-width="1.8" stroke-dasharray="4 4" '
                    'fill="none"/>')
        spots = ((0.18, 0.3), (0.55, 0.7), (0.82, 0.25))
        for order, (fx, fy) in enumerate(spots):
            sx = anchor_x + near + max(10.0, far - near) * fx
            body.append(f'<circle cx="{sx:.0f}" cy="{anchor_y - 56 + 48 * fy:.0f}" r="8" '
                        f'class="fig-target {cls}" '
                        f'style="animation-delay:{order * 1.2:.1f}s"/>')
        css.append(f"@keyframes aim{uid}a{side}{{0%{{opacity:0}}8%{{opacity:1}}"
                   "30%{opacity:1}38%{opacity:0}100%{opacity:0}}")
        css.append(f".{cls}{{opacity:0;animation-name:aim{uid}a{side};"
                   f"animation-duration:{T}s;animation-iteration-count:infinite}}")
        if kind == "spawnnear":
            note = "it can spawn on top of you" if not strong else "it is pushed out"
        else:
            note = "a tight spawn area" if not strong else "it can spawn anywhere"
        body.append(text(mid + 24, cy + 56, note, "fig-muted", size=10, weight=600))

    elif kind == "spawnapart":
        # The rule is a keep-apart distance, so it is drawn as that distance. A circle of the same
        # radius would be truthful and would not fit: the panel is 102 px tall.
        gap = 26.0 if not strong else 78.0
        left = mid - 40
        body.append(f'<circle cx="{left:.0f}" cy="{cy - 8}" r="12" class="fig-target"/>')
        body.append(f'<circle cx="{left + gap:.0f}" cy="{cy - 8}" r="12" class="fig-target"/>')
        body.append(f'<path d="M{left:.0f} {cy + 18}H{left + gap:.0f}" '
                    'class="fig-accent-stroke" stroke-width="2" stroke-dasharray="4 3"/>')
        body.append(f'<path d="M{left:.0f} {cy + 13}V{cy + 23}'
                    f'M{left + gap:.0f} {cy + 13}V{cy + 23}" '
                    'class="fig-accent-stroke" stroke-width="2"/>')
        body.append(text(left + gap / 2, cy + 36, "kept apart", "fig-muted",
                         size=8, weight=600))
        body.append(crosshair("fig-ink-stroke", mid - 40, cy + 52))
        body.append(text(mid + 30, cy + 56, "one flick covers both" if not strong
                         else "two separate flicks", "fig-muted", size=10, weight=600))

    else:
        # Seen from above: your view cone, and the spawns it refuses. One field is the cone's
        # angle, the other is how far out the rule is consulted at all.
        wide = kind == "spawnangle" and strong
        half = 42.0 if (wide or kind == "spawnreach") else 16.0
        reach = 68.0 if kind == "spawnangle" else (26.0 if not strong else 76.0)
        dx = reach * math.tan(math.radians(half))
        body.append(crosshair("fig-ink-stroke", mid, cy + 30))
        body.append(f'<path d="M{mid} {cy + 30}L{mid - dx:.1f} {cy + 30 - reach:.0f}'
                    f'L{mid + dx:.1f} {cy + 30 - reach:.0f}Z" class="fig-accent-stroke" '
                    'stroke-width="1.8" stroke-dasharray="4 4" fill="none" opacity="0.85"/>')
        for spot_x, spot_y in ((-54, 34), (0, 52), (46, 26)):
            inside = abs(spot_x) <= reach * math.tan(math.radians(half)) and spot_y <= reach
            style = "fig-grid-fill" if inside else "fig-target"
            body.append(f'<circle cx="{mid + spot_x}" cy="{cy + 30 - spot_y}" r="8" '
                        f'class="{style}" opacity="{0.4 if inside else 1}"/>')
        if kind == "spawnangle":
            note = "only dead ahead is blocked" if not strong else "a wide blocked wedge"
        else:
            note = "the rule barely reaches" if not strong else "it reaches far out"
        body.append(text(mid, cy + 52, note, "fig-muted", size=10, weight=600))

    return body, css
