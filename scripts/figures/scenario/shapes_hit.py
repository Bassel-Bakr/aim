"""Shapes for the dodge and bot fields the first pass drew wrong.

Every shape here exists because a borrowed one lied. A damage reaction needs a shot in the picture,
a forward and back toggle needs depth rather than a sideways slide, a blocked check needs an
obstacle, and a switch that turns motion off needs a cell that actually holds still.

The panel behind each cell runs from y 34 to y 136, so nothing may stray past cy - 42 or cy + 60.
"""
import math

from figure_kit import crosshair, keyframes, smooth, text

T = 4.0
FRAMES = 48
HIT = 0.26  # where in the loop the shot lands, just before the reduced-motion freeze at 30%
KINDS = ("hit", "hitdepth", "ignorehit", "threshold", "decay", "bias", "depth", "depthrate",
         "wall", "variance", "jumpvary", "crouchvary", "notarget", "botaim", "botfire", "altinput", "vanish", "strafeon",
         "biasleft",
         "firstturn", "everyspawn", "noscore", "swapout", "respawnwait")


def _spark(uid: str, side: int, cx: float, cy: float, at: float) -> tuple[str, list[str]]:
    """A brief burst where the shot lands, so the reaction has a visible cause."""
    cls = f"aim-{uid}-{side}spark"
    body = (f'<circle cx="{cx:.1f}" cy="{cy}" r="18" class="fig-tense-stroke {cls}" '
            'stroke-width="3" fill="none" opacity="0"/>')
    pct = at * 100
    css = [f"@keyframes aim{uid}h{side}{{0%{{opacity:0}}{max(0.0, pct - 2):.1f}%{{opacity:0}}"
           f"{pct:.1f}%{{opacity:0.9}}{min(100.0, pct + 9):.1f}%{{opacity:0}}100%{{opacity:0}}}}",
           f".{cls}{{animation-name:aim{uid}h{side};animation-duration:{T}s;"
           "animation-iteration-count:infinite}"]
    return body, css


def _shotline(uid: str, side: int, x0: float, y0: float, x1: float, y1: float,
              at: float) -> tuple[str, list[str]]:
    """The shot itself, on its way in. Without it the burst has no source."""
    cls = f"aim-{uid}-{side}shot"
    body = (f'<path d="M{x0:.1f} {y0}L{x1:.1f} {y1}" class="fig-tense-stroke {cls}" '
            'stroke-width="2" stroke-dasharray="6 5" opacity="0"/>')
    pct = at * 100
    css = [f"@keyframes aim{uid}t{side}{{0%{{opacity:0}}{max(0.0, pct - 10):.1f}%{{opacity:0}}"
           f"{max(0.0, pct - 4):.1f}%{{opacity:0.85}}{pct:.1f}%{{opacity:0.85}}"
           f"{min(100.0, pct + 5):.1f}%{{opacity:0}}100%{{opacity:0}}}}",
           f".{cls}{{animation-name:aim{uid}t{side};animation-duration:{T}s;"
           "animation-iteration-count:infinite}"]
    return body, css


def _slide(uid: str, side: int, letter: str, frames: list[tuple[float, float]]) -> list[str]:
    cls = f"aim-{uid}-{side}"
    return [keyframes(f"aim{uid}{letter}{side}", frames,
                      lambda p: f"translate({p[0]:.1f}px,{p[1]:.1f}px)"),
            f".{cls}{{animation-name:aim{uid}{letter}{side};animation-duration:{T}s;"
            "animation-timing-function:linear;animation-iteration-count:infinite}"]


def draw(kind: str, index: int, uid: str, side: int, strong: bool,
         mid: float, cy: float) -> tuple[list[str], list[str]]:
    body: list[str] = []
    css: list[str] = []
    cls = f"aim-{uid}-{side}"

    if kind in ("hit", "hitdepth"):
        # A shot lands partway through the loop. The question is only whether the bot's own motion
        # changes at that instant, so the shot has to be on screen for either answer to mean
        # anything.
        line = cy - 2
        if kind == "hit":
            if strong:
                frames = []
                turn = round(FRAMES * HIT)
                swing = round(FRAMES * 0.22)
                for i in range(turn):
                    frames.append((-62 + 112 * smooth(i / turn), 0.0))
                for i in range(swing):
                    frames.append((50 - 112 * smooth(i / swing), 0.0))
                for i in range(FRAMES - turn - swing + 1):
                    frames.append((-62 + 112 * smooth(i / (FRAMES - turn - swing)), 0.0))
            else:
                frames = [(70 * math.sin(i / FRAMES * 6.28318), 0.0)
                          for i in range(FRAMES + 1)]
            body.append(f'<path d="M{mid - 76} {line}H{mid + 76}" class="fig-grid-stroke" '
                        'stroke-width="3" stroke-linecap="round" opacity="0.5"/>')
            body.append(f'<g class="{cls}"><circle cx="{mid}" cy="{line}" r="11" '
                        'class="fig-target"/></g>')
            css += _slide(uid, side, "a", frames)
            land = frames[round(FRAMES * HIT)][0]
            note = "the hit swaps it" if strong else "the hit changes nothing"
        else:
            # Depth, not a slide: the bot is coming at you or backing off, and a hit either
            # reverses that or does not.
            if strong:
                # It has to be visibly smaller by the freeze at 30%, so the retreat is quick and
                # the slow part is the approach that follows it.
                scales = []
                turn = round(FRAMES * HIT)
                drop = round(FRAMES * 0.18)
                for i in range(turn):
                    scales.append(0.7 + 0.65 * smooth(i / turn))
                for i in range(drop):
                    scales.append(1.35 - 0.65 * smooth(i / drop))
                for i in range(FRAMES - turn - drop + 1):
                    scales.append(0.7 + 0.65 * smooth(i / (FRAMES - turn - drop)))
            else:
                scales = [1.0 + 0.35 * math.sin(i / FRAMES * 6.28318)
                          for i in range(FRAMES + 1)]
            body.append(f'<circle cx="{mid}" cy="{line}" r="21" '
                        'class="fig-grid-stroke" stroke-width="1.4" stroke-dasharray="3 5" '
                        'fill="none" opacity="0.6"/>')
            body.append(f'<g class="{cls}" style="transform-box:fill-box;'
                        'transform-origin:center">'
                        f'<circle cx="{mid}" cy="{line}" r="15" class="fig-target"/></g>')
            css.append(keyframes(f"aim{uid}a{side}", scales, lambda s: f"scale({s:.3f})"))
            css.append(f".{cls}{{animation-name:aim{uid}a{side};animation-duration:{T}s;"
                       "animation-timing-function:linear;animation-iteration-count:infinite}")
            land = 0.0
            note = "reverses its approach" if strong else "holds its depth"
        mark, rules = _spark(uid, side, mid + land, line, HIT)
        body.append(mark)
        css += rules
        shot, rules = _shotline(uid, side, mid, cy + 32, mid + land, line + 12, HIT)
        body.append(shot)
        css += rules
        body.append(crosshair("fig-ink-stroke", mid, cy + 36))
        body.append(text(mid, cy + 56, note, "fig-muted", size=10, weight=600))

    elif kind == "ignorehit":
        # Four shots along a timeline, and a reaction mark under the ones that produced one.
        body.append(f'<path d="M{mid - 78} {cy} H{mid + 78}" class="fig-grid-stroke" '
                    'stroke-width="2"/>')
        reacts = (True, False, False, True) if strong else (True, True, True, True)
        for slot, answered in enumerate(reacts):
            sx = mid - 78 + 52 * slot + 26
            body.append(f'<path d="M{sx} {cy - 22}V{cy - 4}" class="fig-tense-stroke" '
                        'stroke-width="2.6"/>')
            if answered:
                body.append(f'<path d="M{sx} {cy + 4}V{cy + 22}" class="fig-accent-stroke" '
                            'stroke-width="2.6"/>')
            else:
                body.append(f'<circle cx="{sx}" cy="{cy + 13}" r="3" class="fig-grid-fill"/>')
        body.append(f'<g class="{cls}"><circle cx="{mid - 78}" cy="{cy}" r="7" '
                    'class="fig-target"/></g>')
        css += _slide(uid, side, "a", [(156 * i / FRAMES, 0.0) for i in range(FRAMES + 1)])
        body.append(text(mid, cy + 44, "hits above, reactions below", "fig-muted",
                         size=10, weight=600))

    elif kind in ("threshold", "decay"):
        # Damage accumulating in a bar, against the line it has to clear. Threshold moves the line;
        # reset time decides whether what is in the bar survives to the next hit.
        top, tall = cy - 22, 34
        body.append(f'<rect x="{mid - 74}" y="{top}" width="148" height="{tall}" rx="5" '
                    'class="fig-grid-fill" opacity="0.4"/>')
        levels = (0.25, 0.5, 0.75, 1.0)
        if kind == "threshold":
            line = 0.85 if strong else 0.3
            widths = []
            for i in range(FRAMES + 1):
                widths.append(levels[min(3, int(i / FRAMES * 4))])
            note = "needs several hits" if strong else "one hit clears it"
        else:
            line = 0.55
            widths = []
            for i in range(FRAMES + 1):
                phase = (i / FRAMES * 4) % 1.0
                step = levels[min(3, int(i / FRAMES * 4))]
                widths.append(step if strong else 0.25 * (1.0 - smooth(phase)) + 0.02)
            note = "it keeps the total" if strong else "it drains between hits"
        body.append(f'<rect x="{mid - 74}" y="{top}" width="148" height="{tall}" rx="5" '
                    f'class="fig-tense-fill {cls}" style="transform-box:fill-box;'
                    'transform-origin:left center"/>')
        css.append(keyframes(f"aim{uid}a{side}", widths, lambda w: f"scaleX({w:.3f})"))
        css.append(f".{cls}{{animation-name:aim{uid}a{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")
        lx = mid - 74 + 148 * line
        body.append(f'<path d="M{lx:.1f} {top - 6}V{top + tall + 6}" '
                    'class="fig-accent-stroke" stroke-width="2.4"/>')
        body.append(text(mid, cy + 40, note, "fig-muted", size=10, weight=600))

    elif kind in ("bias", "biasleft"):
        # One side is held longer than the other, which is the whole point of the multiplier. An
        # even track would show nothing at all, and the band has to sit on the side the field
        # names: the left multiplier lengthens left strafes, not right ones.
        way = -1.0 if kind == "biasleft" else 1.0
        body.append(f'<path d="M{mid - 74} {cy}H{mid + 74}" class="fig-grid-stroke" '
                    'stroke-width="4" stroke-linecap="round" opacity="0.5"/>')
        body.append(f'<path d="M{mid} {cy - 20}V{cy + 20}" class="fig-grid-stroke" '
                    'stroke-width="1.6" opacity="0.7"/>')
        if strong:
            band = mid if way > 0 else mid - 74
            body.append(f'<rect x="{band}" y="{cy - 14}" width="74" height="28" rx="6" '
                        'class="fig-accent-fill" opacity="0.26"/>')
            legs = ((0.18, -74.0 * way, 74.0 * way), (0.52, 74.0 * way, 74.0 * way),
                    (0.18, 74.0 * way, -74.0 * way), (0.12, -74.0 * way, -74.0 * way))
        else:
            legs = ((0.3, -74.0, 74.0), (0.2, 74.0, 74.0), (0.3, 74.0, -74.0),
                    (0.2, -74.0, -74.0))
        frames = []
        for share, start, end in legs:
            steps = max(2, round(FRAMES * share))
            frames += [(start + (end - start) * smooth(i / steps), 0.0) for i in range(steps)]
        frames.append((frames[0][0], 0.0))
        body.append(f'<g class="{cls}"><circle cx="{mid}" cy="{cy}" r="11" '
                    'class="fig-target"/></g>')
        css += _slide(uid, side, "a", frames)
        side_word = "left" if way < 0 else "right"
        body.append(text(mid, cy + 40, f"it lives on the {side_word}" if strong
                         else "even either way", "fig-muted", size=10, weight=600))

    elif kind in ("depth", "depthrate"):
        # Toward and away, which changes how big the target is. Drawing that as a sideways slide
        # was the original mistake.
        if kind == "depth":
            span = 0.0 if not strong else 0.42
            cycles = 1
            note = "it comes in and backs off" if strong else "it holds its distance"
        else:
            span = 0.36
            cycles = 3 if not strong else 1
            note = "one long approach" if strong else "quick reversals"
        scales = [1.0 + span * math.sin(i / FRAMES * 6.28318 * cycles)
                  for i in range(FRAMES + 1)]
        body.append(f'<circle cx="{mid}" cy="{cy - 4}" r="30" class="fig-grid-stroke" '
                    'stroke-width="1.4" stroke-dasharray="3 5" fill="none" opacity="0.6"/>')
        body.append(f'<g class="{cls}" style="transform-box:fill-box;transform-origin:center">'
                    f'<circle cx="{mid}" cy="{cy - 4}" r="18" class="fig-target"/></g>')
        css.append(keyframes(f"aim{uid}a{side}", scales, lambda s: f"scale({s:.3f})"))
        css.append(f".{cls}{{animation-name:aim{uid}a{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")
        body.append(crosshair("fig-ink-stroke", mid, cy + 30))
        body.append(text(mid, cy + 54, note, "fig-muted", size=10, weight=600))

    elif kind == "wall":
        wall = mid + 52
        body.append(f'<rect x="{wall}" y="{cy - 30}" width="16" height="60" '
                    'class="fig-grid-fill"/>')
        body.append(f'<path d="M{mid - 76} {cy}H{wall}" class="fig-grid-stroke" '
                    'stroke-width="3" stroke-linecap="round" opacity="0.5"/>')
        press = 0.3 if strong else 0.3
        frames = []
        steps = max(2, round(FRAMES * press))
        for i in range(steps):
            frames.append((-76 + 113 * smooth(i / steps), 0.0))
        if strong:
            hold = round(FRAMES * 0.12)
            frames += [(37.0, 0.0)] * hold
            back = FRAMES - steps - hold + 1
            frames += [(37 - 113 * smooth(i / back), 0.0) for i in range(back)]
            note = "it turns around"
        else:
            frames += [(37.0, 0.0)] * (FRAMES - steps + 1)
            note = "it grinds along it"
        body.append(f'<g class="{cls}"><circle cx="{mid}" cy="{cy}" r="11" '
                    'class="fig-target"/></g>')
        css += _slide(uid, side, "a", frames)
        body.append(text(mid, cy + 42, note, "fig-muted", size=10, weight=600))

    elif kind == "variance":
        # Three stretches of time on one line. Nine fields use this and every one of them is a
        # duration, so it has to read as duration: an arc would say the target jumped.
        spans: tuple[float, ...] = ((1.0, 1.0, 1.0) if not strong else (0.35, 1.5, 0.75))
        body.append(f'<path d="M{mid - 76} {cy + 22}H{mid + 76}" class="fig-grid-stroke" '
                    'stroke-width="1.6" opacity="0.6"/>')
        at = mid - 76
        for rep, span in enumerate(spans):
            width = 140 * span / sum(spans) - 8
            body.append(f'<rect x="{at:.1f}" y="{cy - 10}" width="{width:.1f}" height="22" '
                        'rx="5" class="fig-cool-fill" opacity="0.85"/>')
            body.append(f'<path d="M{at:.1f} {cy + 14}V{cy + 30}" class="fig-grid-stroke" '
                        'stroke-width="1.4"/>')
            at += width + 8
        body.append(f'<path d="M{at:.1f} {cy + 14}V{cy + 30}" class="fig-grid-stroke" '
                    'stroke-width="1.4"/>')
        body.append(text(mid, cy + 48, "no two the same" if strong else "every one the same",
                         "fig-muted", size=10, weight=600))

    elif kind in ("jumpvary", "crouchvary"):
        # The two that are not durations: how high each jump goes, and how far each crouch dips.
        sizes: tuple[float, ...] = ((28.0, 28.0, 28.0) if not strong else (13.0, 38.0, 23.0))
        floor = cy + 26 if kind == "jumpvary" else cy - 24
        body.append(f'<path d="M{mid - 78} {floor}H{mid + 78}" class="fig-grid-stroke" '
                    'stroke-width="2"/>')
        way = -1.0 if kind == "jumpvary" else 1.0
        for rep, size in enumerate(sizes):
            hx = mid - 52 + rep * 52
            body.append(f'<path d="M{hx - 16} {floor}Q{hx} {floor + way * size * 2:.1f} '
                        f'{hx + 16} {floor}" class="fig-grid-stroke" stroke-width="1.4" '
                        'stroke-dasharray="3 4" fill="none" opacity="0.55"/>')
        frames = []
        for rep, size in enumerate(sizes):
            hx = -52.0 + rep * 52
            steps = FRAMES // 3
            for i in range(steps):
                u = i / steps
                frames.append((hx - 16 + 32 * u, way * size * 4 * u * (1 - u)))
        frames.append((frames[0][0], frames[0][1]))
        body.append(f'<g class="{cls}"><circle cx="{mid}" cy="{floor}" r="9" '
                    'class="fig-target"/></g>')
        css += _slide(uid, side, "a", frames)
        label = "height" if kind == "jumpvary" else "depth"
        body.append(text(mid, cy + 50 if kind == "jumpvary" else cy + 44,
                         f"every {label} differs" if strong else f"every {label} matches",
                         "fig-muted", size=10, weight=600))

    elif kind == "notarget":
        # Two other bots looking for something to shoot. They have to end up on this one or drift
        # away from it: an earlier version had them cross over, which reads as neither.
        body.append(f'<circle cx="{mid}" cy="{cy - 4}" r="16" class="fig-target"/>')
        for lane, dx in enumerate((-64, 64)):
            letter = "l" if lane == 0 else "r"
            sub = f"{cls}{letter}"
            body.append(f'<g class="{sub}">'
                        f'{crosshair("fig-ink-stroke", mid + dx, cy - 4)}</g>')
            # Travel is measured from where the crosshair is drawn, so it ends on the bot when
            # this one is targetable and further out when it is not.
            shift = dx * 0.3 if strong else -dx
            frames = [(shift * smooth(min(1.0, i / FRAMES * 2)), 0.0)
                      for i in range(FRAMES + 1)]
            css.append(keyframes(f"aim{uid}{letter}{side}", frames,
                                 lambda p: f"translate({p[0]:.1f}px,0)"))
            css.append(f".{sub}{{animation-name:aim{uid}{letter}{side};"
                       f"animation-duration:{T}s;animation-timing-function:linear;"
                       "animation-iteration-count:infinite}")
        body.append(text(mid, cy + 40, "nothing settles on it" if strong
                         else "they settle on it", "fig-muted", size=10, weight=600))

    elif kind in ("botaim", "botfire"):
        # The bot's gaze, and whether anything comes out of it. Two different switches, so two
        # shapes: one turns the tracking off, the other keeps it and holds the trigger.
        reach = 34.0
        body.append(f'<circle cx="{mid}" cy="{cy - 18}" r="13" class="fig-target"/>')
        tracks = (not strong) if kind == "botaim" else True
        travel = [(58 * math.sin(i / FRAMES * 6.28318), 0.0) for i in range(FRAMES + 1)]
        body.append(f'<g class="{cls}y">'
                    f'{crosshair("fig-ink-stroke", mid, cy + 34)}</g>')
        css += [keyframes(f"aim{uid}y{side}", travel,
                          lambda p: f"translate({p[0]:.1f}px,0)"),
                f".{cls}y{{animation-name:aim{uid}y{side};animation-duration:{T}s;"
                "animation-timing-function:linear;animation-iteration-count:infinite}"]
        # The shot has to leave along the gaze, so it lives inside the group that rotates. Drawn
        # outside it, the bot aimed at you and fired at the floor.
        barrel = [f'<path d="M{mid} {cy - 18}V{cy + 16}" class="fig-cool-stroke" '
                  'stroke-width="2.4"/>']
        if kind == "botfire" and strong:
            shot, rules = _shotline(uid, side, mid, cy + 18, mid, cy + 40, 0.30)
            barrel.append(shot)
            css += rules
        body.append(f'<g class="{cls}g" style="transform-box:fill-box;'
                    'transform-origin:top center">' + "".join(barrel) + '</g>')
        if tracks:
            # Positive rotation is clockwise in SVG, so a downward line tracking a target to the
            # right needs a negative angle.
            angles = [-math.degrees(math.atan2(p[0], reach)) for p in travel]
        else:
            angles = [0.0] * (FRAMES + 1)
        css.append(keyframes(f"aim{uid}g{side}", angles, lambda a: f"rotate({a:.2f}deg)"))
        css.append(f".{cls}g{{animation-name:aim{uid}g{side};animation-duration:{T}s;"
                   "animation-timing-function:linear;animation-iteration-count:infinite}")
        if kind == "botfire" and strong:
            note = "it aims and fires"
        elif kind == "botfire":
            note = "it aims, fires nothing"
        else:
            note = "it looks straight ahead" if strong else "it tracks you"
        body.append(text(mid, cy + 56, note, "fig-muted", size=10, weight=600))

    elif kind == "altinput":
        # Two keys on a timeline. Unchecked, each has its own frequency; checked, the bot holds one
        # then the other, forever.
        for lane, (label, dy) in enumerate((("jump", -18), ("crouch", 14))):
            body.append(text(mid - 78, cy + dy + 4, label, "fig-muted", anchor="start",
                             size=9, weight=600))
            body.append(f'<path d="M{mid - 34} {cy + dy}H{mid + 78}" class="fig-grid-stroke" '
                        'stroke-width="1.6" opacity="0.6"/>')
            holds: tuple[tuple[float, float], ...]
            if strong:
                holds = ((0.0, 0.5),) if lane == 0 else ((0.5, 1.0),)
            else:
                holds = ((0.05, 0.2), (0.55, 0.68)) if lane == 0 else ((0.3, 0.38),)
            for start, end in holds:
                hx = mid - 34 + 112 * start
                body.append(f'<rect x="{hx:.1f}" y="{cy + dy - 7}" '
                            f'width="{112 * (end - start):.1f}" height="14" rx="4" '
                            'class="fig-accent-fill"/>')
        frames = [(112 * i / FRAMES, 0.0) for i in range(FRAMES + 1)]
        body.append(f'<g class="{cls}"><path d="M{mid - 34} {cy - 30}V{cy + 26}" '
                    'class="fig-tense-stroke" stroke-width="1.8"/></g>')
        css += _slide(uid, side, "a", frames)
        body.append(text(mid, cy + 48, "strictly alternating" if strong
                         else "each on its own", "fig-muted", size=10, weight=600))

    elif kind == "vanish":
        body.append(crosshair("fig-ink-stroke", mid - 56, cy + 6))
        body.append(f'<path d="M{mid - 42} {cy + 6}H{mid + 14}" class="fig-cool-stroke" '
                    'stroke-width="1.8" stroke-dasharray="4 4" opacity="0.7"/>')
        body.append(f'<circle cx="{mid + 34}" cy="{cy + 6}" r="16" '
                    f'class="fig-target {cls}"/>')
        if strong:
            css.append(f"@keyframes aim{uid}a{side}{{0%{{opacity:1}}20%{{opacity:1}}"
                       "26%{opacity:0}100%{opacity:0}}")
        else:
            css.append(f"@keyframes aim{uid}a{side}{{0%{{opacity:1}}100%{{opacity:1}}}}")
        css.append(f".{cls}{{animation-name:aim{uid}a{side};animation-duration:{T}s;"
                   "animation-iteration-count:infinite}")
        body.append(text(mid, cy + 44, "it kills itself on sight" if strong
                         else "it stays and fights", "fig-muted", size=10, weight=600))

    elif kind == "noscore":
        # Your own shot landing, and whether anything comes back for it. Untargetable is about
        # other bots; this one is about your score, so the score is what has to be on screen.
        body.append(f'<circle cx="{mid}" cy="{cy - 6}" r="16" class="fig-target"/>')
        shot, rules = _shotline(uid, side, mid, cy + 30, mid, cy + 8, 0.24)
        body.append(shot)
        css += rules
        mark, rules = _spark(uid, side, mid, cy - 6, 0.26)
        body.append(mark)
        css += rules
        if not strong:
            body.append(text(mid + 34, cy - 14, "+100", f"fig-accent-text {cls}",
                             size=12, weight=700))
            css.append(f"@keyframes aim{uid}a{side}{{0%{{opacity:0}}24%{{opacity:0}}"
                       "28%{opacity:1}88%{opacity:1}94%{opacity:0}100%{opacity:0}}")
        else:
            body.append(text(mid + 34, cy - 14, "0", f"fig-muted {cls}", size=12, weight=700))
            css.append(f"@keyframes aim{uid}a{side}{{0%{{opacity:0.5}}100%{{opacity:0.5}}}}")
        css.append(f".{cls}{{animation-name:aim{uid}a{side};animation-duration:{T}s;"
                   "animation-iteration-count:infinite}")
        body.append(crosshair("fig-ink-stroke", mid, cy + 34))
        body.append(text(mid, cy + 56, "the hit pays nothing" if strong else "the hit scores",
                         "fig-muted", size=10, weight=600))

    elif kind == "swapout":
        # A hit lands and the bot leaves this dodge profile for another one, which is a change of
        # pattern rather than a death.
        body.append(f'<path d="M{mid - 76} {cy - 14}H{mid + 76}" class="fig-grid-stroke" '
                    'stroke-width="3" stroke-linecap="round" opacity="0.45"/>')
        if strong:
            body.append(f'<path d="M{mid - 40} {cy + 24}H{mid + 40}" '
                        'class="fig-cool-stroke" stroke-width="3" stroke-linecap="round" '
                        'opacity="0.6"/>')
            body.append(text(mid - 86, cy + 28, "B", "fig-muted", size=11, weight=700))
            frames = []
            turn = round(FRAMES * HIT)
            for i in range(turn):
                frames.append((-62 + 112 * smooth(i / turn), 0.0))
            for i in range(FRAMES - turn + 1):
                u = i / (FRAMES - turn)
                frames.append((50 - 90 * smooth(u), 38 * smooth(min(1.0, u * 6.0))))
            note = "it leaves for another profile"
        else:
            frames = [(70 * math.sin(i / FRAMES * 6.28318), 0.0) for i in range(FRAMES + 1)]
            note = "it stays on this one"
        body.append(text(mid - 86, cy - 10, "A", "fig-muted", size=11, weight=700))
        body.append(f'<g class="{cls}"><circle cx="{mid}" cy="{cy - 14}" r="11" '
                    'class="fig-target"/></g>')
        css += _slide(uid, side, "a", frames)
        mark, rules = _spark(uid, side, mid + frames[round(FRAMES * HIT)][0], cy - 14, HIT)
        body.append(mark)
        css += rules
        body.append(text(mid, cy + 56, note, "fig-muted", size=10, weight=600))

    elif kind == "respawnwait":
        # Death, then the gap before the target is back. The field is that gap, not a spawn point.
        body.append(f'<circle cx="{mid}" cy="{cy - 4}" r="16" class="fig-target {cls}"/>')
        back = 62 if strong else 22
        css.append(f"@keyframes aim{uid}a{side}{{0%{{opacity:1}}12%{{opacity:1}}"
                   f"16%{{opacity:0}}{back}%{{opacity:0}}{back + 4}%{{opacity:1}}"
                   "100%{opacity:1}}")
        css.append(f".{cls}{{animation-name:aim{uid}a{side};animation-duration:{T}s;"
                   "animation-iteration-count:infinite}")
        body.append(f'<rect x="{mid - 74}" y="{cy + 26}" width="148" height="8" rx="4" '
                    'class="fig-grid-fill" opacity="0.5"/>')
        body.append(f'<rect x="{mid - 74 + 148 * 0.14:.1f}" y="{cy + 26}" '
                    f'width="{148 * (back - 14) / 100:.1f}" height="8" rx="4" '
                    'class="fig-accent-fill"/>')
        body.append(text(mid, cy + 52, "it waits the minimum" if strong
                         else "it comes straight back", "fig-muted", size=10, weight=600))

    elif kind == "strafeon":
        # The off cell has to be genuinely still, or the switch shows nothing.
        body.append(f'<path d="M{mid - 74} {cy}H{mid + 74}" class="fig-grid-stroke" '
                    'stroke-width="4" stroke-linecap="round" opacity="0.5"/>')
        frames = ([(74 * math.sin(i / FRAMES * 6.28318), 0.0) for i in range(FRAMES + 1)]
                  if strong else [(0.0, 0.0)] * (FRAMES + 1))
        body.append(f'<g class="{cls}"><circle cx="{mid}" cy="{cy}" r="11" '
                    'class="fig-target"/></g>')
        css += _slide(uid, side, "a", frames)
        body.append(text(mid, cy + 40, "it strafes" if strong else "it does not move",
                         "fig-muted", size=10, weight=600))

    elif kind == "firstturn":
        body.append(f'<path d="M{mid - 74} {cy}H{mid + 74}" class="fig-grid-stroke" '
                    'stroke-width="4" stroke-linecap="round" opacity="0.5"/>')
        body.append(f'<circle cx="{mid}" cy="{cy}" r="4" class="fig-grid-fill"/>')
        end = 66.0 if strong else -66.0
        frames = [(end * smooth(min(1.0, i / FRAMES * 1.6)), 0.0) for i in range(FRAMES + 1)]
        body.append(f'<g class="{cls}"><circle cx="{mid}" cy="{cy}" r="11" '
                    'class="fig-target"/></g>')
        css += _slide(uid, side, "a", frames)
        body.append(text(mid, cy + 40, "first move goes right" if strong
                         else "first move goes left", "fig-muted", size=10, weight=600))

    else:
        # Once at the start, or again on every respawn.
        for order in range(3):
            sx = mid - 62 + order * 62
            flagged = strong or order == 0
            fill = "fig-accent-fill" if flagged else "fig-grid-fill"
            body.append(f'<circle cx="{sx}" cy="{cy}" r="10" class="{fill}"/>')
            body.append(text(sx, cy + 26, f"spawn {order + 1}", "fig-muted", size=9, weight=600))
        body.append(text(mid, cy + 48, "applied every spawn" if strong
                         else "applied on the first only", "fig-muted", size=10, weight=600))

    return body, css
