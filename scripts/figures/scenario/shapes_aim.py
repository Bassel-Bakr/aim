"""Shapes for the aim profile and the ability profile.

An aim profile is about a second crosshair: where the bot thinks you are, how fast it gets there,
and how far off it lands. An ability profile is about charges and the conditions that release them.
Neither is a strafe, so neither borrows one.

The panel behind each cell runs from y 34 to y 136, so nothing may stray past cy - 42 or cy + 60.
Every strip is frozen at 30% of its loop for readers with motion turned off, so whatever tells the
two cells apart has to be on screen by then.
"""
import math

from figure_kit import crosshair, keyframes, smooth, text

T = 4.0
FRAMES = 48
FREEZE = 0.30
KINDS = ("sampletarget", "sampleself", "flickfov", "flickspeed", "flickerror", "trackspeed",
         "trackerror", "desklimit", "recenter", "optimalcone", "outerpenalty", "shootfov",
         "aimoffset", "spreadtol", "distancespread", "errorceiling",
         "chargebar", "chargespawn", "chargerefill", "refund", "holduse", "blockattack",
         "blockwhenattack", "useground", "useair", "usecombat", "useoutcombat",
         "selfhealth", "targethealth", "aimgate", "hurtbox", "inputlock")

# The four "uses it here" switches, each with the state that has to be drawn for it to mean
# anything: on the floor, off it, with a target in view, or with none.
WHERE = {
    "useground": ("on the ground", True, False),
    "useair": ("off the ground", True, True),
    "usecombat": ("with a target", False, False),
    "useoutcombat": ("with nobody around", False, False),
}


def _cone(mid: float, cy: float, half: float, cls: str = "fig-grid-stroke") -> str:
    """The bot's cone, opening downward toward you."""
    reach = 54.0
    dx = reach * math.tan(math.radians(half))
    return (f'<path d="M{mid} {cy - 26}L{mid - dx:.1f} {cy + 28}L{mid + dx:.1f} {cy + 28}Z" '
            f'class="{cls}" stroke-width="1.8" stroke-dasharray="4 4" fill="none" '
            'opacity="0.75"/>')


def _pips(mid: float, cy: float, total: int, filled: int) -> list[str]:
    out = []
    span = (total - 1) * 26
    for pip in range(total):
        px = mid - span / 2 + pip * 26
        style = "fig-accent-fill" if pip < filled else "fig-grid-fill"
        out.append(f'<rect x="{px - 9}" y="{cy - 13}" width="18" height="26" rx="4" '
                   f'class="{style}" opacity="{1 if pip < filled else 0.45}"/>')
    return out


def _run(uid: str, side: int, letter: str, frames: list[tuple[float, float]]) -> list[str]:
    cls = f"aim-{uid}-{side}{letter}" if letter != "a" else f"aim-{uid}-{side}"
    return [keyframes(f"aim{uid}{letter}{side}", frames,
                      lambda p: f"translate({p[0]:.1f}px,{p[1]:.1f}px)"),
            f".{cls}{{animation-name:aim{uid}{letter}{side};animation-duration:{T}s;"
            "animation-timing-function:linear;animation-iteration-count:infinite}"]


def draw(kind: str, index: int, uid: str, side: int, strong: bool,
         mid: float, cy: float) -> tuple[list[str], list[str]]:
    body: list[str] = []
    css: list[str] = []
    cls = f"aim-{uid}-{side}"

    if kind in ("sampletarget", "sampleself"):
        # The bot does not aim late. It aims at an older guess, so the guess has to be drawn beside
        # the thing it is a guess about.
        line = cy + 4
        body.append(f'<path d="M{mid - 76} {line}H{mid + 76}" class="fig-grid-stroke" '
                    'stroke-width="2" opacity="0.6"/>')
        real = [(70 * math.sin(i / FRAMES * 6.28318), 0.0) for i in range(FRAMES + 1)]
        # A rare estimate holds its last reading for a long time, which is what leaves the guess
        # behind the truth.
        every = 3 if not strong else 16
        guess = [real[(i // every) * every] for i in range(FRAMES + 1)]
        if kind == "sampletarget":
            body.append(f'<g class="{cls}b"><circle cx="{mid}" cy="{line}" r="11" '
                        'class="fig-target"/></g>')
            body.append(f'<g class="{cls}"><circle cx="{mid}" cy="{line}" r="13" '
                        'class="fig-cool-stroke" stroke-width="2.4" stroke-dasharray="4 4" '
                        'fill="none"/></g>')
            note = "it aims at an old guess" if strong else "the guess keeps up"
        else:
            body.append(f'<g class="{cls}b">{crosshair("fig-ink-stroke", mid, line)}</g>')
            body.append(f'<g class="{cls}"><circle cx="{mid}" cy="{line}" r="13" '
                        'class="fig-cool-stroke" stroke-width="2.4" stroke-dasharray="4 4" '
                        'fill="none"/></g>')
            note = "stale idea of itself" if strong else "it knows where it is"
        css += _run(uid, side, "b", real)
        css += _run(uid, side, "a", guess)
        body.append(text(mid, cy + 48, note, "fig-muted", size=10, weight=600))

    elif kind in ("flickfov", "shootfov", "optimalcone", "aimgate"):
        # A cone out of the bot, and a target either inside it or not. Four different fields use
        # one, so each says what crossing the edge actually changes.
        half = 16.0 if not strong else 44.0
        inside = half > 30
        body.append(_cone(mid, cy - 6, half,
                          "fig-accent-stroke" if inside else "fig-grid-stroke"))
        body.append(f'<circle cx="{mid}" cy="{cy - 30}" r="11" class="fig-target"/>')
        body.append(crosshair("fig-ink-stroke", mid + 32, cy + 18))
        if kind == "flickfov":
            note = "it flicks to you" if inside else "you are outside it"
        elif kind == "shootfov":
            note = "it fires from here" if inside else "it holds fire"
        elif kind == "aimgate":
            note = "the ability is allowed" if inside else "not aimed close enough"
        else:
            note = "you are in its best cone" if inside else "outside, it aims worse"
        body.append(text(mid, cy + 48, note, "fig-muted", size=10, weight=600))

    elif kind == "flickspeed":
        body.append(f'<circle cx="{mid}" cy="{cy - 22}" r="12" class="fig-target"/>')
        frames = []
        for i in range(FRAMES + 1):
            u = i / FRAMES
            rate = 8.0 if strong else 1.1
            moved = smooth(min(1.0, max(0.0, (u - 0.08) * rate)))
            frames.append((-52 + 52 * moved, 34 - 56 * moved))
        body.append(f'<g class="{cls}">{crosshair("fig-ink-stroke", mid, cy)}</g>')
        css += _run(uid, side, "a", frames)
        body.append(text(mid, cy + 52, "it is already there" if strong
                         else "it is still arriving", "fig-muted", size=10, weight=600))

    elif kind in ("flickerror", "trackerror", "errorceiling"):
        # Where the bot's shots actually land. Error is the only thing stopping it being an aimbot,
        # so it is drawn as a group around you rather than as a number.
        body.append(crosshair("fig-ink-stroke", mid, cy))
        if kind == "errorceiling":
            spread = 46.0 if strong else 20.0
            body.append(f'<circle cx="{mid}" cy="{cy}" r="{spread}" class="fig-tense-stroke" '
                        'stroke-width="2.2" stroke-dasharray="5 4" fill="none"/>')
            note = "a loose ceiling" if strong else "clamped tight"
        else:
            spread = 40.0 if strong else 12.0
            note = ("wide misses" if strong else "near perfect") if kind == "flickerror" else (
                "it wanders off you" if strong else "it stays on you")
        marks = ((0.6, -0.5), (-0.8, 0.3), (0.2, 0.85), (-0.35, -0.75), (0.9, 0.2))
        for order, (fx, fy) in enumerate(marks):
            body.append(f'<circle cx="{mid + fx * spread:.1f}" cy="{cy + fy * spread:.1f}" '
                        'r="4" class="fig-accent-fill"/>')
        body.append(text(mid, cy + 54, note, "fig-muted", size=10, weight=600))

    elif kind == "trackspeed":
        # The bot following a moving target. A slow one trails; a fast one is glued to it.
        line = cy - 2
        body.append(f'<path d="M{mid - 76} {line}H{mid + 76}" class="fig-grid-stroke" '
                    'stroke-width="2" opacity="0.6"/>')
        real = [(70 * math.sin(i / FRAMES * 6.28318), 0.0) for i in range(FRAMES + 1)]
        lag = 1 if strong else 9
        follow = [real[max(0, i - lag)] for i in range(FRAMES + 1)]
        body.append(f'<g class="{cls}b"><circle cx="{mid}" cy="{line}" r="11" '
                    'class="fig-target"/></g>')
        body.append(f'<g class="{cls}">{crosshair("fig-ink-stroke", mid, line)}</g>')
        css += _run(uid, side, "b", real)
        css += _run(uid, side, "a", follow)
        body.append(text(mid, cy + 46, "glued to it" if strong else "it trails behind",
                         "fig-muted", size=10, weight=600))

    elif kind in ("desklimit", "recenter"):
        # A mousepad with a middle, and a cursor that has run out of desk.
        body.append(f'<rect x="{mid - 62}" y="{cy - 26}" width="124" height="52" rx="6" '
                    'class="fig-grid-stroke" stroke-width="1.8" fill="none"/>')
        allowed = 16.0 if not strong else 46.0
        body.append(f'<rect x="{mid - 58}" y="{cy - 22}" width="116" height="44" rx="5" '
                    'class="fig-tense-fill" opacity="0.14"/>')
        body.append(f'<rect x="{mid - allowed:.0f}" y="{cy - 22}" width="{allowed * 2:.0f}" '
                    'height="44" rx="5" class="fig-accent-fill" opacity="0.22"/>')
        if kind == "desklimit":
            frames = [(42 * math.sin(i / FRAMES * 6.28318), 0.0) for i in range(FRAMES + 1)]
            note = "a lot of desk" if strong else "it runs out early"
        else:
            # A lift and reset. The quick one has to be home by the freeze at 30% and the slow one
            # still at the edge, or both cells show a cursor somewhere in between.
            start, span = (0.06, 0.18) if not strong else (0.58, 0.3)
            frames = []
            for i in range(FRAMES + 1):
                u = i / FRAMES
                done = 0.0 if u < start else smooth(min(1.0, (u - start) / span))
                frames.append((42 * (1 - done), 0.0))
            note = "a slow reset" if strong else "back in the middle"
        body.append(f'<g class="{cls}">{crosshair("fig-ink-stroke", mid, cy)}</g>')
        css += _run(uid, side, "a", frames)
        body.append(text(mid, cy + 46, note, "fig-muted", size=10, weight=600))

    elif kind == "outerpenalty":
        # Two groups from the same bot: one taken inside its optimal cone, one outside it.
        for lane, (dx, spread, label) in enumerate(((-44, 8.0, "inside"),
                                                    (44, 30.0 if strong else 13.0, "outside"))):
            body.append(crosshair("fig-ink-stroke", mid + dx, cy - 4))
            for fx, fy in ((0.7, -0.4), (-0.6, 0.5), (0.1, 0.9), (-0.9, -0.2)):
                body.append(f'<circle cx="{mid + dx + fx * spread:.1f}" '
                            f'cy="{cy - 4 + fy * spread:.1f}" r="3.5" '
                            'class="fig-accent-fill"/>')
            body.append(text(mid + dx, cy + 34, label, "fig-muted", size=9, weight=600))
        body.append(text(mid, cy + 52, "the penalty bites" if strong else "barely a penalty",
                         "fig-muted", size=10, weight=600))

    elif kind == "aimoffset":
        body.append(f'<rect x="{mid - 16}" y="{cy - 30}" width="32" height="58" rx="10" '
                    'class="fig-target"/>')
        aim_y = cy + 16 if not strong else cy - 20
        body.append(crosshair("fig-ink-stroke", mid, aim_y))
        body.append(f'<path d="M{mid + 30} {cy - 20}V{cy + 16}" class="fig-grid-stroke" '
                    'stroke-width="1.4" stroke-dasharray="3 3"/>')
        body.append(text(mid, cy + 48, "it aims high" if strong else "it aims low",
                         "fig-muted", size=10, weight=600))

    elif kind in ("spreadtol", "distancespread"):
        # The bot waiting for its own spread to come inside what it will accept before firing.
        if kind == "spreadtol":
            ring = 20.0 if not strong else 44.0
            body.append(crosshair("fig-ink-stroke", mid, cy))
            body.append(f'<circle cx="{mid}" cy="{cy}" r="{ring}" class="fig-cool-stroke" '
                        'stroke-width="2.2" stroke-dasharray="5 4" fill="none"/>')
            body.append(f'<circle cx="{mid}" cy="{cy}" r="16" class="fig-accent-fill" '
                        'opacity="0.35"/>')
            note = "it fires anyway" if strong else "it waits for a tight one"
        else:
            for lane, (dx, radius, label) in enumerate(((-44, 12, "near"), (44, 30, "far"))):
                shown = radius if strong else 12
                body.append(crosshair("fig-ink-stroke", mid + dx, cy - 4))
                body.append(f'<circle cx="{mid + dx}" cy="{cy - 4}" r="{shown}" '
                            'class="fig-cool-stroke" stroke-width="2.2" stroke-dasharray="5 4" '
                            'fill="none"/>')
                body.append(text(mid + dx, cy + 38, label, "fig-muted", size=9, weight=600))
            note = "distance loosens it" if strong else "distance plays no part"
        body.append(text(mid, cy + 54, note, "fig-muted", size=10, weight=600))

    elif kind in ("chargebar", "chargespawn"):
        total = 2 if not strong else 4
        if kind == "chargebar":
            body += _pips(mid, cy, total, total)
            note = f"{total} charges at most"
        else:
            total = 4
            ready = 1 if not strong else 4
            body += _pips(mid, cy, total, ready)
            note = f"{ready} ready at spawn"
        body.append(text(mid, cy + 40, note, "fig-muted", size=10, weight=600))

    elif kind in ("chargerefill", "refund"):
        body += _pips(mid, cy - 4, 3, 1)
        px = mid + 26
        body.append(f'<rect x="{px - 9}" y="{cy - 17}" width="18" height="26" rx="4" '
                    f'class="fig-accent-fill {cls}" style="transform-box:fill-box;'
                    'transform-origin:bottom center"/>')
        if kind == "chargerefill":
            arrive = 0.2 if strong else 0.8
            note = "it comes back fast" if strong else "a long wait"
        else:
            arrive = 0.2 if strong else 2.0
            body.append(f'<path d="M{mid - 64} {cy - 16}l16 16M{mid - 48} {cy - 16}l-16 16" '
                        'class="fig-muted-stroke" stroke-width="2.6" stroke-linecap="round"/>')
            note = "the kill refunds one" if strong else "a kill refunds nothing"
        pct = min(100.0, arrive * 100)
        css.append(f"@keyframes aim{uid}a{side}{{0%{{transform:scaleY(0)}}"
                   f"{max(0.0, pct - 6):.0f}%{{transform:scaleY(0)}}"
                   f"{pct:.0f}%{{transform:scaleY(1)}}100%{{transform:scaleY(1)}}}}")
        css.append(f".{cls}{{animation-name:aim{uid}a{side};animation-duration:{T}s;"
                   "animation-iteration-count:infinite}")
        body.append(text(mid, cy + 40, note, "fig-muted", size=10, weight=600))

    elif kind == "holduse":
        body.append(f'<path d="M{mid - 74} {cy + 4}H{mid + 74}" class="fig-grid-stroke" '
                    'stroke-width="1.6" opacity="0.6"/>')
        presses = ((0.0, 0.85),) if strong else ((0.0, 0.1), (0.35, 0.45), (0.7, 0.8))
        for start, end in presses:
            hx = mid - 74 + 148 * start
            body.append(f'<rect x="{hx:.1f}" y="{cy - 5}" width="{148 * (end - start):.1f}" '
                        'height="18" rx="4" class="fig-accent-fill"/>')
        uses = 5 if strong else 3
        for use in range(uses):
            ux = mid - 62 + use * (124 / max(1, uses - 1))
            body.append(f'<circle cx="{ux:.1f}" cy="{cy - 22}" r="4" class="fig-tense-fill"/>')
        body.append(text(mid, cy + 42, "one hold, many uses" if strong
                         else "one press, one use", "fig-muted", size=10, weight=600))

    elif kind in ("blockattack", "blockwhenattack"):
        # An attack, and the window after it where the ability is not available.
        body.append(f'<path d="M{mid - 74} {cy + 6}H{mid + 74}" class="fig-grid-stroke" '
                    'stroke-width="1.6" opacity="0.6"/>')
        body.append(f'<path d="M{mid - 60} {cy - 16}V{cy + 16}" class="fig-tense-stroke" '
                    'stroke-width="3"/>')
        body.append(text(mid - 60, cy - 24, "attack", "fig-muted", size=9, weight=600))
        blocked = 0.28 if not strong else 0.86
        body.append(f'<rect x="{mid - 60}" y="{cy - 4}" width="{134 * blocked:.0f}" '
                    'height="20" rx="4" class="fig-grid-fill" opacity="0.75"/>')
        if kind == "blockwhenattack":
            note = "blocked while attacking" if strong else "usable either way"
        else:
            note = "a long block" if strong else "a short one"
        body.append(text(mid, cy + 44, note, "fig-muted", size=10, weight=600))

    elif kind in WHERE:
        what, floor, airborne = WHERE[kind]
        base = cy + 26
        if floor:
            body.append(f'<path d="M{mid - 70} {base}H{mid + 70}" class="fig-grid-stroke" '
                        'stroke-width="2"/>')
        body.append(f'<circle cx="{mid - 26}" cy="{base - (34 if airborne else 14)}" r="13" '
                    'class="fig-target"/>')
        if kind == "usecombat":
            body.append(crosshair("fig-ink-stroke", mid + 40, cy - 6))
        elif kind == "useoutcombat":
            body.append(f'<circle cx="{mid + 40}" cy="{cy - 6}" r="12" class="fig-grid-stroke" '
                        'stroke-width="1.6" stroke-dasharray="3 4" fill="none" opacity="0.6"/>')
        if strong:
            spark_x = mid - 26 if not floor else mid + 34
            rays = "".join(f'M{spark_x} {base - 26}l{13 * math.cos(r * 1.0472):.1f} '
                           f'{13 * math.sin(r * 1.0472):.1f}' for r in range(6))
            body.append(f'<path d="{rays}" class="fig-accent-stroke" stroke-width="2.6" '
                        'stroke-linecap="round"/>')
        body.append(text(mid, cy + 50, f"it uses it {what}" if strong
                         else f"never {what}", "fig-muted", size=10, weight=600))

    elif kind in ("selfhealth", "targethealth"):
        # A health bar with the band the ability is allowed in, and where health actually sits.
        whose = "its own" if kind == "selfhealth" else "yours"
        body.append(text(mid, cy - 22, f"health, {whose}", "fig-muted", size=9, weight=600))
        body.append(f'<rect x="{mid - 74}" y="{cy - 12}" width="148" height="22" rx="5" '
                    'class="fig-grid-fill" opacity="0.45"/>')
        lo, hi = (0.0, 0.35) if not strong else (0.0, 0.95)
        body.append(f'<rect x="{mid - 74 + 148 * lo:.0f}" y="{cy - 12}" '
                    f'width="{148 * (hi - lo):.0f}" height="22" rx="5" '
                    'class="fig-accent-fill" opacity="0.3"/>')
        frames = [(148 * (0.08 + 0.84 * abs(math.sin(i / FRAMES * 3.14159))), 0.0)
                  for i in range(FRAMES + 1)]
        body.append(f'<g class="{cls}"><path d="M{mid - 74} {cy - 20}V{cy + 18}" '
                    'class="fig-tense-stroke" stroke-width="2.6"/></g>')
        css += _run(uid, side, "a", frames)
        body.append(text(mid, cy + 40, "allowed at almost any health" if strong
                         else "only allowed when low", "fig-muted", size=10, weight=600))

    elif kind == "hurtbox":
        # A movement ability that damages what it passes through.
        body.append(f'<circle cx="{mid + 34}" cy="{cy - 4}" r="13" class="fig-target"/>')
        size = 14.0 if not strong else 34.0
        body.append(f'<g class="{cls}"><rect x="{mid - size:.0f}" y="{cy - 4 - size:.0f}" '
                    f'width="{size * 2:.0f}" height="{size * 2:.0f}" rx="5" '
                    'class="fig-tense-fill" opacity="0.4"/></g>')
        css += _run(uid, side, "a",
                    [(-58 + 116 * (i / FRAMES), 0.0) for i in range(FRAMES + 1)])
        body.append(text(mid, cy + 44, "a wide hurtbox" if strong else "it barely touches",
                         "fig-muted", size=10, weight=600))

    else:
        # Which inputs still work while the ability is running.
        for lane, label in enumerate(("move", "fire", "jump")):
            lx = mid - 62 + lane * 62
            allowed = not strong or lane == 0
            style = "fig-cool-fill" if allowed else "fig-grid-fill"
            body.append(f'<rect x="{lx - 22}" y="{cy - 22}" width="44" height="28" rx="5" '
                        f'class="{style}" opacity="{0.9 if allowed else 0.4}"/>')
            body.append(text(lx, cy + 10, label, "fig-muted", size=10, weight=600))
        body.append(text(mid, cy + 40, "most inputs locked out" if strong
                         else "everything still works", "fig-muted", size=10, weight=600))

    return body, css
