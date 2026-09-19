"""Render a tab's field strips, or a list of shapes, to throwaway pages under site/.

Checking a figure by eye needs it on a real page with the real stylesheet. Doing that by hand each
time is slow and easy to get subtly wrong, so this builds the pages: three strips each, in pairs,
one showing the animation and one frozen at 30% of the loop, which is what a reader with motion
turned off sees.

    python probe.py tab tabs_dodge MAIN      # every field of a tab, three per page
    python probe.py kind standoff swappause  # named shapes, with placeholder labels

Then open http://localhost:<port>/probe-<name>.html. Delete them with `python probe.py clean`.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = HERE.parents[2] / "site"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import fields  # noqa: E402

HEAD = ('<link rel="stylesheet" href="/assets/stylesheets/modern/main.ce62732f.min.css">'
        '<link rel="stylesheet" href="/assets/stylesheets/aim.css">')
FREEZE = ("<style>*{animation-play-state:paused!important;"
          "animation-delay:-1.2s!important}</style>")
BODY = ('<body data-md-color-scheme="default" style="margin:0">'
        '<div class="md-typeset" style="max-width:none;width:900px">'
        '<figure class="aim-figure" style="margin:0">')


def write(slug: str, svg: str) -> None:
    for name, extra in ((slug, ""), (slug + "-frozen", FREEZE)):
        (SITE / f"probe-{name}.html").write_text(
            HEAD + extra + BODY + svg + "</figure></div>", encoding="utf-8", newline="\n")


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] == "clean":
        for stale in SITE.glob("probe-*.html"):
            stale.unlink()
        print("probe pages removed")
        return
    mode = sys.argv[1]
    if mode == "tab":
        module_name, tab = sys.argv[2], sys.argv[3]
        module = __import__(module_name)
        spec = getattr(module, tab)
        for start in range(0, len(spec), 3):
            slug = f"{module_name}-{tab.lower()}-{start}"
            write(slug, fields.sheet(slug.replace("-", ""), f"{tab} from {start}", "",
                                     spec[start:start + 3]))
            print(f"probe-{slug}.html")
    else:
        names = sys.argv[2:]
        for start in range(0, len(names), 3):
            chunk = names[start:start + 3]
            slug = f"kinds-{start}"
            spec = tuple((k, "", k, "low", "high") for k in chunk)
            write(slug, fields.sheet(slug.replace("-", ""), "Shapes", "", spec))
            print(f"probe-{slug}.html: {', '.join(chunk)}")


if __name__ == "__main__":
    main()
