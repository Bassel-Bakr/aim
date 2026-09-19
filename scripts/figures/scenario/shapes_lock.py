"""Shapes for the weapon's Cheats tab, aim down sights, recoil and spread.

The lock is a second hand on your mouse, so every field on that tab is drawn as something happening
to your crosshair rather than as a number. Recoil is an excursion off a resting line, spread is a
cone over time, and aiming down sights is a sight picture with a clock under it.

The panel behind each cell runs from y 34 to y 136, so nothing may stray past cy - 42 or cy + 60,
and every strip is frozen at 30% of its loop for readers with motion turned off.
"""
import math

from figure_kit import crosshair, keyframes, smooth, text

T = 4.0
FRAMES = 48
KINDS = ("lockpull", "lockrate", "lockcone", "lockdead", "lockheight", "lockhold",
         "lockregrab", "triggerwait",
         "zoomramp", "zoomwait", "zoomsens", "tpscamera",
         "swerve", "recoilpeak", "recoilreset", "shotrecoil", "patternloop", "pelletlist",
         "stillgate", "spreadhold")


def _lane(mid: float, cy: float) -> str:
    return (f'<path d="M{mid - 78} {cy}H{mid + 78}" class="fig-grid-stroke" '
            'stroke-width="1.6" opacity="0.6"/>')


def _hold(mid: float, cy: float, start: float, end: float, cls: str, label: str) -> list[str]:
    x0, x1 = mid - 74 + 148 * start, mid - 74 + 148 * end
    return [f'<rect x="{x0:.1f}" y="{cy - 8}" width="{max(3.0, x1 - x0):.1f}" height="16" '
            f'rx="4" class="{cls}" opacity="0.9"/>',
            text((x0 + x1) / 2, cy + 20, label, "fig-muted", size=8, weight=600)]


def draw(kind: str, index: int, uid: str, side: int, strong: bool,
         mid: float, cy: float) -> tuple[list[str], list[str]]:
    body: list[str] = []
    css: list[str] = []
    cls = f"aim-{uid}-{side}"

    if kind in ("lockpull", "lockrate"):
        # Three marks on one axis: where you aimed, where the target is, and where the lock put
        # you. Strength is how far along that gap it drags you; max speed caps each step.
        aim_x, target_x = mid - 62, mid + 58
        body.append(_lane(mid, cy + 2))
        body.append(f'<circle cx="{target_x}" cy="{cy + 2}" r="12" class="fig-target"/>')
        body.append(f'<path d="M{aim_x} {cy - 16}V{cy + 20}" class="fig-grid-stroke" '
                    'stroke-width="2" stroke-dasharray="3 3"/>')
        body.append(text(aim_x, cy - 22, "you aimed", "fig-muted", anchor="start",
                         size=8, weight=600))
        share = 0.3 if not strong else 0.92
        landed = aim_x + (target_x - aim_x) * share
        body.append(f'<path d="M{aim_x} {cy + 2}H{landed:.0f}" class="fig-tense-stroke" '
                    'stroke-width="2.4"/>')
        if kind == "lockrate":
            # Max speed is a ceiling on each step, so the steps themselves are drawn.
            steps = 2 if not strong else 6
            for step in range(1, steps + 1):
                sx = aim_x + (landed - aim_x) * step / steps
                body.append(f'<path d="M{sx:.0f} {cy - 4}V{cy + 8}" '
                            'class="fig-tense-stroke" stroke-width="1.6"/>')
            note = "it crawls across" if not strong else "it crosses at once"
        else:
            note = "it tugs a little" if not strong else "it drags you on target"
        body.append(f'<g class="{cls}">{crosshair("fig-ink-stroke", landed, cy + 2)}</g>')
        css.append(keyframes(f"aim{uid}a{side}",
                             [(-(landed - aim_x) * (1 - smooth(min(1.0, i / FRAMES * 2))), 0.0)
                              for i in range(FRAMES + 1)],
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".{cls}{{animation-name:aim{uid}a{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")
        body.append(text(mid, cy + 46, note, "fig-muted", size=10, weight=600))

    elif kind == "lockcone":
        # A window out of your own view. Inside it the lock grabs; outside it nothing happens.
        half = 16.0 if not strong else 44.0
        reach = 60.0
        dx = reach * math.tan(math.radians(half))
        body.append(crosshair("fig-ink-stroke", mid, cy + 32))
        body.append(f'<path d="M{mid} {cy + 32}L{mid - dx:.1f} {cy - 28}'
                    f'L{mid + dx:.1f} {cy - 28}Z" class="fig-accent-stroke" stroke-width="1.8" '
                    'stroke-dasharray="4 4" fill="none" opacity="0.85"/>')
        for spot in (-40, 34):
            inside = abs(spot) <= dx
            body.append(f'<circle cx="{mid + spot}" cy="{cy - 12}" r="11" '
                        f'class="fig-target" opacity="{1 if inside else 0.35}"/>')
        body.append(text(mid, cy + 52, "only dead ahead" if not strong
                         else "it grabs from far off", "fig-muted", size=10, weight=600))

    elif kind in ("lockdead", "lockheight"):
        # A band around the target the lock refuses to enter, or the point on the target it
        # parks your aim at. Both are about where the crosshair ends up on the body.
        body.append(f'<rect x="{mid - 16}" y="{cy - 30}" width="32" height="54" rx="11" '
                    'class="fig-target"/>')
        if kind == "lockdead":
            band = 14.0 if not strong else 42.0
            body.append(f'<rect x="{mid - band:.0f}" y="{cy - 34}" '
                        f'width="{band * 2:.0f}" height="62" rx="8" '
                        'class="fig-grid-stroke" stroke-width="1.8" stroke-dasharray="4 4" '
                        'fill="none" opacity="0.85"/>')
            body.append(crosshair("fig-ink-stroke", mid + band + 12, cy - 4))
            note = "it holds you on target" if not strong else "it lets go early"
        else:
            up = 14.0 if not strong else -20.0
            body.append(crosshair("fig-ink-stroke", mid, cy - 4 + up))
            body.append(f'<path d="M{mid + 34} {cy - 4}H{mid + 52}" class="fig-grid-stroke" '
                        'stroke-width="1.4" stroke-dasharray="3 3"/>')
            note = "it parks on the body" if not strong else "it parks over the head"
        body.append(text(mid, cy + 48, note, "fig-muted", size=10, weight=600))

    elif kind in ("lockhold", "lockregrab", "triggerwait"):
        # One clock, with the stretch this field owns filled in.
        if kind == "lockhold":
            span = 0.25 if not strong else 0.82
            body += _hold(mid, cy - 4, 0.05, 0.05 + span, "fig-tense-fill", "locked on")
            note = "it lets go quickly" if not strong else "it holds on and on"
        elif kind == "lockregrab":
            span = 0.2 if not strong else 0.74
            body += _hold(mid, cy - 4, 0.05, 0.05 + span, "fig-grid-fill", "cannot grab")
            note = "it grabs again at once" if not strong else "a long wait to re-grab"
        else:
            span = 0.12 if not strong else 0.62
            body += _hold(mid, cy - 4, 0.05, 0.05 + span, "fig-grid-fill", "waiting")
            body.append(f'<path d="M{mid - 74 + 148 * (0.05 + span):.1f} {cy - 26}V{cy - 12}" '
                        'class="fig-tense-stroke" stroke-width="3"/>')
            body.append(text(mid - 74 + 148 * (0.05 + span), cy - 30, "it fires", "fig-muted",
                             anchor="end", size=8, weight=600))
            note = "it fires the instant you cross" if not strong else "it hesitates first"
        body.append(f'<path d="M{mid - 74} {cy + 10}H{mid + 74}" class="fig-grid-stroke" '
                    'stroke-width="1.4" opacity="0.6"/>')
        body.append(text(mid, cy + 46, note, "fig-muted", size=9, weight=600))

    elif kind in ("zoomramp", "zoomwait"):
        # A sight picture with the clock under it, so the reader sees what the delay is a delay
        # to. Both cells end zoomed; only the timing differs.
        body.append(f'<rect x="{mid - 46}" y="{cy - 34}" width="92" height="50" rx="6" '
                    'class="fig-grid-stroke" stroke-width="1.6" fill="none"/>')
        body.append(f'<circle cx="{mid}" cy="{cy - 9}" r="{9 if not strong else 9}" '
                    'class="fig-target"/>')
        body.append(crosshair("fig-ink-stroke", mid, cy - 9))
        if kind == "zoomramp":
            body += _hold(mid, cy + 30, 0.04, 0.04 + (0.2 if not strong else 0.74),
                          "fig-cool-fill", "zooming")
        else:
            wait = 0.08 if not strong else 0.52
            body += _hold(mid, cy + 30, 0.04, 0.04 + wait, "fig-grid-fill", "nothing yet")
            body += _hold(mid, cy + 30, 0.04 + wait, 0.04 + wait + 0.28, "fig-cool-fill", "")
        body.append(text(mid, cy + 56, ("a slow zoom" if strong else "it snaps in")
                         if kind == "zoomramp"
                         else ("it hangs first" if strong else "it starts at once"),
                         "fig-muted", size=9, weight=600))

    elif kind in ("zoomsens", "tpscamera"):
        # Two lanes for the sensitivity field: the same hand travel below, a different amount of
        # view travel above. The camera field is a rig seen from behind.
        if kind == "zoomsens":
            body.append(_lane(mid, cy - 16))
            body.append(_lane(mid, cy + 18))
            body.append(text(mid - 78, cy - 22, "view", "fig-muted", anchor="start",
                             size=8, weight=600))
            body.append(text(mid - 78, cy + 12, "hand", "fig-muted", anchor="start",
                             size=8, weight=600))
            hand = 56.0
            view = hand if not strong else hand * 0.34
            body.append(f'<path d="M{mid - 40} {cy + 18}H{mid - 40 + hand:.0f}" '
                        'class="fig-cool-stroke" stroke-width="3"/>')
            body.append(f'<path d="M{mid - 40} {cy - 16}H{mid - 40 + view:.0f}" '
                        'class="fig-accent-stroke" stroke-width="3"/>')
            note = "the view keeps up" if not strong else "the same hand moves less"
        else:
            body.append(f'<rect x="{mid - 6}" y="{cy - 26}" width="34" height="46" rx="12" '
                        'class="fig-target"/>')
            off = 18.0 if not strong else 56.0
            body.append(f'<rect x="{mid + 28 - off:.0f}" y="{cy - 6}" width="16" height="12" '
                        'rx="3" class="fig-cool-fill"/>')
            body.append(text(mid + 36 - off, cy + 22, "camera", "fig-muted",
                             size=8, weight=600))
            note = "it sits behind you" if not strong else "it swings out wide"
        body.append(text(mid, cy + 48, note, "fig-muted", size=9, weight=600))

    elif kind in ("swerve", "recoilpeak", "recoilreset", "shotrecoil"):
        # The crosshair's excursion off its resting line. Which part of the excursion the field
        # owns is what changes between these four.
        rest = cy + 14
        body.append(f'<path d="M{mid - 76} {rest}H{mid + 76}" class="fig-grid-stroke" '
                    'stroke-width="1.6" stroke-dasharray="4 4" opacity="0.7"/>')
        body.append(text(mid - 76, rest + 14, "resting", "fig-muted", anchor="start",
                         size=8, weight=600))
        if kind == "swerve":
            wide = 10.0 if not strong else 46.0
            marks = (-0.9, -0.3, 0.2, 0.7, 1.0)
            for step, fx in enumerate(marks):
                body.append(f'<circle cx="{mid + fx * wide:.1f}" '
                            f'cy="{rest - 8 - step * 8}" r="4" class="fig-accent-fill"/>')
            note = "it climbs straight" if not strong else "it wanders sideways"
        else:
            peak = 0.3 if kind == "recoilpeak" and not strong else (
                0.72 if kind == "recoilpeak" else 0.4)
            back = (0.55 if kind == "recoilreset" and not strong else
                    0.95 if kind == "recoilreset" else 0.8)
            if kind == "shotrecoil":
                peak, back = (0.2, 0.42) if not strong else (0.42, 0.9)
            pts = [(0.0, 0.0), (peak, 1.0), (back, 0.0), (1.0, 0.0)]
            path = " ".join(f"{mid - 76 + 152 * px:.1f},{rest - 40 * py:.1f}"
                            for px, py in pts)
            body.append(f'<polyline points="{path}" class="fig-accent-stroke" '
                        'stroke-width="2.6" fill="none"/>')
            body.append(f'<path d="M{mid - 76 + 152 * peak:.1f} {rest}V{rest - 44}" '
                        'class="fig-grid-stroke" stroke-width="1.2" stroke-dasharray="3 3"/>')
            if kind == "recoilpeak":
                note = "it reaches the top at once" if not strong else "it climbs slowly"
            elif kind == "recoilreset":
                note = "home before the next shot" if not strong else "still high when you fire"
            else:
                note = "a short clip" if not strong else "a long one, blocking reset"
        body.append(text(mid, cy + 50, note, "fig-muted", size=9, weight=600))

    elif kind in ("patternloop", "pelletlist"):
        # A list of fixed offsets, and which entry the playhead uses. One field is the length of
        # that list, the other is where it jumps back to.
        total = 6
        entries = total if kind == "patternloop" else (2 if not strong else 6)
        for slot in range(entries):
            sx = mid - 74 + slot * 30
            body.append(f'<rect x="{sx:.0f}" y="{cy - 18}" width="24" height="24" rx="4" '
                        'class="fig-grid-fill" opacity="0.6"/>')
            body.append(text(sx + 12, cy - 2, f"{slot + 1}", "fig-muted", size=9, weight=600))
        if kind == "patternloop":
            back = 0 if not strong else 3
            bx = mid - 74 + back * 30 + 12
            body.append(f'<path d="M{mid - 74 + 5 * 30 + 12} {cy + 12}V{cy + 24}H{bx:.0f}'
                        f'V{cy + 12}" class="fig-accent-stroke" stroke-width="2.4" '
                        'fill="none"/>')
            body.append(f'<path d="M{bx - 4:.0f} {cy + 18}l4 -6l4 6" '
                        'class="fig-accent-stroke" stroke-width="2.4" fill="none"/>')
            note = "it loops the whole list" if not strong else "it loops the tail only"
        else:
            note = "a two-shot pattern" if not strong else "a six-shot pattern"
        body.append(text(mid, cy + 48, note, "fig-muted", size=9, weight=600))

    else:
        # Spread: the threshold that decides whether you count as still, and the plateau before
        # the cone starts closing again.
        if kind == "stillgate":
            body.append(f'<rect x="{mid - 74}" y="{cy - 26}" width="148" height="16" rx="5" '
                        'class="fig-grid-fill" opacity="0.5"/>')
            gate = 0.28 if not strong else 0.78
            body.append(f'<path d="M{mid - 74 + 148 * gate:.1f} {cy - 34}V{cy - 4}" '
                        'class="fig-accent-stroke" stroke-width="2.6"/>')
            body.append(text(mid - 74 + 148 * gate, cy - 38, "counts as still", "fig-muted",
                             size=8, weight=600))
            body.append(f'<rect x="{mid - 74}" y="{cy - 26}" width="{148 * 0.5:.0f}" '
                        'height="16" rx="5" class="fig-cool-fill"/>')
            body.append(text(mid - 50, cy + 2, "your speed", "fig-muted", size=8, weight=600))
            body.append(crosshair("fig-ink-stroke", mid, cy + 26))
            note = "moving, so the cone opens" if not strong else "it still counts as still"
        else:
            base, top = cy + 26, cy - 20
            body.append(f'<path d="M{mid - 76} {base}H{mid + 76}" class="fig-grid-stroke" '
                        'stroke-width="1.6"/>')
            hold = 0.15 if not strong else 0.62
            pts = [(0.0, 1.0), (hold, 1.0), (min(1.0, hold + 0.3), 0.0), (1.0, 0.0)]
            path = " ".join(f"{mid - 76 + 152 * px:.1f},{base - (base - top) * py:.1f}"
                            for px, py in pts)
            body.append(f'<polyline points="{path}" class="fig-accent-stroke" '
                        'stroke-width="2.6" fill="none"/>')
            body.append(text(mid - 76 + 152 * hold / 2, top - 6, "held open", "fig-muted",
                             size=8, weight=600))
            note = "it starts closing at once" if not strong else "it stays open a while"
        body.append(text(mid, cy + 48, note, "fig-muted", size=9, weight=600))

    return body, css
