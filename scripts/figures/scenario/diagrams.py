"""The diagrams across docs/wiki/scenarios/. build.py says which one belongs to which page.

`profiles` draws what a scenario is made of: the three profiles it cannot do without, the two
optional ones that shape a target, and the decision each profile holds. `spawn` animates the same
scenario under two settings, so the difference between a narrow slow target and a wide fast one is
shown rather than asserted. `hitboxes` draws the main and projectile boxes against a wall, since
"passes through the world" is the one thing a table cannot say. `dials` shows a smaller target and a
further one raising the same demand, which is the point of the page it sits on.

None of them copies a trainer's interface. They name the tabs and fields the editor uses and
arrange them as the reader needs to understand them, which is a diagram, not a screenshot.
"""
import math
import random
import sys
from collections.abc import Sequence
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figure_kit import crosshair, keyframes, lane_label, metadata, smooth, text  # noqa: E402

# A node is a rounded box with its name on the first line and, under it, the decision it holds.
# Required nodes are drawn solid; an optional one is dashed, and the legend says so.
Node = tuple[float, float, float, float, str, str, bool]

PROF_W = 760
PROF_H = 300

PROF_NODES: tuple[Node, ...] = (
    (300, 20, 160, 52, "Scenario", "Challenge · Scoring · Tags", True),
    (70, 110, 210, 58, "Player character", "your hitboxes and weapons", True),
    (480, 110, 210, 58, "Bot", "which character, which dodge", True),
    (380, 208, 190, 58, "Bot character", "size · health · spawn", True),
    (590, 208, 150, 58, "Dodge profile", "how the target moves", False),
)
# Parent index to child index, as an elbow: down out of the parent, across, down into the child.
PROF_EDGES = ((0, 1), (0, 2), (2, 3), (2, 4))
# How deep each node sits, which is also the order it arrives in: unpacking reveals a level at a time.
PROF_DEPTH = (0, 1, 1, 2, 2)
PROF_T = 5.0


def node(x: float, y: float, w: float, h: float, name: str, note: str, required: bool) -> str:
    """One box. An optional profile is dashed and muted, so the required spine reads first."""
    stroke = "fig-ink-stroke" if required else "fig-grid-stroke"
    dash = "" if required else ' stroke-dasharray="6 5"'
    ink = "fig-ink" if required else "fig-muted"
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" class="fig-panel {stroke}" '
            f'stroke-width="2"{dash}/>'
            + text(x + w / 2, y + 22, name, ink, size=16, weight=700)
            + text(x + w / 2, y + 42, note, "fig-muted", size=13, weight=500))


def elbow(parent: Node, child: Node) -> str:
    """A line from the bottom of the parent to the top of the child, turning once halfway down."""
    px, py = parent[0] + parent[2] / 2, parent[1] + parent[3]
    cx, cy = child[0] + child[2] / 2, child[1]
    mid = (py + cy) / 2
    return (f'<path d="M{px} {py}V{mid}H{cx}V{cy}" class="fig-grid-stroke" stroke-width="2" '
            'fill="none" marker-end="url(#fig-scn-arrow)"/>')


def profiles() -> str:
    body = ['<defs><marker id="fig-scn-arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto">'
            '<path d="M0 0 L10 5 L0 10 Z" class="fig-grid-fill"/></marker></defs>']
    for a, b in PROF_EDGES:
        body.append(f'<g class="aim-prof-in" style="animation-delay:'
                    f'{PROF_DEPTH[b] * PROF_T * 0.2:.2f}s">{elbow(PROF_NODES[a], PROF_NODES[b])}</g>')
    for index, spec in enumerate(PROF_NODES):
        body.append(f'<g class="aim-prof-in" style="animation-delay:'
                    f'{PROF_DEPTH[index] * PROF_T * 0.2:.2f}s">{node(*spec)}</g>')
    # The legend carries the one thing the shapes alone cannot say.
    body.append('<rect x="70" y="278" width="26" height="3" rx="1.5" class="fig-ink-fill"/>')
    body.append(text(106, 280, "required", "fig-muted", anchor="start", size=13, weight=500,
                     middle=True))
    body.append('<rect x="210" y="278" width="26" height="3" rx="1.5" class="fig-grid-fill"/>')
    body.append(text(246, 280, "optional", "fig-muted", anchor="start", size=13, weight=500,
                     middle=True))
    css = ["@keyframes aimProfIn{0%{opacity:0}5%{opacity:1}100%{opacity:1}}",
           ".aim-prof-in{opacity:0;animation-name:aimProfIn;animation-iteration-count:infinite;"
           f"animation-duration:{PROF_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-prof-in{opacity:1;animation:none!important}}"]
    return (f'<svg viewBox="0 0 {PROF_W} {PROF_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-profiles-title"><title id="fig-profiles-title">A scenario holds '
            'the challenge rules, the scoring and the tags, and links to a player character and a '
            'bot. The bot links to its own character profile, which carries target size, health and '
            'spawn, and optionally to a dodge profile, which carries how the target moves.</title>'
            + metadata() + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


SPAWN_W = 760
SPAWN_H = 330
SPAWN_CY = 186
# Two panels, same target size, differing only in how far a target may spawn and how fast it moves.
# Left: a narrow spawn box and a slow dodge with long pauses. Right: a wide box and a fast one.
# A panel's half-box has to clear its amplitude plus TARGET_R, or the target hangs over the edge of
# the area it is meant to stay inside, which reads as a mistake rather than as a setting.
SPAWN_PANELS = (
    (12, 190, "Narrow spawn, slow dodge", "small corrections", 70, 48, 4.0, 0.22),
    (392, 570, "Wide spawn, fast dodge", "large repositioning", 172, 150, 2.0, 0.06),
)
SPAWN_PANEL_W = 356
SPAWN_FRAMES = 40
TARGET_R = 14


def strafe(amp: float, pause: float, frames: int) -> list[float]:
    """One dodge cycle: hold at the left edge, sweep across, hold, sweep back. The sweeps are eased,
    because a target that changes direction instantly reads as a glitch rather than as a strafe."""
    sweep = 0.5 - pause
    out = []
    for i in range(frames + 1):
        u = i / frames
        if u < pause:
            out.append(-amp)
        elif u < pause + sweep:
            out.append(-amp + 2 * amp * smooth((u - pause) / sweep))
        elif u < 2 * pause + sweep:
            out.append(amp)
        else:
            out.append(amp - 2 * amp * smooth((u - 2 * pause - sweep) / sweep))
    return out


def spawn() -> str:
    css = []
    body = []
    for index, (x, cx, name, note, box, amp, period, pause) in enumerate(SPAWN_PANELS):
        body.append(f'<rect x="{x}" y="46" width="{SPAWN_PANEL_W}" height="{SPAWN_H - 60}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        # The spawn box is the area a target may appear in, drawn dashed because it is a rule
        # rather than a thing the player sees in the scenario.
        body.append(f'<rect x="{cx - box}" y="{SPAWN_CY - 52}" width="{box * 2}" height="104" '
                    'rx="8" class="fig-grid-stroke" stroke-width="2" stroke-dasharray="7 6" '
                    'fill="none"/>')
        body.append(text(cx, SPAWN_CY + 76, "Spawn Offset Min and Max", "fig-muted", size=13,
                         weight=500))
        # The path the target actually travels, so a paused frame still shows the range.
        body.append(f'<path d="M{cx - amp} {SPAWN_CY}H{cx + amp}" class="fig-grid-stroke" '
                    'stroke-width="2" stroke-linecap="round" opacity="0.7"/>')
        body.append(text(cx, SPAWN_CY - 68, "Dodge profile", "fig-muted", size=13, weight=500))
        body.append(f'<g class="aim-scn-anim aim-scn-anim{index}">'
                    f'<circle cx="{cx}" cy="{SPAWN_CY}" r="{TARGET_R}" class="fig-target"/></g>')
        body.append(crosshair("fig-ink-stroke", cx, SPAWN_CY))
        css.append(keyframes(f"aimScnStrafe{index}", strafe(amp, pause, SPAWN_FRAMES),
                             lambda v: f"translate({v:.1f}px,0)"))
        css.append(f".aim-scn-anim{index}{{animation-name:aimScnStrafe{index};"
                   f"animation-duration:{period}s}}")
    css.append(".aim-scn-anim{animation-timing-function:linear;animation-iteration-count:infinite}")
    # Readers who ask for less motion get the frame where the two panels differ most: the slow
    # target still waiting at its edge, the fast one already at the far side of a much wider box.
    css.append("@media (prefers-reduced-motion:reduce){.aim-scn-anim{animation-play-state:paused}"
               f".aim-scn-anim0{{animation-delay:-{SPAWN_PANELS[0][6] * 0.1:.2f}s!important}}"
               f".aim-scn-anim1{{animation-delay:-{SPAWN_PANELS[1][6] * 0.5:.2f}s!important}}}}")
    return (f'<svg viewBox="0 0 {SPAWN_W} {SPAWN_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-spawn-title"><title id="fig-spawn-title">Two panels showing the '
            'same scenario under different settings. On the left a narrow spawn box and a slow '
            'dodge keep the target near the crosshair, so the run asks for small corrections. On '
            'the right a much wider spawn box and a faster dodge carry the target far past the '
            'crosshair, so the run asks for large repositioning.</title>'
            + metadata() + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


HITBOX_W = 760
HITBOX_H = 290
# Both panels draw the same character in the same place against the same wall, so the only thing
# that changes between them is which box is drawn and what reaches it.
HITBOX_PANELS = (
    (12, "Main box", "hitscan and projectile", "collides with the world"),
    (392, "Projectile box", "projectile only", "passes through the world"),
)
HITBOX_PANEL_W = 356


def figure_body(x: float, cy: float) -> str:
    """A plain capsule standing in for a character: enough to read as a body, not a drawing of one."""
    return (f'<rect x="{x - 15}" y="{cy - 46}" width="30" height="92" rx="15" '
            'class="fig-muted-stroke" stroke-width="2" fill="none" opacity="0.8"/>')


def hitboxes() -> str:
    body = []
    for index, (x, name, takes, world) in enumerate(HITBOX_PANELS):
        cx = x + 250
        cy = 150
        wall_x = x + 176
        body.append(f'<rect x="{x}" y="46" width="{HITBOX_PANEL_W}" height="{HITBOX_H - 74}" '
                    'rx="12" class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, takes))
        # A wall between the shooter and the target, so "passes through the world" has something
        # to pass through.
        body.append(f'<rect x="{wall_x}" y="70" width="16" height="130" class="fig-grid-fill"/>')
        body.append(figure_body(cx, cy))
        if index == 0:
            # The main box stops at the wall, so it is drawn tight to the body and solid.
            box_x, box_w, cls, dash = cx - 22, 44, "fig-accent-stroke", ""
        else:
            # The projectile box is the wider, world-ignoring one, so it is drawn crossing the wall.
            box_x, box_w, cls, dash = wall_x - 24, 108, "fig-cool-stroke", ' stroke-dasharray="7 5"'
        body.append(f'<rect x="{box_x}" y="{cy - 52}" width="{box_w}" height="104" rx="6" '
                    f'class="{cls}" stroke-width="2.4" fill="none"{dash}/>')
        body.append(text(x + 178, 238, world, "fig-muted", size=13, weight=500))
    return (f'<svg viewBox="0 0 {HITBOX_W} {HITBOX_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-hitboxes-title"><title id="fig-hitboxes-title">Two panels showing '
            'the same character beside the same wall. The main box is drawn tight around the body '
            'and stops at the wall, and it takes both hitscan and projectile fire. The projectile '
            'box is wider and crosses through the wall, and it takes projectile fire '
            'only.</title>' + metadata() + "".join(body) + "</svg>")


DIALS_W = 760
DIALS_H = 250
# The same crosshair and the same baseline in each panel, so the eye compares one change at a time.
# Panels two and three reach the same demand by different routes, which is the whole point.
DIALS_PANELS = (
    (12, "Baseline", 150, 17, 96),
    (263, "Smaller target", 150, 10, 150),
    (514, "Further away", 214, 17, 150),
)
DIALS_PANEL_W = 234
DIALS_BAR_Y = 182
DIALS_T = 3.4


def dials() -> str:
    body = []
    css = [".aim-dial-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{DIALS_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-dial-anim{animation-play-state:paused;"
           f"animation-delay:-{DIALS_T * 0.34:.2f}s!important}}}}"]
    for x, name, reach, radius, demand in DIALS_PANELS:
        body.append(f'<rect x="{x}" y="42" width="{DIALS_PANEL_W}" height="{DIALS_H - 58}" rx="12" '
                    'class="fig-panel"/>')
        body.append(text(x + 16, 30, name, "fig-ink", anchor="start", size=15, weight=700))
        cross_x = x + 26
        target_x = x + 26 + reach * (DIALS_PANEL_W - 60) / 214
        body.append(f'<path d="M{cross_x} 112H{target_x}" class="fig-grid-stroke" stroke-width="2" '
                    'stroke-dasharray="5 5"/>')
        # The crosshair travels the gap and arrives late where the demand bar is long, so the bar
        # and the motion say the same thing two ways.
        arrive = demand / 150 * 0.62
        css.append(f"@keyframes aimDialRun{name.replace(' ', '')}{{0%{{transform:translate(0,0)}}"
                   f"{arrive * 100:.4g}%{{transform:translate({target_x - cross_x:.1f}px,0)}}"
                   f"100%{{transform:translate({target_x - cross_x:.1f}px,0)}}}}")
        css.append(f".aim-dial-{name.replace(' ', '')}{{animation-name:"
                   f"aimDialRun{name.replace(' ', '')}}}")
        body.append(f'<circle cx="{target_x}" cy="112" r="{radius}" class="fig-target"/>')
        # The crosshair travels onto the target, so it is drawn after it and stays visible on arrival.
        body.append(f'<g class="aim-dial-anim aim-dial-{name.replace(" ", "")}">'
                    f'{crosshair("fig-ink-stroke", cross_x, 112)}</g>')
        # One bar per panel, read against the baseline's, so "the same demand" is visible rather
        # than claimed.
        body.append(f'<rect x="{x + 16}" y="{DIALS_BAR_Y}" width="{demand}" height="12" rx="6" '
                    'class="fig-accent-fill"/>')
        body.append(text(x + 16, DIALS_BAR_Y + 34, "demand", "fig-muted", anchor="start", size=13,
                         weight=500))
    return (f'<svg viewBox="0 0 {DIALS_W} {DIALS_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-dials-title"><title id="fig-dials-title">Three panels, each with a '
            'crosshair and a target, and a bar showing how much the shot demands. A baseline panel. '
            'A panel where the target is smaller at the same distance. A panel where the target is '
            'the baseline size but further away. The second and third panels show the same raised '
            'demand as each other.</title>' + metadata() + f"<style>{''.join(css)}</style>"
            + "".join(body) + "</svg>")


def walk(points: Sequence[tuple[float, float]], frames: int,
         hold: float = 0.0) -> list[tuple[float, float]]:
    """Positions along a polyline at constant speed, as offsets from the first point.

    `hold` is the fraction of the cycle spent stationary at the last point, for a path that ends
    somewhere rather than looping. Constant speed matters: a bot that slows into a corner reads as
    hesitation, which is a behavior this figure is not claiming."""
    legs = [((points[i + 1][0] - points[i][0]), (points[i + 1][1] - points[i][1]))
            for i in range(len(points) - 1)]
    lengths = [(dx * dx + dy * dy) ** 0.5 for dx, dy in legs]
    total = sum(lengths)
    out = []
    for i in range(frames + 1):
        u = i / frames
        if hold and u > 1 - hold:
            u = 1 - hold
        travelled = (u / (1 - hold) if hold else u) * total
        x, y = points[0]
        for (dx, dy), length in zip(legs, lengths):
            if travelled >= length and length:
                x, y = x + dx, y + dy
                travelled -= length
            elif length:
                x, y = x + dx * travelled / length, y + dy * travelled / length
                travelled = 0
                break
        out.append((x - points[0][0], y - points[0][1]))
    return out


WAY_W = 760
WAY_H = 300
WAY_T = 5.0
WAY_FRAMES = 44
WAY_PANEL_W = 356
# The same three waypoints and the same player in both panels, so the only difference the reader
# sees is what the bot does about them.
WAY_PANELS = (
    (12, "Seek Waypoint", "ignores you, repeats forever"),
    (392, "Seek Combat", "breaks off when it finds you"),
)


def waypoints() -> str:
    css = [".aim-way-anim{animation-timing-function:linear;animation-iteration-count:infinite}"]
    body = []
    for index, (x, name, note) in enumerate(WAY_PANELS):
        marks = [(x + 98, 112), (x + 258, 112), (x + 178, 208)]
        player = (x + 178, 252)
        body.append(f'<rect x="{x}" y="46" width="{WAY_PANEL_W}" height="{WAY_H - 58}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        # Both panels are given the same three-waypoint route, drawn the same way. What differs is
        # what the bot does about it, so the route itself must not move between them.
        body.append(f'<path d="M{marks[0][0]} {marks[0][1]}L{marks[1][0]} {marks[1][1]}'
                    f'L{marks[2][0]} {marks[2][1]}Z" class="fig-grid-stroke" stroke-width="2" '
                    'stroke-dasharray="4 6" fill="none" opacity="0.6"/>')
        if index == 0:
            route = marks + [marks[0]]
            hold = 0.0
            skipped = -1
        else:
            # It stops just short of the player, so the crosshair it came for stays readable.
            closed = (player[0], player[1] - 26)
            route = [marks[0], marks[1], closed]
            hold = 0.28
            # The third waypoint is never reached here, so it is dimmed and the break-off is drawn
            # as its own line rather than bent through a marker the bot does not visit. The dimming
            # and that line carry it; a label there would land under the bot at rest.
            skipped = 2
            body.append(f'<path d="M{marks[1][0]} {marks[1][1]}L{closed[0]} {closed[1]}" '
                        'class="fig-accent-stroke" stroke-width="2" stroke-dasharray="4 5" '
                        'fill="none"/>')
        for order, (mx, my) in enumerate(marks):
            dim = ' opacity="0.35"' if order == skipped else ""
            body.append(f'<circle cx="{mx}" cy="{my}" r="9" class="fig-grid-stroke" '
                        f'stroke-width="2" fill="none"{dim}/>')
            body.append(f'<g{dim}>' + text(mx, my + 1, str(order + 1), "fig-muted", size=11,
                                           weight=600, middle=True) + "</g>")
        body.append(f'<g class="aim-way-anim aim-way-anim{index}">'
                    f'<circle cx="{marks[0][0]}" cy="{marks[0][1]}" r="13" '
                    'class="fig-target"/></g>')
        body.append(crosshair("fig-ink-stroke", *player))
        body.append(text(player[0], player[1] + 26, "you", "fig-muted", size=13, weight=500))
        css.append(keyframes(f"aimWayPath{index}", walk(route, WAY_FRAMES, hold),
                             lambda p: f"translate({p[0]:.1f}px,{p[1]:.1f}px)"))
        css.append(f".aim-way-anim{index}{{animation-name:aimWayPath{index};"
                   f"animation-duration:{WAY_T}s}}")
    # Paused, the panels have to differ: the looping bot mid-leg, the other already sat on the player.
    css.append("@media (prefers-reduced-motion:reduce){.aim-way-anim{animation-play-state:paused}"
               f".aim-way-anim0{{animation-delay:-{WAY_T * 0.22:.2f}s!important}}"
               f".aim-way-anim1{{animation-delay:-{WAY_T * 0.85:.2f}s!important}}}}")
    return (f'<svg viewBox="0 0 {WAY_W} {WAY_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-waypoints-title"><title id="fig-waypoints-title">Two panels with '
            'the same three waypoints and the same player. On the left the bot walks the three '
            'waypoints in a loop and never approaches the player. On the right the bot leaves the '
            'route after the second waypoint and moves to the player, then stays '
            'there.</title>' + metadata() + f"<style>{''.join(css)}</style>" + "".join(body)
            + "</svg>")


BRUSH_W = 760
BRUSH_H = 330
BRUSH_T = 3.6
BRUSH_START = 190
BRUSH_WALL = 470
BRUSH_END = 726
# The three brush types whose behavior is not obvious from the name. The other three are on the
# page's table; a figure repeating all six would be a slower table.
BRUSH_ROWS = (
    ("Default", True, True),
    ("Clip", True, False),
    ("Weapon Clip", False, True),
)


def brushes() -> str:
    css = [".aim-brush-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{BRUSH_T}s}}"]
    body = []
    # Both travellers cover the same ground at the same speed, so where one stops and the other
    # does not is the only thing the eye has to compare.
    span = BRUSH_END - BRUSH_START
    stop = BRUSH_WALL - 34 - BRUSH_START
    for index, (name, stops_player, stops_bullet) in enumerate(BRUSH_ROWS):
        top = 56 + index * 92
        body.append(f'<rect x="12" y="{top}" width="736" height="80" rx="10" class="fig-panel"/>')
        body.append(text(30, top + 40, name, "fig-ink", anchor="start", size=15, weight=700,
                         middle=True))
        body.append(f'<rect x="{BRUSH_WALL}" y="{top + 10}" width="16" height="60" '
                    'class="fig-grid-fill"/>')
        for lane, (label, stopped) in enumerate((("player", stops_player),
                                                 ("bullet", stops_bullet))):
            y = top + 26 + lane * 30
            body.append(text(BRUSH_START - 22, y, label, "fig-muted", anchor="end", size=12,
                             weight=500, middle=True))
            shape = (f'<rect x="{BRUSH_START - 8}" y="{y - 8}" width="16" height="16" rx="3" '
                     'class="fig-muted-stroke" stroke-width="2" fill="none"/>' if lane == 0
                     else f'<circle cx="{BRUSH_START}" cy="{y}" r="6" class="fig-accent-fill"/>')
            reach = stop if stopped else span
            body.append(f'<g class="aim-brush-anim aim-brush-{index}{lane}">{shape}</g>')
            # A stopper covers less ground in the same time, so it arrives early and waits, which
            # is what being blocked looks like.
            arrive = reach / span
            css.append(f"@keyframes aimBrush{index}{lane}{{0%{{transform:translate(0,0)}}"
                       f"{arrive * 88:.4g}%{{transform:translate({reach}px,0)}}"
                       f"100%{{transform:translate({reach}px,0)}}}}")
            css.append(f".aim-brush-{index}{lane}{{animation-name:aimBrush{index}{lane}}}")
    css.append("@media (prefers-reduced-motion:reduce){.aim-brush-anim{animation-play-state:paused;"
               f"animation-delay:-{BRUSH_T * 0.93:.2f}s!important}}}}")
    return (f'<svg viewBox="0 0 {BRUSH_W} {BRUSH_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-brushes-title"><title id="fig-brushes-title">Three rows, each with '
            'a player marker and a bullet travelling toward the same brush. Against a Default brush '
            'both stop. Against a Clip brush the player stops and the bullet passes through. Against '
            'a Weapon Clip brush the player passes through and the bullet stops.</title>'
            + metadata() + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


SPREAD_W = 760
SPREAD_H = 300
SPREAD_T = 4.4
SPREAD_SHOTS = 7
SPREAD_R = 62
SPREAD_CY = 168


def cone_shots(seed: int, count: int, radius: float) -> list[tuple[float, float]]:
    """Shot placements inside a circle, deterministic so a rebuild does not reshuffle the figure."""
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        angle = rng.uniform(0, 6.28318)
        dist = radius * (rng.random() ** 0.5)
        out.append((dist * math.cos(angle), dist * math.sin(angle)))
    return out


def spread() -> str:
    # Both panels fire two volleys per cycle. The left panel's second volley lands somewhere new;
    # the right panel's repeats the first exactly. That repeat is the whole distinction.
    # The fixed pattern covers the same ground as the cone on purpose. Per bullet spread is not
    # tighter than spread, it is repeatable, and a smaller pattern would teach the wrong difference.
    fixed = [(SPREAD_R * 0.82 * math.cos(i * 6.28318 / (SPREAD_SHOTS - 1)),
              SPREAD_R * 0.82 * math.sin(i * 6.28318 / (SPREAD_SHOTS - 1)))
             for i in range(SPREAD_SHOTS - 1)] + [(0.0, 0.0)]
    volleys: dict[int, tuple[list[tuple[float, float]], list[tuple[float, float]] | None]] = {
        0: (cone_shots(11, SPREAD_SHOTS, SPREAD_R), cone_shots(29, SPREAD_SHOTS, SPREAD_R)),
        1: (fixed, None),
    }
    css = ["@keyframes aimSpreadMark{0%{opacity:0}4%{opacity:1}44%{opacity:1}50%{opacity:0}"
           "100%{opacity:0}}",
           ".aim-spread-mark{opacity:0;animation-name:aimSpreadMark;animation-iteration-count:"
           f"infinite;animation-duration:{SPREAD_T}s}}"]
    body = []
    for index, (x, name, note) in enumerate(((12, "Spread", "a new pattern every volley"),
                                             (392, "Per bullet spread", "the same pattern, always"))):
        cx = x + 178
        first, second = volleys[index]
        second = second or first
        body.append(f'<rect x="{x}" y="46" width="356" height="{SPREAD_H - 62}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        body.append(f'<circle cx="{cx}" cy="{SPREAD_CY}" r="{SPREAD_R}" class="fig-grid-stroke" '
                    'stroke-width="2" stroke-dasharray="6 6" fill="none"/>')
        marks = []
        for half, shots in enumerate((first, second)):
            for order, (dx, dy) in enumerate(shots):
                # Each mark waits its turn inside its own half of the cycle, so the volley reads as
                # a burst rather than as everything appearing at once.
                delay = half * SPREAD_T / 2 + order * SPREAD_T / 2 * 0.055
                marks.append(f'<circle cx="{cx + dx:.1f}" cy="{SPREAD_CY + dy:.1f}" r="5" '
                             f'class="fig-target aim-spread-mark" '
                             f'style="animation-delay:{delay:.2f}s"/>')
        body += marks
        body.append(crosshair("fig-ink-stroke", cx, SPREAD_CY))
    # Paused late in the second volley, both panels show a full pattern, which is when they are
    # most comparable.
    css.append("@media (prefers-reduced-motion:reduce){.aim-spread-mark{opacity:1;"
               "animation:none!important}}")
    return (f'<svg viewBox="0 0 {SPREAD_W} {SPREAD_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-spread-title"><title id="fig-spread-title">Two panels, each firing '
            'two volleys at the same target. With spread, the second volley lands in a different '
            'scatter from the first. With per bullet spread, the second volley repeats the first '
            'exactly.</title>' + metadata() + f"<style>{''.join(css)}</style>" + "".join(body)
            + "</svg>")


SHORT_W = 760
SHORT_H = 300
SHORT_T = 4.0
SHORT_FRAMES = 48
SHORT_CY = 170


def shortcut() -> str:
    """Left: a target whose path crosses the resting crosshair, so waiting scores. Right: a path
    that never returns to the same point, so the shot has to be taken."""
    css = [".aim-short-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{SHORT_T}s}}",
           "@keyframes aimShortHit{0%{opacity:0}2%{opacity:1}12%{opacity:0}100%{opacity:0}}",
           ".aim-short-hit{opacity:0;animation-name:aimShortHit;animation-iteration-count:infinite;"
           f"animation-duration:{SHORT_T}s}}"]
    body = []
    for index, (x, name, note) in enumerate((
            (12, "Beatable by waiting", "the path returns to your crosshair"),
            (392, "Has to be aimed", "the path never comes back"))):
        cx = x + 178
        body.append(f'<rect x="{x}" y="46" width="356" height="{SHORT_H - 62}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        frames = []
        for i in range(SHORT_FRAMES + 1):
            u = i / SHORT_FRAMES
            if index == 0:
                # A flat left-right sweep through the center: the crosshair sits on the path.
                frames.append((120 * math.sin(u * 6.28318), 0.0))
            else:
                # An orbit offset upward, so the target circles without ever crossing the center.
                frames.append((110 * math.sin(u * 6.28318), -52 + 34 * math.cos(u * 6.28318)))
        if index == 0:
            body.append(f'<path d="M{cx - 120} {SHORT_CY}H{cx + 120}" class="fig-grid-stroke" '
                        'stroke-width="2" stroke-dasharray="6 6" opacity="0.7"/>')
            # The flash marks the two moments a still crosshair is already on target.
            for delay in (0.0, SHORT_T / 2):
                body.append(f'<circle cx="{cx}" cy="{SHORT_CY}" r="26" '
                            'class="fig-accent-stroke aim-short-hit" stroke-width="3" fill="none" '
                            f'style="animation-delay:{delay:.2f}s"/>')
            body.append(text(cx, SHORT_CY + 74, "free hits, no aiming", "fig-muted", size=13,
                             weight=500))
        else:
            ring = " ".join(f"{cx + fx:.1f} {SHORT_CY + fy:.1f}" for fx, fy in frames[::4])
            body.append(f'<polyline points="{ring}" class="fig-grid-stroke" stroke-width="2" '
                        'stroke-dasharray="6 6" fill="none" opacity="0.7"/>')
            body.append(text(cx, SHORT_CY + 74, "every hit is a correction", "fig-muted", size=13,
                             weight=500))
        body.append(f'<g class="aim-short-anim aim-short-{index}">'
                    f'<circle cx="{cx}" cy="{SHORT_CY}" r="15" class="fig-target"/></g>')
        # The crosshair goes last everywhere in this file: it is the reader's own position and has
        # to stay visible when a target passes over it.
        body.append(crosshair("fig-ink-stroke", cx, SHORT_CY))
        css.append(keyframes(f"aimShortPath{index}", frames,
                             lambda p: f"translate({p[0]:.1f}px,{p[1]:.1f}px)"))
        css.append(f".aim-short-{index}{{animation-name:aimShortPath{index}}}")
    css.append("@media (prefers-reduced-motion:reduce){.aim-short-anim{animation-play-state:paused}"
               ".aim-short-hit{opacity:1;animation:none!important}}")
    return (f'<svg viewBox="0 0 {SHORT_W} {SHORT_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-shortcut-title"><title id="fig-shortcut-title">Two panels with a '
            'still crosshair. On the left the target sweeps straight through the crosshair twice a '
            'cycle, so a player who never moves still scores. On the right the target orbits above '
            'the crosshair and never crosses it, so every hit needs a '
            'correction.</title>' + metadata() + f"<style>{''.join(css)}</style>" + "".join(body)
            + "</svg>")


SPAWNS_W = 760
SPAWNS_H = 300
SPAWNS_T = 5.0
SPAWNS_COUNT = 6


def spawns() -> str:
    """Offsets turn one spawn marker into an area. Left shows the marker alone, right the spread."""
    css = ["@keyframes aimSpawnPop{0%{opacity:0;transform:scale(0.4)}4%{opacity:1;"
           "transform:scale(1)}14%{opacity:1;transform:scale(1)}18%{opacity:0;transform:scale(1)}"
           "100%{opacity:0}}",
           ".aim-spawn-pop{opacity:0;animation-name:aimSpawnPop;animation-iteration-count:infinite;"
           f"animation-duration:{SPAWNS_T}s}}"]
    body = []
    rng = random.Random(41)
    for index, (x, name, note) in enumerate((
            (12, "Offsets at zero", "every target on the marker"),
            (392, "Offsets widened", "a target anywhere in the box"))):
        cx, cy = x + 178, 168
        body.append(f'<rect x="{x}" y="46" width="356" height="{SPAWNS_H - 62}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        half_w, half_h = (0, 0) if index == 0 else (128, 62)
        if index == 1:
            body.append(f'<rect x="{cx - half_w}" y="{cy - half_h}" width="{half_w * 2}" '
                        f'height="{half_h * 2}" rx="8" class="fig-grid-stroke" stroke-width="2" '
                        'stroke-dasharray="7 6" fill="none"/>')
        # The marker itself, which both panels share and neither moves.
        body.append(f'<path d="M{cx - 9} {cy + 9}L{cx} {cy}L{cx + 9} {cy + 9}" '
                    'class="fig-muted-stroke" stroke-width="2" fill="none"/>')
        body.append(text(cx, cy + 96, "spawn point", "fig-muted", size=13, weight=500))
        for order in range(SPAWNS_COUNT):
            dx = rng.uniform(-half_w, half_w) if half_w else 0.0
            dy = rng.uniform(-half_h, half_h) if half_h else 0.0
            delay = order * SPAWNS_T / SPAWNS_COUNT
            body.append(f'<circle cx="{cx + dx:.1f}" cy="{cy + dy:.1f}" r="14" '
                        f'class="fig-target aim-spawn-pop" style="animation-delay:{delay:.2f}s;'
                        f'transform-origin:{cx + dx:.1f}px {cy + dy:.1f}px"/>')
    css.append("@media (prefers-reduced-motion:reduce){.aim-spawn-pop{opacity:1;"
               "animation:none!important;transform:none!important}}")
    return (f'<svg viewBox="0 0 {SPAWNS_W} {SPAWNS_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-spawns-title"><title id="fig-spawns-title">Two panels sharing a '
            'spawn marker. With offsets at zero every target appears on the marker itself. With the '
            'offsets widened, targets appear one after another at scattered points inside a box '
            'around the marker.</title>' + metadata() + f"<style>{''.join(css)}</style>"
            + "".join(body) + "</svg>")


TABS_W = 760
TABS_H = 300
TABS_T = 6.0


def chip(x: float, y: float, label: str, cls: str = "") -> str:
    """A small rounded token standing for a profile being moved between tabs."""
    return (f'<g class="{cls}"><rect x="{x}" y="{y}" width="132" height="34" rx="8" '
            'class="fig-panel fig-accent-stroke" stroke-width="2"/>'
            + text(x + 66, y + 17, label, "fig-accent-text", size=13, weight=600, middle=True)
            + "</g>")


def twotabs() -> str:
    """The trap the page warns about, run twice: naming a profile on Main only leaves challenge
    mode empty, and naming it on both fills it."""
    css = ["@keyframes aimTabsRun{0%{opacity:0}3%{opacity:1}44%{opacity:1}48%{opacity:0}"
           "100%{opacity:0}}",
           ".aim-tabs-step{opacity:0;animation-name:aimTabsRun;animation-iteration-count:infinite;"
           f"animation-duration:{TABS_T}s}}"]
    body = []
    for index, (x, name, note, reaches) in enumerate((
            (12, "Main only", "challenge mode stays empty", False),
            (392, "Main, then Challenge", "the profile is used", True))):
        body.append(f'<rect x="{x}" y="46" width="356" height="{TABS_H - 62}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        for slot, (label, filled) in enumerate((("Main", True), ("Challenge", reaches))):
            top = 82 + slot * 82
            body.append(f'<rect x="{x + 24}" y="{top}" width="308" height="62" rx="10" '
                        'class="fig-grid-stroke" stroke-width="2" fill="none"/>')
            body.append(text(x + 38, top + 18, label, "fig-muted", anchor="start", size=13,
                             weight=600))
            if filled:
                body.append(chip(x + 168, top + 16, "bot profile",
                                 f"aim-tabs-step aim-tabs-{index}{slot}"))
                css.append(f".aim-tabs-{index}{slot}{{animation-delay:{slot * 0.9:.2f}s}}")
            else:
                body.append(text(x + 234, top + 34, "nothing here", "fig-muted", size=13,
                                 weight=500))
        # The arrow between the two boxes only exists where the second step was taken.
        if reaches:
            body.append(f'<path d="M{x + 178} 144V164" class="fig-grid-stroke" stroke-width="2" '
                        'marker-end="url(#fig-tabs-arrow)"/>')
    css.append("@media (prefers-reduced-motion:reduce){.aim-tabs-step{opacity:1;"
               "animation:none!important}}")
    return (f'<svg viewBox="0 0 {TABS_W} {TABS_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-twotabs-title"><title id="fig-twotabs-title">Two panels, each with '
            'a Main box and a Challenge box. On the left the profile appears on Main and the '
            'Challenge box stays empty. On the right the profile appears on Main and then on '
            'Challenge as well.</title>'
            '<defs><marker id="fig-tabs-arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto">'
            '<path d="M0 0 L10 5 L0 10 Z" class="fig-grid-fill"/></marker></defs>'
            + metadata() + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


NOISE_W = 760
NOISE_H = 290
NOISE_T = 6.0
NOISE_RUNS = 12
NOISE_X0 = 80
NOISE_X1 = 700
NOISE_BASE = 210
NOISE_RISE = 62


def noise() -> str:
    """Twelve runs appearing one at a time. Any two neighbours disagree; the trend only shows once
    they are all on screen, which is the page's whole argument about a single result."""
    rng = random.Random(23)
    css = ["@keyframes aimNoiseDot{0%{opacity:0}3%{opacity:1}100%{opacity:1}}",
           ".aim-noise-dot{opacity:0;animation-name:aimNoiseDot;animation-iteration-count:infinite;"
           f"animation-duration:{NOISE_T}s}}",
           "@keyframes aimNoiseLine{0%{opacity:0}74%{opacity:0}82%{opacity:1}100%{opacity:1}}",
           ".aim-noise-line{opacity:0;animation-name:aimNoiseLine;animation-iteration-count:"
           f"infinite;animation-duration:{NOISE_T}s}}"]
    body = [f'<rect x="12" y="46" width="736" height="{NOISE_H - 62}" rx="12" class="fig-panel"/>']
    body.append(lane_label(32, 30, "Twelve runs of the same scenario", "the trend, not the run"))
    step = (NOISE_X1 - NOISE_X0) / (NOISE_RUNS - 1)
    for run in range(NOISE_RUNS):
        x = NOISE_X0 + run * step
        trend = NOISE_BASE - NOISE_RISE * run / (NOISE_RUNS - 1)
        y = trend + rng.uniform(-26, 26)
        delay = run * NOISE_T * 0.062
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" class="fig-target aim-noise-dot" '
                    f'style="animation-delay:{delay:.2f}s"/>')
    body.append(f'<path d="M{NOISE_X0} {NOISE_BASE}L{NOISE_X1} {NOISE_BASE - NOISE_RISE}" '
                'class="fig-accent-stroke aim-noise-line" stroke-width="3" '
                'stroke-linecap="round"/>')
    body.append(text(NOISE_X0, 252, "run 1", "fig-muted", anchor="start", size=13, weight=500))
    body.append(text(NOISE_X1, 252, "run 12", "fig-muted", anchor="end", size=13, weight=500))
    css.append("@media (prefers-reduced-motion:reduce){.aim-noise-dot,.aim-noise-line{opacity:1;"
               "animation:none!important}}")
    return (f'<svg viewBox="0 0 {NOISE_W} {NOISE_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-noise-title"><title id="fig-noise-title">Twelve scores from the '
            'same scenario appearing one at a time, scattered up and down so that neighbouring runs '
            'disagree. Once all twelve are shown, a rising line through them appears, which no '
            'single run would have revealed.</title>' + metadata()
            + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


UPLOAD_W = 760
UPLOAD_H = 280
UPLOAD_T = 7.0
UPLOAD_STAGES = (
    (60, "Local copy", "yours, editable"),
    (310, "Workshop", "uploaded, unique name"),
    (560, "Edited locally", "the arrow lights again"),
)


def upload() -> str:
    """The loop the page describes: upload, edit, re-upload. Shown as a cycle because the third
    stage returns to the second, which is the part readers miss."""
    css = ["@keyframes aimUpMove{0%{opacity:0}4%{opacity:1}26%{opacity:1}30%{opacity:0}"
           "100%{opacity:0}}",
           ".aim-up-token{opacity:0;animation-name:aimUpMove;animation-iteration-count:infinite;"
           f"animation-duration:{UPLOAD_T}s}}"]
    body = [f'<rect x="12" y="46" width="736" height="{UPLOAD_H - 74}" rx="12" class="fig-panel"/>']
    body.append(lane_label(32, 30, "Upload, edit, upload again", "an edit never travels on its own"))
    for order, (x, name, note) in enumerate(UPLOAD_STAGES):
        body.append(f'<rect x="{x}" y="96" width="140" height="70" rx="10" '
                    'class="fig-grid-stroke" stroke-width="2" fill="none"/>')
        body.append(text(x + 70, 124, name, "fig-ink", size=14, weight=700))
        body.append(text(x + 70, 146, note, "fig-muted", size=12, weight=500))
        if order < len(UPLOAD_STAGES) - 1:
            body.append(f'<path d="M{x + 148} 131H{x + 242}" class="fig-grid-stroke" '
                        'stroke-width="2" marker-end="url(#fig-up-arrow)"/>')
            # A token crosses each gap in turn, so the sequence reads left to right.
            body.append(f'<circle cx="{x + 152}" cy="131" r="8" '
                        f'class="fig-target aim-up-token aim-up-{order}"/>')
            css.append(f"@keyframes aimUpSlide{order}{{0%{{transform:translate(0,0)}}"
                       f"30%{{transform:translate(86px,0)}}100%{{transform:translate(86px,0)}}}}")
            css.append(f".aim-up-{order}{{animation-delay:{order * UPLOAD_T * 0.22:.2f}s;"
                       f"animation-name:aimUpMove,aimUpSlide{order};"
                       f"animation-duration:{UPLOAD_T}s,{UPLOAD_T}s}}")
    # The return leg: the third stage goes back to the workshop, not to a new entry.
    body.append(f'<path d="M{UPLOAD_STAGES[2][0] + 70} 174V206H{UPLOAD_STAGES[1][0] + 70}V174" '
                'class="fig-accent-stroke" stroke-width="2" stroke-dasharray="6 5" fill="none" '
                'marker-end="url(#fig-up-arrow-accent)"/>')
    body.append(text(435, 226, "re-upload, or the change reaches nobody", "fig-accent-text",
                     size=13, weight=600))
    css.append("@media (prefers-reduced-motion:reduce){.aim-up-token{opacity:1;"
               "animation:none!important}}")
    return (f'<svg viewBox="0 0 {UPLOAD_W} {UPLOAD_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-upload-title"><title id="fig-upload-title">Three stages in a row: '
            'a local copy, the workshop, and a locally edited copy. A token travels from the local '
            'copy to the workshop, then on to the edited copy. A return arrow runs from the edited '
            'copy back to the workshop, labelled as a re-upload without which the change reaches '
            'nobody.</title>'
            '<defs><marker id="fig-up-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
            'markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 Z" class="fig-grid-fill"/>'
            '</marker><marker id="fig-up-arrow-accent" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 Z" '
            'class="fig-accent-fill"/></marker></defs>'
            + metadata() + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


COPY_W = 760
COPY_H = 280
COPY_T = 6.0


def copying() -> str:
    """The section's premise in one loop: a published scenario is copied, unpacked into profiles,
    and one of them is replaced. Nothing here starts from an empty scenario."""
    css: list[str] = []
    body = [f'<rect x="12" y="46" width="736" height="{COPY_H - 72}" rx="12" class="fig-panel"/>']
    body.append(lane_label(32, 30, "Every scenario starts as a copy",
                           "the editor offers no blank one"))
    body.append(f'<rect x="44" y="110" width="150" height="66" rx="10" class="fig-grid-stroke" '
                'stroke-width="2" fill="none"/>')
    body.append(text(119, 138, "Existing", "fig-ink", size=14, weight=700))
    body.append(text(119, 160, "scenario", "fig-muted", size=12, weight=500))
    body.append('<path d="M202 143H262" class="fig-grid-stroke" stroke-width="2" '
                'marker-end="url(#fig-copy-arrow)"/>')
    body.append(text(232, 124, "unpack", "fig-muted", size=12, weight=500))
    for order, label in enumerate(("character", "bot", "dodge")):
        top = 96 + order * 40
        body.append(f'<g><rect x="276" y="{top}" width="150" height="32" rx="8" class="fig-panel '
                    'fig-grid-stroke" stroke-width="2"/>'
                    + text(351, top + 16, label, "fig-muted", size=13, weight=600, middle=True)
                    + "</g>")
    body.append('<path d="M436 143H496" class="fig-grid-stroke" stroke-width="2" '
                'marker-end="url(#fig-copy-arrow)"/>')
    body.append(text(466, 124, "replace", "fig-muted", size=12, weight=500))
    body.append('<g><rect x="510" y="110" width="176" height="66" rx="10" '
                'class="fig-panel fig-accent-stroke" stroke-width="2.4"/>'
                + text(598, 138, "Your scenario", "fig-accent-text", size=14, weight=700)
                + text(598, 160, "one profile changed", "fig-muted", size=12, weight=500)
                + "</g>")
    return (f'<svg viewBox="0 0 {COPY_W} {COPY_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-copying-title"><title id="fig-copying-title">An existing scenario '
            'on the left. Unpacking it produces a character profile, a bot profile and a dodge '
            'profile. Replacing one of them produces your own '
            'scenario on the right.</title>'
            '<defs><marker id="fig-copy-arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 Z" '
            'class="fig-grid-fill"/></marker></defs>'
            + metadata() + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


RECOIL_W = 760
RECOIL_H = 300
RECOIL_T = 4.8
RECOIL_SHOTS = 8


def recoil() -> str:
    """Recoil against per shot recoil. The left panel climbs somewhere new each burst; the right
    climbs the same way every time, which is what makes it learnable."""
    css = ["@keyframes aimRecMark{0%{opacity:0}3%{opacity:1}44%{opacity:1}50%{opacity:0}"
           "100%{opacity:0}}",
           ".aim-rec-mark{opacity:0;animation-name:aimRecMark;animation-iteration-count:infinite;"
           f"animation-duration:{RECOIL_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-rec-mark{opacity:1;"
           "animation:none!important}}"]
    body = []
    rng = random.Random(83)
    # One deterministic climb the right panel repeats, and two different climbs for the left.
    # Starts at the origin like the random climb does, so both panels fire their first shot from
    # the same point on the line and only the climb above it differs.
    pattern = [(i * 3.4, -i * 19.0) for i in range(RECOIL_SHOTS)]
    for index, (x, name, note) in enumerate((
            (12, "Recoil", "a new climb every burst"),
            (392, "Per shot recoil", "the same climb, learnable"))):
        cx, base = x + 178, 246
        body.append(f'<rect x="{x}" y="46" width="356" height="{RECOIL_H - 62}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        body.append(f'<path d="M{cx - 120} {base}H{cx + 120}" class="fig-grid-stroke" '
                    'stroke-width="2" opacity="0.6"/>')
        for half in range(2):
            if index == 0:
                climb = [(0.0, 0.0)] + [(rng.uniform(-30, 30), -i * 19.0 - rng.uniform(0, 9))
                                        for i in range(1, RECOIL_SHOTS)]
            else:
                climb = pattern
            points = " ".join(f"{cx + dx:.1f} {base + dy:.1f}" for dx, dy in climb)
            delay = half * RECOIL_T / 2
            body.append(f'<polyline points="{points}" class="fig-accent-stroke aim-rec-mark" '
                        f'stroke-width="2.4" fill="none" stroke-linejoin="round" '
                        f'style="animation-delay:{delay:.2f}s"/>')
            for order, (dx, dy) in enumerate(climb):
                body.append(f'<circle cx="{cx + dx:.1f}" cy="{base + dy:.1f}" r="5" '
                            f'class="fig-target aim-rec-mark" '
                            f'style="animation-delay:{delay + order * 0.03:.2f}s"/>')
    return (f'<svg viewBox="0 0 {RECOIL_W} {RECOIL_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-recoil-title"><title id="fig-recoil-title">Two panels firing two '
            'bursts each, with the shots joined into a climbing line. Under recoil, the two bursts '
            'climb along different lines. Under per shot recoil, both bursts climb along exactly '
            'the same line.</title>' + metadata() + f"<style>{''.join(css)}</style>"
            + "".join(body) + "</svg>")


REACT_W = 760
REACT_H = 300
REACT_T = 4.6
REACT_FRAMES = 48


def reactive() -> str:
    """A path you can learn against a path that answers you. Both targets move the same distance;
    only one of them can be anticipated, which is the distinction the page draws."""
    css = [".aim-react-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{REACT_T}s}}"]
    body = []
    rng = random.Random(5)
    for index, (x, name, note) in enumerate((
            (12, "Predictable", "learn it once, ride it"),
            (392, "Reactive", "cannot be anticipated"))):
        cx, cy = x + 178, 172
        body.append(f'<rect x="{x}" y="46" width="356" height="{REACT_H - 62}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        frames = []
        if index == 0:
            for i in range(REACT_FRAMES + 1):
                u = i / REACT_FRAMES
                frames.append((118 * math.sin(u * 6.28318), 40 * math.sin(u * 12.56636)))
        else:
            # Direction changes at irregular moments, so no cycle of it looks like the last.
            pos, target, held = 0.0, rng.uniform(-118, 118), 0
            for _ in range(REACT_FRAMES + 1):
                if held <= 0:
                    target = rng.uniform(-118, 118)
                    held = rng.randint(3, 8)
                pos += (target - pos) * 0.28
                held -= 1
                frames.append((pos, 40 * math.sin(pos / 40)))
        trail = " ".join(f"{cx + fx:.1f} {cy + fy:.1f}" for fx, fy in frames)
        body.append(f'<polyline points="{trail}" class="fig-grid-stroke" stroke-width="2" '
                    'fill="none" opacity="0.55"/>')
        body.append(text(cx, cy + 92, "the path it will take" if index == 0
                         else "the path it took once", "fig-muted", size=13, weight=500))
        body.append(f'<g class="aim-react-anim aim-react-{index}">'
                    f'<circle cx="{cx}" cy="{cy}" r="15" class="fig-target"/></g>')
        css.append(keyframes(f"aimReactPath{index}", frames,
                             lambda p: f"translate({p[0]:.1f}px,{p[1]:.1f}px)"))
        css.append(f".aim-react-{index}{{animation-name:aimReactPath{index}}}")
    css.append("@media (prefers-reduced-motion:reduce){.aim-react-anim{"
               f"animation-play-state:paused;animation-delay:-{REACT_T * 0.3:.2f}s!important}}}}")
    return (f'<svg viewBox="0 0 {REACT_W} {REACT_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-reactive-title"><title id="fig-reactive-title">Two panels with a '
            'moving target and its path drawn behind it. The predictable target traces a smooth '
            'repeating figure, the same every cycle. The reactive target jumps between directions '
            'at irregular intervals, so its drawn path is a record of one run rather than a '
            'prediction of the next.</title>' + metadata() + f"<style>{''.join(css)}</style>"
            + "".join(body) + "</svg>")


LOOP_W = 760
LOOP_H = 280
LOOP_T = 6.4


def testloop() -> str:
    """Two loops the page keeps apart. Editing a profile and pressing Play carries the change into
    the run. Editing in the Session Manager does not survive the save."""
    css = ["@keyframes aimLoopStep{0%{opacity:0.25}6%{opacity:1}30%{opacity:1}36%{opacity:0.25}"
           "100%{opacity:0.25}}",
           ".aim-loop-step{opacity:0.25;animation-name:aimLoopStep;animation-iteration-count:"
           f"infinite;animation-duration:{LOOP_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-loop-step{opacity:1;"
           "animation:none!important}}"]
    body = []
    for index, (x, name, note, keeps) in enumerate((
            (12, "Edit a profile", "Play applies it, no save needed", True),
            (392, "Edit the Session Manager", "the save drops it", False))):
        body.append(f'<rect x="{x}" y="46" width="356" height="{LOOP_H - 74}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        for order, label in enumerate(("edit", "play")):
            bx = x + 28 + order * 104
            body.append(f'<g class="aim-loop-step" style="animation-delay:'
                        f'{order * LOOP_T * 0.16:.2f}s">'
                        f'<rect x="{bx}" y="104" width="92" height="44" rx="9" '
                        'class="fig-panel fig-ink-stroke" stroke-width="2"/>'
                        + text(bx + 46, 126, label, "fig-ink", size=14, weight=600, middle=True)
                        + "</g>")
            if order == 0:
                body.append(f'<path d="M{bx + 96} 126H{bx + 108}" class="fig-grid-stroke" '
                            'stroke-width="2"/>')
        # The loop arrow says the two steps repeat without a save between them.
        body.append(f'<path d="M{x + 74} 152V178H{x + 178}V152" class="fig-grid-stroke" '
                    'stroke-width="2" stroke-dasharray="5 5" fill="none"/>')
        outcome = "kept" if keeps else "discarded"
        cls = "fig-balanced-fill" if keeps else "fig-tense-fill"
        body.append(f'<path d="M{x + 232} 126H{x + 244}" class="fig-grid-stroke" '
                    'stroke-width="2"/>')
        body.append(f'<g><rect x="{x + 244}" y="104" width="96" height="44" '
                    f'rx="9" class="fig-panel {cls.replace("-fill", "-stroke")}" stroke-width="2"/>'
                    + text(x + 292, 126, outcome, cls, size=13, weight=700, middle=True)
                    + "</g>")
        body.append(text(x + 292, 172, "on save", "fig-muted", size=12, weight=500))
    return (f'<svg viewBox="0 0 {LOOP_W} {LOOP_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-testloop-title"><title id="fig-testloop-title">Two panels, each '
            'looping between an edit step and a play step. On the left the edit is a profile change '
            'and the outcome on save is kept. On the right the edit is made in the Session Manager '
            'and the outcome on save is discarded.</title>' + metadata()
            + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


SCORE_W = 760
SCORE_H = 300
SCORE_T = 5.6
SCORE_SHOTS = 9


def scoring() -> str:
    """One identical run read by two score models. Whatever the model pays for is what the player
    will practise, which is the page's claim about inheriting a copied scenario's scoring."""
    # The same nine shots in both panels: five hits, four misses, in the same order.
    shots = [True, False, True, True, False, True, False, True, False]
    css = ["@keyframes aimScoreShot{0%{opacity:0}4%{opacity:1}100%{opacity:1}}",
           ".aim-score-shot{opacity:0;animation-name:aimScoreShot;animation-iteration-count:"
           f"infinite;animation-duration:{SCORE_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-score-shot{opacity:1;"
           "animation:none!important}}"]
    body = []
    for index, (x, name, note, per_hit, per_miss) in enumerate((
            (12, "Hits only", "rewards volume", 10, 0),
            (392, "Hits minus misses", "rewards restraint", 10, -10))):
        body.append(f'<rect x="{x}" y="46" width="356" height="{SCORE_H - 62}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        for order, hit in enumerate(shots):
            sx = x + 42 + order * 34
            # What this shot is worth, not the running total: a reader should be able to check the
            # arithmetic from the row itself rather than reconstruct it.
            value = per_hit if hit else per_miss
            label = f"+{value}" if value > 0 else str(value)
            tone = ("fig-balanced-fill" if value > 0 else
                    "fig-tense-fill" if value < 0 else "fig-muted")
            delay = order * SCORE_T * 0.075
            mark = (f'<circle cx="{sx}" cy="126" r="9" class="fig-target"/>' if hit else
                    f'<path d="M{sx - 7} 119l14 14M{sx + 7} 119l-14 14" class="fig-muted-stroke" '
                    'stroke-width="2.4"/>')
            body.append(f'<g class="aim-score-shot" style="animation-delay:{delay:.2f}s">{mark}'
                        + text(sx, 162, label, tone, size=12, weight=700) + "</g>")
        total = sum(per_hit if hit else per_miss for hit in shots)
        hits, misses = shots.count(True), shots.count(False)
        sums = (f"{hits} hits at +{per_hit}" if not per_miss
                else f"{hits} at +{per_hit}  ·  {misses} at {per_miss}")
        body.append(f'<g class="aim-score-shot" style="animation-delay:{SCORE_T * 0.72:.2f}s">'
                    + text(x + 178, 200, sums, "fig-muted", size=13, weight=500)
                    + text(x + 178, 232, f"total {total}", "fig-accent-text", size=20, weight=700)
                    + "</g>")
    return (f'<svg viewBox="0 0 {SCORE_W} {SCORE_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-scoring-title"><title id="fig-scoring-title">The same nine shots, '
            'five hits and four misses, scored twice. A model paying only for hits reaches fifty. A '
            'model subtracting for misses reaches ten. The run was identical in both '
            'cases.</title>' + metadata() + f"<style>{''.join(css)}</style>" + "".join(body)
            + "</svg>")


OBJ_W = 760
OBJ_H = 300
OBJ_T = 6.0


def gameobjects() -> str:
    """The three volumes that change what space does, each shown by what happens to a character
    that enters it: a teleporter, a jump pad and a hurt volume."""
    css = [".aim-obj-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{OBJ_T}s}}",
           "@keyframes aimObjHurt{0%{opacity:0}52%{opacity:0}56%{opacity:1}70%{opacity:0}"
           "100%{opacity:0}}",
           ".aim-obj-hurt{opacity:0;animation-name:aimObjHurt;animation-iteration-count:infinite;"
           f"animation-duration:{OBJ_T}s}}"]
    body = []
    for index, (x, name, note) in enumerate((
            (12, "Teleporter", "arrives at a named waypoint"),
            (263, "Jump pad", "launched toward a waypoint"),
            (514, "Hurt volume", "damage while inside"))):
        cx = x + 117
        body.append(f'<rect x="{x}" y="46" width="234" height="{OBJ_H - 62}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 16, 30, name, ""))
        body.append(text(cx, 254, note, "fig-muted", size=12, weight=500))
        volume_cls = "fig-tense-stroke" if index == 2 else "fig-cool-stroke"
        body.append(f'<rect x="{x + 34}" y="150" width="62" height="74" rx="8" '
                    f'class="{volume_cls}" stroke-width="2" stroke-dasharray="6 5" fill="none"/>')
        if index != 2:
            # The destination waypoint, which both the teleporter and the jump pad aim at.
            # Wide enough for the arriving character to sit inside it, so the marker still reads
            # once the animation lands on it.
            way_y = 110 if index else 186
            body.append(f'<circle cx="{x + 186}" cy="{way_y}" r="18" class="fig-grid-stroke" '
                        'stroke-width="2" stroke-dasharray="5 4" fill="none"/>')
            body.append(text(x + 186, way_y - 28, "waypoint", "fig-muted", size=11, weight=600))
        frames = []
        for i in range(41):
            u = i / 40
            if index == 0:
                # Walks in, vanishes at the volume, reappears standing on the waypoint.
                frames.append((0.0, 0.0) if u < 0.4 else (142.0, 0.0))
            elif index == 1:
                # Launched on an arc that peaks above the line and lands on the waypoint.
                if u < 0.35:
                    frames.append((u / 0.35 * 20, 0.0))
                else:
                    v = (u - 0.35) / 0.65
                    frames.append((20 + 122 * v, -76 * v - 34 * math.sin(v * 3.14159)))
            else:
                # Walks in and stays, which is what a damage-over-time volume punishes.
                frames.append((min(u / 0.4, 1.0) * 22, 0.0))
        body.append(f'<g class="aim-obj-anim aim-obj-{index}">'
                    f'<circle cx="{x + 44}" cy="186" r="11" class="fig-target"/></g>')
        css.append(keyframes(f"aimObjPath{index}", frames,
                             lambda p: f"translate({p[0]:.1f}px,{p[1]:.1f}px)"))
        css.append(f".aim-obj-{index}{{animation-name:aimObjPath{index}}}")
        if index == 2:
            body.append('<g class="aim-obj-hurt">'
                        + text(x + 66, 136, "-25 hp", "fig-tense-fill", size=14, weight=700)
                        + "</g>")
    css.append("@media (prefers-reduced-motion:reduce){.aim-obj-anim{animation-play-state:paused;"
               f"animation-delay:-{OBJ_T * 0.72:.2f}s!important}}"
               ".aim-obj-hurt{opacity:1;animation:none!important}}")
    return (f'<svg viewBox="0 0 {OBJ_W} {OBJ_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-gameobjects-title"><title id="fig-gameobjects-title">Three '
            'panels, each with a character entering a volume. The teleporter panel shows the '
            'character vanish and reappear at a named waypoint. The jump pad panel shows it '
            'launched on an arc toward a waypoint. The hurt volume panel shows it walk in, stay, '
            'and lose health.</title>' + metadata() + f"<style>{''.join(css)}</style>"
            + "".join(body) + "</svg>")


ISO_W = 760
ISO_H = 300
ISO_T = 5.4


def isolate() -> str:
    """A drill testing three things returns one number that moves for three reasons. Split it and
    each half says which part moved, which is the page's argument for one demand per scenario."""
    css = ["@keyframes aimIsoIn{0%{opacity:0}6%{opacity:1}100%{opacity:1}}",
           ".aim-iso-in{opacity:0;animation-name:aimIsoIn;animation-iteration-count:infinite;"
           f"animation-duration:{ISO_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-iso-in{opacity:1;"
           "animation:none!important}}"]
    body = []
    for index, (x, name, note, inputs) in enumerate((
            (12, "Three demands", "one number, three reasons",
             ("acquisition", "tracking", "movement")),
            (392, "Split in two", "one reason each",
             ("acquisition", "tracking")))):
        body.append(f'<rect x="{x}" y="46" width="356" height="{ISO_H - 62}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        for order, label in enumerate(inputs):
            top = 92 + order * 44
            body.append(f'<g class="aim-iso-in" style="animation-delay:{order * 0.4:.2f}s">'
                        f'<rect x="{x + 24}" y="{top}" width="130" height="34" rx="8" '
                        'class="fig-panel fig-grid-stroke" stroke-width="2"/>'
                        + text(x + 89, top + 17, label, "fig-muted", size=12, weight=600,
                               middle=True) + "</g>")
            if index == 0:
                body.append(f'<path d="M{x + 158} {top + 17}L{x + 214} 136" '
                            'class="fig-grid-stroke" stroke-width="2" opacity="0.6"/>')
            else:
                body.append(f'<path d="M{x + 158} {top + 17}H{x + 214}" class="fig-grid-stroke" '
                            'stroke-width="2" opacity="0.6"/>')
        if index == 0:
            body.append('<g>'
                        + text(x + 268, 130, "one score", "fig-tense-fill", size=16, weight=700)
                        + text(x + 268, 154, "moved: unknown", "fig-muted", size=12, weight=500)
                        + "</g>")
        else:
            for order, label in enumerate(("score A", "score B")):
                body.append(f'<g style="animation-delay:{order * 0.3:.2f}s">'
                            + text(x + 268, 114 + order * 44, label, "fig-balanced-fill", size=15,
                                   weight=700) + "</g>")
            body.append('<g>'
                        + text(x + 268, 204, "moved: readable", "fig-muted", size=12, weight=500)
                        + "</g>")
    return (f'<svg viewBox="0 0 {ISO_W} {ISO_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-isolate-title"><title id="fig-isolate-title">On the left, three '
            'demands feed into a single score, so when the score moves the cause is unknown. On the '
            'right, the drill is split so two demands feed two separate scores, and a change in '
            'either is readable.</title>' + metadata() + f"<style>{''.join(css)}</style>"
            + "".join(body) + "</svg>")


HEALTH_W = 760
HEALTH_H = 290
HEALTH_T = 5.0


def health() -> str:
    """Health on the character's Main tab decides how many hits a target costs. One hit makes a
    scenario about acquisition; several make it about staying on the target after the first."""
    css = ["@keyframes aimHpShot{0%{opacity:0}5%{opacity:1}22%{opacity:1}26%{opacity:0}"
           "100%{opacity:0}}",
           ".aim-hp-shot{opacity:0;animation-name:aimHpShot;animation-iteration-count:infinite;"
           f"animation-duration:{HEALTH_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-hp-shot{opacity:1;"
           "animation:none!important}}"]
    body = []
    for index, (x, name, note, hits) in enumerate((
            (12, "One hit", "acquisition only", 1),
            (392, "Three hits", "acquire, then stay on it", 3))):
        cx = x + 178
        body.append(f'<rect x="{x}" y="46" width="356" height="{HEALTH_H - 62}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        body.append(f'<circle cx="{cx}" cy="140" r="30" class="fig-target"/>')
        body.append(crosshair("fig-ink-stroke", cx, 140))
        # One pip per hit the target costs, filling left to right as the burst lands.
        span = 32 * hits
        for order in range(hits):
            px = cx - span / 2 + 16 + order * 32
            body.append(f'<rect x="{px - 11}" y="196" width="22" height="10" rx="5" '
                        'class="fig-grid-fill"/>')
            body.append(f'<rect x="{px - 11}" y="196" width="22" height="10" rx="5" '
                        'class="fig-accent-fill aim-hp-shot" '
                        f'style="animation-delay:{order * 0.45:.2f}s"/>')
        body.append(text(cx, 232, f"{hits} hit{'s' if hits > 1 else ''} to kill", "fig-muted",
                         size=13, weight=500))
    return (f'<svg viewBox="0 0 {HEALTH_W} {HEALTH_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-health-title"><title id="fig-health-title">Two panels with the '
            'same target and crosshair. On the left a single pip fills and the target dies to one '
            'hit. On the right three pips fill one after another, so the shot has to stay on the '
            'target after the first hit lands.</title>' + metadata()
            + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


TRAVEL_W = 760
TRAVEL_H = 340
TRAVEL_T = 3.6
TRAVEL_FRAMES = 48
# The scene is drawn from behind the player's own eyes: horizon, a target strafing across it, and
# the weapon in the corner of the screen. A top-down diagram cannot show a lead, because the whole
# point of a lead is that it is a distance on your screen rather than a distance in the world.
TRAVEL_TOP = 46
TRAVEL_BOTTOM = 326
TRAVEL_HORIZON = 214
TRAVEL_EYE = 186
TRAVEL_AMP = 96.0
# How far ahead of the target the projectile player holds, as a fraction of the strafe cycle. It is
# a phase rather than a fixed offset, so the lead grows and shrinks with the target's speed the way
# a real one does.
TRAVEL_LEAD = 0.12


def gun(x: float) -> str:
    """A weapon in the lower right of the view: barrel, receiver and a hint of a stock. Deliberately
    plain, because it is scenery for the crosshair rather than the subject of the figure."""
    muzzle_x, muzzle_y = x + 268, 262
    return (f'<path d="M{muzzle_x} {muzzle_y}L{x + 322} {TRAVEL_BOTTOM}" class="fig-muted-stroke" '
            'stroke-width="11" stroke-linecap="round" opacity="0.85"/>'
            f'<path d="M{x + 300} {muzzle_y + 40}L{x + 338} {muzzle_y + 32}" '
            'class="fig-muted-stroke" stroke-width="7" stroke-linecap="round" opacity="0.6"/>'
            f'<circle cx="{muzzle_x}" cy="{muzzle_y}" r="4" class="fig-muted-stroke" '
            'stroke-width="2" fill="none" opacity="0.85"/>')


def bot(cx: float) -> str:
    """The target, as a body rather than a dot: a lead reads as a distance beside a shape."""
    return (f'<rect x="{cx - 15}" y="{TRAVEL_EYE - 26}" width="30" height="58" rx="15" '
            'class="fig-target"/>'
            f'<circle cx="{cx}" cy="{TRAVEL_EYE - 38}" r="12" class="fig-target"/>')


def travel() -> str:
    css = [".aim-travel-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{TRAVEL_T}s}}",
           "@keyframes aimTravelFlash{0%{opacity:0}50%{opacity:0}54%{opacity:1}70%{opacity:1}"
           "74%{opacity:0}100%{opacity:0}}",
           ".aim-travel-flash{opacity:0;animation-name:aimTravelFlash;"
           f"animation-iteration-count:infinite;animation-duration:{TRAVEL_T}s}}",
           "@keyframes aimTravelRound{0%{opacity:0}50%{opacity:0}53%{opacity:1}75%{opacity:1}"
           "79%{opacity:0}100%{opacity:0}}",
           ".aim-travel-round{opacity:0;animation-name:aimTravelRound;"
           f"animation-iteration-count:infinite;animation-duration:{TRAVEL_T}s}}"]
    body = []
    for index, (x, name, note) in enumerate((
            (12, "Hitscan", "hold the crosshair on it"),
            (392, "Projectile", "hold the crosshair ahead of it"))):
        cx = x + 178
        muzzle_x, muzzle_y = x + 268, 262
        body.append(f'<clipPath id="fig-travel-clip{index}"><rect x="{x}" y="{TRAVEL_TOP}" '
                    f'width="356" height="{TRAVEL_BOTTOM - TRAVEL_TOP}" rx="12"/></clipPath>')
        body.append(f'<rect x="{x}" y="{TRAVEL_TOP}" width="356" '
                    f'height="{TRAVEL_BOTTOM - TRAVEL_TOP}" rx="12" class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        body.append(f'<g clip-path="url(#fig-travel-clip{index})">')
        # Ground below the horizon, with a few converging lines so the view reads as depth rather
        # than as a flat panel.
        body.append(f'<rect x="{x}" y="{TRAVEL_HORIZON}" width="356" '
                    f'height="{TRAVEL_BOTTOM - TRAVEL_HORIZON}" class="fig-grid-fill" '
                    'opacity="0.28"/>')
        for step in range(-3, 4):
            body.append(f'<path d="M{cx + step * 22} {TRAVEL_HORIZON}'
                        f'L{cx + step * 96} {TRAVEL_BOTTOM}" class="fig-grid-stroke" '
                        'stroke-width="1" opacity="0.4"/>')
        body.append(f'<path d="M{x} {TRAVEL_HORIZON}H{x + 356}" class="fig-grid-stroke" '
                    'stroke-width="1.5" opacity="0.7"/>')
        target = [(TRAVEL_AMP * math.sin(i / TRAVEL_FRAMES * 6.28318), 0.0)
                  for i in range(TRAVEL_FRAMES + 1)]
        aim = [(TRAVEL_AMP * math.sin((i / TRAVEL_FRAMES + (TRAVEL_LEAD if index else 0.0))
                                      * 6.28318), 0.0) for i in range(TRAVEL_FRAMES + 1)]
        if index:
            # Where the round is going, marked on the ground so the gap to the target is a distance
            # the reader can see rather than a claim in the caption.
            body.append(f'<g class="aim-travel-anim aim-travel-mark">'
                        f'<path d="M{cx} {TRAVEL_EYE - 52}V{TRAVEL_HORIZON + 6}" '
                        'class="fig-cool-stroke" stroke-width="2" stroke-dasharray="5 5"/></g>')
            css.append(keyframes("aimTravelMark", aim,
                                 lambda p: f"translate({p[0]:.1f}px,0)"))
            css.append(".aim-travel-mark{animation-name:aimTravelMark}")
        body.append(f'<g class="aim-travel-anim aim-travel-tgt{index}">{bot(cx)}</g>')
        css.append(keyframes(f"aimTravelTgt{index}", target,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".aim-travel-tgt{index}{{animation-name:aimTravelTgt{index}}}")
        if index == 0:
            # Hitscan resolves along the line the crosshair was already on.
            body.append(f'<g class="aim-travel-anim aim-travel-tgt{index}">'
                        f'<path d="M{muzzle_x} {muzzle_y}L{cx} {TRAVEL_EYE}" '
                        'class="fig-accent-stroke aim-travel-flash" stroke-width="3" '
                        'stroke-linecap="round"/></g>')
        else:
            body.append('<g class="aim-travel-round">'
                        f'<circle cx="{muzzle_x}" cy="{muzzle_y}" r="6" '
                        'class="fig-accent-fill aim-travel-round-move"/></g>')
            # Released at the half-cycle and landing at three quarters, where the target has swung
            # out to the far left: a long diagonal across the view rather than a hop above the gun.
            land_x = cx + TRAVEL_AMP * math.sin(0.75 * 6.28318) - muzzle_x
            land_y = TRAVEL_EYE - muzzle_y
            css.append("@keyframes aimTravelFly{0%{transform:translate(0,0)}"
                       "50%{transform:translate(0,0)}"
                       f"75%{{transform:translate({land_x:.1f}px,{land_y}px)}}"
                       f"100%{{transform:translate({land_x:.1f}px,{land_y}px)}}}}")
            css.append(".aim-travel-round-move{animation-name:aimTravelFly;"
                       f"animation-duration:{TRAVEL_T}s;animation-timing-function:linear;"
                       "animation-iteration-count:infinite}")
        # The crosshair is the reader's own aim, so it goes over everything else in the scene.
        body.append(f'<g class="aim-travel-anim aim-travel-aim{index}">'
                    f'{crosshair("fig-ink-stroke", cx, TRAVEL_EYE)}</g>')
        css.append(keyframes(f"aimTravelAim{index}", aim,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".aim-travel-aim{index}{{animation-name:aimTravelAim{index}}}")
        body.append(gun(x))
        body.append("</g>")
        body.append(text(cx, TRAVEL_BOTTOM - 14,
                         "the shot lands where you pointed" if index == 0
                         else "the round arrives after the target does", "fig-muted", size=13,
                         weight=500))
    # Held a tenth of the way in: the target is off-center, the projectile player's crosshair is
    # visibly ahead of it, and the round is still in the air between the two.
    # Held just past the shot: the target is out to the left, the crosshair is further left still,
    # and the round is halfway across the gap between the gun and where the target is heading.
    css.append("@media (prefers-reduced-motion:reduce){.aim-travel-anim,.aim-travel-round-move{"
               f"animation-play-state:paused;animation-delay:-{TRAVEL_T * 0.63:.2f}s!important}}"
               ".aim-travel-flash,.aim-travel-round{opacity:1;animation:none!important}}")
    return (f'<svg viewBox="0 0 {TRAVEL_W} {TRAVEL_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-travel-title"><title id="fig-travel-title">Two first-person views '
            'down a weapon at a target strafing across the screen. In the hitscan view the '
            'crosshair sits on the target and the shot resolves along that line. In the projectile '
            'view the crosshair is held to one side of the target, ahead of it, and the round is '
            'shown in flight toward the place the target is moving into.</title>'
            + metadata() + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


SNAP_W = 760
SNAP_H = 280
SNAP_T = 5.2


def gridsnap() -> str:
    """Grid snap decides how fine a move can be. The same drag lands on different places depending
    on the snap value, which is why the value is a setting and not a detail."""
    css = [".aim-snap-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{SNAP_T}s}}"]
    body = []
    for index, (x, name, note, snap) in enumerate((
            (12, "Coarse snap", "fast blockout, no fine work", 64),
            (392, "Fine snap", "small moves, slower", 16))):
        left, top = x + 30, 96
        body.append(f'<rect x="{x}" y="46" width="356" height="{SNAP_H - 62}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        # The grid the brush snaps to, drawn at the panel's own snap value.
        lines = []
        step = snap / 2
        column = float(left)
        while column <= left + 288:
            lines.append(f'M{column:.0f} {top}V{top + 96}')
            column += step
        row = float(top)
        while row <= top + 96:
            lines.append(f'M{left} {row:.0f}H{left + 288}')
            row += step
        body.append(f'<path d="{"".join(lines)}" class="fig-grid-stroke" stroke-width="1" '
                    'opacity="0.55" fill="none"/>')
        stops = [s for s in (0.0, step, step * 2, step * 3, step * 4) if s <= 288 - 56]
        frames = []
        for i in range(41):
            u = i / 40
            frames.append((stops[min(int(u * len(stops)), len(stops) - 1)], 0.0))
        body.append(f'<g class="aim-snap-anim aim-snap-{index}">'
                    f'<rect x="{left}" y="{top + 20}" width="56" height="56" rx="4" '
                    'class="fig-cool-stroke" stroke-width="2.4" fill="none"/></g>')
        css.append(keyframes(f"aimSnapStep{index}", frames,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".aim-snap-{index}{{animation-name:aimSnapStep{index}}}")
        body.append(text(x + 178, 232, f"snap {snap}", "fig-muted", size=13, weight=500))
    css.append("@media (prefers-reduced-motion:reduce){.aim-snap-anim{animation-play-state:paused;"
               f"animation-delay:-{SNAP_T * 0.45:.2f}s!important}}}}")
    return (f'<svg viewBox="0 0 {SNAP_W} {SNAP_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-gridsnap-title"><title id="fig-gridsnap-title">Two panels showing '
            'the same brush dragged across a grid. Under a coarse snap value it jumps in large '
            'steps and can only land on a few positions. Under a fine snap value it moves in small '
            'steps and can land almost anywhere.</title>' + metadata()
            + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


WEIGHT_W = 760
WEIGHT_H = 300
WEIGHT_T = 7.2
WEIGHT_FRAMES = 60


def weights() -> str:
    """A bot holding two dodge profiles at different weightings. Heavily weighted one way, the run
    is repeatable; evenly weighted, which behavior you get is luck."""
    css = [".aim-wt-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{WEIGHT_T}s}}"]
    body = []
    # Fixed leg orders rather than random ones, so the paused frame always catches the left panel
    # on a narrow strafe and the right panel on a wide one. Randomness here would sometimes freeze
    # the two panels looking identical, which is the opposite of the point.
    orders = ((False, False, False, True), (False, True, False, True))
    for index, (x, name, note) in enumerate((
            (12, "Weighted 90 / 10", "one behavior, mostly"),
            (392, "Weighted 50 / 50", "a coin flip each time"))):
        cx, cy = x + 178, 158
        body.append(f'<rect x="{x}" y="46" width="356" height="{WEIGHT_H - 62}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        frames = []
        for wide in orders[index]:
            amp = 132.0 if wide else 54.0
            for i in range(WEIGHT_FRAMES // 4):
                u = i / (WEIGHT_FRAMES // 4)
                frames.append((amp * math.sin(u * 6.28318), 0.0))
        frames.append((0.0, 0.0))
        # Each strafe's reach is drawn and labelled where it ends, so the target's position on a
        # frozen frame says which of the two profiles is running.
        body.append(f'<path d="M{cx - 132} {cy}H{cx + 132}" class="fig-grid-stroke" '
                    'stroke-width="2" opacity="0.45"/>')
        body.append(f'<path d="M{cx - 54} {cy}H{cx + 54}" class="fig-grid-stroke" '
                    'stroke-width="5" opacity="0.7" stroke-linecap="round"/>')
        body.append(text(cx + 54, cy - 22, "narrow", "fig-muted", size=12, weight=600))
        body.append(text(cx + 132, cy + 32, "wide", "fig-muted", size=12, weight=600))
        body.append(f'<g class="aim-wt-anim aim-wt-{index}">'
                    f'<circle cx="{cx}" cy="{cy}" r="15" class="fig-target"/></g>')
        css.append(keyframes(f"aimWtPath{index}", frames,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".aim-wt-{index}{{animation-name:aimWtPath{index}}}")
    # A quarter into the second leg: both panels sit at the far end of whichever strafe they are
    # running, so the difference in reach is the whole picture.
    css.append("@media (prefers-reduced-motion:reduce){.aim-wt-anim{animation-play-state:paused;"
               f"animation-delay:-{WEIGHT_T * 0.3125:.2f}s!important}}}}")
    return (f'<svg viewBox="0 0 {WEIGHT_W} {WEIGHT_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-weights-title"><title id="fig-weights-title">Two panels showing a '
            'bot running four strafes per cycle along a short narrow track and a long wide one. '
            'Weighted ninety to ten, nearly every strafe is the narrow one. Weighted fifty to '
            'fifty, narrow and wide strafes alternate unpredictably.</title>' + metadata()
            + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


WEAK_W = 760
WEAK_H = 280
WEAK_T = 5.0
# Six subcategory scores. The lowest is not the one that feels worst, which is the page's point, so
# the bars are deliberately close together rather than one obvious trough.
WEAK_SCORES = (("static", 0.78), ("dynamic", 0.71), ("precise", 0.52),
               ("reactive", 0.74), ("speed", 0.81), ("evasive", 0.69))


def weakest() -> str:
    """A benchmark read as a shape rather than a rank: the lowest bar is the scenario to build."""
    css = ["@keyframes aimWeakGrow{0%{transform:scaleY(0)}18%{transform:scaleY(1)}"
           "100%{transform:scaleY(1)}}",
           ".aim-weak-bar{transform-box:fill-box;transform-origin:center bottom;"
           "animation-name:aimWeakGrow;"
           f"animation-iteration-count:infinite;animation-duration:{WEAK_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-weak-bar{animation:none!important}}"]
    base, top = 206, 84
    body = [f'<rect x="12" y="46" width="736" height="{WEAK_H - 72}" rx="12" class="fig-panel"/>']
    body.append(lane_label(32, 30, "Your last benchmark", "lowest relative, not worst feeling"))
    lowest = min(range(len(WEAK_SCORES)), key=lambda i: WEAK_SCORES[i][1])
    for order, (name, score) in enumerate(WEAK_SCORES):
        x = 72 + order * 108
        height = (base - top) * score
        fill = "fig-accent-fill" if order == lowest else "fig-grid-fill"
        body.append(f'<rect x="{x}" y="{base - height:.1f}" width="56" height="{height:.1f}" '
                    f'rx="4" class="{fill} aim-weak-bar" '
                    f'style="animation-delay:{order * 0.09:.2f}s"/>')
        body.append(text(x + 28, base + 20, name, "fig-muted", size=12, weight=500))
    px = 72 + lowest * 108
    body.append(f'<g><path d="M{px + 28} {base + 34}V{base + 48}" '
                'class="fig-accent-stroke" stroke-width="2"/>'
                + text(px + 28, base + 66, "build for this one", "fig-accent-text", size=13,
                       weight=700) + "</g>")
    return (f'<svg viewBox="0 0 {WEAK_W} {WEAK_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-weakest-title"><title id="fig-weakest-title">Six subcategory '
            'scores drawn as bars of similar height. The shortest bar is highlighted and labelled '
            'as the one to build a scenario for, even though several others are close to '
            'it.</title>' + metadata() + f"<style>{''.join(css)}</style>" + "".join(body)
            + "</svg>")


DELIB_W = 760
DELIB_H = 290
DELIB_T = 6.0
DELIB_STEPS = (("a defined goal", "one demand, named"),
               ("feedback each attempt", "a stat or a replay"),
               ("harder as you improve", "or it stops teaching"))


def deliberate() -> str:
    """The loop the research describes, drawn as a loop: without the third step it is repetition."""
    css = ["@keyframes aimDelStep{0%{opacity:0.22}8%{opacity:1}30%{opacity:1}38%{opacity:0.22}"
           "100%{opacity:0.22}}",
           ".aim-del-step{opacity:0.22;animation-name:aimDelStep;animation-iteration-count:"
           f"infinite;animation-duration:{DELIB_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-del-step{opacity:1;"
           "animation:none!important}}"]
    body = [f'<rect x="12" y="46" width="736" height="{DELIB_H - 76}" rx="12" class="fig-panel"/>']
    body.append(lane_label(32, 30, "What makes practice purposeful", "drop a step and it is reps"))
    for order, (name, note) in enumerate(DELIB_STEPS):
        x = 56 + order * 224
        body.append(f'<g class="aim-del-step" style="animation-delay:{order * DELIB_T * 0.2:.2f}s">'
                    f'<rect x="{x}" y="100" width="188" height="66" rx="10" '
                    'class="fig-panel fig-ink-stroke" stroke-width="2"/>'
                    + text(x + 94, 128, name, "fig-ink", size=14, weight=700)
                    + text(x + 94, 150, note, "fig-muted", size=12, weight=500) + "</g>")
        if order < len(DELIB_STEPS) - 1:
            body.append(f'<path d="M{x + 196} 133H{x + 216}" class="fig-grid-stroke" '
                        'stroke-width="2" marker-end="url(#fig-del-arrow)"/>')
    # The return leg: getting harder is what sends you back to a new goal rather than to more reps.
    body.append('<path d="M694 174V212H150V174" class="fig-grid-stroke" stroke-width="2" '
                'stroke-dasharray="6 5" fill="none" marker-end="url(#fig-del-arrow)"/>')
    body.append(text(420, 232, "then a new goal, not more of the same", "fig-muted", size=13,
                     weight=500))
    return (f'<svg viewBox="0 0 {DELIB_W} {DELIB_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-deliberate-title"><title id="fig-deliberate-title">Three steps in '
            'a row, lighting one after another: a defined goal, feedback on each attempt, and '
            'getting harder as you improve. A return arrow runs from the third back to the first, '
            'labelled as a new goal rather than more of the same.</title>'
            '<defs><marker id="fig-del-arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 Z" '
            'class="fig-grid-fill"/></marker></defs>'
            + metadata() + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


DEC_W = 760
DEC_H = 300
DEC_T = 6.4
DEC_QUESTIONS = (("What should be hard?", "one demand, in a sentence"),
                 ("How hard?", "you fail in one nameable way"),
                 ("What should be quiet?", "everything not under test"),
                 ("How will you know?", "the scenario you compare against"))


def decisions() -> str:
    """The four questions, answered before the editor opens. They arrive in order because each one
    is only answerable once the one above it is settled."""
    css = ["@keyframes aimDecIn{0%{opacity:0;transform:translateX(-10px)}"
           "7%{opacity:1;transform:translateX(0)}100%{opacity:1;transform:translateX(0)}}",
           ".aim-dec-row{opacity:0;animation-name:aimDecIn;animation-iteration-count:infinite;"
           f"animation-duration:{DEC_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-dec-row{opacity:1;"
           "animation:none!important;transform:none!important}}"]
    body = [f'<rect x="12" y="46" width="736" height="{DEC_H - 70}" rx="12" class="fig-panel"/>']
    body.append(lane_label(32, 30, "Before the editor opens", "four answers, in this order"))
    for order, (question, note) in enumerate(DEC_QUESTIONS):
        y = 88 + order * 50
        body.append(f'<g class="aim-dec-row" style="animation-delay:{order * DEC_T * 0.14:.2f}s">'
                    f'<circle cx="64" cy="{y + 13}" r="13" class="fig-accent-stroke" '
                    'stroke-width="2" fill="none"/>'
                    + text(64, y + 14, str(order + 1), "fig-accent-text", size=12, weight=700,
                           middle=True)
                    + text(92, y + 8, question, "fig-ink", anchor="start", size=15, weight=700)
                    + text(92, y + 28, note, "fig-muted", anchor="start", size=12, weight=500)
                    + "</g>")
    return (f'<svg viewBox="0 0 {DEC_W} {DEC_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-decisions-title"><title id="fig-decisions-title">Four numbered '
            'questions appearing one after another: what should be hard, how hard, what should be '
            'quiet, and how will you know it worked. Each carries a one-line note on what answering '
            'it means.</title>' + metadata() + f"<style>{''.join(css)}</style>" + "".join(body)
            + "</svg>")


LOWEFF_W = 760
LOWEFF_H = 290
LOWEFF_T = 6.0


def loweffort() -> str:
    """Two uploads of the same donor scenario. Only the one that changed something survives, which
    is the workshop's own stated rule rather than a matter of taste."""
    css = ["@keyframes aimLowIn{0%{opacity:0}6%{opacity:1}100%{opacity:1}}",
           ".aim-low-in{opacity:0;animation-name:aimLowIn;animation-iteration-count:infinite;"
           f"animation-duration:{LOWEFF_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-low-in{opacity:1;"
           "animation:none!important}}"]
    body = []
    for index, (x, name, change, verdict, tone) in enumerate((
            (12, "Renamed only", "nothing but the title", "removed", "fig-tense-fill"),
            (392, "Actually changed", "a demand the original lacked", "stays", "fig-balanced-fill"))):
        body.append(f'<rect x="{x}" y="46" width="356" height="{LOWEFF_H - 72}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, ""))
        for slot, label in enumerate(("the original", "your upload")):
            top = 88 + slot * 62
            body.append(f'<g class="aim-low-in" style="animation-delay:{slot * 0.5:.2f}s">'
                        f'<rect x="{x + 28}" y="{top}" width="300" height="48" rx="9" '
                        'class="fig-panel fig-grid-stroke" stroke-width="2"/>'
                        + text(x + 178, top + 20, label, "fig-muted", size=12, weight=600)
                        + text(x + 178, top + 38, change if slot else "someone else's work",
                               "fig-muted", size=11, weight=500) + "</g>")
        body.append(f'<g>'
                    f'<rect x="{x + 108}" y="218" width="140" height="36" rx="9" '
                    f'class="fig-panel {tone.replace("-fill", "-stroke")}" stroke-width="2"/>'
                    + text(x + 178, 236, verdict, tone, size=14, weight=700, middle=True)
                    + "</g>")
    return (f'<svg viewBox="0 0 {LOWEFF_W} {LOWEFF_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-loweffort-title"><title id="fig-loweffort-title">Two uploads of '
            'the same original scenario. The one that changed only the title is marked removed. The '
            'one that added a demand the original lacked is marked as staying.</title>'
            + metadata() + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


ANCHOR_W = 760
ANCHOR_H = 290
ANCHOR_T = 5.6


def anchor() -> str:
    """A new scenario's score against a known one's. Alone the new number is unreadable; beside a
    scenario you have a history on, it says what kind of day you are having."""
    css = ["@keyframes aimAncIn{0%{opacity:0}8%{opacity:1}100%{opacity:1}}",
           ".aim-anc-in{opacity:0;animation-name:aimAncIn;animation-iteration-count:infinite;"
           f"animation-duration:{ANCHOR_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-anc-in{opacity:1;"
           "animation:none!important}}"]
    body = [f'<rect x="12" y="46" width="736" height="{ANCHOR_H - 72}" rx="12" class="fig-panel"/>']
    body.append(lane_label(32, 30, "One session, two scenarios", "the known one is the reading"))
    # The familiar scenario's own history, which is what turns today's number into information.
    history = (0.62, 0.71, 0.58, 0.74, 0.66)
    base, top = 196, 96
    for order, v in enumerate(history):
        x = 96 + order * 34
        body.append(f'<circle cx="{x}" cy="{base - (base - top) * v:.1f}" r="5" '
                    'class="fig-grid-fill"/>')
    body.append(f'<path d="M92 {base - (base - top) * 0.66:.1f}H272" class="fig-grid-stroke" '
                'stroke-width="2" stroke-dasharray="5 5" opacity="0.8"/>')
    body.append(text(180, 226, "known scenario", "fig-ink", size=14, weight=700))
    body.append(text(180, 246, "five runs of history", "fig-muted", size=12, weight=500))
    body.append(f'<g class="aim-anc-in"><circle cx="{96 + 5 * 34}" cy="{base - (base - top) * 0.55:.1f}" '
                'r="8" class="fig-accent-fill"/></g>')
    body.append(text(96 + 5 * 34, 226, "today", "fig-accent-text", size=13, weight=700))
    body.append(f'<path d="M330 90V210" class="fig-grid-stroke" stroke-width="1.5" '
                'stroke-dasharray="4 6" opacity="0.7"/>')
    # The new scenario: one point, no line, nothing to read it against on its own.
    body.append('<g class="aim-anc-in" style="animation-delay:0.7s">'
                f'<circle cx="470" cy="{base - (base - top) * 0.6:.1f}" r="8" '
                'class="fig-accent-fill"/></g>')
    body.append(text(470, 226, "new scenario", "fig-ink", size=14, weight=700))
    body.append(text(470, 246, "one run, no history", "fig-muted", size=12, weight=500))
    body.append('<g>'
                + text(620, 140, "known run low today", "fig-muted", size=13, weight=500)
                + text(620, 164, "so the new one is not", "fig-balanced-fill", size=14, weight=700)
                + text(620, 186, "the design's fault", "fig-balanced-fill", size=14, weight=700)
                + "</g>")
    return (f'<svg viewBox="0 0 {ANCHOR_W} {ANCHOR_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-anchor-title"><title id="fig-anchor-title">On the left a familiar '
            'scenario with five runs of history and today\\u2019s run below its average. On the right a '
            'new scenario with a single run and nothing to compare it against. A note concludes that '
            'because the known run was low today, the new scenario\\u2019s score is not evidence about '
            'its design.</title>' + metadata() + f"<style>{''.join(css)}</style>" + "".join(body)
            + "</svg>")


COMFY_W = 760
COMFY_H = 290
COMFY_T = 4.8


def comfortable() -> str:
    """A drill that feels easy on the first run is usually mis-set: either the difficulty is under
    you, or a shortcut exists and you already found it."""
    css = ["@keyframes aimCfyHit{0%{opacity:0}5%{opacity:1}100%{opacity:1}}",
           ".aim-cfy-hit{opacity:0;animation-name:aimCfyHit;animation-iteration-count:infinite;"
           f"animation-duration:{COMFY_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-cfy-hit{opacity:1;"
           "animation:none!important}}"]
    body = []
    for index, (x, name, hits, verdict) in enumerate((
            (12, "Every rep clean", 9, "difficulty is under you"),
            (392, "Clean a different way", 9, "a shortcut you already found"))):
        body.append(f'<rect x="{x}" y="46" width="356" height="{COMFY_H - 72}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, ""))
        for order in range(hits):
            cx = x + 54 + (order % 5) * 62
            cy = 108 + (order // 5) * 56
            body.append(f'<g class="aim-cfy-hit" style="animation-delay:{order * 0.08:.2f}s">'
                        f'<circle cx="{cx}" cy="{cy}" r="15" class="fig-target"/>'
                        f'<path d="M{cx - 6} {cy}l4 5l8 -10" class="fig-panel" fill="none" '
                        'stroke="currentColor" stroke-width="2.4" stroke-linecap="round" '
                        'stroke-linejoin="round"/></g>')
        body.append(f'<g>'
                    + text(x + 178, 246, verdict, "fig-tense-fill", size=14, weight=700) + "</g>")
    return (f'<svg viewBox="0 0 {COMFY_W} {COMFY_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-comfortable-title"><title id="fig-comfortable-title">Two panels, '
            'each showing nine clean hits in a row. The first is labelled as difficulty set below '
            'you, the second as a shortcut you have already found. Neither is a drill working as '
            'intended.</title>' + metadata() + f"<style>{''.join(css)}</style>" + "".join(body)
            + "</svg>")


FREEZE_W = 760
FREEZE_H = 290
FREEZE_T = 6.4


def freeze() -> str:
    """Every edit restarts the history. A scenario you keep tuning can never show improvement,
    because it is never the same scenario twice."""
    css = ["@keyframes aimFrzDot{0%{opacity:0}6%{opacity:1}100%{opacity:1}}",
           ".aim-frz-dot{opacity:0;animation-name:aimFrzDot;animation-iteration-count:infinite;"
           f"animation-duration:{FREEZE_T}s}}",
           "@keyframes aimFrzCut{0%{opacity:0}4%{opacity:1}100%{opacity:1}}",
           ".aim-frz-cut{opacity:0;animation-name:aimFrzCut;animation-iteration-count:infinite;"
           f"animation-duration:{FREEZE_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-frz-dot,.aim-frz-cut{opacity:1;"
           "animation:none!important}}"]
    body = []
    for index, (x, name, note, edits) in enumerate((
            (12, "Edited every session", "three runs, then nothing", (3, 6)),
            (392, "Frozen after the build", "nine runs of one thing", ()))):
        body.append(f'<rect x="{x}" y="46" width="356" height="{FREEZE_H - 72}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        base, top = 190, 100
        body.append(f'<path d="M{x + 36} {base}H{x + 324}" class="fig-grid-stroke" '
                    'stroke-width="1.5" opacity="0.7"/>')
        # A rising trend only exists where the runs belong to the same scenario.
        for order in range(9):
            cx = x + 52 + order * 34
            run = order % 3 if edits else order
            span = 2 if edits else 8
            cy = base - (base - top) * (0.25 + 0.7 * run / span)
            body.append(f'<circle cx="{cx}" cy="{cy:.1f}" r="6" class="fig-target aim-frz-dot" '
                        f'style="animation-delay:{order * 0.2:.2f}s"/>')
        for order, cut in enumerate(edits):
            cx = x + 52 + cut * 34 - 17
            body.append(f'<g class="aim-frz-cut" style="animation-delay:{cut * 0.2:.2f}s">'
                        f'<path d="M{cx} {top - 14}V{base + 14}" class="fig-tense-stroke" '
                        'stroke-width="2" stroke-dasharray="4 4"/>'
                        + text(cx, top - 22, "edit", "fig-tense-fill", size=11, weight=700)
                        + "</g>")
        body.append(text(x + 178, 232, "no trend, three times" if edits else "a trend you can read",
                         "fig-muted", size=13, weight=500))
    return (f'<svg viewBox="0 0 {FREEZE_W} {FREEZE_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-freeze-title"><title id="fig-freeze-title">Two panels of nine '
            'runs. On the left the scenario is edited twice, so the runs form three short unrelated '
            'climbs and no overall trend. On the right it is left alone and the nine runs form one '
            'rising line.</title>' + metadata() + f"<style>{''.join(css)}</style>" + "".join(body)
            + "</svg>")


TRADE_W = 760
TRADE_H = 300
TRADE_T = 6.0
TRADE_FRAMES = 40


def tradeoff() -> str:
    """Speed against accuracy as a curve you ride rather than a rule you obey. The rider sweeps up
    the pace axis and accuracy falls away under it, which is the exchange being measurable."""
    css = [".aim-trd-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{TRADE_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-trd-anim{animation-play-state:paused;"
           f"animation-delay:-{TRADE_T * 0.62:.2f}s!important}}}}"]
    left, right, base, top = 96, 660, 234, 82
    body = [f'<rect x="12" y="46" width="736" height="{TRADE_H - 70}" rx="12" class="fig-panel"/>']
    body.append(lane_label(32, 30, "Pace against accuracy", "the exchange is measurable"))

    def acc(u: float) -> float:
        # Flat while there is headroom, then falling away: pace is cheap until it is not.
        return 0.94 - 0.78 * u ** 2.1

    def px(u: float) -> float:
        return left + (right - left) * u

    def py(a: float) -> float:
        return base - (base - top) * a

    curve = " ".join(f"{px(i / 60):.1f} {py(acc(i / 60)):.1f}" for i in range(61))
    body.append(f'<path d="M{left} {base}H{right}" class="fig-grid-stroke" stroke-width="1.5"/>')
    body.append(f'<path d="M{left} {base}V{top - 8}" class="fig-grid-stroke" stroke-width="1.5"/>')
    body.append(text(left - 12, top + 4, "accuracy", "fig-muted", anchor="end", size=12,
                     weight=500))
    body.append(text(right, base + 24, "pace", "fig-muted", anchor="end", size=12, weight=500))
    body.append(f'<polyline points="{curve}" class="fig-accent-stroke" stroke-width="3" '
                'fill="none" stroke-linecap="round"/>')
    # The band worth training in: fast enough to cost something, slow enough to still land.
    body.append(f'<g><rect x="{px(0.34):.1f}" y="{top - 6}" '
                f'width="{px(0.62) - px(0.34):.1f}" height="{base - top + 6:.1f}" rx="6" '
                'class="fig-balanced-fill" opacity="0.16"/>'
                + text((px(0.34) + px(0.62)) / 2, base + 48, "build accuracy here, then push",
                       "fig-balanced-fill", size=13, weight=700) + "</g>")
    frames = [(px(i / TRADE_FRAMES) - left, py(acc(i / TRADE_FRAMES)) - base)
              for i in range(TRADE_FRAMES + 1)]
    body.append(f'<g class="aim-trd-anim aim-trd-ride">'
                f'<circle cx="{left}" cy="{base}" r="9" class="fig-target"/></g>')
    css.append(keyframes("aimTrdRide", frames, lambda p: f"translate({p[0]:.1f}px,{p[1]:.1f}px)"))
    css.append(".aim-trd-ride{animation-name:aimTrdRide}")
    return (f'<svg viewBox="0 0 {TRADE_W} {TRADE_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-tradeoff-title"><title id="fig-tradeoff-title">A curve of accuracy '
            'against pace. It stays high while pace is low, then falls away steeply. A marker rides '
            'along it, and a band over the middle marks the range where accuracy is worth building '
            'before pace is pushed further.</title>' + metadata()
            + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


SLOW_W = 760
SLOW_H = 300
SLOW_T = 4.4
SLOW_FRAMES = 44


def slower() -> str:
    """The same correction at two paces. Slow, the crosshair lands once; fast, it overshoots and
    saws back, which is the habit a slowed-down variant is there to stop you building."""
    css = [".aim-slw-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{SLOW_T}s}}"]
    body = []
    for index, (x, name, note) in enumerate((
            (12, "At a pace you can hit", "one motion, lands clean"),
            (392, "Past it", "overshoot, then saw back"))):
        cx, cy = x + 178, 164
        body.append(f'<rect x="{x}" y="46" width="356" height="{SLOW_H - 74}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        body.append(f'<circle cx="{cx + 92}" cy="{cy}" r="26" class="fig-target" opacity="0.9"/>')
        frames = []
        for i in range(SLOW_FRAMES + 1):
            u = i / SLOW_FRAMES
            if index == 0:
                frames.append((-92 + 184 * smooth(min(u / 0.55, 1.0)) * 0.5 + 46 * 0, 0.0))
            else:
                # Overshoot past the target, then two shrinking corrections back onto it.
                if u < 0.36:
                    pos = -92 + 150 * smooth(u / 0.36)
                elif u < 0.56:
                    pos = 58 - 38 * smooth((u - 0.36) / 0.20)
                elif u < 0.76:
                    pos = 20 + 22 * smooth((u - 0.56) / 0.20)
                else:
                    pos = 42 - 4 * smooth((u - 0.76) / 0.24)
                frames.append((pos, 0.0))
        if index == 0:
            frames = [(-92 + 184 * smooth(min(i / SLOW_FRAMES / 0.62, 1.0)) * 0.5, 0.0)
                      for i in range(SLOW_FRAMES + 1)]
        body.append(f'<path d="M{cx - 92} {cy}H{cx + 92}" class="fig-grid-stroke" '
                    'stroke-width="2" stroke-dasharray="5 5" opacity="0.6"/>')
        body.append(f'<g class="aim-slw-anim aim-slw-{index}">'
                    f'{crosshair("fig-ink-stroke", cx - 92, cy)}</g>')
        css.append(keyframes(f"aimSlwPath{index}", frames,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".aim-slw-{index}{{animation-name:aimSlwPath{index}}}")
        body.append(text(cx, 244, "one correction" if index == 0 else "three corrections",
                         "fig-muted", size=13, weight=500))
    css.append("@media (prefers-reduced-motion:reduce){.aim-slw-anim{animation-play-state:paused;"
               f"animation-delay:-{SLOW_T * 0.62:.2f}s!important}}}}")
    return (f'<svg viewBox="0 0 {SLOW_W} {SLOW_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-slower-title"><title id="fig-slower-title">Two panels with the '
            'same target and the same distance to cover. At a manageable pace the crosshair travels '
            'once and stops on the target. Pushed past it, the crosshair overshoots and corrects '
            'back twice before settling.</title>' + metadata()
            + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


STAGE_W = 760
STAGE_H = 290
STAGE_T = 5.2


def stage() -> str:
    """What difficulty is for changes with the stage. Early it has to let the movement happen at
    all; later the useful work is at the edge of what holds together."""
    css = ["@keyframes aimStgIn{0%{opacity:0}8%{opacity:1}100%{opacity:1}}",
           ".aim-stg-in{opacity:0;animation-name:aimStgIn;animation-iteration-count:infinite;"
           f"animation-duration:{STAGE_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-stg-in{opacity:1;"
           "animation:none!important}}"]
    body = []
    for index, (x, name, note, band, mark) in enumerate((
            (12, "Learning it", "room to get it right", (0.12, 0.46), 0.3),
            (392, "Owning it", "work at the edge", (0.58, 0.9), 0.78))):
        left, right, y = x + 44, x + 312, 160
        body.append(f'<rect x="{x}" y="46" width="356" height="{STAGE_H - 74}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        body.append(f'<path d="M{left} {y}H{right}" class="fig-grid-stroke" stroke-width="2"/>')
        body.append(text(left, y + 34, "easy", "fig-muted", size=12, weight=500))
        body.append(text(right, y + 34, "past you", "fig-muted", size=12, weight=500))
        span = right - left
        body.append(f'<g class="aim-stg-in"><rect x="{left + span * band[0]:.1f}" y="{y - 22}" '
                    f'width="{span * (band[1] - band[0]):.1f}" height="44" rx="8" '
                    'class="fig-balanced-fill" opacity="0.22"/></g>')
        body.append(f'<g class="aim-stg-in" style="animation-delay:0.5s">'
                    f'<circle cx="{left + span * mark:.1f}" cy="{y}" r="9" '
                    'class="fig-accent-fill"/></g>')
        body.append(text(x + 178, 236, "set it where the motion holds" if index == 0
                         else "set it where it just stops holding", "fig-muted", size=13,
                         weight=500))
    return (f'<svg viewBox="0 0 {STAGE_W} {STAGE_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-stage-title"><title id="fig-stage-title">Two difficulty scales '
            'running from easy to past you. While learning, the useful band sits toward the easy '
            'end, where the movement can come together. Once the skill is owned, the band sits near '
            'the far end, at the edge of what still holds.</title>' + metadata()
            + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


VER_W = 760
VER_H = 290
VER_T = 5.6


def versions() -> str:
    """Two ways to make a second version. One dial changed tells you what that dial does; five
    changed tells you only that something moved."""
    css = ["@keyframes aimVerIn{0%{opacity:0}8%{opacity:1}100%{opacity:1}}",
           ".aim-ver-in{opacity:0;animation-name:aimVerIn;animation-iteration-count:infinite;"
           f"animation-duration:{VER_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-ver-in{opacity:1;"
           "animation:none!important}}"]
    dials = ("size", "spread", "speed", "bots", "time")
    body = []
    for index, (x, name, changed, verdict, tone) in enumerate((
            (12, "One dial moved", {0}, "you learned what size does", "fig-balanced-fill"),
            (392, "Five dials moved", {0, 1, 2, 3, 4}, "you learned nothing", "fig-tense-fill"))):
        body.append(f'<rect x="{x}" y="46" width="356" height="{VER_H - 72}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, ""))
        for order, dial in enumerate(dials):
            cy = 96 + order * 30
            moved = order in changed
            body.append(text(x + 40, cy + 4, dial, "fig-muted", anchor="start", size=12,
                             weight=500))
            body.append(f'<path d="M{x + 116} {cy}H{x + 300}" class="fig-grid-stroke" '
                        'stroke-width="2" opacity="0.5"/>')
            at = x + (240 if moved else 150)
            body.append(f'<g class="aim-ver-in" style="animation-delay:{order * 0.12:.2f}s">'
                        f'<circle cx="{at}" cy="{cy}" r="7" '
                        f'class="{"fig-accent-fill" if moved else "fig-grid-fill"}"/></g>')
        body.append(f'<g>'
                    + text(x + 178, 262, verdict, tone, size=14, weight=700) + "</g>")
    return (f'<svg viewBox="0 0 {VER_W} {VER_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-versions-title"><title id="fig-versions-title">Two second '
            'versions of the same scenario, each shown as five dials. In the first only one dial has '
            'moved and the result says what that dial does. In the second all five have moved and '
            'the result says nothing.</title>' + metadata()
            + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


ADAPT_W = 760
ADAPT_H = 290
ADAPT_T = 6.0
ADAPT_RUNS = 9


def adapt() -> str:
    """Static against adapt on the Challenge tab. Under static the difficulty is a line you set;
    under adapt it chases your performance, so a score is no longer measured against a constant."""
    css = ["@keyframes aimAdpDot{0%{opacity:0}4%{opacity:1}100%{opacity:1}}",
           ".aim-adp-dot{opacity:0;animation-name:aimAdpDot;animation-iteration-count:infinite;"
           f"animation-duration:{ADAPT_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-adp-dot{opacity:1;"
           "animation:none!important}}"]
    body = []
    # The same nine runs in both panels. Only what the scenario did about them differs.
    scores = (0.42, 0.55, 0.48, 0.62, 0.58, 0.70, 0.64, 0.76, 0.72)
    for index, (x, name, note, moves) in enumerate((
            (12, "Static", "difficulty holds still", False),
            (392, "Adapt", "difficulty chases you", True))):
        left, right = x + 48, x + 320
        base, top = 208, 96
        body.append(f'<rect x="{x}" y="46" width="356" height="{ADAPT_H - 72}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        step = (right - left) / (ADAPT_RUNS - 1)
        # The difficulty line: flat under static, climbing under adapt.
        if moves:
            pts = " ".join(f"{left + i * step:.1f} "
                           f"{base - (base - top) * (0.34 + 0.4 * i / (ADAPT_RUNS - 1)):.1f}"
                           for i in range(ADAPT_RUNS))
            body.append(f'<polyline points="{pts}" class="fig-tense-stroke" stroke-width="2.4" '
                        'fill="none" stroke-dasharray="6 5"/>')
        else:
            body.append(f'<path d="M{left} {base - (base - top) * 0.34:.1f}'
                        f'H{right}" class="fig-balanced-stroke" stroke-width="2.4" '
                        'stroke-dasharray="6 5"/>')
        body.append(text(x + 178, base + 46, "difficulty", "fig-muted", size=12, weight=500))
        for run, v in enumerate(scores):
            body.append(f'<circle cx="{left + run * step:.1f}" '
                        f'cy="{base - (base - top) * v:.1f}" r="6" '
                        f'class="fig-target aim-adp-dot" style="animation-delay:'
                        f'{run * ADAPT_T * 0.07:.2f}s"/>')
        body.append(text(x + 178, base + 24,
                         "your score rose against a fixed bar" if not moves
                         else "the bar rose with you", "fig-muted", size=13, weight=500))
    return (f'<svg viewBox="0 0 {ADAPT_W} {ADAPT_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-adapt-title"><title id="fig-adapt-title">The same nine rising '
            'scores in two panels. Under static the difficulty line is flat, so the rise is '
            'improvement against a fixed bar. Under adapt the difficulty line rises alongside the '
            'scores, so the same rise says much less.</title>' + metadata()
            + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


RADIUS_W = 760
RADIUS_H = 290
RADIUS_T = 4.6


def hitradius() -> str:
    """Two ways to make a shot land: change the target, or change the bullet. They look the same on
    a hit counter and are not the same demand."""
    css = ["@keyframes aimRadShot{0%{opacity:0}6%{opacity:1}52%{opacity:1}58%{opacity:0}"
           "100%{opacity:0}}",
           ".aim-rad-shot{opacity:0;animation-name:aimRadShot;animation-iteration-count:infinite;"
           f"animation-duration:{RADIUS_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-rad-shot{opacity:1;"
           "animation:none!important}}"]
    body = []
    for index, (x, name, note, target_r, shot_r) in enumerate((
            (12, "Bigger target", "Boxes tab, body radius", 46, 5),
            (392, "Wider bullet", "Effects tab, hitscan radius", 26, 24))):
        cx, cy = x + 178, 150
        body.append(f'<rect x="{x}" y="46" width="356" height="{RADIUS_H - 72}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        # The baseline target, drawn in both so the change is visible against it.
        body.append(f'<circle cx="{cx}" cy="{cy}" r="26" class="fig-grid-stroke" '
                    'stroke-width="2" stroke-dasharray="5 5" fill="none"/>')
        body.append(f'<circle cx="{cx}" cy="{cy}" r="{target_r}" class="fig-target" '
                    f'opacity="{0.9 if index == 0 else 1}"/>')
        # The shot lands in the same wrong place in both panels, and counts in both.
        body.append(f'<g class="aim-rad-shot"><circle cx="{cx + 38}" cy="{cy - 14}" '
                    f'r="{shot_r}" class="fig-accent-stroke" stroke-width="2.4" fill="none"/>'
                    f'<circle cx="{cx + 38}" cy="{cy - 14}" r="3" class="fig-accent-fill"/></g>')
        body.append(crosshair("fig-ink-stroke", cx + 38, cy - 14))
        body.append(text(cx, 222, "the same miss counts as a hit", "fig-muted", size=13,
                         weight=500))
        body.append(text(cx, 244, "harder to see coming" if index else "you can see it is bigger",
                         "fig-muted", size=12, weight=500))
    return (f'<svg viewBox="0 0 {RADIUS_W} {RADIUS_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-hitradius-title"><title id="fig-hitradius-title">Two panels with '
            'the same crosshair placed off-center. On the left the target itself is drawn larger, so '
            'the shot lands inside it. On the right the target is the original size but the shot has '
            'a wide radius, so it registers anyway.</title>' + metadata()
            + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


WIRE_W = 760
WIRE_H = 300
WIRE_T = 5.4
# The bot's own box, then the three it points at. Weapons hang off the character, not off the bot,
# which is the wiring mistake the page warns about.
WIRE_NODES = (
    (300, 26, 160, 52, "Bot", "names the others", True),
    (40, 130, 190, 56, "Character", "size · health · spawn", True),
    (285, 130, 190, 56, "Dodge", "how it moves", True),
    (530, 130, 190, 56, "Aim", "how it aims at you", False),
    (40, 224, 190, 50, "Weapons", "listed on the character", False),
)


def wiring() -> str:
    """A bot profile drawn as what it is: a junction box. Almost nothing is set on it."""
    css = ["@keyframes aimWireIn{0%{opacity:0}8%{opacity:1}100%{opacity:1}}",
           ".aim-wire-in{opacity:0;animation-name:aimWireIn;animation-iteration-count:infinite;"
           f"animation-duration:{WIRE_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-wire-in{opacity:1;"
           "animation:none!important}}"]
    body = ['<defs><marker id="fig-wire-arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto">'
            '<path d="M0 0 L10 5 L0 10 Z" class="fig-grid-fill"/></marker></defs>']
    for order, (bx, by, bw, bh, name, note, solid) in enumerate(WIRE_NODES):
        if order:
            parent = WIRE_NODES[0] if order < 4 else WIRE_NODES[1]
            px, py = parent[0] + parent[2] / 2, parent[1] + parent[3]
            cx, cy = bx + bw / 2, by
            mid = (py + cy) / 2
            body.append(f'<g class="aim-wire-in" style="animation-delay:{order * 0.4:.2f}s">'
                        f'<path d="M{px} {py}V{mid}H{cx}V{cy}" class="fig-grid-stroke" '
                        'stroke-width="2" fill="none" marker-end="url(#fig-wire-arrow)"/></g>')
        stroke = "fig-ink-stroke" if solid else "fig-grid-stroke"
        dash = "" if solid else ' stroke-dasharray="6 5"'
        ink = "fig-ink" if solid else "fig-muted"
        body.append(f'<g class="aim-wire-in" style="animation-delay:{order * 0.4:.2f}s">'
                    f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="10" '
                    f'class="fig-panel {stroke}" stroke-width="2"{dash}/>'
                    + text(bx + bw / 2, by + 22, name, ink, size=15, weight=700)
                    + text(bx + bw / 2, by + 41, note, "fig-muted", size=12, weight=500) + "</g>")
    return (f'<svg viewBox="0 0 {WIRE_W} {WIRE_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-wiring-title"><title id="fig-wiring-title">A bot profile at the '
            'top pointing to a character profile, a dodge profile and an aim profile. A fourth box, '
            'the weapon list, hangs off the character profile rather than off the '
            'bot.</title>' + metadata() + f"<style>{''.join(css)}</style>" + "".join(body)
            + "</svg>")


RHY_W = 760
RHY_H = 300
RHY_T = 6.0
RHY_FRAMES = 72
RHY_AMP = 118.0


def rhythm() -> str:
    """Toggle L/R Time, the field that decides whether a target is a metronome or a coin flip. Both
    panels strafe the same distance at the same speed; only the leg lengths differ."""
    css = [".aim-rhy-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{RHY_T}s}}"]
    body = []
    # Fixed leg lengths rather than random ones, so the right panel is reproducibly irregular and a
    # paused frame always catches the two panels out of step with each other.
    legs = {0: (1.0, 1.0, 1.0, 1.0, 1.0, 1.0), 1: (0.45, 1.6, 0.7, 1.9, 0.5, 0.85)}
    for index, (x, name, note) in enumerate((
            (12, "Narrow range", "a metronome you can learn"),
            (392, "Wide range", "a target you have to read"))):
        cx, cy = x + 178, 156
        body.append(f'<rect x="{x}" y="46" width="356" height="{RHY_H - 74}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        body.append(f'<path d="M{cx - RHY_AMP} {cy}H{cx + RHY_AMP}" class="fig-grid-stroke" '
                    'stroke-width="2" stroke-dasharray="6 6" opacity="0.6"/>')
        # One frame list built from consecutive legs, each sweeping the full width.
        spans = legs[index]
        total = sum(spans)
        frames, direction = [], 1.0
        for leg, span in enumerate(spans):
            count = max(2, round(RHY_FRAMES * span / total))
            for i in range(count):
                u = i / count
                pos = -RHY_AMP + 2 * RHY_AMP * smooth(u)
                frames.append((pos * direction, 0.0))
            direction *= -1
        frames.append((frames[0][0], 0.0))
        body.append(f'<g class="aim-rhy-anim aim-rhy-{index}">'
                    f'<circle cx="{cx}" cy="{cy}" r="15" class="fig-target"/></g>')
        css.append(keyframes(f"aimRhyPath{index}", frames,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".aim-rhy-{index}{{animation-name:aimRhyPath{index}}}")
        # A tick per direction change, drawn along a timeline so the spacing is visible at rest.
        marks, at = [], 0.0
        for span in spans:
            at += span / total
            marks.append(at)
        body.append(f'<path d="M{cx - 140} {cy + 74}H{cx + 140}" class="fig-grid-stroke" '
                    'stroke-width="2"/>')
        for at in marks[:-1]:
            mx = cx - 140 + 280 * at
            body.append(f'<path d="M{mx:.1f} {cy + 66}V{cy + 82}" class="fig-accent-stroke" '
                        'stroke-width="2.4"/>')
        body.append(text(cx, cy + 104, "direction changes", "fig-muted", size=12, weight=500))
    css.append("@media (prefers-reduced-motion:reduce){.aim-rhy-anim{animation-play-state:paused;"
               f"animation-delay:-{RHY_T * 0.28:.2f}s!important}}}}")
    return (f'<svg viewBox="0 0 {RHY_W} {RHY_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-rhythm-title"><title id="fig-rhythm-title">Two strafing targets '
            'covering the same distance. Under a narrow toggle range the direction changes are '
            'evenly spaced along a timeline. Under a wide range they are irregular, so the next '
            'change cannot be anticipated.</title>' + metadata()
            + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


CONE_W = 760
CONE_H = 330
CONE_T = 5.6
CONE_FRAMES = 48


def aimcone() -> str:
    """Optimal Aim FOV as a place on the screen rather than a number. Inside the cone the bot aims
    well; outside it, the penalty multiplier degrades it, which is a thing you can play around."""
    css = [".aim-cone-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{CONE_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-cone-anim{animation-play-state:paused;"
           f"animation-delay:-{CONE_T * 0.12:.2f}s!important}}}}"]
    # The panel runs from y=46 to y=CONE_H-28, so every label has to sit inside that band. An
    # earlier version put two of them below the floor, where they rendered outside the figure.
    bot_x, bot_y = 176, 168
    body = [f'<rect x="12" y="46" width="736" height="{CONE_H - 74}" rx="12" class="fig-panel"/>']
    body.append(lane_label(32, 30, "Optimal aim FOV", "where the bot is actually dangerous"))
    body.append(f'<path d="M{bot_x} {bot_y}L{bot_x + 452} {bot_y - 86}'
                f'L{bot_x + 452} {bot_y + 46}Z" class="fig-tense-fill" opacity="0.16"/>')
    body.append(f'<path d="M{bot_x} {bot_y}L{bot_x + 452} {bot_y - 86}M{bot_x} {bot_y}'
                f'L{bot_x + 452} {bot_y + 46}" class="fig-tense-stroke" stroke-width="2" '
                'stroke-dasharray="6 5"/>')
    body.append(text(bot_x + 300, bot_y - 14, "inside: it aims well", "fig-tense-fill",
                     size=13, weight=700))
    body.append(text(bot_x + 300, bot_y + 86, "outside: the penalty degrades it", "fig-muted",
                     size=13, weight=700))
    body.append(f'<circle cx="{bot_x}" cy="{bot_y}" r="16" class="fig-target"/>')
    body.append(text(bot_x, bot_y + 38, "the bot", "fig-muted", size=12, weight=500))
    # You, dropping out of the cone and back. The travel stays inside the panel at both ends.
    frames = []
    for i in range(CONE_FRAMES + 1):
        u = i / CONE_FRAMES
        frames.append((0.0, 96 * smooth(min(u / 0.5, 1.0)) if u < 0.5
                       else 96 * (1 - smooth((u - 0.5) / 0.5))))
    body.append('<g class="aim-cone-anim aim-cone-you">'
                + crosshair("fig-ink-stroke", bot_x + 392, bot_y - 44) + "</g>")
    css.append(keyframes("aimConeYou", frames, lambda p: f"translate(0,{p[1]:.1f}px)"))
    css.append(".aim-cone-you{animation-name:aimConeYou}")
    body.append('<g>'
                + text(bot_x + 300, bot_y + 116, "step out and you fight a worse opponent",
                       "fig-balanced-fill", size=13, weight=700) + "</g>")
    return (f'<svg viewBox="0 0 {CONE_W} {CONE_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-aimcone-title"><title id="fig-aimcone-title">A bot with a shaded '
            'cone spreading out in front of it, marked as the range where it aims well. A crosshair '
            'moves down out of the cone and back, and a note says that stepping outside it means '
            'fighting a worse opponent.</title>' + metadata()
            + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


INT_W = 760
INT_H = 280
INT_T = 6.0


def interrupt() -> str:
    """What an ability costs a drill: the run stops being continuous. Same sixty seconds, one of
    them broken into pieces that are not aiming."""
    css = ["@keyframes aimIntFill{0%{transform:scaleX(0)}100%{transform:scaleX(1)}}",
           ".aim-int-bar{transform-box:fill-box;transform-origin:left center;"
           "animation-name:aimIntFill;"
           f"animation-iteration-count:infinite;animation-duration:{INT_T}s;"
           "animation-timing-function:linear}"]
    body = [f'<rect x="12" y="46" width="736" height="{INT_H - 72}" rx="12" class="fig-panel"/>']
    body.append(lane_label(32, 30, "Sixty seconds, twice", "one of them is not all aiming"))
    left, width = 60, 640
    for index, (label, blocks) in enumerate((
            ("Aim only", ()),
            ("With an ability", ((0.22, 0.10), (0.52, 0.10), (0.80, 0.10))))):
        y = 108 + index * 78
        body.append(text(left, y - 16, label, "fig-ink", anchor="start", size=14, weight=700))
        body.append(f'<rect x="{left}" y="{y}" width="{width}" height="34" rx="6" '
                    'class="fig-grid-fill" opacity="0.35"/>')
        body.append(f'<rect x="{left}" y="{y}" width="{width}" height="34" rx="6" '
                    'class="fig-balanced-fill" opacity="0.5"/>')
        for at, span in blocks:
            body.append(f'<rect x="{left + width * at:.1f}" y="{y}" '
                        f'width="{width * span:.1f}" height="34" class="fig-tense-fill" '
                        'opacity="0.85"/>')
        # A playhead crossing both bars at the same rate, so the gaps land at the same moments.
        body.append(f'<rect x="{left}" y="{y}" width="{width}" height="34" rx="6" '
                    'class="fig-accent-fill aim-int-bar" opacity="0.18"/>')
    body.append(text(400, 258, "red is time the drill is not measuring your aim", "fig-muted",
                     size=13, weight=500))
    css.append("@media (prefers-reduced-motion:reduce){.aim-int-bar{animation:none!important;"
               "transform:none!important}}")
    return (f'<svg viewBox="0 0 {INT_W} {INT_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-interrupt-title"><title id="fig-interrupt-title">Two bars of the '
            'same length, each a sixty second run. The first is continuous aiming. The second is '
            'broken by three blocks of ability time, which the drill is not measuring '
            'aim during.</title>' + metadata() + f"<style>{''.join(css)}</style>"
            + "".join(body) + "</svg>")


SMUL_W = 760
SMUL_H = 300
SMUL_T = 6.4
SMUL_AMP = 118.0


def strafemult() -> str:
    """Strafe Time Multiplier, which the editor describes as multiplying how long the bot keeps
    going once it starts strafing left or right. A value per side, so the two can differ."""
    css = [".aim-sm-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{SMUL_T}s}}"]
    body = []
    for index, (x, name, note, left_mul, right_mul) in enumerate((
            (12, "1 and 1", "even ground either way", 1.0, 1.0),
            (392, "1 and 2", "it lives on the right", 1.0, 2.0))):
        cx, cy = x + 178, 150
        body.append(f'<rect x="{x}" y="46" width="356" height="{SMUL_H - 74}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        # Keeping going for longer means getting further, so the multiplier sets how far the bot
        # reaches on that side, not merely how slowly it travels there. An earlier version varied
        # only the duration, which left both panels sweeping the same track.
        span = max(left_mul, right_mul)
        reach_l = -SMUL_AMP * left_mul / span
        reach_r = SMUL_AMP * right_mul / span
        body.append(f'<path d="M{cx + reach_l:.1f} {cy}H{cx + reach_r:.1f}" '
                    'class="fig-grid-stroke" stroke-width="4" stroke-linecap="round" '
                    'opacity="0.5"/>')
        body.append(f'<path d="M{cx} {cy - 22}V{cy + 22}" class="fig-grid-stroke" '
                    'stroke-width="2" opacity="0.5"/>')
        spans = (left_mul, right_mul)
        total = sum(spans)
        frames = []
        for leg in range(2):
            count = max(4, round(64 * spans[leg] / total))
            a, b = (reach_r, reach_l) if leg == 0 else (reach_l, reach_r)
            for i in range(count):
                u = i / count
                frames.append((a + (b - a) * smooth(u), 0.0))
        frames.append(frames[0])
        body.append(f'<g class="aim-sm-anim aim-sm-{index}">'
                    f'<circle cx="{cx}" cy="{cy}" r="15" class="fig-target"/></g>')
        css.append(keyframes(f"aimSmPath{index}", frames,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".aim-sm-{index}{{animation-name:aimSmPath{index}}}")
        # A bar per side showing how long each leg lasts, which is the setting itself.
        span_w = 128
        for side, mul in enumerate(spans):
            bx = cx - 134 if side == 0 else cx + 6
            w = span_w * mul / max(spans)
            body.append(f'<rect x="{bx if side == 0 else bx}" y="{cy + 66}" width="{w:.1f}" '
                        f'height="11" rx="5" class="fig-accent-fill"/>')
            body.append(text(bx + 2, cy + 98, "left leg" if side == 0 else "right leg",
                             "fig-muted", anchor="start", size=12, weight=500))
    css.append("@media (prefers-reduced-motion:reduce){.aim-sm-anim{animation-play-state:paused;"
               f"animation-delay:-{SMUL_T * 0.30:.2f}s!important}}}}")
    return (f'<svg viewBox="0 0 {SMUL_W} {SMUL_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-strafemult-title"><title id="fig-strafemult-title">Two strafing '
            'targets with a bar under each side showing how long that leg lasts. With both '
            'multipliers equal the legs match and the target sits centerd over time. With the right '
            'multiplier doubled the right leg is twice as long, so the target spends most of its '
            'time on that side.</title>' + metadata() + f"<style>{''.join(css)}</style>"
            + "".join(body) + "</svg>")


BLK_W = 760
BLK_H = 300
BLK_T = 5.2
BLK_FRAMES = 60


def blocked() -> str:
    """Trigger On Blocking Collision, and the reaction time beside it: when the bot works out it
    cannot keep strafing, how long before it turns around."""
    css = [".aim-blk-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{BLK_T}s}}"]
    body = []
    for index, (x, name, note, waits) in enumerate((
            (12, "Reaction time 0", "turns the moment it is blocked", 0.0),
            (392, "Reaction time set", "presses into the wall first", 0.22))):
        cx, cy = x + 178, 156
        wall = cx + 104
        body.append(f'<rect x="{x}" y="46" width="356" height="{BLK_H - 74}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        body.append(f'<rect x="{wall}" y="{cy - 54}" width="16" height="108" '
                    'class="fig-grid-fill"/>')
        body.append(f'<path d="M{cx - 118} {cy}H{wall - 6}" class="fig-grid-stroke" '
                    'stroke-width="2" stroke-dasharray="6 6" opacity="0.6"/>')
        # Out to the wall, held there for the reaction time, then back the other way.
        frames = []
        for i in range(BLK_FRAMES + 1):
            u = i / BLK_FRAMES
            out, hold = 0.34, waits
            if u < out:
                pos = -118 + 202 * smooth(u / out)
            elif u < out + hold:
                pos = 84.0
            else:
                pos = 84 - 202 * smooth((u - out - hold) / (1 - out - hold))
            frames.append((pos, 0.0))
        body.append(f'<g class="aim-blk-anim aim-blk-{index}">'
                    f'<circle cx="{cx}" cy="{cy}" r="15" class="fig-target"/></g>')
        css.append(keyframes(f"aimBlkPath{index}", frames,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".aim-blk-{index}{{animation-name:aimBlkPath{index}}}")
        if waits:
            body.append(f'<g>'
                        + text(cx + 20, cy - 74, "stuck on the wall", "fig-tense-fill", size=13,
                               weight=700) + "</g>")
        body.append(text(cx, cy + 92, "counter strafe on collision" if not waits
                         else "counter strafe, after a delay", "fig-muted", size=13, weight=500))
    css.append("@media (prefers-reduced-motion:reduce){.aim-blk-anim{animation-play-state:paused;"
               f"animation-delay:-{BLK_T * 0.44:.2f}s!important}}}}")
    return (f'<svg viewBox="0 0 {BLK_W} {BLK_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-blocked-title"><title id="fig-blocked-title">Two targets strafing '
            'into a wall. With no reaction time the target turns around the moment it collides. '
            'With a reaction time set it presses into the wall for a moment first, marked as stuck, '
            'before turning.</title>' + metadata() + f"<style>{''.join(css)}</style>"
            + "".join(body) + "</svg>")


PBM_W = 760
PBM_H = 330
PBM_T = 6.0
PBM_FRAMES = 52


def playbackmode() -> str:
    """The three playback modes, which differ only in what a knockback does to a recorded path.
    Input Only replays keystrokes and gets shoved off course; Absolute Position matches the recorded
    location regardless; Moveable Absolute Position is the first until it is hit, then the second."""
    css = [".aim-pbm-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{PBM_T}s}}"]
    body = []
    for index, (x, name, note) in enumerate((
            (12, "Input Only", "knockback shoves it off"),
            (263, "Absolute Position", "ignores the shove"),
            (514, "Moveable Absolute", "absolute until it is hit"))):
        cx, cy = x + 117, 178
        body.append(f'<rect x="{x}" y="46" width="234" height="{PBM_H - 92}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 16, 30, name, ""))
        body.append(text(x + 117, PBM_H - 26, note, "fig-muted", size=12, weight=500))
        # The recorded path every mode is trying to follow.
        recorded = [(-82 + 164 * (i / PBM_FRAMES), -34 * math.sin(i / PBM_FRAMES * 3.14159))
                    for i in range(PBM_FRAMES + 1)]
        pts = " ".join(f"{cx + dx:.1f} {cy + dy:.1f}" for dx, dy in recorded)
        body.append(f'<polyline points="{pts}" class="fig-grid-stroke" stroke-width="2" '
                    'stroke-dasharray="5 5" fill="none" opacity="0.7"/>')
        # A knockback arrives at 38% of the cycle and pushes downward.
        frames = []
        for i, (dx, dy) in enumerate(recorded):
            u = i / PBM_FRAMES
            push = 0.0
            if u > 0.38:
                ramp = min(1.0, (u - 0.38) / 0.16)
                if index == 0:
                    push = 62 * ramp
                elif index == 2:
                    push = 62 * ramp
            frames.append((dx, dy + push))
        body.append(f'<g class="aim-pbm-anim aim-pbm-{index}">'
                    f'<circle cx="{cx}" cy="{cy}" r="12" class="fig-target"/></g>')
        css.append(keyframes(f"aimPbmPath{index}", frames,
                             lambda p: f"translate({p[0]:.1f}px,{p[1]:.1f}px)"))
        css.append(f".aim-pbm-{index}{{animation-name:aimPbmPath{index}}}")
        body.append(f'<g><path d="M{cx + 4} {cy - 58}V{cy - 30}" '
                    'class="fig-tense-stroke" stroke-width="3" '
                    'marker-end="url(#fig-pbm-arrow)"/>'
                    + text(cx + 4, cy - 66, "knockback", "fig-tense-fill", size=11, weight=700)
                    + "</g>")
    css.append("@media (prefers-reduced-motion:reduce){.aim-pbm-anim{animation-play-state:paused;"
               f"animation-delay:-{PBM_T * 0.72:.2f}s!important}}}}")
    return (f'<svg viewBox="0 0 {PBM_W} {PBM_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-playbackmode-title"><title id="fig-playbackmode-title">Three '
            'panels, each with the same recorded path and the same knockback arriving partway '
            'through. Under Input Only the target is pushed off the path and stays off it. Under '
            'Absolute Position it stays on the path. Under Moveable Absolute Position it holds the '
            'path until the hit, then drifts like Input Only.</title>'
            '<defs><marker id="fig-pbm-arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 Z" '
            'class="fig-tense-fill"/></marker></defs>'
            + metadata() + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


SWAP_W = 760
SWAP_H = 300
SWAP_T = 6.4


def profileswap() -> str:
    """Triggers Profile Change. Under Mimic or Oppose, a damage reaction throws the bot out of the
    current dodge profile: it looks for one using Ignore, and failing that picks anything."""
    css = ["@keyframes aimSwpStep{0%{opacity:0.2}6%{opacity:1}34%{opacity:1}40%{opacity:0.2}"
           "100%{opacity:0.2}}",
           ".aim-swp-step{opacity:0.2;animation-name:aimSwpStep;animation-iteration-count:infinite;"
           f"animation-duration:{SWAP_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-swp-step{opacity:1;"
           "animation:none!important}}"]
    body = ['<defs><marker id="fig-swp-arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto">'
            '<path d="M0 0 L10 5 L0 10 Z" class="fig-grid-fill"/></marker></defs>',
            f'<rect x="12" y="46" width="736" height="{SWAP_H - 76}" rx="12" class="fig-panel"/>']
    body.append(lane_label(32, 30, "A damage reaction ejects the bot",
                           "only under Mimic or Oppose"))
    steps = (("Mimic profile", "it is answering you", "fig-ink-stroke", "fig-ink"),
             ("takes damage", "reaction fires", "fig-tense-stroke", "fig-tense-fill"),
             ("an Ignore profile", "preferred", "fig-balanced-stroke", "fig-balanced-fill"))
    for order, (name, note, stroke, ink) in enumerate(steps):
        bx = 48 + order * 224
        body.append(f'<g class="aim-swp-step" style="animation-delay:{order * SWAP_T * 0.16:.2f}s">'
                    f'<rect x="{bx}" y="104" width="190" height="66" rx="10" '
                    f'class="fig-panel {stroke}" stroke-width="2"/>'
                    + text(bx + 95, 132, name, ink, size=14, weight=700)
                    + text(bx + 95, 154, note, "fig-muted", size=12, weight=500) + "</g>")
        if order < len(steps) - 1:
            body.append(f'<path d="M{bx + 198} 137H{bx + 216}" class="fig-grid-stroke" '
                        'stroke-width="2" marker-end="url(#fig-swp-arrow)"/>')
    # The fallback the tooltip describes: if no Ignore profile exists, anything at all.
    body.append('<g>'
                '<path d="M591 176V212H400" class="fig-grid-stroke" stroke-width="2" '
                'stroke-dasharray="5 5" fill="none" marker-end="url(#fig-swp-arrow)"/>'
                + text(392, 216, "none available? it picks at random", "fig-muted", anchor="end",
                       size=13, weight=600) + "</g>")
    return (f'<svg viewBox="0 0 {SWAP_W} {SWAP_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-profileswap-title"><title id="fig-profileswap-title">Three steps '
            'lighting in turn: a bot running a Mimic dodge profile, taking damage, and being moved '
            'to a profile that uses Ignore. A dashed branch notes that where no such profile exists '
            'the replacement is picked at random.</title>' + metadata()
            + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


RCT_W = 760
RCT_H = 310
RCT_T = 5.4
RCT_FRAMES = 60


def recoiltiming() -> str:
    """Time To Peak plus Time To Reset against Time Between Shots. The editor recommends the first
    two add up to less than the third; when they do not, the crosshair never gets home between
    shots and the climb stacks."""
    css = [".aim-rct-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{RCT_T}s}}"]
    body = []
    for index, (x, name, note, peak, reset, gap) in enumerate((
            (12, "Peak + reset < gap", "home before the next shot", 0.14, 0.26, 0.5),
            (392, "Peak + reset > gap", "the climb stacks", 0.2, 0.46, 0.34))):
        cx, base = x + 178, 210
        body.append(f'<rect x="{x}" y="46" width="356" height="{RCT_H - 84}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        body.append(f'<path d="M{cx - 128} {base}H{cx + 128}" class="fig-grid-stroke" '
                    'stroke-width="2" opacity="0.7"/>')
        body.append(text(cx - 128, base + 24, "resting crosshair", "fig-muted", anchor="start",
                         size=12, weight=500))
        # The crosshair's vertical offset over two shots: up to peak, back down, shot again.
        frames, carry = [], 0.0
        for i in range(RCT_FRAMES + 1):
            u = i / RCT_FRAMES
            shot = 0 if u < 0.5 else 1
            local = (u - shot * 0.5) / 0.5 * gap
            if local < peak:
                rise = smooth(local / peak)
            elif local < peak + reset:
                rise = 1 - smooth((local - peak) / reset)
            else:
                rise = 0.0
            # What has not come back down by the next shot is still there when it starts.
            left = 0.0 if peak + reset <= gap else (1 - smooth(min(1.0, (gap - peak) / reset)))
            carry = left * shot
            frames.append((0.0, -(rise + carry) * 92))
        body.append(f'<g class="aim-rct-anim aim-rct-{index}">'
                    f'{crosshair("fig-ink-stroke", cx, base)}</g>')
        css.append(keyframes(f"aimRctPath{index}", frames,
                             lambda p: f"translate(0,{p[1]:.1f}px)"))
        css.append(f".aim-rct-{index}{{animation-name:aimRctPath{index}}}")
        # The shot marks along the bottom, so the gap between them is visible.
        for shot in range(2):
            sx = cx - 100 + shot * 128
            body.append(f'<path d="M{sx} {base + 38}V{base + 56}" class="fig-accent-stroke" '
                        'stroke-width="3"/>')
        body.append(f'<path d="M{cx - 100} {base + 47}H{cx + 28}" class="fig-accent-stroke" '
                    'stroke-width="2" opacity="0.6"/>')
        body.append(text(cx - 36, base + 76, "time between shots", "fig-accent-text", size=12,
                         weight=600))
    css.append("@media (prefers-reduced-motion:reduce){.aim-rct-anim{animation-play-state:paused;"
               f"animation-delay:-{RCT_T * 0.52:.2f}s!important}}}}")
    return (f'<svg viewBox="0 0 {RCT_W} {RCT_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-recoiltiming-title"><title id="fig-recoiltiming-title">Two '
            'panels, each firing two shots with the gap between them marked. On the left the '
            'crosshair climbs and returns to rest before the second shot. On the right it has not '
            'finished returning, so the second shot starts from higher up and the climb '
            'stacks.</title>' + metadata() + f"<style>{''.join(css)}</style>" + "".join(body)
            + "</svg>")


SHP_W = 760
SHP_H = 290
SHP_T = 4.8
SHP_SHOTS = 11


def spreadshape() -> str:
    """Circular Spread, whose tooltip says only that unchecking it gives a square-shape spread.
    The difference is in the corners, which is where a shot is most likely to surprise you."""
    rng = random.Random(19)
    css = ["@keyframes aimShpMark{0%{opacity:0}5%{opacity:1}66%{opacity:1}72%{opacity:0}"
           "100%{opacity:0}}",
           ".aim-shp-mark{opacity:0;animation-name:aimShpMark;animation-iteration-count:infinite;"
           f"animation-duration:{SHP_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-shp-mark{opacity:1;"
           "animation:none!important}}"]
    body = []
    R = 66
    for index, (x, name, note) in enumerate((
            (12, "Circular spread", "checked, the default"),
            (392, "Square spread", "unchecked"))):
        cx, cy = x + 178, 152
        body.append(f'<rect x="{x}" y="46" width="356" height="{SHP_H - 72}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        if index == 0:
            body.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" class="fig-grid-stroke" '
                        'stroke-width="2" stroke-dasharray="6 6" fill="none"/>')
        else:
            body.append(f'<rect x="{cx - R}" y="{cy - R}" width="{R * 2}" height="{R * 2}" '
                        'class="fig-grid-stroke" stroke-width="2" stroke-dasharray="6 6" '
                        'fill="none"/>')
        for order in range(SHP_SHOTS):
            if index == 0:
                ang = rng.uniform(0, 6.28318)
                dist = R * (rng.random() ** 0.5)
                dx, dy = dist * math.cos(ang), dist * math.sin(ang)
            else:
                dx, dy = rng.uniform(-R, R), rng.uniform(-R, R)
            body.append(f'<circle cx="{cx + dx:.1f}" cy="{cy + dy:.1f}" r="5" '
                        f'class="fig-target aim-shp-mark" '
                        f'style="animation-delay:{order * SHP_T * 0.05:.2f}s"/>')
        body.append(crosshair("fig-ink-stroke", cx, cy))
        body.append(text(cx, cy + 108, "corners reach further out" if index else
                         "every direction reaches the same", "fig-muted", size=13, weight=500))
    return (f'<svg viewBox="0 0 {SHP_W} {SHP_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-spreadshape-title"><title id="fig-spreadshape-title">Two spread '
            'patterns around the same crosshair. The circular one reaches the same distance in '
            'every direction. The square one reaches further at its corners than along its '
            'edges.</title>' + metadata() + f"<style>{''.join(css)}</style>" + "".join(body)
            + "</svg>")


LCK_W = 760
LCK_H = 300
LCK_T = 5.0
LCK_FRAMES = 54


def lockdeadzone() -> str:
    """Lock Deadzone, described in the editor as the distance from the target at which the lock
    stops tracking. Inside it the aimbot lets go, so the shot lands near the target rather than
    dead on it: the difference between a build tool and an unbeatable opponent."""
    css = [".aim-lck-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{LCK_T}s}}"]
    body = []
    for index, (x, name, note, dead) in enumerate((
            (12, "Deadzone 0", "it lands dead center", 0.0),
            (392, "Deadzone set", "it stops short", 34.0))):
        cx, cy = x + 190, 156
        start = cx - 132
        body.append(f'<rect x="{x}" y="46" width="356" height="{LCK_H - 74}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        body.append(f'<circle cx="{cx}" cy="{cy}" r="30" class="fig-target"/>')
        if dead:
            body.append(f'<circle cx="{cx}" cy="{cy}" r="{dead}" class="fig-cool-stroke" '
                        'stroke-width="2.4" stroke-dasharray="6 5" fill="none"/>')
            body.append(text(cx, cy + dead + 26, "deadzone", "fig-cool-fill", size=12,
                             weight=600))
        # The lock drags the crosshair in, then releases at the deadzone edge.
        stop = cx - dead if dead else cx
        frames = [((start + (stop - start) * smooth(min(1.0, i / LCK_FRAMES / 0.55))) - start, 0.0)
                  for i in range(LCK_FRAMES + 1)]
        body.append(f'<g class="aim-lck-anim aim-lck-{index}">'
                    f'{crosshair("fig-ink-stroke", start, cy)}</g>')
        css.append(keyframes(f"aimLckPath{index}", frames,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".aim-lck-{index}{{animation-name:aimLckPath{index}}}")
        body.append(f'<g>'
                    + text(x + 178, cy + 92, "lock releases here" if dead
                           else "lock never releases",
                           "fig-balanced-fill" if dead else "fig-tense-fill", size=13, weight=700)
                    + "</g>")
    css.append("@media (prefers-reduced-motion:reduce){.aim-lck-anim{animation-play-state:paused;"
               f"animation-delay:-{LCK_T * 0.62:.2f}s!important}}}}")
    return (f'<svg viewBox="0 0 {LCK_W} {LCK_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-lockdeadzone-title"><title id="fig-lockdeadzone-title">Two '
            'panels, each with a locked crosshair dragged toward a target. With no deadzone it '
            'arrives at dead center. With a deadzone set it stops at the edge of a marked ring '
            'short of the middle.</title>' + metadata() + f"<style>{''.join(css)}</style>"
            + "".join(body) + "</svg>")


PIE_W = 760
PIE_H = 270
PIE_T = 4.4


def piercing() -> str:
    """Piercing, which the editor describes as letting a hitscan shot go through targets and damage
    more than one thing. It turns a line-up from a selection problem into a single shot."""
    css = ["@keyframes aimPieRay{0%{transform:scaleX(0);opacity:0}8%{opacity:1}"
           "46%{transform:scaleX(1);opacity:1}62%{transform:scaleX(1);opacity:1}"
           "70%{opacity:0}100%{opacity:0}}",
           ".aim-pie-ray{transform-box:fill-box;transform-origin:left center;opacity:0;"
           "animation-name:aimPieRay;"
           f"animation-iteration-count:infinite;animation-duration:{PIE_T}s}}",
           "@keyframes aimPieHit{0%{opacity:0}100%{opacity:1}}",
           "@media (prefers-reduced-motion:reduce){.aim-pie-ray{opacity:1;"
           "transform:none!important;animation:none!important}}"]
    body = []
    for index, (x, name, note, through) in enumerate((
            (12, "Piercing off", "the first target stops it", False),
            (392, "Piercing on", "one shot, three targets", True))):
        muzzle = x + 46
        cy = 150
        stop = muzzle + (268 if through else 96)
        body.append(f'<rect x="{x}" y="46" width="356" height="{PIE_H - 72}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        for slot in range(3):
            tx = muzzle + 96 + slot * 86
            hit = through or slot == 0
            body.append(f'<circle cx="{tx}" cy="{cy}" r="19" class="fig-target" '
                        f'opacity="{1 if hit else 0.35}"/>')
        body.append(f'<g class="aim-pie-ray"><path d="M{muzzle} {cy}H{stop}" '
                    'class="fig-accent-stroke" stroke-width="4" stroke-linecap="round"/></g>')
        body.append(crosshair("fig-ink-stroke", muzzle, cy))
        body.append(text(x + 178, cy + 72, "two left standing" if not through
                         else "all three take damage", "fig-muted", size=13, weight=500))
    return (f'<svg viewBox="0 0 {PIE_W} {PIE_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-piercing-title"><title id="fig-piercing-title">Two panels with '
            'three targets lined up. With piercing off the shot stops at the first target and the '
            'other two are left faded. With piercing on the shot passes through all '
            'three.</title>' + metadata() + f"<style>{''.join(css)}</style>" + "".join(body)
            + "</svg>")


SFV_W = 760
SFV_H = 320
SFV_T = 5.6
SFV_SPOTS = ((-118, -46), (-38, -74), (46, -58), (126, -30), (-92, 22), (24, 34), (118, 18))


def spawnfov() -> str:
    """Block Other Spawn FOV, and the distance field that silently switches it off. The editor
    recommends a FOV of 15 to 30, and warns that leaving the distance at zero means the FOV is
    never checked at all."""
    css = ["@keyframes aimSfvPop{0%{opacity:0}6%{opacity:1}100%{opacity:1}}",
           ".aim-sfv-pop{opacity:0;animation-name:aimSfvPop;animation-iteration-count:infinite;"
           f"animation-duration:{SFV_T}s}}",
           "@keyframes aimSfvBlock{0%{opacity:0}40%{opacity:0}48%{opacity:0.25}100%{opacity:0.25}}",
           ".aim-sfv-block{opacity:0;animation-name:aimSfvBlock;animation-iteration-count:infinite;"
           f"animation-duration:{SFV_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-sfv-pop{opacity:1;animation:none!important}"
           ".aim-sfv-block{opacity:0.25;animation:none!important}}"]
    body = []
    for index, (x, name, note, checks) in enumerate((
            (12, "Distance set", "spawns in your view are blocked", True),
            (392, "Distance left at 0", "the FOV is never checked", False))):
        cx, eye = x + 178, 250
        body.append(f'<rect x="{x}" y="46" width="356" height="{SFV_H - 86}" rx="12" '
                    'class="fig-panel"/>')
        # The recommendation belongs in the header: inside the panel it landed on a spawn dot.
        body.append(lane_label(x + 20, 30, name,
                               "recommended 15 to 30 degrees" if checks else ""))
        body.append(text(x + 178, SFV_H - 18, note, "fig-muted", size=12, weight=500))
        # The cone the player is looking down.
        body.append(f'<path d="M{cx} {eye}L{cx - 78} 84L{cx + 78} 84Z" '
                    'class="fig-cool-stroke" stroke-width="2" stroke-dasharray="6 5" '
                    'fill="none" opacity="0.8"/>')
        body.append(crosshair("fig-ink-stroke", cx, eye - 8))
        body.append(text(cx, eye + 22, "you", "fig-muted", size=12, weight=500))
        for order, (dx, dy) in enumerate(SFV_SPOTS):
            sx, sy = cx + dx, 168 + dy
            inside = abs(dx) < 78 * (eye - sy) / (eye - 84)
            blocked = inside and checks
            body.append(f'<circle cx="{sx}" cy="{sy}" r="13" class="fig-target aim-sfv-pop'
                        f'{" aim-sfv-block" if blocked else ""}" '
                        f'style="animation-delay:{order * 0.18:.2f}s"/>')
    return (f'<svg viewBox="0 0 {SFV_W} {SFV_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-spawnfov-title"><title id="fig-spawnfov-title">Two panels with a '
            'player looking down a marked cone and seven spawn points around them. With the '
            'distance set, the spawns inside the cone fade out as blocked. With the distance left '
            'at zero every spawn stays available, because the field of view is never '
            'checked.</title>' + metadata() + f"<style>{''.join(css)}</style>" + "".join(body)
            + "</svg>")


SRD_W = 760
SRD_H = 290
SRD_T = 5.0
SRD_COUNT = 6


def selfradius() -> str:
    """Blocked Self Spawn Radius: the rule that stops two targets appearing close enough that one
    flick covers both, which quietly turns a switching drill into a single-target one."""
    rng = random.Random(53)
    css = ["@keyframes aimSrdPop{0%{opacity:0;transform:scale(0.5)}5%{opacity:1;transform:scale(1)}"
           "100%{opacity:1;transform:scale(1)}}",
           ".aim-srd-pop{opacity:0;animation-name:aimSrdPop;animation-iteration-count:infinite;"
           f"animation-duration:{SRD_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-srd-pop{opacity:1;"
           "animation:none!important;transform:none!important}}"]
    body = []
    for index, (x, name, note, radius) in enumerate((
            (12, "Radius 0", "two can share a flick", 0.0),
            (392, "Radius set", "every target its own trip", 56.0))):
        cx, cy = x + 178, 156
        body.append(f'<rect x="{x}" y="46" width="356" height="{SRD_H - 72}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        # Placed by rejection sampling, which is what the setting itself does.
        spots: list[tuple[float, float]] = []
        guard = 0
        while len(spots) < SRD_COUNT and guard < 400:
            guard += 1
            px, py = rng.uniform(-128, 128), rng.uniform(-64, 64)
            if radius and any((px - qx) ** 2 + (py - qy) ** 2 < radius ** 2 for qx, qy in spots):
                continue
            spots.append((px, py))
        for order, (dx, dy) in enumerate(spots):
            if radius:
                body.append(f'<circle cx="{cx + dx:.1f}" cy="{cy + dy:.1f}" r="{radius / 2:.0f}" '
                            'class="fig-grid-stroke" stroke-width="1.5" stroke-dasharray="4 4" '
                            'fill="none" opacity="0.5"/>')
            body.append(f'<circle cx="{cx + dx:.1f}" cy="{cy + dy:.1f}" r="14" '
                        f'class="fig-target aim-srd-pop" style="animation-delay:'
                        f'{order * 0.16:.2f}s;transform-origin:{cx + dx:.1f}px {cy + dy:.1f}px"/>')
        body.append(text(cx, cy + 104, "clusters happen" if not radius else "spaced by the rule",
                         "fig-muted", size=13, weight=500))
    return (f'<svg viewBox="0 0 {SRD_W} {SRD_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-selfradius-title"><title id="fig-selfradius-title">Two panels of '
            'six spawned targets. With the radius at zero some land close enough to overlap. With '
            'a radius set each target carries a marked exclusion ring and none of them '
            'cluster.</title>' + metadata() + f"<style>{''.join(css)}</style>" + "".join(body)
            + "</svg>")


HBX_W = 760
HBX_H = 300
HBX_T = 4.8


def headbox() -> str:
    """Has Head, and the two settings that depend on it: Headshot Only, which makes body shots do
    no damage, and Camera Height Offset, whose zero point moves to the head when one exists."""
    css = ["@keyframes aimHbxShot{0%{opacity:0}8%{opacity:1}56%{opacity:1}64%{opacity:0}"
           "100%{opacity:0}}",
           ".aim-hbx-shot{opacity:0;animation-name:aimHbxShot;animation-iteration-count:infinite;"
           f"animation-duration:{HBX_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-hbx-shot{opacity:1;"
           "animation:none!important}}"]
    body = []
    for index, (x, name, note, has_head) in enumerate((
            (12, "No head", "eyes sit at the body's middle", False),
            (392, "Has head", "eyes sit at the head's middle", True))):
        cx = x + 178
        top = 92
        body.append(f'<rect x="{x}" y="46" width="356" height="{HBX_H - 72}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        body_top = top + (40 if has_head else 0)
        body.append(f'<rect x="{cx - 26}" y="{body_top}" width="52" height="96" rx="12" '
                    'class="fig-target"/>')
        if has_head:
            body.append(f'<circle cx="{cx}" cy="{top + 18}" r="20" class="fig-target"/>')
            zero = top + 18
        else:
            zero = body_top + 48
        body.append(f'<path d="M{cx - 92} {zero}H{cx - 34}" class="fig-cool-stroke" '
                    'stroke-width="2" stroke-dasharray="5 4"/>')
        body.append(text(cx - 96, zero + 4, "offset 0", "fig-cool-fill", anchor="end", size=12,
                         weight=600))
        # A body shot, which Headshot Only makes worthless.
        body.append(f'<g class="aim-hbx-shot">'
                    f'<circle cx="{cx + 4}" cy="{body_top + 56}" r="6" class="fig-accent-fill"/>'
                    + text(cx + 92, body_top + 60, "no damage", "fig-tense-fill", size=12,
                           weight=700) + "</g>")
        body.append(text(cx, HBX_H - 42, "under Headshot Only", "fig-muted", size=12, weight=500))
    return (f'<svg viewBox="0 0 {HBX_W} {HBX_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-headbox-title"><title id="fig-headbox-title">Two characters, one '
            'without a head box and one with. A marked line shows where a camera height offset of '
            'zero sits: the middle of the body when there is no head, the middle of the head when '
            'there is. A body shot on each is marked as doing no damage under Headshot '
            'Only.</title>' + metadata() + f"<style>{''.join(css)}</style>" + "".join(body)
            + "</svg>")


END_W = 760
END_H = 300
END_T = 6.0


def endconditions() -> str:
    """The three ways the Challenge tab can end a run. They are not alternatives so much as a race:
    whichever fires first stops the scenario, which is easy to set by accident."""
    css = ["@keyframes aimEndFill{0%{transform:scaleX(0)}100%{transform:scaleX(1)}}",
           # transform-box is not optional here: without it a keyword transform-origin resolves
           # against the SVG's own viewport rather than the element, so the bar scales from the
           # far left of the figure and swings outside its panel.
           ".aim-end-bar{transform-box:fill-box;transform-origin:left center;"
           "animation-name:aimEndFill;"
           f"animation-iteration-count:infinite;animation-duration:{END_T}s;"
           "animation-timing-function:linear}",
           "@keyframes aimEndStop{0%{opacity:0}100%{opacity:1}}",
           ".aim-end-stop{opacity:0;animation-name:aimEndStop;animation-iteration-count:infinite;"
           f"animation-duration:{END_T}s;animation-timing-function:steps(1,end)}}",
           "@media (prefers-reduced-motion:reduce){.aim-end-bar{animation:none!important;"
           "transform:none!important}.aim-end-stop{opacity:1;animation:none!important}}"]
    left, width = 210, 460
    body = [f'<rect x="12" y="46" width="736" height="{END_H - 76}" rx="12" class="fig-panel"/>']
    body.append(lane_label(32, 30, "Three ways to end a run", "the first one to fire wins"))
    rows = (("Time limit", "60 seconds", 1.0),
            ("End after num kills", "reached at 70%", 0.7),
            ("End after damage", "reached at 45%", 0.45))
    for order, (name, note, at) in enumerate(rows):
        y = 96 + order * 54
        body.append(text(36, y + 4, name, "fig-ink", anchor="start", size=13, weight=700))
        body.append(text(36, y + 22, note, "fig-muted", anchor="start", size=11, weight=500))
        body.append(f'<rect x="{left}" y="{y - 10}" width="{width}" height="20" rx="6" '
                    'class="fig-grid-fill" opacity="0.4"/>')
        body.append(f'<rect x="{left}" y="{y - 10}" width="{width * at:.1f}" height="20" rx="6" '
                    'class="fig-accent-fill aim-end-bar" '
                    f'style="animation-duration:{END_T * at:.2f}s"/>')
        stop = left + width * at
        body.append(f'<g class="aim-end-stop" style="animation-delay:{END_T * at:.2f}s">'
                    f'<path d="M{stop:.1f} {y - 18}V{y + 18}" class="fig-tense-stroke" '
                    'stroke-width="3"/></g>')
    body.append(text(left + width * 0.45, 266, "this one ends the run", "fig-tense-fill", size=13,
                     weight=700))
    return (f'<svg viewBox="0 0 {END_W} {END_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-endconditions-title"><title id="fig-endconditions-title">Three '
            'bars filling at once: a time limit, a kill count and a damage total. The damage bar '
            'reaches its mark first and is labelled as the condition that ends the '
            'run.</title>' + metadata() + f"<style>{''.join(css)}</style>" + "".join(body)
            + "</svg>")


TRG_W = 760
TRG_H = 290
TRG_T = 6.0


def timeregained() -> str:
    """Time Regained per Kill. With it set, the clock is no longer a fixed run length: a good run
    lasts longer than a bad one, so two scores are not measured over the same time."""
    css = ["@keyframes aimTrgTick{0%{transform:scaleX(1)}100%{transform:scaleX(0)}}",
           ".aim-trg-clock{transform-box:fill-box;transform-origin:left center;"
           "animation-name:aimTrgTick;"
           f"animation-iteration-count:infinite;animation-duration:{TRG_T}s;"
           "animation-timing-function:linear}",
           "@keyframes aimTrgAdd{0%{opacity:0}4%{opacity:1}22%{opacity:1}30%{opacity:0}"
           "100%{opacity:0}}",
           ".aim-trg-add{opacity:0;animation-name:aimTrgAdd;animation-iteration-count:infinite;"
           f"animation-duration:{TRG_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-trg-clock{animation:none!important;"
           "transform:none!important}.aim-trg-add{opacity:1;animation:none!important}}"]
    body = []
    for index, (x, name, note, adds) in enumerate((
            (12, "Regain 0", "every run is the same length", ()),
            (392, "Regain set", "a good run lasts longer", (0.3, 0.55, 0.78)))):
        left, width = x + 30, 296
        body.append(f'<rect x="{x}" y="46" width="356" height="{TRG_H - 74}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        body.append(f'<rect x="{left}" y="128" width="{width}" height="26" rx="8" '
                    'class="fig-grid-fill" opacity="0.4"/>')
        body.append(f'<rect x="{left}" y="128" width="{width}" height="26" rx="8" '
                    f'class="fig-balanced-fill aim-trg-clock" '
                    f'style="animation-duration:{TRG_T * (1 + 0.28 * len(adds)):.2f}s"/>')
        body.append(text(x + 178, 118, "time remaining", "fig-muted", size=12, weight=500))
        for order, at in enumerate(adds):
            ax = left + width * at
            body.append(f'<g class="aim-trg-add" style="animation-delay:{TRG_T * at:.2f}s">'
                        f'<path d="M{ax:.1f} 170V190" class="fig-accent-stroke" stroke-width="2.4" '
                        'marker-end="url(#fig-trg-arrow)"/>'
                        + text(ax, 208, "+ kill", "fig-accent-text", size=12, weight=700) + "</g>")
        body.append(text(x + 178, 244, "two scores over one clock" if not adds
                         else "two scores over different clocks", "fig-muted", size=13,
                         weight=500))
    return (f'<svg viewBox="0 0 {TRG_W} {TRG_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-timeregained-title"><title id="fig-timeregained-title">Two '
            'countdown bars. Without time regained the bar empties once and every run is the same '
            'length. With it set, three kills each add time, so the run stretches and two scores '
            'are no longer measured over the same clock.</title>'
            '<defs><marker id="fig-trg-arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 Z" '
            'class="fig-accent-fill"/></marker></defs>'
            + metadata() + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


MUL_W = 760
MUL_H = 300
MUL_T = 6.4


def multipliers() -> str:
    """Final score multipliers, and the warning beside them: the editor recommends not checking
    both Accuracy and Damage Efficiency, because the same misses are then charged for twice."""
    css = ["@keyframes aimMulStep{0%{opacity:0}6%{opacity:1}100%{opacity:1}}",
           ".aim-mul-step{opacity:0;animation-name:aimMulStep;animation-iteration-count:infinite;"
           f"animation-duration:{MUL_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-mul-step{opacity:1;"
           "animation:none!important}}"]
    body = []
    for index, (x, name, note, chain, final, tone) in enumerate((
            (12, "One multiplier", "misses charged once", ("1000", "x 0.8"), "800",
             "fig-balanced-fill"),
            (392, "Both checked", "the same misses, twice", ("1000", "x 0.8", "x 0.8"), "640",
             "fig-tense-fill"))):
        body.append(f'<rect x="{x}" y="46" width="356" height="{MUL_H - 76}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        labels = ("subtotal", "accuracy", "damage efficiency")
        for order, part in enumerate(chain):
            y = 104 + order * 44
            body.append(f'<g class="aim-mul-step" style="animation-delay:{order * 0.5:.2f}s">'
                        + text(x + 40, y, part, "fig-ink", anchor="start", size=16, weight=700)
                        + text(x + 130, y, labels[order], "fig-muted", anchor="start", size=12,
                               weight=500) + "</g>")
        y = 104 + len(chain) * 44
        body.append(f'<path d="M{x + 36} {y - 18}H{x + 300}" class="fig-grid-stroke" '
                    'stroke-width="2"/>')
        body.append(f'<g class="aim-mul-step" style="animation-delay:{len(chain) * 0.5:.2f}s">'
                    + text(x + 40, y + 12, final, tone, anchor="start", size=20, weight=700)
                    + "</g>")
        if index == 1:
            body.append('<g>'
                        + text(x + 178, MUL_H - 34, "the editor advises against this",
                               "fig-tense-fill", size=13, weight=700) + "</g>")
    return (f'<svg viewBox="0 0 {MUL_W} {MUL_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-multipliers-title"><title id="fig-multipliers-title">Two score '
            'calculations from the same subtotal of one thousand. Applying one multiplier gives '
            'eight hundred. Applying accuracy and damage efficiency together gives six hundred and '
            'forty, and is marked as advised against.</title>' + metadata()
            + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


LFV_W = 760
LFV_H = 290
LFV_T = 5.2


def lockfov() -> str:
    """Lock Hipfire FOV and the range beside it. A target's angular size depends on the reader's
    field of view, so a scenario that does not clamp it is a slightly different scenario for
    everyone who plays it.

    Both readers are drawn side by side rather than alternating. An alternating pair cannot show a
    comparison in a still frame, and a still frame is what a reduced-motion reader gets."""
    css = ["@keyframes aimLfvIn{0%{opacity:0}8%{opacity:1}100%{opacity:1}}",
           ".aim-lfv-in{opacity:0;animation-name:aimLfvIn;animation-iteration-count:infinite;"
           f"animation-duration:{LFV_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-lfv-in{opacity:1;"
           "animation:none!important}}"]
    body = []
    for index, (x, name, note, locked) in enumerate((
            (12, "Unlocked", "each reader gets a different drill", False),
            (392, "Locked to a range", "the same angular target for all", True))):
        cy = 150
        body.append(f'<rect x="{x}" y="46" width="356" height="{LFV_H - 74}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        for slot, (label, wide) in enumerate((("90 FOV", False), ("103 FOV", True))):
            cx = x + 100 + slot * 156
            r = 34 if (locked or not wide) else 21
            body.append(f'<g class="aim-lfv-in" style="animation-delay:{slot * 0.5:.2f}s">'
                        f'<circle cx="{cx}" cy="{cy}" r="{r}" class="fig-target"/></g>')
            body.append(crosshair("fig-ink-stroke", cx, cy))
            body.append(text(cx, cy + 64, label, "fig-muted", size=13, weight=600))
        body.append(text(x + 178, LFV_H - 34, "the wider view shrinks the target" if not locked
                         else "the clamp holds both the same", "fig-muted", size=12, weight=500))
    return (f'<svg viewBox="0 0 {LFV_W} {LFV_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-lockfov-title"><title id="fig-lockfov-title">Two panels, each '
            'showing two readers side by side at ninety and at a hundred and three degrees of '
            'field of view. Unlocked, the target is visibly smaller for the wider field of view. '
            'Locked to a range, both targets are the same size.</title>' + metadata()
            + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


FBK_W = 760
FBK_H = 280
FBK_T = 4.4


def feedback() -> str:
    """The disable switches on the Challenge tab, read as what they take away. Hit markers and hit
    sounds are the confirmation you normally get; turning them off makes a drill more like a game
    and harder to learn from."""
    css = ["@keyframes aimFbkShot{0%{opacity:0}10%{opacity:1}44%{opacity:1}52%{opacity:0}"
           "100%{opacity:0}}",
           ".aim-fbk-shot{opacity:0;animation-name:aimFbkShot;animation-iteration-count:infinite;"
           f"animation-duration:{FBK_T}s}}",
           "@keyframes aimFbkMark{0%{opacity:0}16%{opacity:1}40%{opacity:1}48%{opacity:0}"
           "100%{opacity:0}}",
           ".aim-fbk-mark{opacity:0;animation-name:aimFbkMark;animation-iteration-count:infinite;"
           f"animation-duration:{FBK_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-fbk-shot,.aim-fbk-mark{opacity:1;"
           "animation:none!important}}"]
    body = []
    for index, (x, name, note, shows) in enumerate((
            (12, "Markers on", "you know instantly", True),
            (392, "Markers off", "you have to watch the target", False))):
        cx, cy = x + 178, 142
        body.append(f'<rect x="{x}" y="46" width="356" height="{FBK_H - 76}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        body.append(f'<circle cx="{cx}" cy="{cy}" r="34" class="fig-target"/>')
        body.append(crosshair("fig-ink-stroke", cx + 10, cy - 8))
        if shows:
            body.append('<g class="aim-fbk-mark">'
                        f'<path d="M{cx - 6} {cy - 24}l-12 -12M{cx + 26} {cy - 24}l12 -12'
                        f'M{cx - 6} {cy + 8}l-12 12M{cx + 26} {cy + 8}l12 12" '
                        'class="fig-accent-stroke" stroke-width="3" stroke-linecap="round"/></g>')
            body.append('<g class="aim-fbk-shot">'
                        + text(cx, cy + 74, "hit", "fig-accent-text", size=14, weight=700)
                        + "</g>")
        else:
            body.append('<g class="aim-fbk-shot">'
                        + text(cx, cy + 74, "did that land?", "fig-muted", size=14, weight=700)
                        + "</g>")
        body.append(text(cx, FBK_H - 30, "feedback on every shot" if shows
                         else "closer to a game, harder to read", "fig-muted", size=12,
                         weight=500))
    return (f'<svg viewBox="0 0 {FBK_W} {FBK_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-feedback-title"><title id="fig-feedback-title">The same shot on '
            'the same target, twice. With hit markers on, four marks appear around the crosshair '
            'and the shot is labelled a hit. With them off there is no mark and the label asks '
            'whether it landed.</title>' + metadata() + f"<style>{''.join(css)}</style>"
            + "".join(body) + "</svg>")


FMD_W = 760
FMD_H = 320
FMD_T = 5.2
FMD_FRAMES = 44


def firemodes() -> str:
    """Three bot behaviors from two switches. No Aiming/Shooting strips the aiming logic entirely;
    Fire Weapons left unchecked keeps the aim but holds the trigger.

    The player moves in all three panels, so "aims" is shown by the bot's gaze following rather
    than stated. The gaze sits in a group rotated about the bot, which keeps the line attached at
    both ends; an earlier version translated a fixed line and detached it from both."""
    css = [".aim-fmd-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{FMD_T}s}}",
           "@keyframes aimFmdShot{0%{opacity:0;transform:translate(0,0)}"
           "44%{opacity:0;transform:translate(0,0)}48%{opacity:1;transform:translate(0,0)}"
           "62%{opacity:1;transform:translate(0,104px)}"
           "66%{opacity:0;transform:translate(0,104px)}"
           "100%{opacity:0;transform:translate(0,104px)}}",
           ".aim-fmd-shot{opacity:0;animation-name:aimFmdShot;animation-iteration-count:infinite;"
           f"animation-duration:{FMD_T}s;animation-timing-function:linear}}"]
    body = []
    amp, reach = 54.0, 126.0
    for index, (x, name, note, aims, fires) in enumerate((
            (12, "No aiming", "an inert target", False, False),
            (263, "Aims only", "tracks you, holds fire", True, False),
            (514, "Aims and fires", "a duel", True, True))):
        cx, bot_y = x + 117, 104
        you_y = bot_y + reach
        body.append(f'<rect x="{x}" y="46" width="234" height="{FMD_H - 76}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 16, 30, name, ""))
        body.append(text(cx, FMD_H - 20, note, "fig-muted", size=12, weight=500))
        # The player, moving in every panel so the bot's response is the only variable.
        moves = [(amp * math.sin(i / FMD_FRAMES * 6.28318), 0.0)
                 for i in range(FMD_FRAMES + 1)]
        if aims:
            # Negated: a positive SVG rotation is clockwise, so a line pointing down swings
            # its tip toward negative x. Without the sign the gaze tracked away from you.
            angles = [-math.degrees(math.atan2(dx, reach)) for dx, _ in moves]
            gaze = [f'<path d="M{cx} {bot_y + 20}V{bot_y + reach - 16}" '
                    'class="fig-cool-stroke" stroke-width="2" stroke-dasharray="4 4"/>']
            if fires:
                gaze.append(f'<circle cx="{cx}" cy="{bot_y + 22}" r="6" '
                            'class="fig-accent-fill aim-fmd-shot"/>')
            body.append(f'<g class="aim-fmd-anim aim-fmd-g{index}">{"".join(gaze)}</g>')
            css.append(keyframes(f"aimFmdGaze{index}", angles,
                                 lambda a: f"rotate({a:.2f}deg)"))
            css.append(f".aim-fmd-g{index}{{animation-name:aimFmdGaze{index};"
                       f"transform-box:view-box;transform-origin:{cx}px {bot_y}px}}")
        else:
            body.append(f'<path d="M{cx} {bot_y + 18}V{bot_y + 44}" class="fig-grid-stroke" '
                        'stroke-width="2" stroke-dasharray="4 4" opacity="0.6"/>')
            body.append(text(cx, bot_y + 64, "looks straight ahead", "fig-muted", size=11,
                             weight=500))
        body.append(f'<circle cx="{cx}" cy="{bot_y}" r="18" class="fig-target"/>')
        body.append(f'<g class="aim-fmd-anim aim-fmd-y{index}">'
                    f'{crosshair("fig-ink-stroke", cx, you_y)}</g>')
        css.append(keyframes(f"aimFmdYou{index}", moves,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".aim-fmd-y{index}{{animation-name:aimFmdYou{index}}}")
        body.append(text(cx, you_y + 28, "you", "fig-muted", size=11, weight=500))
    # Frozen off-centre, where a tracking gaze is visibly angled rather than straight down.
    css.append("@media (prefers-reduced-motion:reduce){.aim-fmd-anim{animation-play-state:paused;"
               f"animation-delay:-{FMD_T * 0.18:.2f}s!important}}"
               ".aim-fmd-shot{animation-play-state:paused;"
               f"animation-delay:-{FMD_T * 0.55:.2f}s!important}}}}")
    return (f'<svg viewBox="0 0 {FMD_W} {FMD_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-firemodes-title"><title id="fig-firemodes-title">Three panels, '
            'each with a bot above and your crosshair below, and in each the crosshair slides from '
            'side to side. In the first the bot keeps looking straight ahead. In the second a '
            'dashed line of sight swings to follow you. In the third it follows you and a round '
            'travels down it.</title>' + metadata() + f"<style>{''.join(css)}</style>"
            + "".join(body) + "</svg>")


MPD_W = 760
MPD_H = 300
MPD_T = 5.6
MPD_FRAMES = 52


def mousepad() -> str:
    """Max Turn On Mousepad and Max Aiming Error together. The bot's error grows once it turns past
    the given angle from its mousepad center, and is then clamped at the maximum. It is how an AI
    opponent is made to run out of desk the way a person does."""
    css = [".aim-mpd-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{MPD_T}s}}"]
    left, right = 92, 664
    base, top = 232, 104
    body = [f'<rect x="12" y="46" width="736" height="{MPD_H - 76}" rx="12" class="fig-panel"/>']
    body.append(lane_label(32, 30, "Turning past the mousepad",
                           "error grows, then stops growing"))
    limit, clamp = 0.42, 0.74
    body.append(f'<path d="M{left} {base}H{right}" class="fig-grid-stroke" stroke-width="2"/>')
    body.append(f'<path d="M{left} {base}V{top - 26}" class="fig-grid-stroke" '
                'stroke-width="2"/>')
    body.append(text(left - 10, top - 18, "error", "fig-muted", anchor="end", size=12,
                     weight=500))
    body.append(text(right, base + 24, "degrees turned", "fig-muted", anchor="end", size=12,
                     weight=500))

    def px(u: float) -> float:
        return left + (right - left) * u

    def err(u: float) -> float:
        if u < limit:
            return 0.12
        return min(1.0, 0.12 + (u - limit) * 2.6)

    pts = " ".join(f"{px(i / 60):.1f} {base - (base - top) * err(i / 60):.1f}" for i in range(61))
    body.append(f'<polyline points="{pts}" class="fig-accent-stroke" stroke-width="3" '
                'fill="none" stroke-linecap="round"/>')
    body.append(f'<path d="M{px(limit):.1f} {top - 4}V{base + 10}" class="fig-cool-stroke" '
                'stroke-width="2" stroke-dasharray="5 5"/>')
    body.append(text(px(limit), top - 14, "max turn on mousepad", "fig-cool-fill", size=12,
                     weight=600))
    body.append(f'<path d="M{left} {base - (base - top):.1f}H{right}" class="fig-tense-stroke" '
                'stroke-width="2" stroke-dasharray="5 5" opacity="0.8"/>')
    body.append(text(right - 4, base - (base - top) - 10, "max aiming error", "fig-tense-fill",
                     anchor="end", size=12, weight=600))
    frames = [(px(i / MPD_FRAMES) - left, base - (base - top) * err(i / MPD_FRAMES) - base)
              for i in range(MPD_FRAMES + 1)]
    body.append(f'<g class="aim-mpd-anim aim-mpd-ride">'
                f'<circle cx="{left}" cy="{base}" r="8" class="fig-target"/></g>')
    css.append(keyframes("aimMpdRide", frames,
                         lambda p: f"translate({p[0]:.1f}px,{p[1]:.1f}px)"))
    css.append(".aim-mpd-ride{animation-name:aimMpdRide}")
    css.append("@media (prefers-reduced-motion:reduce){.aim-mpd-anim{animation-play-state:paused;"
               f"animation-delay:-{MPD_T * 0.66:.2f}s!important}}}}")
    return (f'<svg viewBox="0 0 {MPD_W} {MPD_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-mousepad-title"><title id="fig-mousepad-title">A curve of the '
            'bot\\u2019s aiming error against how far it has turned. The error stays low until a '
            'marked mousepad limit, then climbs steeply, and flattens where it meets a marked '
            'maximum aiming error.</title>' + metadata() + f"<style>{''.join(css)}</style>"
            + "".join(body) + "</svg>")


EST_W = 760
EST_H = 290
EST_T = 5.6
EST_FRAMES = 56


def estimating() -> str:
    """Reaction Time, which the editor describes as how often the bot estimates its opponent's
    position and its own. It is a sampling rate rather than a delay: a slow one leaves the bot
    aiming at where you were when it last looked."""
    css = [".aim-est-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{EST_T}s}}"]
    body = []
    for index, (x, name, note, samples) in enumerate((
            (12, "Estimates often", "its guess stays current", 14),
            (392, "Estimates rarely", "it aims at where you were", 4))):
        cx, cy = x + 178, 148
        body.append(f'<rect x="{x}" y="46" width="356" height="{EST_H - 74}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        amp = 118.0
        body.append(f'<path d="M{cx - amp} {cy}H{cx + amp}" class="fig-grid-stroke" '
                    'stroke-width="2" stroke-dasharray="6 6" opacity="0.6"/>')
        # You move continuously; the bot's estimate updates in steps.
        you = [(amp * math.sin(i / EST_FRAMES * 6.28318), 0.0) for i in range(EST_FRAMES + 1)]
        guess = []
        for i in range(EST_FRAMES + 1):
            held = (i // max(1, EST_FRAMES // samples)) * max(1, EST_FRAMES // samples)
            guess.append((you[min(held, EST_FRAMES)][0], 0.0))
        body.append(f'<g class="aim-est-anim aim-est-g{index}">'
                    f'<circle cx="{cx}" cy="{cy}" r="21" class="fig-cool-stroke" '
                    'stroke-width="2.4" stroke-dasharray="5 4" fill="none"/></g>')
        css.append(keyframes(f"aimEstGuess{index}", guess,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".aim-est-g{index}{{animation-name:aimEstGuess{index}}}")
        body.append(f'<g class="aim-est-anim aim-est-y{index}">'
                    f'<circle cx="{cx}" cy="{cy}" r="14" class="fig-target"/></g>')
        css.append(keyframes(f"aimEstYou{index}", you,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".aim-est-y{index}{{animation-name:aimEstYou{index}}}")
        body.append(text(cx, cy - 46, "you", "fig-muted", size=12, weight=500))
        body.append(text(cx, cy + 52, "its estimate", "fig-cool-fill", size=12, weight=600))
        body.append(text(cx, EST_H - 30, f"{samples} estimates per pass", "fig-muted", size=12,
                         weight=500))
    css.append("@media (prefers-reduced-motion:reduce){.aim-est-anim{animation-play-state:paused;"
               f"animation-delay:-{EST_T * 0.19:.2f}s!important}}}}")
    return (f'<svg viewBox="0 0 {EST_W} {EST_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-estimating-title"><title id="fig-estimating-title">Two panels, '
            'each with a target moving smoothly and a ring marking where the bot thinks it is. '
            'Estimating often, the ring stays closed around the target. Estimating rarely, it '
            'lags behind on the same track in visible steps.</title>' + metadata()
            + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


CHG_W = 760
CHG_H = 280
CHG_T = 6.0


def charges() -> str:
    """Max Charges, Charges On Spawn and the charge timer together. They set how often an ability
    interrupts a run, which is the only part of an ability profile an aim drill cares about."""
    css = ["@keyframes aimChgUse{0%{opacity:1}24%{opacity:1}28%{opacity:0.2}100%{opacity:0.2}}",
           ".aim-chg-spent{animation-name:aimChgUse;animation-iteration-count:infinite;"
           f"animation-duration:{CHG_T}s}}",
           "@keyframes aimChgBack{0%{opacity:0.2}62%{opacity:0.2}70%{opacity:1}100%{opacity:1}}",
           ".aim-chg-back{opacity:0.2;animation-name:aimChgBack;animation-iteration-count:"
           f"infinite;animation-duration:{CHG_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-chg-spent,.aim-chg-back{opacity:1;"
           "animation:none!important}}"]
    body = []
    for index, (x, name, note, total, on_spawn) in enumerate((
            (12, "One charge", "one interruption, then nothing", 1, 1),
            (392, "Three charges", "three, and a timer refilling them", 3, 2))):
        cx = x + 178
        body.append(f'<rect x="{x}" y="46" width="356" height="{CHG_H - 76}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        span = 46 * total
        for pip in range(total):
            px_ = cx - span / 2 + 23 + pip * 46
            filled = pip < on_spawn
            cls = "aim-chg-spent" if filled and pip == 0 else (
                "aim-chg-back" if not filled else "")
            body.append(f'<circle cx="{px_}" cy="128" r="16" class="fig-grid-stroke" '
                        'stroke-width="2" fill="none"/>')
            dim = "" if filled else ' opacity="0.2"'
            body.append(f'<circle cx="{px_}" cy="128" r="11" class="fig-accent-fill {cls}"'
                        f'{dim}/>')
        body.append(text(cx, 176, f"{on_spawn} of {total} on spawn", "fig-muted", size=12,
                         weight=500))
        body.append(text(cx, CHG_H - 30, "spent, and gone" if total == 1
                         else "spent, and the timer brings one back", "fig-muted", size=12,
                         weight=500))
    return (f'<svg viewBox="0 0 {CHG_W} {CHG_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-charges-title"><title id="fig-charges-title">Two rows of ability '
            'charges drawn as rings. In the first a single charge is spent and stays empty. In the '
            'second one of three is spent and an empty ring fills again as the charge timer '
            'returns it.</title>' + metadata() + f"<style>{''.join(css)}</style>" + "".join(body)
            + "</svg>")


FRC_W = 760
FRC_H = 310
FRC_T = 5.6
FRC_FRAMES = 56


def friction() -> str:
    """The three frictions, which are three different questions. Scaling Friction is how fast a
    direction change happens, Let Off Friction is how fast a stop happens, and Aerial Friction is
    how fast horizontal speed is pulled back toward run speed in the air."""
    css = [".aim-frc-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{FRC_T}s}}"]
    body = []
    for index, (x, name, field, note) in enumerate((
            (12, "Scaling", "ground friction", "changing direction"),
            (263, "Let off", "braking drag", "coming to a stop"),
            (514, "Aerial", "in the air", "drifting back to run speed"))):
        cx, cy = x + 117, 160
        body.append(f'<rect x="{x}" y="46" width="234" height="{FRC_H - 92}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 16, 30, name, ""))
        body.append(text(cx, 84, field, "fig-muted", size=12, weight=600))
        body.append(text(cx, FRC_H - 30, note, "fig-muted", size=12, weight=500))
        body.append(f'<path d="M{cx - 82} {cy}H{cx + 82}" class="fig-grid-stroke" '
                    'stroke-width="2" stroke-dasharray="5 5" opacity="0.6"/>')
        frames = []
        for i in range(FRC_FRAMES + 1):
            u = i / FRC_FRAMES
            if index == 0:
                # A reversal: low friction overshoots the turn, high friction snaps.
                pos = 76 * math.sin(u * 6.28318)
            elif index == 1:
                # Run, then let go and coast to a halt.
                pos = -76 + 152 * smooth(min(1.0, u / 0.45)) if u < 0.7 else 76.0
            else:
                # In the air, speed decays toward the run-speed line.
                pos = 76 * math.cos(u * 6.28318) * max(0.0, 1 - u * 0.8)
            frames.append((pos, 0.0))
        body.append(f'<g class="aim-frc-anim aim-frc-{index}">'
                    f'<circle cx="{cx}" cy="{cy}" r="13" class="fig-target"/></g>')
        css.append(keyframes(f"aimFrcPath{index}", frames,
                             lambda p: f"translate({p[0]:.1f}px,0)"))
        css.append(f".aim-frc-{index}{{animation-name:aimFrcPath{index}}}")
        if index == 1:
            body.append(f'<path d="M{cx + 76} {cy - 26}V{cy + 26}" class="fig-balanced-stroke" '
                        'stroke-width="2.4"/>')
            body.append(text(cx + 76, cy + 46, "stops", "fig-balanced-fill", size=11, weight=700))
    css.append("@media (prefers-reduced-motion:reduce){.aim-frc-anim{animation-play-state:paused;"
               f"animation-delay:-{FRC_T * 0.4:.2f}s!important}}}}")
    return (f'<svg viewBox="0 0 {FRC_W} {FRC_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-friction-title"><title id="fig-friction-title">Three panels, one '
            'per friction field. The first shows a target reversing direction along a track. The '
            'second shows one running and coasting to a marked stop. The third shows one whose '
            'swing shrinks toward the middle as its speed is pulled back.</title>'
            + metadata() + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


SPB_W = 760
SPB_H = 300
SPB_T = 5.0


def speedbias() -> str:
    """Forward Speed Bias. The editor gives the default a precise meaning: at 1 a diagonal input
    moves you at 45 degrees to where you are looking. Larger favors forward and back, smaller
    favors the sides."""
    css = ["@keyframes aimSpbIn{0%{opacity:0}10%{opacity:1}100%{opacity:1}}",
           ".aim-spb-in{opacity:0;animation-name:aimSpbIn;animation-iteration-count:infinite;"
           f"animation-duration:{SPB_T}s}}",
           "@media (prefers-reduced-motion:reduce){.aim-spb-in{opacity:1;"
           "animation:none!important}}"]
    body = []
    for index, (x, name, note, angle) in enumerate((
            (12, "Below 1", "more to the sides", 66.0),
            (263, "1", "45 degrees, the default", 45.0),
            (514, "Above 1", "more forward and back", 24.0))):
        cx, cy = x + 117, 200
        body.append(f'<rect x="{x}" y="46" width="234" height="{SPB_H - 82}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 16, 30, name, ""))
        body.append(text(cx, SPB_H - 22, note, "fig-muted", size=12, weight=500))
        # Where you are looking, and where a forward-and-strafe input actually sends you.
        body.append(f'<path d="M{cx} {cy}V{cy - 104}" class="fig-grid-stroke" stroke-width="2" '
                    'stroke-dasharray="5 5"/>')
        body.append(text(cx, cy - 116, "looking", "fig-muted", size=11, weight=500))
        rad = math.radians(angle)
        ex, ey = cx + 104 * math.sin(rad), cy - 104 * math.cos(rad)
        body.append(f'<g class="aim-spb-in" style="animation-delay:{index * 0.3:.2f}s">'
                    f'<path d="M{cx} {cy}L{ex:.1f} {ey:.1f}" class="fig-accent-stroke" '
                    'stroke-width="3.4" stroke-linecap="round" '
                    'marker-end="url(#fig-spb-arrow)"/></g>')
        body.append(f'<circle cx="{cx}" cy="{cy}" r="7" class="fig-ink-fill"/>')
        body.append(text(cx, cy + 28, f"{angle:.0f} degrees", "fig-accent-text", size=12,
                         weight=700))
    return (f'<svg viewBox="0 0 {SPB_W} {SPB_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-speedbias-title"><title id="fig-speedbias-title">Three panels, '
            'each showing the direction you look and the direction a forward-and-strafe input '
            'actually sends you. Below one the arrow leans toward the side, at one it sits at '
            'forty-five degrees, above one it leans toward straight ahead.</title>'
            '<defs><marker id="fig-spb-arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 Z" '
            'class="fig-accent-fill"/></marker></defs>'
            + metadata() + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")


STP_W = 760
STP_H = 300
STP_T = 5.2
STP_FRAMES = 48


def stepup() -> str:
    """Step Up Height, whose tooltip names both failure modes: at zero the character has to jump at
    every step, and set huge it warps on top of obstacles."""
    css = [".aim-stp-anim{animation-timing-function:linear;animation-iteration-count:infinite;"
           f"animation-duration:{STP_T}s}}"]
    body = []
    for index, (x, name, note, mode) in enumerate((
            (12, "Zero", "jumps at every step", "jump"),
            (263, "Matched", "walks up it", "walk"),
            (514, "Huge", "warps on top", "warp"))):
        cx = x + 117
        ground, step_h = 214, 34
        body.append(f'<rect x="{x}" y="46" width="234" height="{STP_H - 82}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 16, 30, name, ""))
        body.append(text(cx, STP_H - 22, note, "fig-muted", size=12, weight=500))
        body.append(f'<path d="M{cx - 96} {ground}H{cx + 6}" class="fig-grid-stroke" '
                    'stroke-width="3"/>')
        body.append(f'<path d="M{cx + 6} {ground}V{ground - step_h}H{cx + 96}" '
                    'class="fig-grid-stroke" stroke-width="3" fill="none"/>')
        # Each mode needs its own profile, or the three panels agree everywhere except mid-step
        # and a frozen frame shows nothing. Zero leaves the ground to clear the lip, matched rises
        # as it crosses it, huge is already on top well before reaching it.
        frames = []
        for i in range(STP_FRAMES + 1):
            u = i / STP_FRAMES
            along = -84 + 168 * min(1.0, u / 0.86)
            if mode == "jump":
                rise = -60 * math.sin(max(0.0, min(1.0, (u - 0.26) / 0.34)) * 3.14159)
                if along >= 6:
                    rise = min(rise, -step_h)
            elif mode == "walk":
                rise = -step_h * max(0.0, min(1.0, (along - 2) / 12))
            else:
                rise = -step_h * max(0.0, min(1.0, (along + 52) / 10))
            frames.append((along, rise))
        body.append(f'<g class="aim-stp-anim aim-stp-{index}">'
                    f'<circle cx="{cx}" cy="{ground - 14}" r="12" class="fig-target"/></g>')
        css.append(keyframes(f"aimStpPath{index}", frames,
                             lambda p: f"translate({p[0]:.1f}px,{p[1]:.1f}px)"))
        css.append(f".aim-stp-{index}{{animation-name:aimStpPath{index}}}")
        if mode == "warp":
            body.append(f'<path d="M{cx - 58} {ground - 18}L{cx - 34} {ground - step_h - 20}" '
                        'class="fig-tense-stroke" stroke-width="2" stroke-dasharray="4 4"/>')
    css.append("@media (prefers-reduced-motion:reduce){.aim-stp-anim{animation-play-state:paused;"
               f"animation-delay:-{STP_T * 0.42:.2f}s!important}}}}")
    return (f'<svg viewBox="0 0 {STP_W} {STP_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-stepup-title"><title id="fig-stepup-title">Three panels, each '
            'with a character approaching the same low step. At zero it has to jump to clear it. '
            'Matched to the step it walks up. Set huge it jumps to the top from further '
            'away.</title>' + metadata() + f"<style>{''.join(css)}</style>" + "".join(body)
            + "</svg>")


CRB_W = 760
CRB_H = 300
CRB_T = 4.8


def crouchbox() -> str:
    """Crouch Height Multiplier, which the editor calls a multiplier of bounding box height, and
    Crouch Animation Rate, which it gives in seconds: 1 is 0.3, 2 is 0.15. A crouching target is a
    smaller target that arrives at a speed you set."""
    css = ["@keyframes aimCrbDuck{0%{transform:scaleY(1)}30%{transform:scaleY(0.55)}"
           "70%{transform:scaleY(0.55)}100%{transform:scaleY(1)}}",
           ".aim-crb-body{transform-box:fill-box;transform-origin:center bottom;"
           "animation-name:aimCrbDuck;animation-iteration-count:infinite;"
           "animation-timing-function:linear}",
           "@media (prefers-reduced-motion:reduce){.aim-crb-body{animation-play-state:paused;"
           f"animation-delay:-{CRB_T * 0.45:.2f}s!important}}"]
    body = []
    for index, (x, name, note, rate) in enumerate((
            (12, "Rate 1", "0.3 seconds to duck", 1.0),
            (392, "Rate 2", "0.15 seconds to duck", 2.0))):
        cx, floor = x + 178, 218
        body.append(f'<rect x="{x}" y="46" width="356" height="{CRB_H - 82}" rx="12" '
                    'class="fig-panel"/>')
        body.append(lane_label(x + 20, 30, name, note))
        body.append(f'<path d="M{cx - 110} {floor}H{cx + 110}" class="fig-grid-stroke" '
                    'stroke-width="3"/>')
        # The standing outline stays put so the shrink is measurable against it.
        body.append(f'<rect x="{cx - 30}" y="{floor - 104}" width="60" height="104" rx="10" '
                    'class="fig-grid-stroke" stroke-width="2" stroke-dasharray="5 5" '
                    'fill="none"/>')
        body.append(f'<rect x="{cx - 26}" y="{floor - 100}" width="52" height="100" rx="9" '
                    f'class="fig-target aim-crb-body" '
                    f'style="animation-duration:{CRB_T / rate:.2f}s"/>')
        # Both labels have to clear the panel floor, which sits at CRB_H - 82.
        body.append(text(cx, floor + 24, "standing height", "fig-muted", size=12, weight=500))
        body.append(text(cx, floor + 42, "crouched multiplier", "fig-cool-fill", size=12,
                         weight=600))
    css.append("}")
    return (f'<svg viewBox="0 0 {CRB_W} {CRB_H}" class="fig-fit" role="img" '
            'aria-labelledby="fig-crouchbox-title"><title id="fig-crouchbox-title">Two characters '
            'ducking inside a dashed outline of their standing height. Both shrink to the same '
            'crouched height, but the second reaches it in half the time.</title>'
            + metadata() + f"<style>{''.join(css)}</style>" + "".join(body) + "</svg>")
