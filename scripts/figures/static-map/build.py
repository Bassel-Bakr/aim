"""Regenerates the 48 node figures cited by docs/articles/weakness-targeted-static-flowchart.md.

    python scripts/figures/static-map/build.py

One figure per node of the static clicking chart. The nodes are data in nodes.py and the drawing is
five renderers, one per node kind, so a node is a row rather than a function.

All 48 land in one HTML document, where an inline <style> is page-global. A keyframe name or a CSS
class shared by two figures therefore breaks one of them, silently and only sometimes. The check
below is the reason this build has one: it caught the issue renderer sharing a reduced-motion rule
across all fourteen of its figures, which left thirteen paused on the wrong frame.
"""
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import nodes as node_table  # noqa: E402
import render_issue  # noqa: E402
import render_result  # noqa: E402
import render_scenario  # noqa: E402
import render_symptom  # noqa: E402
import render_technique  # noqa: E402
from publish import publish  # noqa: E402

RENDERERS = {"issue": render_issue, "symptom": render_symptom, "scenario": render_scenario,
             "result": render_result, "technique": render_technique}

# A figure is allowed two rule bodies for one class: the rule itself, and its reduced-motion
# override. A third means two figures disagree about what that class does.
MAX_RULE_BODIES = 2


def check_shared_names(figures: dict[str, str]) -> None:
    """Refuse to publish when two figures would fight over a name on the rendered page."""
    keyframes: Counter[str] = Counter()
    ids: Counter[str] = Counter()
    rules: defaultdict[str, set[str]] = defaultdict(set)
    for svg in figures.values():
        keyframes.update(re.findall(r"@keyframes\s+([A-Za-z0-9_-]+)", svg))
        ids.update(re.findall(r'id="([^"]+)"', svg))
        for match in re.finditer(r"(\.aim-[A-Za-z0-9_-]+)(?:,\.aim-[A-Za-z0-9_-]+)*\{([^}]*)\}",
                                 svg):
            rules[match.group(1)].add(match.group(2))
    problems = []
    for name, count in keyframes.items():
        if count > 1:
            problems.append(f"keyframe {name} is defined by {count} figures")
    for name, count in ids.items():
        if count > 1:
            problems.append(f"id {name} is used by {count} figures")
    for name, bodies in rules.items():
        if len(bodies) > MAX_RULE_BODIES:
            problems.append(f"class {name} has {len(bodies)} different rules across figures")
    if problems:
        raise SystemExit("figures would collide on the page:\n  " + "\n  ".join(problems))


def main() -> None:
    figures = {n.key: RENDERERS[n.kind].render(n) for n in node_table.NODES}
    check_shared_names(figures)
    publish(figures)


if __name__ == "__main__":
    main()
