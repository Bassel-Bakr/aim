"""One-shot: lift every inline SVG out of the pages and into docs/figures.

The pages carried their figures inline, which left them at about 94 percent generated markup: a
page was a megabyte of SVG with some prose in it, unreadable in a diff and unreviewable in a pull
request. Each figure moves to its own file and the page keeps a marker the aim_figures extension
resolves at build time, so the rendered HTML is unchanged.

Run once from the repository root:

    python scripts/figures/extract.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
FIGURES = DOCS / "figures"
# The convention every generator already uses to find its own figure in a page.
SVG = re.compile(r'<svg\b[^>]*aria-labelledby="fig-([A-Za-z0-9_-]+)-title".*?</svg>', re.S)


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    seen: dict[str, Path] = {}
    moved = 0
    for page in sorted(DOCS.rglob("*.md")):
        text = page.read_text(encoding="utf-8")
        if "<svg" not in text:
            continue
        names: list[str] = []

        def take(match: re.Match[str]) -> str:
            name = match.group(1)
            if name in seen:
                raise SystemExit(f"two figures named {name}: {seen[name]} and {page}")
            seen[name] = page
            (FIGURES / f"{name}.svg").write_text(match.group(0) + "\n", encoding="utf-8",
                                                 newline="\n")
            names.append(name)
            return f"<!-- aim:figure {name} -->"

        text = SVG.sub(take, text)
        if not names:
            continue
        page.write_text(text, encoding="utf-8", newline="\n")
        moved += len(names)
        print(f"{page.relative_to(ROOT)}: {len(names)} figures")
    print(f"{moved} figures now in {FIGURES.relative_to(ROOT)}")
    left = [p for p in DOCS.rglob("*.md") if "<svg" in p.read_text(encoding="utf-8")]
    if left:
        raise SystemExit("inline SVG left behind in: "
                         + ", ".join(str(p.relative_to(ROOT)) for p in left))


if __name__ == "__main__":
    main()
