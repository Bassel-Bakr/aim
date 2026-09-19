"""Shapes for health, respawn, knockback, visual effects and the last of the timers.

Thirty-five fields were still a marker on a track. Health is a bar that empties and refills,
respawn is the stretch between dying and standing up, knockback is a body being shoved, an effect
is something left on screen, and a timer is a stretch of a clock. None of them is a slider.

The panel behind each cell runs from y 34 to y 136, so nothing may stray past cy - 42 or cy + 60,
and every strip is frozen at 30% of its loop for readers with motion turned off.
"""
import math

from figure_kit import crosshair, keyframes, smooth, text

T = 4.0
FRAMES = 48
KINDS = ("hitpoints", "killheal", "regentick", "lifesteal", "ammodrop",
         "respawnmin", "respawnmax", "respawnanim", "spawnguard",
         "sharedcool", "startblock",
         "groundshove", "airshove", "flatshove", "rampslow", "stunfreeze", "tagdrag",
         "tracerlife", "tracerwidth", "traceorigin", "muzzlescale", "wallburst",
         "bodyburst", "decalmark",
         "chancetick", "usechance", "permitcheck", "weaponhold", "runlength", "endtally",
         "usegap", "abilityanswer")

# The three fields that pay health back, and where the health comes from.
HEAL = {
    "killheal": ("a kill", 0.18, 0.62),
    "regentick": ("every second", 0.08, 0.34),
    "lifesteal": ("damage you dealt", 0.12, 0.48),
}
# The clock fields: the label on the filled stretch, and how long it runs in each cell.
CLOCKS = {
    "respawnmin": ("cannot respawn yet", 0.18, 0.72, "back at once", "held down a while"),
    "respawnmax": ("your choice to wait", 0.24, 0.8, "forced up at once", "you may lie there"),
    "respawnanim": ("standing up", 0.16, 0.66, "control returns at once", "a long animation"),
    "spawnguard": ("cannot be hurt", 0.14, 0.7, "hittable at once", "safe for a while"),
    "startblock": ("abilities shut", 0.12, 0.74, "usable at once", "shut for a while"),
    "chancetick": ("waiting", 0.16, 0.72, "chance after chance", "long gaps between"),
    "permitcheck": ("same decision holds", 0.18, 0.76, "it rethinks often", "it rarely rethinks"),
    "weaponhold": ("this weapon out", 0.2, 0.82, "it swaps constantly", "it keeps one"),
    "runlength": ("the run", 0.28, 0.9, "a short run", "a long one"),
    "usegap": ("cannot use it", 0.14, 0.68, "back to back", "spaced out"),
    "stunfreeze": ("frozen", 0.14, 0.66, "a flinch", "a long freeze"),
    "tagdrag": ("slowed", 0.16, 0.72, "it shrugs it off", "it crawls a while"),
    "tracerlife": ("the trail on screen", 0.14, 0.7, "gone at once", "it lingers"),
}


def _clock(mid: float, cy: float, share: float, label: str, fill: str) -> list[str]:
    out = [f'<rect x="{mid - 74}" y="{cy - 10}" width="148" height="20" rx="5" '
           'class="fig-grid-fill" opacity="0.4"/>',
           f'<rect x="{mid - 74}" y="{cy - 10}" width="{148 * share:.0f}" height="20" rx="5" '
           f'class="{fill}" opacity="0.9"/>']
    if label:
        out.append(text(mid - 74 + 148 * share / 2, cy + 24, label, "fig-muted",
                        size=8, weight=600))
    return out


def _bar(mid: float, cy: float, share: float, fill: str = "fig-tense-fill") -> list[str]:
    return [f'<rect x="{mid - 70}" y="{cy - 9}" width="140" height="18" rx="5" '
            'class="fig-grid-fill" opacity="0.45"/>',
            f'<rect x="{mid - 70}" y="{cy - 9}" width="{140 * share:.0f}" height="18" rx="5" '
            f'class="{fill}"/>']


def draw(kind: str, index: int, uid: str, side: int, strong: bool,
         mid: float, cy: float) -> tuple[list[str], list[str]]:
    body: list[str] = []
    css: list[str] = []
    cls = f"aim-{uid}-{side}"

    if kind in CLOCKS:
        # One clock with the stretch this field owns filled in. Thirteen fields share it because
        # thirteen fields really are the same thing: a window during which something is true.
        label, low, high, lownote, highnote = CLOCKS[kind]
        share = high if strong else low
        fill = "fig-cool-fill" if kind in ("runlength", "tracerlife") else "fig-grid-fill"
        body += _clock(mid, cy - 6, share, label, fill)
        body.append(f'<path d="M{mid - 74 + 148 * share:.1f} {cy - 22}V{cy + 6}" '
                    'class="fig-accent-stroke" stroke-width="2.4"/>')
        body.append(text(mid, cy + 46, highnote if strong else lownote, "fig-muted",
                         size=10, weight=600))

    elif kind == "hitpoints":
        # How many shots the target soaks, drawn as the shots rather than as a number.
        shots = 1 if not strong else 5
        body += _bar(mid, cy - 12, 1.0)
        for shot in range(shots):
            sx = mid - 64 + shot * (128 / max(1, shots))
            body.append(f'<path d="M{sx:.0f} {cy + 10}V{cy + 26}" class="fig-tense-stroke" '
                        'stroke-width="2.6"/>')
        # No crosshair: the ticks already read as shots, and it landed on the caption.
        body.append(text(mid, cy + 46, "one shot and it drops" if not strong
                         else f"{shots} shots to drop it", "fig-muted", size=10, weight=600))

    elif kind in HEAL:
        # Health coming back, and what paid for it. The empty part of the bar is the point.
        what, low, high = HEAL[kind]
        back = high if strong else low
        body += _bar(mid, cy - 6, 0.35)
        body.append(f'<rect x="{mid - 70 + 140 * 0.35:.0f}" y="{cy - 15}" '
                    f'width="{140 * back:.0f}" height="18" rx="5" '
                    f'class="fig-cool-fill {cls}"/>')
        css.append(f"@keyframes aim{uid}a{side}{{0%{{opacity:0}}18%{{opacity:1}}"
                   "100%{opacity:1}}")
        css.append(f".{cls}{{opacity:0;animation-name:aim{uid}a{side};"
                   f"animation-duration:{T}s;animation-iteration-count:infinite}}")
        body.append(text(mid, cy + 18, f"from {what}", "fig-muted", size=8, weight=600))
        body.append(text(mid, cy + 44, "a trickle back" if not strong
                         else "a real top-up", "fig-muted", size=10, weight=600))

    elif kind == "ammodrop":
        # Rounds handed to whoever made the kill, which is a thing to put on a bot character.
        body.append(f'<path d="M{mid - 76} {cy - 18}l16 16M{mid - 60} {cy - 18}l-16 16" '
                    'class="fig-muted-stroke" stroke-width="2.6" stroke-linecap="round"/>')
        body.append(text(mid - 68, cy + 16, "it dies", "fig-muted", size=8, weight=600))
        given = 2 if not strong else 8
        for slot in range(given):
            sx = mid - 24 + slot * 15
            body.append(f'<rect x="{sx:.0f}" y="{cy - 18}" width="9" height="20" rx="2" '
                        f'class="fig-accent-fill {cls}" '
                        f'style="animation-delay:{slot * 0.1:.2f}s"/>')
        css.append(f"@keyframes aim{uid}a{side}{{0%{{opacity:0}}20%{{opacity:1}}"
                   "100%{opacity:1}}")
        css.append(f".{cls}{{opacity:0;animation-name:aim{uid}a{side};"
                   f"animation-duration:{T}s;animation-iteration-count:infinite}}")
        body.append(text(mid + 20, cy + 16, "to the killer", "fig-muted", size=8, weight=600))
        body.append(text(mid, cy + 44, f"{given} rounds" if strong else "a couple of rounds",
                         "fig-muted", size=10, weight=600))

    elif kind == "sharedcool":
        # Four ability slots wired to one timer, which is the whole point of a global cooldown.
        for slot in range(4):
            sx = mid - 66 + slot * 44
            body.append(f'<rect x="{sx:.0f}" y="{cy - 34}" width="30" height="24" rx="5" '
                        'class="fig-grid-fill" opacity="0.7"/>')
            body.append(f'<path d="M{sx + 15:.0f} {cy - 10}V{cy - 2}" '
                        'class="fig-grid-stroke" stroke-width="1.4"/>')
        share = 0.22 if not strong else 0.78
        body += _clock(mid, cy + 8, share, "all four locked", "fig-grid-fill")
        body.append(text(mid, cy + 52, "free again at once" if not strong
                         else "all four wait together", "fig-muted", size=10, weight=600))

    elif kind in ("groundshove", "airshove", "flatshove"):
        # A body being pushed by the hit that damaged it. The floor decides how far it goes, so
        # whether there is one is part of the field.
        floor = cy + 28
        if kind == "airshove":
            body.append(f'<path d="M{mid - 80} {floor}H{mid + 80}" class="fig-grid-stroke" '
                        'stroke-width="1.6" stroke-dasharray="5 5" opacity="0.5"/>')
            body.append(text(mid - 80, floor + 14, "airborne", "fig-muted", anchor="start",
                             size=8, weight=600))
            rest = floor - 34
        else:
            body.append(f'<path d="M{mid - 80} {floor}H{mid + 80}" class="fig-grid-stroke" '
                        'stroke-width="2"/>')
            rest = floor - 13
        push = 18.0 if not strong else 66.0
        body.append(f'<path d="M{mid - 60} {rest}H{mid - 60 + push:.0f}" '
                    'class="fig-accent-stroke" stroke-width="2" stroke-dasharray="4 3"/>')
        body.append(f'<circle cx="{mid - 60}" cy="{rest}" r="11" class="fig-grid-stroke" '
                    'stroke-width="1.6" stroke-dasharray="3 3" fill="none" opacity="0.7"/>')
        body.append(f'<circle cx="{mid - 60 + push:.0f}" cy="{rest}" r="11" '
                    'class="fig-target"/>')
        body.append(crosshair("fig-ink-stroke", mid - 86, rest))
        note = ("it barely moves" if not strong else "it is thrown")
        if kind == "flatshove":
            note = ("a nudge, whatever the damage" if not strong
                    else "a shove, whatever the damage")
        body.append(text(mid, cy + 50, note, "fig-muted", size=9, weight=600))

    elif kind == "rampslow":
        # Holding this weapon multiplies your acceleration, so the speed curve is what changes.
        base, top = cy + 26, cy - 24
        body.append(f'<path d="M{mid - 76} {base}H{mid + 76}" class="fig-grid-stroke" '
                    'stroke-width="1.8"/>')
        body.append(f'<path d="M{mid - 76} {top}H{mid + 76}" class="fig-grid-stroke" '
                    'stroke-width="1.4" stroke-dasharray="4 4" opacity="0.7"/>')
        body.append(text(mid + 46, top - 6, "top speed", "fig-muted", size=8, weight=600))
        knee = 26.0 if strong else 108.0
        curve = [f"M{mid - 76} {base}"]
        for step in range(1, 25):
            x = -76 + step * 152 / 24
            curve.append(f"L{mid + x:.1f} "
                         f"{base - (base - top) * smooth(min(1.0, (x + 76) / knee)):.1f}")
        body.append(f'<path d="{"".join(curve)}" class="fig-accent-stroke" stroke-width="2.6" '
                    'fill="none"/>')
        body.append(text(mid, cy + 48, "this weapon makes you sluggish" if not strong
                         else "it barely slows your start", "fig-muted", size=9, weight=600))

    elif kind in ("muzzlescale", "wallburst", "bodyburst", "decalmark", "tracerwidth"):
        # Effects left on screen, each measured against the thing you are trying to see past.
        size = 8.0 if not strong else 26.0
        if kind == "muzzlescale":
            body.append(f'<path d="M{mid - 30} {cy + 22}h26v-12h-26z" class="fig-grid-fill"/>')
            rays = "".join(f'M{mid + 4} {cy + 16}l{size * math.cos(r * 1.0472):.1f} '
                           f'{size * math.sin(r * 1.0472):.1f}' for r in range(6))
            body.append(f'<path d="{rays}" class="fig-accent-stroke" stroke-width="2.6" '
                        'stroke-linecap="round"/>')
            body.append(f'<circle cx="{mid + 52}" cy="{cy - 8}" r="12" class="fig-target"/>')
            note = "you can see past it" if not strong else "it covers the target"
        elif kind == "tracerwidth":
            body.append(f'<circle cx="{mid + 58}" cy="{cy - 4}" r="12" class="fig-target"/>')
            body.append(f'<path d="M{mid - 70} {cy - 4}H{mid + 46}" '
                        'class="fig-cool-stroke" stroke-width="'
                        f'{size / 2:.1f}" opacity="0.5"/>')
            body.append(f'<path d="M{mid - 70} {cy - 4}H{mid + 46}" '
                        'class="fig-tense-stroke" stroke-width="1.4"/>')
            note = "a hairline trail" if not strong else "a fat trail"
        elif kind == "decalmark":
            body.append(f'<rect x="{mid - 70}" y="{cy - 28}" width="140" height="52" rx="4" '
                        'class="fig-grid-fill" opacity="0.4"/>')
            for spot_x, spot_y in ((-40, -10), (-8, 8), (26, -14), (48, 6)):
                body.append(f'<circle cx="{mid + spot_x}" cy="{cy - 2 + spot_y}" '
                            f'r="{size / 2:.1f}" class="fig-muted-stroke" stroke-width="2" '
                            'fill="none"/>')
            note = "small marks" if not strong else "the wall fills up"
        else:
            hit_x = mid + 30 if kind == "bodyburst" else mid + 46
            if kind == "bodyburst":
                body.append(f'<circle cx="{hit_x}" cy="{cy - 4}" r="14" class="fig-target"/>')
            else:
                body.append(f'<rect x="{mid + 34}" y="{cy - 34}" width="14" height="62" '
                            'class="fig-grid-fill"/>')
            rays = "".join(f'M{hit_x} {cy - 4}l{size * math.cos(r * 1.0472):.1f} '
                           f'{size * math.sin(r * 1.0472):.1f}' for r in range(6))
            body.append(f'<path d="{rays}" class="fig-accent-stroke" stroke-width="2.6" '
                        'stroke-linecap="round"/>')
            body.append(crosshair("fig-ink-stroke", mid - 54, cy - 4))
            note = ("easy to miss" if not strong else "impossible to miss")
        body.append(text(mid, cy + 48, note, "fig-muted", size=9, weight=600))

    elif kind == "traceorigin":
        # Two trails that end in the same place and start in different ones.
        body.append(f'<circle cx="{mid + 60}" cy="{cy - 4}" r="12" class="fig-target"/>')
        drop = 0.0 if not strong else 22.0
        body.append(f'<path d="M{mid - 66} {cy - 4 + drop:.0f}L{mid + 48} {cy - 4}" '
                    'class="fig-cool-stroke" stroke-width="3" opacity="0.8"/>')
        body.append(f'<circle cx="{mid - 66}" cy="{cy - 4 + drop:.0f}" r="4" '
                    'class="fig-accent-fill"/>')
        body.append(f'<path d="M{mid - 66} {cy - 4}H{mid + 48}" class="fig-grid-stroke" '
                    'stroke-width="1.4" stroke-dasharray="3 3" opacity="0.7"/>')
        body.append(text(mid - 62, cy + 22 + drop, "drawn from", "fig-muted",
                         anchor="start", size=8, weight=600))
        body.append(text(mid, cy + 50, "the trail follows the shot" if not strong
                         else "the trail starts elsewhere", "fig-muted", size=9, weight=600))

    elif kind == "usechance":
        # How often a chance is taken, drawn as the chances and which ones were used.
        taken = (True, False, False, False) if not strong else (True, True, False, True)
        body.append(f'<path d="M{mid - 74} {cy}H{mid + 74}" class="fig-grid-stroke" '
                    'stroke-width="1.6" opacity="0.6"/>')
        for slot, used in enumerate(taken):
            sx = mid - 56 + slot * 38
            body.append(f'<path d="M{sx} {cy - 18}V{cy - 4}" class="fig-grid-stroke" '
                        'stroke-width="2"/>')
            if used:
                rays = "".join(f'M{sx} {cy + 14}l{9 * math.cos(r * 1.0472):.1f} '
                               f'{9 * math.sin(r * 1.0472):.1f}' for r in range(6))
                body.append(f'<path d="{rays}" class="fig-accent-stroke" stroke-width="2.4" '
                            'stroke-linecap="round"/>')
        body.append(text(mid, cy + 44, "it rarely takes one" if not strong
                         else "it takes most of them", "fig-muted", size=10, weight=600))

    elif kind == "endtally":
        # A target the run is counting up to, with the count part way there.
        # The goal is the field, so the goal line is what moves. Pinning it and changing only the
        # number printed beside it left the two cells identical.
        goal, at = (4, 0.58) if not strong else (10, 0.97)
        body += _bar(mid, cy - 6, 0.3, "fig-cool-fill")
        gx = mid - 70 + 140 * at
        body.append(f'<path d="M{gx:.0f} {cy - 20}V{cy + 16}" class="fig-tense-stroke" '
                    'stroke-width="2.6"/>')
        body.append(text(gx - 4, cy + 30, f"stop at {goal}", "fig-muted", anchor="end",
                         size=8, weight=600))
        body.append(text(mid - 70, cy + 30, "so far", "fig-muted", anchor="start",
                         size=8, weight=600))
        body.append(text(mid, cy + 50, "the run ends early" if not strong
                         else "it runs a long time", "fig-muted", size=10, weight=600))

    else:
        # A hit lands and the ability answers after a gap. The gap is the field.
        gap = 0.1 if not strong else 0.56
        for dy in (-18, 18):
            body.append(f'<path d="M{mid - 74} {cy + dy}H{mid + 74}" '
                        'class="fig-grid-stroke" stroke-width="1.6" opacity="0.6"/>')
        cause = mid - 54
        answer = cause + 124 * gap
        body.append(f'<path d="M{cause} {cy - 30}V{cy - 6}" class="fig-tense-stroke" '
                    'stroke-width="3"/>')
        body.append(text(cause, cy - 34, "a hit lands", "fig-muted", anchor="start",
                         size=8, weight=600))
        rays = "".join(f'M{answer:.1f} {cy + 18}l{9 * math.cos(r * 1.0472):.1f} '
                       f'{9 * math.sin(r * 1.0472):.1f}' for r in range(6))
        body.append(f'<path d="{rays}" class="fig-accent-stroke" stroke-width="2.4" '
                    'stroke-linecap="round"/>')
        body.append(f'<path d="M{cause} {cy}H{answer:.1f}" class="fig-muted-stroke" '
                    'stroke-width="1.6" stroke-dasharray="3 3"/>')
        body.append(text(mid, cy + 48, "the ability answers at once" if not strong
                         else "it answers late", "fig-muted", size=9, weight=600))

    return body, css
