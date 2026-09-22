"""Write the article's hotspot data block from the node table.

The page names all forty-eight figures in one JSON block, which aim-hotspots.js reads to build the
layer and which check_pages.py counts as citing them. Keeping that block generated means the page
and the table cannot disagree about which nodes exist.

    python scripts/figures/static-map/make_page.py

It rewrites only the block between the <script class="aim-hotspot-data"> tags, so the prose around
it is edited by hand like any other article.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import chart_text  # noqa: E402
import hotspots  # noqa: E402
import nodes  # noqa: E402

PAGE = HERE.parents[2] / "docs" / "articles" / "weakness-targeted-static-flowchart.md"
BLOCK = re.compile(r'(<script type="application/json" class="aim-hotspot-data">\n).*?(\n</script>)',
                   re.S)
# What kind of node this is. The chart says it in colour, which the panel does not inherit, so it
# is the one thing worth adding beside the chart's own sentence. Naming the node again underneath
# its own words would just be the sentence twice.
KIND = {"technique": "Technique", "issue": "Issue", "symptom": "What you see",
        "scenario": "What to play", "result": "What to expect"}


def data() -> dict[str, dict[str, object]]:
    """Each node's box, what the chart says, and which kind of node it is.

    The chart's own wording is the description. Paraphrasing it underneath itself said the same
    thing twice, so only the kind survives: it is what the chart carries in colour and the panel
    cannot.
    """
    return {n.key: {"box": list(hotspots.TEXT_BOXES[n.key]),
                    "says": chart_text.CHART_TEXT[n.key],
                    "kind": KIND[n.kind]}
            for n in nodes.NODES}


def main() -> None:
    text = PAGE.read_text(encoding="utf-8")
    block = json.dumps(data(), separators=(",", ":"))
    updated, count = BLOCK.subn(lambda m: m.group(1) + block + m.group(2), text)
    if not count:
        raise SystemExit("no aim-hotspot-data block on " + str(PAGE))
    PAGE.write_text(updated, encoding="utf-8")
    print(f"{len(data())} nodes written to {PAGE.name}")


if __name__ == "__main__":
    main()
