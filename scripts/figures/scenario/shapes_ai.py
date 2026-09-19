"""Shapes for the dodge and bot editors.

A dodge field is about a strafe: where it turns, how evenly, and what interrupts it. A track with a
marker sliding along it does not say that, so these draw the strafe itself, the weighting between
two profiles, and the two bot switches that are about visibility rather than motion.
"""
import math

from figure_kit import crosshair, keyframes, smooth, text

T = 4.0
FRAMES = 44
KINDS = ("strafe", "evenness", "weight", "xray", "pointer", "waypointlogic", "reactmode")


def draw(kind: str, index: int, uid: str, side: int, strong: bool,
         mid: float, cy: float) -> tuple[list[str], list[str]]:
    body: list[str] = []
    css: list[str] = []
    cls = f"aim-{uid}-{side}"

    if kind == "strafe":
        # The track is the strafe, with its centre marked, because these fields set how far and how
        # long the bot runs before turning around.
        amp = 30.0 if not strong else 74.0
        body.append(f'<path d="M{mid - amp:.0f} {cy}H{mid + amp:.0f}" '
                    'class="fig-grid-stroke" stroke-width="4" stroke-linecap="round" '
                    'opacity="0.55"/>')
        body.append(f'<path d="M{mid} {cy - 16}V{cy + 16}" class="fig-grid-stroke" '
                    'stroke-width="1.6" opacity="0.7"/>')
        frames = [(amp * math.sin(i / FRAMES * 6.28318), 0.0) for i in range(FRAMES + 1)]
        body.append(f'<g class="{cls}"><circle cx="{mid}" cy="{cy}" r="11" '
                    'class="fig-target"/></g>')
        css.append(keyframes(f"aim{uid}s{side}", frames,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".{cls}{{animation-name:aim{uid}s{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")

    elif kind == "evenness":
        # A timeline with a mark at every turn, and a playhead crossing it at a constant rate. The
        # question is only whether the gaps between marks are equal, so nothing else moves: a
        # marker swinging above the line would be a second, unrelated use of the same axis.
        spans = (1.0, 1.0, 1.0, 1.0, 1.0) if not strong else (0.4, 1.7, 0.55, 1.25, 1.1)
        total = sum(spans)
        body.append(f'<path d="M{mid - 76} {cy + 6}H{mid + 76}" class="fig-grid-stroke" '
                    'stroke-width="2"/>')
        at = 0.0
        for span in spans[:-1]:
            at += span / total
            tx = mid - 76 + 152 * at
            body.append(f'<path d="M{tx:.1f} {cy - 8}V{cy + 20}" class="fig-accent-stroke" '
                        'stroke-width="2.6"/>')
        frames = [(-76 + 152 * i / FRAMES, 0.0) for i in range(FRAMES + 1)]
        body.append(f'<g class="{cls}"><circle cx="{mid}" cy="{cy + 6}" r="8" '
                    'class="fig-target"/></g>')
        css.append(keyframes(f"aim{uid}e{side}", frames,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".{cls}{{animation-name:aim{uid}e{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")
        body.append(text(mid, cy + 44, "evenly spaced" if not strong else "ragged spacing",
                         "fig-muted", size=10, weight=600))

    elif kind == "weight":
        # Two profiles and how often each is chosen, drawn as a split bar.
        share = 0.9 if not strong else 0.5
        body.append(f'<rect x="{mid - 70}" y="{cy - 14}" width="140" height="28" rx="6" '
                    'class="fig-grid-fill" opacity="0.4"/>')
        body.append(f'<rect x="{mid - 70}" y="{cy - 14}" width="{140 * share:.0f}" height="28" '
                    'rx="6" class="fig-accent-fill"/>')
        body.append(text(mid - 70 + 140 * share / 2, cy + 5, f"{share * 100:.0f}%",
                         "fig-muted", size=11, weight=700))
        body.append(text(mid, cy + 38, "one profile, mostly" if not strong
                         else "a coin flip each time", "fig-muted", size=10, weight=600))

    elif kind == "xray":
        wall = mid - 6
        body.append(f'<rect x="{wall}" y="{cy - 30}" width="14" height="60" '
                    'class="fig-grid-fill"/>')
        body.append(f'<circle cx="{mid + 46}" cy="{cy}" r="16" class="fig-target" '
                    f'opacity="{1 if strong else 0.18}"/>')
        if strong:
            body.append(f'<path d="M{mid - 52} {cy}H{mid + 28}" class="fig-cool-stroke" '
                        'stroke-width="2" stroke-dasharray="4 4"/>')
        body.append(crosshair("fig-ink-stroke", mid - 62, cy))
        body.append(text(mid, cy + 44, "hidden by the wall" if not strong
                         else "seen through it", "fig-muted", size=10, weight=600))

    elif kind == "pointer":
        body.append(f'<circle cx="{mid - 44}" cy="{cy}" r="15" class="fig-target"/>')
        if strong:
            body.append(f'<path d="M{mid - 30} {cy}H{mid + 60}" '
                        f'class="fig-tense-stroke {cls}" stroke-width="2"/>')
            body.append(f'<circle cx="{mid + 62}" cy="{cy}" r="5" '
                        f'class="fig-tense-fill {cls}"/>')
            css.append(f"@keyframes aim{uid}w{side}{{0%{{opacity:0.35}}50%{{opacity:1}}"
                       "100%{opacity:0.35}}")
            css.append(f".{cls}{{animation-name:aim{uid}w{side};animation-duration:{T / 2}s;"
                       "animation-iteration-count:infinite}")
        body.append(text(mid, cy + 40, "nothing shown" if not strong else "a visible beam",
                         "fig-muted", size=10, weight=600))

    elif kind == "waypointlogic":
        # Three waypoints and whether the bot walks them or breaks off toward you.
        # The whole route has to sit inside the panel, which runs from cy - 42 to cy + 60.
        for dx, dy in ((-52, -26), (52, -26), (0, 10)):
            body.append(f'<circle cx="{mid + dx}" cy="{cy + dy}" r="8" '
                        'class="fig-grid-stroke" stroke-width="1.8" fill="none"/>')
        body.append(f'<path d="M{mid - 52} {cy - 26}L{mid + 52} {cy - 26}'
                    f'L{mid} {cy + 10}Z" class="fig-grid-stroke" stroke-width="1.6" '
                    'stroke-dasharray="4 5" fill="none" opacity="0.6"/>')
        route = [(-52, -26), (52, -26), (0, 10), (-52, -26)] if not strong else \
                [(-52, -26), (52, -26), (0, 30), (0, 30)]
        frames = []
        for leg in range(3):
            a, b = route[leg], route[leg + 1]
            for i in range(FRAMES // 3):
                u = smooth(i / (FRAMES // 3))
                frames.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
        body.append(f'<g class="{cls}"><circle cx="{mid}" cy="{cy}" r="10" '
                    'class="fig-target"/></g>')
        css.append(keyframes(f"aim{uid}v{side}", frames,
                             lambda p: f"translate({p[0]:.1f}px,{p[1]:.1f}px)"))
        css.append(f".{cls}{{animation-name:aim{uid}v{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")
        body.append(crosshair("fig-ink-stroke", mid, cy + 46))

    else:
        # Mimic follows your movement, oppose goes the other way, ignore does its own thing.
        body.append(f'<path d="M{mid - 66} {cy - 18}H{mid + 66}" class="fig-grid-stroke" '
                    'stroke-width="2" stroke-dasharray="5 5" opacity="0.6"/>')
        body.append(f'<path d="M{mid - 66} {cy + 22}H{mid + 66}" class="fig-grid-stroke" '
                    'stroke-width="2" stroke-dasharray="5 5" opacity="0.6"/>')
        you = [(52 * math.sin(i / FRAMES * 6.28318), 0.0) for i in range(FRAMES + 1)]
        sign = 1.0 if strong else -1.0
        bot = [(sign * dx, 0.0) for dx, _ in you]
        body.append(f'<g class="{cls}b"><circle cx="{mid}" cy="{cy - 18}" r="10" '
                    'class="fig-target"/></g>')
        body.append(f'<g class="{cls}y">{crosshair("fig-ink-stroke", mid, cy + 22)}</g>')
        css.append(keyframes(f"aim{uid}m{side}", bot,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(keyframes(f"aim{uid}u{side}", you,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".{cls}b{{animation-name:aim{uid}m{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")
        css.append(f".{cls}y{{animation-name:aim{uid}u{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")
        body.append(text(mid, cy + 46, "it opposes you" if not strong else "it mimics you",
                         "fig-muted", size=10, weight=600))

    return body, css
