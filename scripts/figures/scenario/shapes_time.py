"""Shapes for the fields that were still standing on a generic slider.

`reach`, `delay` and `angle` slide a marker along a dashed track. That is honest for a plain
magnitude, and dishonest for a distance measured from you, a pause at a turn, a lockout, or the gap
between a cause and the answer to it: those have a subject, and the subject was missing.

The panel behind each cell runs from y 34 to y 136, so nothing may stray past cy - 42 or cy + 60,
and every strip is frozen at 30% of its loop for readers with motion turned off.
"""
from figure_kit import crosshair, keyframes, smooth, text

T = 4.0
FRAMES = 44
KINDS = ("standoff", "swappause", "profileclock", "cooldown", "turnrate", "reactlag",
         "hitlag", "wallpress")


def draw(kind: str, index: int, uid: str, side: int, strong: bool,
         mid: float, cy: float) -> tuple[list[str], list[str]]:
    body: list[str] = []
    css: list[str] = []
    cls = f"aim-{uid}-{side}"

    if kind == "standoff":
        # A distance from you is not a dot on a track. It needs you at one end of it.
        gap = 48.0 if not strong else 96.0
        body.append(crosshair("fig-ink-stroke", mid - 76, cy - 6))
        body.append(f'<circle cx="{mid - 76 + gap:.0f}" cy="{cy - 6}" r="12" '
                    'class="fig-target"/>')
        body.append(f'<path d="M{mid - 64} {cy + 22}H{mid - 88 + gap:.0f}" '
                    'class="fig-accent-stroke" stroke-width="2"/>')
        body.append(f'<path d="M{mid - 64} {cy + 17}V{cy + 27}'
                    f'M{mid - 88 + gap:.0f} {cy + 17}V{cy + 27}" '
                    'class="fig-accent-stroke" stroke-width="2"/>')
        body.append(text(mid, cy + 48, "it keeps its distance" if strong
                         else "it closes right in", "fig-muted", size=10, weight=600))

    elif kind in ("swappause", "wallpress"):
        # A hold: at the end of a strafe, or leaning into an obstacle. Either way the point is that
        # the target stops, which a slower slide does not show.
        if kind == "swappause":
            body.append(f'<path d="M{mid - 70} {cy}H{mid + 70}" class="fig-grid-stroke" '
                        'stroke-width="4" stroke-linecap="round" opacity="0.5"/>')
            body.append(f'<path d="M{mid + 70} {cy - 20}V{cy + 20}" '
                        'class="fig-accent-stroke" stroke-width="2.4" stroke-dasharray="3 3"/>')
            far, hold = 70.0, (0.06 if not strong else 0.52)
            note = ("it waits at the turn" if strong else "it turns without stopping")
        else:
            wall = mid + 46
            body.append(f'<rect x="{wall}" y="{cy - 28}" width="16" height="56" '
                        'class="fig-grid-fill"/>')
            body.append(f'<path d="M{mid - 74} {cy}H{wall}" class="fig-grid-stroke" '
                        'stroke-width="3" stroke-linecap="round" opacity="0.5"/>')
            far, hold = 32.0, (0.06 if not strong else 0.52)
            note = ("it leans in a while" if strong else "it gives up at once")
        # Out, hold, back. The hold is the field, so it is the part that changes.
        out = round(FRAMES * (1.0 - hold) / 2)
        held = max(1, round(FRAMES * hold))
        start = -70.0 if kind == "swappause" else -74.0
        frames = [(start + (far - start) * smooth(i / out), 0.0) for i in range(out)]
        frames += [(far, 0.0)] * held
        rest = max(1, FRAMES - out - held + 1)
        frames += [(far - (far - start) * smooth(i / rest), 0.0) for i in range(rest)]
        body.append(f'<g class="{cls}"><circle cx="{mid}" cy="{cy}" r="11" '
                    'class="fig-target"/></g>')
        css.append(keyframes(f"aim{uid}p{side}", frames,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".{cls}{{animation-name:aim{uid}p{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")
        body.append(text(mid, cy + 44, note, "fig-muted", size=10, weight=600))

    elif kind in ("profileclock", "cooldown"):
        # Time spent on one thing before another is allowed, drawn as a stretch of a timeline. A
        # marker sliding along says nothing about how long the stretch is.
        body.append(f'<rect x="{mid - 74}" y="{cy - 12}" width="148" height="24" rx="5" '
                    'class="fig-grid-fill" opacity="0.4"/>')
        share = 0.3 if not strong else 0.85
        fill = "fig-cool-fill" if kind == "profileclock" else "fig-grid-fill"
        body.append(f'<rect x="{mid - 74}" y="{cy - 12}" width="{148 * share:.0f}" '
                    f'height="24" rx="5" class="{fill}" opacity="0.85"/>')
        edge = mid - 74 + 148 * share
        body.append(f'<path d="M{edge:.1f} {cy - 20}V{cy + 20}" class="fig-accent-stroke" '
                    'stroke-width="2.6"/>')
        if kind == "profileclock":
            body.append(text(mid - 74 + 148 * share / 2, cy + 26, "profile A", "fig-muted",
                             size=9, weight=600))
            note = "it stays a long while" if strong else "it swaps out early"
        else:
            body.append(text(mid - 74 + 148 * share / 2, cy + 26, "locked out", "fig-muted",
                             size=9, weight=600))
            note = "a long lockout" if strong else "usable again at once"
        body.append(text(mid, cy + 48, note, "fig-muted", size=10, weight=600))

    elif kind == "turnrate":
        # A corner on a route, taken as a wide arc or as a right angle.
        if strong:
            path = f"M{mid - 58} {cy - 20}L{mid + 12} {cy - 20}L{mid + 12} {cy + 22}"
            note = "it corners sharply"
        else:
            path = (f"M{mid - 58} {cy - 20}L{mid - 24} {cy - 20}"
                    f"Q{mid + 12} {cy - 20} {mid + 12} {cy + 12}L{mid + 12} {cy + 22}")
            note = "it swings wide"
        body.append(f'<path d="{path}" class="fig-grid-stroke" stroke-width="2.4" '
                    'stroke-dasharray="4 4" fill="none"/>')
        for dx, dy in ((-58, -20), (12, 22)):
            body.append(f'<circle cx="{mid + dx}" cy="{cy + dy}" r="6" '
                        'class="fig-grid-stroke" stroke-width="1.8" fill="none"/>')
        body.append(f'<circle cx="{mid - 22}" cy="{cy - 20}" r="10" class="fig-target"/>')
        body.append(text(mid, cy + 46, note, "fig-muted", size=10, weight=600))

    else:
        # Two lanes: the thing that happened, and the bot's answer to it. The gap between the two
        # marks is the field, so the gap is what the reader is being shown.
        gap = 0.1 if not strong else 0.58
        for dy in (-18, 18):
            body.append(f'<path d="M{mid - 74} {cy + dy}H{mid + 74}" '
                        'class="fig-grid-stroke" stroke-width="1.6" opacity="0.6"/>')
        cause = mid - 54
        answer = cause + 124 * gap
        body.append(f'<path d="M{cause} {cy - 30}V{cy - 6}" class="fig-tense-stroke" '
                    'stroke-width="3"/>')
        body.append(f'<path d="M{answer:.1f} {cy + 6}V{cy + 30}" class="fig-accent-stroke" '
                    'stroke-width="3"/>')
        body.append(f'<path d="M{cause} {cy}H{answer:.1f}" class="fig-muted-stroke" '
                    'stroke-width="1.6" stroke-dasharray="3 3"/>')
        body.append(text(cause, cy - 34, "you move" if kind == "reactlag" else "a hit lands",
                         "fig-muted", anchor="start", size=9, weight=600))
        body.append(text(mid, cy + 48, "it answers late" if strong else "it answers at once",
                         "fig-muted", size=10, weight=600))

    return body, css
