"""The second batch of domain shapes.

These cover the fields left on the generic dot after shapes.py: colors, ability slots, input
recordings, invincibility, hitbox shapes, magazines, recoil reset, charge, and the two fields whose
whole content is a name.

Split from shapes.py only for size. Same contract: return the strip's body and the CSS it needs.
"""
import math

from figure_kit import crosshair, keyframes, smooth, text

T = 4.0
FRAMES = 36
KINDS = ("swatch", "slot", "record", "shield", "boxshape", "hidden", "magazine", "reset",
         "charge", "invertfov", "movemodel", "label")


def draw(kind: str, index: int, uid: str, side: int, strong: bool,
         mid: float, cy: float) -> tuple[list[str], list[str]]:
    body: list[str] = []
    css: list[str] = []
    cls = f"aim-{uid}-{side}"

    if kind == "swatch":
        # A character with its two colored parts, since that is what the field actually sets.
        floor = cy + 32
        head = "fig-accent-fill" if strong else "fig-grid-fill"
        torso = "fig-cool-fill" if strong else "fig-grid-fill"
        body.append(f'<rect x="{mid - 13}" y="{floor - 38}" width="26" height="38" rx="6" '
                    f'class="{torso}"/>')
        body.append(f'<circle cx="{mid}" cy="{floor - 50}" r="11" class="{head}"/>')
        body.append(text(mid - 30, floor - 50, "head", "fig-muted", anchor="end", size=10,
                         weight=500))
        body.append(text(mid - 30, floor - 18, "body", "fig-muted", anchor="end", size=10,
                         weight=500))
        body.append(text(mid, floor + 18, "reader may override", "fig-muted", size=9, weight=500))

    elif kind == "slot":
        # Four slots, because a character holds four and the question is how many are filled.
        filled = 1 if not strong else 3
        for slot in range(4):
            sx = mid - 51 + slot * 34
            body.append(f'<rect x="{sx - 13}" y="{cy - 13}" width="26" height="26" rx="6" '
                        'class="fig-grid-stroke" stroke-width="1.8" fill="none"/>')
            if slot < filled:
                body.append(f'<rect x="{sx - 9}" y="{cy - 9}" width="18" height="18" rx="4" '
                            f'class="fig-accent-fill {cls}" '
                            f'style="animation-delay:{slot * 0.2:.2f}s"/>')
        css.append(f"@keyframes aim{uid}o{side}{{0%{{opacity:0.15}}12%{{opacity:1}}"
                   "100%{opacity:1}}")
        css.append(f".{cls}{{opacity:0.15;animation-name:aim{uid}o{side};"
                   f"animation-duration:{T}s;animation-iteration-count:infinite}}")

    elif kind == "record":
        # An input trace being replayed, which is what a playback profile is.
        body.append(f'<path d="M{mid - 70} {cy}H{mid + 70}" class="fig-grid-stroke" '
                    'stroke-width="1.6" opacity="0.6"/>')
        trace = " ".join(f"{mid - 70 + i * 7:.0f} {cy - 16 * math.sin(i * 0.8):.1f}"
                         for i in range(21))
        body.append(f'<polyline points="{trace}" class="fig-cool-stroke" stroke-width="2" '
                    'fill="none" opacity="0.85"/>')
        if strong:
            frames = [(140.0 * (i / FRAMES), 0.0) for i in range(FRAMES + 1)]
            body.append(f'<g class="{cls}"><circle cx="{mid - 70}" cy="{cy}" r="7" '
                        'class="fig-accent-fill"/></g>')
            css.append(keyframes(f"aim{uid}p{side}", frames,
                                 lambda p: f"translate({p[0]:.1f}px,0)"))
            css.append(f".{cls}{{animation-name:aim{uid}p{side};animation-duration:{T}s;"
                       "animation-timing-function:linear;animation-iteration-count:infinite}")
            body.append(text(mid, cy + 34, "replayed", "fig-accent-text", size=10, weight=600))
        else:
            body.append(f'<circle cx="{mid - 70}" cy="{cy}" r="7" class="fig-grid-fill"/>')
            body.append(text(mid, cy + 34, "its own inputs", "fig-muted", size=10, weight=500))

    elif kind == "shield":
        body.append(f'<circle cx="{mid + 34}" cy="{cy}" r="19" class="fig-target"/>')
        if strong:
            body.append(f'<circle cx="{mid + 34}" cy="{cy}" r="30" class="fig-balanced-stroke" '
                        'stroke-width="2.4" stroke-dasharray="5 4" fill="none"/>')
        stop = -6.0 if strong else 58.0
        frames = [(stop * smooth(min(1.0, (i / FRAMES) / 0.6)), 0.0) for i in range(FRAMES + 1)]
        body.append(f'<g class="{cls}"><circle cx="{mid - 54}" cy="{cy}" r="6" '
                    'class="fig-accent-fill"/></g>')
        css.append(keyframes(f"aim{uid}d{side}", frames,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".{cls}{{animation-name:aim{uid}d{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")
        body.append(text(mid, cy + 40, "turned away" if strong else "it lands", "fig-muted",
                         size=10, weight=600))

    elif kind == "boxshape":
        floor = cy + 30
        if strong:
            body.append(f'<circle cx="{mid}" cy="{floor - 24}" r="24" class="fig-target"/>')
            body.append(text(mid, floor + 20, "a sphere", "fig-muted", size=10, weight=500))
        else:
            body.append(f'<rect x="{mid - 17}" y="{floor - 48}" width="34" height="48" rx="17" '
                        'class="fig-target"/>')
            body.append(text(mid, floor + 20, "a cylinder", "fig-muted", size=10, weight=500))
        body.append(f'<path d="M{mid - 40} {floor}H{mid + 40}" class="fig-grid-stroke" '
                    'stroke-width="2"/>')

    elif kind == "hidden":
        floor = cy + 30
        body.append(f'<rect x="{mid - 15}" y="{floor - 44}" width="30" height="44" rx="8" '
                    'class="fig-target"/>')
        outline = "fig-cool-stroke" if not strong else "fig-grid-stroke"
        dash = "" if not strong else ' stroke-dasharray="2 6" opacity="0.35"'
        body.append(f'<rect x="{mid - 24}" y="{floor - 54}" width="48" height="54" rx="10" '
                    f'class="{outline}" stroke-width="2"{dash} fill="none"/>')
        body.append(text(mid, floor + 20, "you can see it" if not strong else "invisible",
                         "fig-muted", size=10, weight=500))

    elif kind == "magazine":
        rounds = 6
        for slot in range(rounds):
            sx = mid - 55 + slot * 22
            body.append(f'<rect x="{sx - 7}" y="{cy - 14}" width="14" height="28" rx="3" '
                        'class="fig-grid-stroke" stroke-width="1.6" fill="none"/>')
            delay = (slot * (T / rounds * 0.8)) if strong else 0.0
            body.append(f'<rect x="{sx - 4}" y="{cy - 11}" width="8" height="22" rx="2" '
                        f'class="fig-accent-fill {cls}" style="animation-delay:{delay:.2f}s"/>')
        css.append(f"@keyframes aim{uid}m{side}{{0%{{opacity:0.12}}10%{{opacity:1}}"
                   "100%{opacity:1}}")
        css.append(f".{cls}{{opacity:0.12;animation-name:aim{uid}m{side};"
                   f"animation-duration:{T}s;animation-iteration-count:infinite}}")
        body.append(text(mid, cy + 34, "all at once" if not strong else "one at a time",
                         "fig-muted", size=10, weight=500))

    elif kind == "reset":
        body.append(f'<path d="M{mid - 60} {cy + 20}H{mid + 60}" class="fig-grid-stroke" '
                    'stroke-width="2" stroke-dasharray="5 5"/>')
        frames = []
        for i in range(FRAMES + 1):
            u = i / FRAMES
            rise = -36 * min(1.0, u / 0.35)
            if strong and u > 0.5:
                rise = -36 * (1 - smooth(min(1.0, (u - 0.5) / 0.45)))
            frames.append((0.0, rise))
        body.append(f'<g class="{cls}">{crosshair("fig-ink-stroke", mid, cy + 20)}</g>')
        css.append(keyframes(f"aim{uid}t{side}", frames,
                             lambda p: f"translate(0,{p[1]:.1f}px)"))
        css.append(f".{cls}{{animation-name:aim{uid}t{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")
        body.append(text(mid, cy + 44, "stays up" if not strong else "comes home", "fig-muted",
                         size=10, weight=600))

    elif kind == "charge":
        body.append(f'<rect x="{mid - 60}" y="{cy - 10}" width="120" height="20" rx="6" '
                    'class="fig-grid-fill" opacity="0.4"/>')
        body.append(f'<rect x="{mid - 60}" y="{cy - 10}" width="120" height="20" rx="6" '
                    f'class="fig-accent-fill {cls}"/>')
        if strong:
            css.append(f"@keyframes aim{uid}g{side}{{0%{{transform:scaleX(0)}}"
                       "48%{transform:scaleX(0.75)}52%{transform:scaleX(0)}"
                       "100%{transform:scaleX(0)}}")
            body.append(text(mid, cy + 32, "interrupted", "fig-tense-fill", size=10, weight=600))
        else:
            css.append(f"@keyframes aim{uid}g{side}{{0%{{transform:scaleX(0)}}"
                       "80%{transform:scaleX(1)}100%{transform:scaleX(1)}}")
            body.append(text(mid, cy + 32, "charge kept", "fig-muted", size=10, weight=600))
        css.append(f".{cls}{{transform-box:fill-box;transform-origin:left center;"
                   f"animation-name:aim{uid}g{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")

    elif kind == "invertfov":
        # The player's cone, and whether spawns are pushed out of it or pulled into it.
        eye = cy + 38
        body.append(f'<path d="M{mid} {eye}L{mid - 46} {cy - 26}L{mid + 46} {cy - 26}Z" '
                    'class="fig-cool-stroke" stroke-width="1.8" stroke-dasharray="5 4" '
                    'fill="none" opacity="0.8"/>')
        inside = [(0, -12), (-20, 4)]
        outside = [(-64, -6), (62, -14)]
        for dx, dy in (inside if strong else outside):
            body.append(f'<circle cx="{mid + dx}" cy="{cy + dy}" r="9" class="fig-target"/>')
        for dx, dy in (outside if strong else inside):
            body.append(f'<circle cx="{mid + dx}" cy="{cy + dy}" r="9" class="fig-target" '
                        'opacity="0.2"/>')
        body.append(crosshair("fig-ink-stroke", mid, eye - 6))

    elif kind == "movemodel":
        floor = cy + 26
        body.append(f'<path d="M{mid - 70} {floor}H{mid + 70}" class="fig-grid-stroke" '
                    'stroke-width="2"/>')
        hops = 3 if strong else 1
        frames = []
        for i in range(FRAMES + 1):
            u = i / FRAMES
            phase = (u * hops) % 1.0
            gain = 1.0 + (0.5 * int(u * hops) if strong else 0.0)
            frames.append((-60 + 120 * u, -26 * gain * abs(math.sin(phase * 3.14159))))
        body.append(f'<g class="{cls}"><circle cx="{mid}" cy="{floor - 10}" r="9" '
                    'class="fig-target"/></g>')
        css.append(keyframes(f"aim{uid}q{side}", frames,
                             lambda p: f"translate({p[0]:.1f}px,{p[1]:.1f}px)"))
        css.append(f".{cls}{{animation-name:aim{uid}q{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")
        body.append(text(mid, floor + 24, "one hop" if not strong else "chained hops",
                         "fig-muted", size=10, weight=500))

    else:
        # A name: a field that is either blank or carries text, and nothing moves.
        body.append(f'<rect x="{mid - 66}" y="{cy - 14}" width="132" height="28" rx="5" '
                    'class="fig-panel fig-grid-stroke" stroke-width="1.6"/>')
        if strong:
            for word in range(3):
                wx = mid - 54 + word * 30
                body.append(f'<rect x="{wx}" y="{cy - 4}" width="{22 - word * 4}" height="8" '
                            'rx="3" class="fig-muted" opacity="0.75"/>')
        body.append(text(mid, cy + 34, "blank" if not strong else "carries a name",
                         "fig-muted", size=10, weight=500))

    return body, css
