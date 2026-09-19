"""Shapes for the character's movement physics.

Eleven fields on the Move tab were drawn as a marker on a dashed track, which says nothing about
ground speed, acceleration or drag. These draw the thing each one changes: how far a body gets in a
fixed time, how sharply its speed curve rises, how long it keeps sliding once you let go, and which
way a diagonal input actually sends you.

The panel behind each cell runs from y 34 to y 136, so nothing may stray past cy - 42 or cy + 60,
and every strip is frozen at 30% of its loop for readers with motion turned off.
"""
import math

from figure_kit import keyframes, smooth, text

T = 4.0
FRAMES = 48
KINDS = ("topspeed", "crouchpace", "speedcap", "dodgepace", "rampup", "rampcrouch",
         "turngrip", "letoff", "flatdrag", "airdrag", "dirmult", "dirmultback", "diagbias")

# The three that are a body covering ground against fixed scenery, and what each cell says.
PACE = {
    "topspeed": (0.45, 1.0, "it covers little ground", "it covers a lot"),
    "crouchpace": (0.35, 0.95, "crouching is a crawl", "crouched and quick"),
    "speedcap": (0.45, 1.0, "this weapon slows you", "it barely slows you"),
    "dodgepace": (0.4, 1.0, "the same path, slowly", "the same path, fast"),
}


def _posts(mid: float, floor: float) -> list[str]:
    """Fixed scenery. Without it, a body moving faster looks the same as one that started later."""
    out = [f'<path d="M{mid - 84} {floor}H{mid + 84}" class="fig-grid-stroke" '
           'stroke-width="2"/>']
    for post in range(5):
        px = mid - 80 + post * 40
        out.append(f'<path d="M{px} {floor}V{floor - 8}" class="fig-grid-stroke" '
                   'stroke-width="1.4" opacity="0.7"/>')
    return out


def draw(kind: str, index: int, uid: str, side: int, strong: bool,
         mid: float, cy: float) -> tuple[list[str], list[str]]:
    body: list[str] = []
    css: list[str] = []
    cls = f"aim-{uid}-{side}"

    if kind in PACE:
        # Distance covered in one loop, measured against posts that do not move. Both cells run the
        # same clock, so the one that is further along at the freeze is the faster one.
        slow, fast, lownote, highnote = PACE[kind]
        rate = fast if strong else slow
        floor = cy + 26
        body += _posts(mid, floor)
        if kind == "crouchpace":
            # The standing run is the reference this field is a fraction of.
            body.append(f'<circle cx="{mid - 80}" cy="{floor - 26}" r="9" '
                        'class="fig-grid-stroke" stroke-width="1.6" stroke-dasharray="3 3" '
                        'fill="none" opacity="0.7"/>')
            body.append(text(mid - 80, floor - 40, "standing", "fig-muted", size=8, weight=600))
        shape = (f'<rect x="{mid - 9}" y="{floor - 18}" width="18" height="18" rx="6" '
                 'class="fig-target"/>' if kind == "crouchpace"
                 else f'<circle cx="{mid}" cy="{floor - 14}" r="11" class="fig-target"/>')
        body.append(f'<g class="{cls}">{shape}</g>')
        css.append(keyframes(f"aim{uid}a{side}",
                             [(-80 + 160 * rate * (i / FRAMES), 0.0)
                              for i in range(FRAMES + 1)],
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".{cls}{{animation-name:aim{uid}a{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")
        body.append(text(mid, cy + 50, highnote if strong else lownote, "fig-muted",
                         size=10, weight=600))

    elif kind in ("rampup", "rampcrouch"):
        # Acceleration is the shape of the speed curve, not the height of it, so both cells reach
        # the same top speed and only the climb differs.
        base, top = cy + 26, cy - 24
        body.append(f'<path d="M{mid - 76} {base}H{mid + 76}" class="fig-grid-stroke" '
                    'stroke-width="1.8"/>')
        body.append(f'<path d="M{mid - 76} {base}V{top - 4}" class="fig-grid-stroke" '
                    'stroke-width="1.8"/>')
        body.append(f'<path d="M{mid - 76} {top}H{mid + 76}" class="fig-grid-stroke" '
                    'stroke-width="1.4" stroke-dasharray="4 4" opacity="0.7"/>')
        body.append(text(mid + 48, top - 6, "top speed", "fig-muted", size=8, weight=600))
        knee = 24.0 if strong else 104.0
        curve = [f"M{mid - 76} {base}"]
        for step in range(1, 25):
            x = -76 + step * 152 / 24
            climb = min(1.0, (x + 76) / knee)
            curve.append(f"L{mid + x:.1f} {base - (base - top) * smooth(climb):.1f}")
        body.append(f'<path d="{"".join(curve)}" class="fig-accent-stroke" stroke-width="2.6" '
                    'fill="none"/>')
        what = "crouched" if kind == "rampcrouch" else "on the ground"
        body.append(text(mid, cy + 48, f"up to speed at once, {what}" if strong
                         else f"a slow build, {what}", "fig-muted", size=9, weight=600))

    elif kind == "turngrip":
        # What the keys asked for against what the body did. Low grip overshoots the reversal; high
        # grip turns where you asked.
        floor = cy + 24
        body.append(f'<path d="M{mid - 80} {floor}H{mid + 80}" class="fig-grid-stroke" '
                    'stroke-width="2"/>')
        body.append(f'<path d="M{mid + 20} {floor - 42}V{floor + 8}" class="fig-accent-stroke" '
                    'stroke-width="2.4" stroke-dasharray="3 3"/>')
        body.append(text(mid + 20, floor - 48, "you reverse here", "fig-muted",
                         size=8, weight=600))
        over = 12.0 if strong else 54.0
        frames = []
        for i in range(FRAMES + 1):
            u = i / FRAMES
            if u < 0.4:
                x = -70 + (90 + over) * smooth(u / 0.4)
            else:
                x = 20 + over - (90 + over) * smooth((u - 0.4) / 0.6)
            frames.append((x, 0.0))
        body.append(f'<g class="{cls}"><circle cx="{mid}" cy="{floor - 14}" r="11" '
                    'class="fig-target"/></g>')
        css.append(keyframes(f"aim{uid}a{side}", frames,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".{cls}{{animation-name:aim{uid}a{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")
        body.append(text(mid, cy + 46, "it turns where you asked" if strong
                         else "it drifts past the turn", "fig-muted", size=10, weight=600))

    elif kind in ("letoff", "flatdrag", "airdrag"):
        # Let go and coast. The field is how far the body travels after the keys are released, so
        # the release point is marked and the stopping point is what moves.
        floor = cy + 26
        if kind == "airdrag":
            body.append(f'<path d="M{mid - 80} {floor}H{mid + 80}" class="fig-grid-stroke" '
                        'stroke-width="1.6" stroke-dasharray="5 5" opacity="0.6"/>')
            body.append(text(mid - 80, floor + 14, "no floor", "fig-muted", anchor="start",
                             size=8, weight=600))
        else:
            body += _posts(mid, floor)
        body.append(f'<path d="M{mid - 54} {floor - 34}V{floor + 4}" class="fig-tense-stroke" '
                    'stroke-width="2.6"/>')
        body.append(text(mid - 54, floor - 40, "keys released", "fig-muted",
                         anchor="start", size=8, weight=600))
        slide = 26.0 if strong else 104.0
        body.append(f'<path d="M{mid - 54 + slide:.0f} {floor - 22}V{floor + 4}" '
                    'class="fig-accent-stroke" stroke-width="2.4" stroke-dasharray="3 3"/>')
        body.append(text(mid - 54 + slide, floor + 16, "stops here", "fig-muted",
                         size=8, weight=600))
        frames = []
        for i in range(FRAMES + 1):
            u = i / FRAMES
            if u < 0.12:
                x = -80 + 26 * (u / 0.12)
            else:
                x = -54 + slide * smooth(min(1.0, (u - 0.12) / 0.5))
            frames.append((x, 0.0))
        body.append(f'<g class="{cls}"><circle cx="{mid}" cy="{floor - 14}" r="11" '
                    'class="fig-target"/></g>')
        css.append(keyframes(f"aim{uid}a{side}", frames,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".{cls}{{animation-name:aim{uid}a{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")
        note = ("it stops almost at once" if strong else "it slides a long way")
        if kind == "airdrag":
            note = ("speed bleeds off fast" if strong else "it keeps its speed")
        body.append(text(mid, cy + 50, note, "fig-muted", size=10, weight=600))

    elif kind in ("dirmult", "dirmultback"):
        # Seen from above, with the forward run pinned as the reference the multiplier scales
        # against. A sidestep is never faster than the run, so its ray has to stay inside it.
        corner = cy + 28
        run = 58.0
        span = run * (0.85 if strong else 0.3)
        body.append(f'<path d="M{mid} {corner}V{corner - run - 14:.0f}" '
                    'class="fig-grid-stroke" stroke-width="1.6" stroke-dasharray="4 4" '
                    'opacity="0.6"/>')
        body.append(text(mid, corner - run - 20, "facing", "fig-muted", size=8, weight=600))
        body.append(f'<path d="M{mid} {corner}V{corner - run:.0f}" class="fig-cool-stroke" '
                    'stroke-width="3"/>')
        body.append(text(mid - 8, corner - run / 2, "run", "fig-muted", anchor="end",
                         size=8, weight=600))
        way = 1 if kind == "dirmult" else -1
        body.append(f'<path d="M{mid} {corner}H{mid + way * span:.0f}" '
                    'class="fig-accent-stroke" stroke-width="3"/>')
        label = "sidestep" if kind == "dirmult" else "backing up"
        body.append(text(mid + way * span / 2, corner + 14, label, "fig-muted",
                         size=8, weight=600))
        body.append(text(mid, cy + 56, f"{label} is a crawl" if not strong
                         else f"{label} keeps up", "fig-muted", size=9, weight=600))

    else:
        # A diagonal press, and the angle it actually sends you at relative to where you look.
        body.append(f'<path d="M{mid - 30} {cy + 30}V{cy - 26}" class="fig-grid-stroke" '
                    'stroke-width="2" stroke-dasharray="4 4" opacity="0.7"/>')
        body.append(text(mid - 30, cy - 32, "facing", "fig-muted", size=8, weight=600))
        angle = 45.0 if strong else 22.0
        reach = 56.0
        dx = reach * math.sin(math.radians(angle))
        dy = reach * math.cos(math.radians(angle))
        body.append(f'<path d="M{mid - 30} {cy + 30}L{mid - 30 + dx:.1f} {cy + 30 - dy:.1f}" '
                    'class="fig-accent-stroke" stroke-width="3"/>')
        body.append(text(mid + 32, cy - 4, f"{angle:.0f} degrees", "fig-muted",
                         size=9, weight=600))
        body.append(text(mid, cy + 50, "a true diagonal" if strong
                         else "it pulls toward forward", "fig-muted", size=10, weight=600))

    return body, css
