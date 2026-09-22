"""Check the generated node figures and the hotspot map they are pointed at by.

    python scripts/check_figures.py

Forty-eight figures are drawn from one table by five renderers, and all forty-eight land in one HTML
document. That makes two kinds of mistake easy and invisible.

The first is a name two figures share. An inline <style> inside an inline SVG is page-global, so a
keyframe name, a CSS class or an element id used by two figures means one of them quietly wins. It
does not throw, it does not fail the build, and it usually still animates, which is why it survives
review: the issue renderer once shared one reduced-motion rule across all fourteen of its figures,
leaving thirteen paused on the wrong frame while playing back perfectly.

The second is a hotspot that does not sit on its node. The boxes are measured from the image rather
than placed by hand, so they are right until the table changes under them. A box that has drifted
opens someone else's node, which is worse than no box at all.

Everything here is checked by rendering, not by reading the files on disk, so a stale SVG cannot
pass a check its generator would fail.
"""
import re
import sys
import xml.etree.ElementTree as ElementTree
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "figures"))
sys.path.insert(0, str(HERE / "figures" / "static-map"))
import chart_text  # noqa: E402
import hotspots  # noqa: E402
import nodes as node_table  # noqa: E402
import render_issue  # noqa: E402
import render_result  # noqa: E402
import render_scenario  # noqa: E402
import render_symptom  # noqa: E402
import render_technique  # noqa: E402

RENDERERS = {"issue": render_issue, "symptom": render_symptom, "scenario": render_scenario,
             "result": render_result, "technique": render_technique}
# Forty-eight figures on one page. The five written by hand for the same article run 7KB to 24KB
# each, which at this count would be a 700KB page, so these are held to a budget instead.
MAX_BYTES = 6144
# A class may carry its rule and its reduced-motion override. A third body means two figures
# disagree about what that class does.
MAX_RULE_BODIES = 2
KEYFRAME = re.compile(r"@keyframes\s+([A-Za-z0-9_-]+)")
ELEMENT_ID = re.compile(r'id="([^"]+)"')
CSS_RULE = re.compile(r"(\.aim-[A-Za-z0-9_-]+)(?:,\.aim-[A-Za-z0-9_-]+)*\{([^}]*)\}")
LITERAL_COLOUR = re.compile(r"#[0-9a-fA-F]{3,6}\b|rgb\(|hsl\(")
# Scenario names get renamed and unpublished by the people who made them, so the drawings carry
# shapes instead. A generated figure is the worst place for one to go stale.
SCENARIO_NAME = re.compile(r"\b1w\d|\bww\d|\bcA |pokeball|sixshot|voxTS|fuglaa", re.I)


def render_all() -> dict[str, str]:
    return {n.key: RENDERERS[n.kind].render(n) for n in node_table.NODES}


def table_errors() -> list[str]:
    """The table, the boxes and the transcription describe the same forty-eight nodes."""
    errors: list[str] = []
    keys = {n.key for n in node_table.NODES}
    for name, mapping in (("hotspots.HOTSPOTS", hotspots.HOTSPOTS),
                          ("hotspots.TEXT_BOXES", hotspots.TEXT_BOXES),
                          ("chart_text.CHART_TEXT", chart_text.CHART_TEXT)):
        for key in sorted(keys - set(mapping)):
            errors.append(f"{name}: no entry for {key}")
        for key in sorted(set(mapping) - keys):
            errors.append(f"{name}: {key} is not a node")
    duplicates = [k for k, count in Counter(n.key for n in node_table.NODES).items() if count > 1]
    errors += [f"nodes.py: {key} appears twice" for key in sorted(duplicates)]
    return errors


def hotspot_errors() -> list[str]:
    """Each box sits on its own node, inside the image, and on nobody else."""
    errors: list[str] = []
    for key, (left, top, width, height) in sorted(hotspots.TEXT_BOXES.items()):
        if key not in hotspots.HOTSPOTS:
            continue
        shape = hotspots.HOTSPOTS[key]
        if width <= 0 or height <= 0:
            errors.append(f"{key}: hotspot has no area")
        if not (0 <= left and 0 <= top and left + width <= 100.5 and top + height <= 100.5):
            errors.append(f"{key}: hotspot falls outside the image")
        # A text box is grown from the text's own centre to stay tappable, and that growth is
        # clamped to the shape. A box outside its shape opens a node the reader is not over.
        if (left < shape[0] - 0.01 or top < shape[1] - 0.01
                or left + width > shape[0] + shape[2] + 0.01
                or top + height > shape[1] + shape[3] + 0.01):
            errors.append(f"{key}: hotspot reaches outside its own node")
    for (key_a, box_a), (key_b, box_b) in combinations(sorted(hotspots.TEXT_BOXES.items()), 2):
        overlap_x = min(box_a[0] + box_a[2], box_b[0] + box_b[2]) - max(box_a[0], box_b[0])
        overlap_y = min(box_a[1] + box_a[3], box_b[1] + box_b[3]) - max(box_a[1], box_b[1])
        if overlap_x > 0 and overlap_y > 0:
            errors.append(f"{key_a} and {key_b}: hotspots overlap, so one covers the other")
    return errors


def figure_errors(figures: dict[str, str]) -> list[str]:
    """Each figure on its own: well formed, animated the way this repo animates, and small."""
    errors: list[str] = []
    for key, svg in sorted(figures.items()):
        try:
            ElementTree.fromstring(svg)
        except ElementTree.ParseError as error:
            errors.append(f"{key}: not well-formed XML, {error}")
            continue
        if "\n\n" in svg:
            errors.append(f"{key}: a blank line splits the figure into paragraphs in Markdown")
        if "<animate" in svg:
            errors.append(f"{key}: uses SMIL; figures here animate with CSS keyframes")
        if "prefers-reduced-motion" not in svg:
            errors.append(f"{key}: no reduced-motion rule")
        if len(svg) > MAX_BYTES:
            errors.append(f"{key}: {len(svg)} bytes, over the {MAX_BYTES} budget")
        body = re.sub(r"<metadata>.*?</metadata>", "", svg, flags=re.S)
        if LITERAL_COLOUR.search(body):
            errors.append(f"{key}: has a literal colour; figures use fig- classes so they follow "
                          "the scheme")
        if SCENARIO_NAME.search(body):
            errors.append(f"{key}: names a trainer scenario, which rots")
    return errors


def collision_errors(figures: dict[str, str]) -> list[str]:
    """No two figures fight over a name once they are on the same page."""
    keyframes: Counter[str] = Counter()
    ids: Counter[str] = Counter()
    rules: defaultdict[str, set[str]] = defaultdict(set)
    for svg in figures.values():
        keyframes.update(KEYFRAME.findall(svg))
        ids.update(ELEMENT_ID.findall(svg))
        for selector, body in CSS_RULE.findall(svg):
            rules[selector].add(body)
    errors = [f"keyframe {name} is defined by {count} figures"
              for name, count in sorted(keyframes.items()) if count > 1]
    errors += [f"id {name} is used by {count} figures"
               for name, count in sorted(ids.items()) if count > 1]
    errors += [f"class {name} has {len(bodies)} different rules across figures"
               for name, bodies in sorted(rules.items()) if len(bodies) > MAX_RULE_BODIES]
    return errors


def determinism_errors(figures: dict[str, str]) -> list[str]:
    """Drawing the same node twice gives the same bytes, or every rebuild churns the diff."""
    return [f"{n.key}: renders differently on a second call"
            for n in node_table.NODES if RENDERERS[n.kind].render(n) != figures[n.key]]


def main() -> int:
    errors = table_errors() + hotspot_errors()
    figures = render_all()
    errors += figure_errors(figures) + collision_errors(figures) + determinism_errors(figures)
    if errors:
        print("\n".join(errors))
        print(f"\n{len(errors)} problem(s) found")
        return 1
    total = sum(len(svg) for svg in figures.values())
    print(f"{len(figures)} figures, {total // 1024} KB, largest "
          f"{max(len(svg) for svg in figures.values())} bytes. All OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
