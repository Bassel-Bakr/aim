"""One-shot: make `variance` mean what its nine duration fields need, and split off the two that
are not durations.

`variance` drew three jump arcs. That is right for Jump Time Max and wrong for a swap pause, a
reaction lag or an ability check interval, which are stretches of time rather than hops. The arcs
move to `jumpvary`, a crouch-depth version becomes `crouchvary`, and `variance` becomes three
stretches on a timeline whose lengths either match or do not.
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

OLD = '''    elif kind == "variance":
        # The same move, three times over. The only question is whether the three match.
        heights: tuple[float, ...] = ((30.0, 30.0, 30.0) if not strong
                                     else (16.0, 40.0, 26.0))
        body.append(f'<path d="M{mid - 78} {cy + 26}H{mid + 78}" class="fig-grid-stroke" '
                    'stroke-width="2"/>')
        for rep, arc in enumerate(heights):
            hx = mid - 52 + rep * 52
            body.append(f'<path d="M{hx - 16} {cy + 26}Q{hx} {cy + 26 - arc * 2} '
                        f'{hx + 16} {cy + 26}" class="fig-grid-stroke" stroke-width="1.4" '
                        'stroke-dasharray="3 4" fill="none" opacity="0.55"/>')
        frames = []
        for rep, arc in enumerate(heights):
            hx = -52.0 + rep * 52
            steps = FRAMES // 3
            for i in range(steps):
                u = i / steps
                frames.append((hx - 16 + 32 * u, -arc * 4 * u * (1 - u)))
        frames.append((frames[0][0], frames[0][1]))
        body.append(f'<g class="{cls}"><circle cx="{mid}" cy="{cy + 26}" r="9" '
                    'class="fig-target"/></g>')
        css += _slide(uid, side, "a", frames)
        body.append(text(mid, cy + 46, "every rep differs" if strong else "every rep matches",
                         "fig-muted", size=10, weight=600))
'''

NEW = '''    elif kind == "variance":
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
'''

RETAG = {
    "Jump Time Max": "jumpvary",
    "Crouch Time Max": "crouchvary",
}


def main() -> None:
    shapes = HERE / "shapes_hit.py"
    text = shapes.read_text(encoding="utf-8")
    if OLD not in text:
        raise SystemExit("the variance branch is not where this expected it")
    text = text.replace(OLD, NEW, 1)
    text = text.replace('"wall", "variance", "notarget",',
                        '"wall", "variance", "jumpvary", "crouchvary", "notarget",')
    shapes.write_text(text, encoding="utf-8", newline="\n")

    tabs = HERE / "tabs_dodge.py"
    spec = tabs.read_text(encoding="utf-8")
    for field, kind in RETAG.items():
        pattern = re.compile(r'(\("' + re.escape(field) + r'",.*?)"variance"', re.S)
        spec, count = pattern.subn(lambda m: f'{m.group(1)}"{kind}"', spec, count=1)
        if not count:
            raise SystemExit(f"no variance spec for {field}")
    tabs.write_text(spec, encoding="utf-8", newline="\n")
    print("variance split into duration, jump height and crouch depth")


if __name__ == "__main__":
    main()
