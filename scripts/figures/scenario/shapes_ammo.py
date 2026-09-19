"""Shapes for the weapon's ammunition, reload timing and damage.

Eighteen fields here were a marker on a track. A magazine is a row of chambers, a reload is a span
during which the weapon is unavailable, and damage is a bite out of a health bar. Each of those is
a thing the reader can see happening, so each is drawn instead of abstracted.

The panel behind each cell runs from y 34 to y 136, so nothing may stray past cy - 42 or cy + 60,
and every strip is frozen at 30% of its loop for readers with motion turned off.
"""
import math

from figure_kit import crosshair, keyframes, smooth, text

T = 4.0
FRAMES = 48
KINDS = ("magsize", "ammobite", "emptyreload", "partialreload", "killammo", "overlapreload",
         "firefloor", "earlyswap", "shotwindup", "shotrecovery",
         "shotbite", "headmult", "falloffband", "rangefloor", "traceend", "muzzleoffset",
         "blastedge", "blastback")


def _mag(mid: float, cy: float, total: int, loaded: int, pitch: float = 17.0) -> list[str]:
    """A magazine as a row of chambers, so "how many rounds" is a count and not a length."""
    out = []
    span = (total - 1) * pitch
    for slot in range(total):
        sx = mid - span / 2 + slot * pitch
        out.append(f'<rect x="{sx - pitch / 2 + 1.5:.1f}" y="{cy - 11}" '
                   f'width="{pitch - 3:.1f}" height="22" rx="3" class="fig-grid-stroke" '
                   'stroke-width="1.4" fill="none" opacity="0.8"/>')
        if slot < loaded:
            out.append(f'<rect x="{sx - pitch / 2 + 3.5:.1f}" y="{cy - 8}" '
                       f'width="{pitch - 7:.1f}" height="16" rx="2" '
                       'class="fig-accent-fill"/>')
    return out


def _span(mid: float, cy: float, start: float, end: float, cls: str, label: str) -> list[str]:
    """A stretch of a 148 px timeline, which is how every "how long" field here is drawn."""
    x0, x1 = mid - 74 + 148 * start, mid - 74 + 148 * end
    return [f'<rect x="{x0:.1f}" y="{cy - 9}" width="{max(3.0, x1 - x0):.1f}" height="18" '
            f'rx="4" class="{cls}" opacity="0.9"/>',
            text((x0 + x1) / 2, cy + 22, label, "fig-muted", size=8, weight=600)]


def draw(kind: str, index: int, uid: str, side: int, strong: bool,
         mid: float, cy: float) -> tuple[list[str], list[str]]:
    body: list[str] = []
    css: list[str] = []
    cls = f"aim-{uid}-{side}"

    if kind in ("magsize", "ammobite"):
        # Both are about the magazine, so both draw one. Magazine Max changes how many chambers
        # there are; Ammo Per Shot holds the magazine fixed and changes how many a press empties.
        if kind == "magsize":
            total = 4 if not strong else 12
            body += _mag(mid, cy - 4, total, total)
            note = f"{total} rounds before a reload"
        else:
            total, takes = 10, (1 if not strong else 4)
            body += _mag(mid, cy - 4, total, total)
            width = 17.0 * takes - 3
            body.append(f'<rect x="{mid - 85 + 17.0 * (total - takes):.1f}" y="{cy - 15}" '
                        f'width="{width:.1f}" height="30" rx="4" '
                        f'class="fig-tense-stroke {cls}" stroke-width="2.4" fill="none"/>')
            css.append(f"@keyframes aim{uid}a{side}{{0%{{opacity:0.25}}20%{{opacity:1}}"
                       "70%{opacity:1}85%{opacity:0.25}100%{opacity:0.25}}")
            css.append(f".{cls}{{animation-name:aim{uid}a{side};animation-duration:{T}s;"
                       "animation-iteration-count:infinite}")
            note = f"{takes} per press" if takes > 1 else "one per press"
        body.append(text(mid, cy + 34, note, "fig-muted", size=10, weight=600))

    elif kind in ("emptyreload", "partialreload"):
        # The reload is the stretch where the weapon is not available, so the stretch is what the
        # reader is shown, with the magazine above it saying what is being filled.
        start = 8 if kind == "partialreload" else 0
        body += _mag(mid, cy - 20, 10, start)
        length = 0.3 if not strong else 0.82
        body += _span(mid, cy + 18, 0.04, 0.04 + length, "fig-cool-fill", "reloading")
        body.append(f'<path d="M{mid - 74} {cy + 32}H{mid + 74}" class="fig-grid-stroke" '
                    'stroke-width="1.4" opacity="0.6"/>')
        kindnote = "from empty" if kind == "emptyreload" else "with rounds left"
        body.append(text(mid, cy + 50, f"a long reload, {kindnote}" if strong
                         else f"a quick reload, {kindnote}", "fig-muted", size=9, weight=600))

    elif kind == "killammo":
        # A kill paying rounds back into the magazine, so the kill has to be in the picture.
        body.append(f'<path d="M{mid - 78} {cy - 26}l16 16M{mid - 62} {cy - 26}l-16 16" '
                    'class="fig-muted-stroke" stroke-width="2.6" stroke-linecap="round"/>')
        body.append(text(mid - 70, cy - 32, "a kill", "fig-muted", size=8, weight=600))
        back = 1 if not strong else 5
        body += _mag(mid + 14, cy - 16, 8, 3)
        for slot in range(back):
            sx = mid + 14 - 59.5 + (3 + slot) * 17.0
            body.append(f'<rect x="{sx - 5:.1f}" y="{cy - 24}" width="10" height="16" rx="2" '
                        f'class="fig-accent-fill {cls}" '
                        f'style="animation-delay:{slot * 0.18:.2f}s"/>')
        css.append(f"@keyframes aim{uid}a{side}{{0%{{opacity:0}}18%{{opacity:1}}"
                   "100%{opacity:1}}")
        css.append(f".{cls}{{opacity:0;animation-name:aim{uid}a{side};"
                   f"animation-duration:{T}s;animation-iteration-count:infinite}}")
        body.append(text(mid, cy + 26, f"the kill returns {back}" if strong
                         else "the kill returns one", "fig-muted", size=10, weight=600))

    elif kind in ("overlapreload", "earlyswap"):
        # Two spans on one clock: the window this weapon is still busy for, and the moment the
        # next thing is allowed. The field is whether the second may start inside the first.
        busy_label = "shot recovery" if kind == "overlapreload" else "this weapon busy"
        next_label = "reload" if kind == "overlapreload" else "the next weapon"
        body += _span(mid, cy - 16, 0.0, 0.55, "fig-grid-fill", busy_label)
        begins = 0.55 if not strong else 0.18
        body += _span(mid, cy + 16, begins, begins + 0.42, "fig-cool-fill", next_label)
        body.append(f'<path d="M{mid - 74 + 148 * begins:.1f} {cy - 30}V{cy + 30}" '
                    'class="fig-accent-stroke" stroke-width="2.4" stroke-dasharray="3 3"/>')
        body.append(text(mid, cy + 50, "it starts early" if strong
                         else "it waits its turn", "fig-muted", size=10, weight=600))

    elif kind == "firefloor":
        # The trigger held down, and the shots the floor lets through. Fewer marks is a slower
        # weapon, which is the whole of this field.
        body.append(f'<rect x="{mid - 74}" y="{cy - 26}" width="148" height="14" rx="4" '
                    'class="fig-grid-fill" opacity="0.7"/>')
        body.append(text(mid, cy - 32, "trigger held", "fig-muted", size=8, weight=600))
        shots = 8 if not strong else 3
        for shot in range(shots):
            sx = mid - 68 + shot * (136 / max(1, shots - 1))
            body.append(f'<path d="M{sx:.1f} {cy - 2}V{cy + 18}" class="fig-tense-stroke" '
                        'stroke-width="2.6"/>')
        body.append(f'<path d="M{mid - 74} {cy + 18}H{mid + 74}" class="fig-grid-stroke" '
                    'stroke-width="1.4" opacity="0.6"/>')
        body.append(text(mid, cy + 40, f"{shots} shots in the same time", "fig-muted",
                         size=10, weight=600))

    elif kind in ("shotwindup", "shotrecovery"):
        # A press, a shot, and the dead window on whichever side of it this field controls. For a
        # recovery the press and the shot are the same instant, so only one of them is marked:
        # two ticks a pixel apart printed their labels on top of each other.
        press = 0.06
        gap = 0.22 if not strong else 0.64
        if kind == "shotwindup":
            fire = press + gap
            body += _span(mid, cy + 12, press, fire, "fig-grid-fill", "wind-up")
            body.append(f'<path d="M{mid - 74 + 148 * press:.1f} {cy - 30}V{cy - 6}" '
                        'class="fig-accent-stroke" stroke-width="2.6"/>')
            # No "press" caption: with a short wind-up it printed on top of the shot's caption,
            # and the wind-up span already starts at the press.
            note = "a long wind-up" if strong else "it fires almost at once"
        else:
            fire = press
            body += _span(mid, cy + 12, fire + 0.03, fire + 0.03 + gap, "fig-grid-fill",
                          "nothing allowed")
            note = "a long recovery" if strong else "ready again at once"
        body.append(f'<path d="M{mid - 74 + 148 * fire:.1f} {cy - 30}V{cy - 6}" '
                    'class="fig-tense-stroke" stroke-width="3"/>')
        body.append(text(mid - 74 + 148 * fire, cy - 34, "the shot", "fig-muted",
                         anchor="start" if kind == "shotrecovery" else "end",
                         size=8, weight=600))
        body.append(text(mid, cy + 50, note, "fig-muted", size=10, weight=600))

    elif kind in ("shotbite", "headmult"):
        # Damage drawn as what it removes from the target, because a number on its own says
        # nothing about how many shots a kill takes.
        body.append(f'<rect x="{mid - 74}" y="{cy - 22}" width="148" height="20" rx="5" '
                    'class="fig-grid-fill" opacity="0.45"/>')
        body.append(text(mid - 74, cy - 28, "health", "fig-muted", anchor="start",
                         size=8, weight=600))
        if kind == "shotbite":
            bite = 0.2 if not strong else 0.55
            body.append(f'<rect x="{mid - 74}" y="{cy - 22}" width="{148 * bite:.0f}" '
                        'height="20" rx="5" class="fig-tense-fill"/>')
            shots = math.ceil(1 / bite)
            body.append(text(mid, cy + 20, f"{shots} shots to kill", "fig-muted",
                             size=10, weight=600))
        else:
            factor = 1.0 if not strong else 2.5
            body.append(f'<rect x="{mid - 74}" y="{cy - 22}" width="{148 * 0.22:.0f}" '
                        'height="20" rx="5" class="fig-tense-fill"/>')
            body.append(text(mid + 40, cy - 12, "body", "fig-muted", size=8, weight=600))
            body.append(f'<rect x="{mid - 74}" y="{cy + 4}" width="148" height="20" rx="5" '
                        'class="fig-grid-fill" opacity="0.45"/>')
            body.append(f'<rect x="{mid - 74}" y="{cy + 4}" '
                        f'width="{min(148.0, 148 * 0.22 * factor):.0f}" height="20" rx="5" '
                        'class="fig-tense-fill"/>')
            body.append(text(mid + 40, cy + 14, "head", "fig-muted", size=8, weight=600))
            body.append(text(mid, cy + 44, "a headshot counts the same" if not strong
                             else "a headshot hits far harder", "fig-muted",
                             size=10, weight=600))

    elif kind in ("falloffband", "rangefloor"):
        # Damage against distance, with you at zero. The field is where the taper runs, or how
        # much is left once it has finished.
        base, top = cy + 26, cy - 24
        body.append(f'<path d="M{mid - 76} {base}H{mid + 76}" class="fig-grid-stroke" '
                    'stroke-width="1.8"/>')
        body.append(f'<path d="M{mid - 76} {base}V{top - 4}" class="fig-grid-stroke" '
                    'stroke-width="1.8"/>')
        body.append(text(mid + 58, base + 14, "distance", "fig-muted", size=8, weight=600))
        body.append(text(mid - 76, top - 8, "damage", "fig-muted", anchor="start",
                         size=8, weight=600))
        if kind == "falloffband":
            begin, finish = (0.22, 0.45) if not strong else (0.5, 0.92)
            floor = 0.3
        else:
            begin, finish = 0.3, 0.6
            floor = 0.1 if not strong else 0.75
        bx = mid - 76 + 152 * begin
        fx = mid - 76 + 152 * finish
        fy = base - (base - top) * floor
        body.append(f'<path d="M{mid - 76} {top}H{bx:.1f}L{fx:.1f} {fy:.1f}H{mid + 76}" '
                    'class="fig-accent-stroke" stroke-width="2.6" fill="none"/>')
        body.append(f'<path d="M{bx:.1f} {base}V{top}M{fx:.1f} {base}V{fy:.1f}" '
                    'class="fig-grid-stroke" stroke-width="1.2" stroke-dasharray="3 3" '
                    'opacity="0.7"/>')
        note = (("it tapers close in" if not strong else "full damage a long way out")
                if kind == "falloffband"
                else ("almost nothing at range" if not strong else "it still hurts at range"))
        body.append(text(mid, cy + 50, note, "fig-muted", size=10, weight=600))

    elif kind in ("traceend", "muzzleoffset"):
        # Where the shot goes and where it comes from. Both are about the line itself, so the
        # line is drawn and the target is left where it is.
        body.append(crosshair("fig-ink-stroke", mid - 78, cy - 4))
        body.append(f'<circle cx="{mid + 62}" cy="{cy - 4}" r="13" class="fig-target"/>')
        if kind == "traceend":
            stop = mid - 78 + (70 if not strong else 138)
            body.append(f'<path d="M{mid - 66} {cy - 4}H{stop:.0f}" class="fig-tense-stroke" '
                        'stroke-width="2.4"/>')
            body.append(f'<path d="M{stop:.0f} {cy - 16}V{cy + 8}" class="fig-tense-stroke" '
                        'stroke-width="2" stroke-dasharray="3 3"/>')
            body.append(text(stop, cy + 22, "it stops here", "fig-muted", size=8, weight=600))
            note = "the shot never reaches" if not strong else "it carries all the way"
        else:
            offset = 0.0 if not strong else 22.0
            body.append(f'<circle cx="{mid - 62}" cy="{cy - 4 + offset:.0f}" r="4" '
                        'class="fig-accent-fill"/>')
            body.append(text(mid - 62, cy + 18 + offset, "muzzle", "fig-muted",
                             size=8, weight=600))
            body.append(f'<path d="M{mid - 62} {cy - 4 + offset:.0f}L{mid + 50} {cy - 4}" '
                        'class="fig-tense-stroke" stroke-width="2.4"/>')
            note = "it leaves from the eye" if not strong else "it leaves off to one side"
        body.append(text(mid, cy + 50, note, "fig-muted", size=10, weight=600))

    else:
        # A blast, and who it reaches: someone standing off to the side, or the person who fired.
        # The radius is capped at 34: the panel is 102 px tall, and a circle drawn to scale with
        # the damage would leave it.
        reach = 15.0 if not strong else 34.0
        centre = mid - 4
        body.append(f'<circle cx="{centre}" cy="{cy - 4}" r="{reach:.0f}" '
                    'class="fig-tense-fill" opacity="0.2"/>')
        body.append(f'<circle cx="{centre}" cy="{cy - 4}" r="{reach:.0f}" '
                    'class="fig-tense-stroke" stroke-width="1.8" stroke-dasharray="4 4" '
                    'fill="none"/>')
        body.append(f'<circle cx="{centre}" cy="{cy - 4}" r="6" class="fig-tense-fill"/>')
        if kind == "blastedge":
            body.append(f'<circle cx="{centre + 30}" cy="{cy - 4}" r="11" '
                        'class="fig-target"/>')
            note = "the edge misses them" if not strong else "the edge still kills"
        else:
            body.append(crosshair("fig-ink-stroke", centre - 30, cy - 4))
            note = "it does not reach you" if not strong else "it takes you with it"
        body.append(text(mid, cy + 46, note, "fig-muted", size=10, weight=600))

    return body, css
