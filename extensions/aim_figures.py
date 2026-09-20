"""Figures live in their own files and are spliced into the page at build time.

A figure is an inline SVG: it carries no literal colours, only semantic classes such as fig-target
and fig-accent-stroke, which resolve from aim.css against the palette the page is using. Served as
a file through an <img>, an <object> or an <iframe>, it would render in a document of its own,
where the page's stylesheet and its [data-md-color-scheme] attribute do not reach, so every figure
would lose its colours and stop following the light and dark toggle.

The answer is indirection at build time rather than at request time, the same shape aim_references
uses for sources. A page carries one marker line:

    <!-- aim:figure dmainfields -->

and this extension replaces it with the contents of docs/figures/dmainfields.svg, so the HTML still
holds the SVG inline and nothing about rendering changes. What changes is the source: a page is
prose again rather than a megabyte of generated markup, and a figure diffs on its own.

An unknown name is a build error rather than a silently missing figure: a typo in a marker would
otherwise leave a hole in the page that nobody notices until a reader finds it.

Configured in zensical.toml:

    [project.markdown_extensions.aim_figures]
    folder = "docs/figures"
"""
import re
from pathlib import Path
from typing import Any

from markdown import Markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

MARKER = re.compile(r"^\s*<!--\s*aim:figure\s+([A-Za-z0-9_-]+)\s*-->\s*$")


class FigurePreprocessor(Preprocessor):
    def __init__(self, md: Markdown, folder: str) -> None:
        super().__init__(md)
        self.folder = Path(folder)

    def run(self, lines: list[str]) -> list[str]:
        out: list[str] = []
        for line in lines:
            found = MARKER.match(line)
            if not found:
                out.append(line)
                continue
            name = found.group(1)
            path = self.folder / f"{name}.svg"
            if not path.is_file():
                raise SystemExit(f"aim:figure {name} has no file at {path}")
            # One line: an SVG holds no blank lines, so Markdown cannot break it into paragraphs,
            # and the surrounding <figure> keeps it out of the typographic flow either way.
            out.append(path.read_text(encoding="utf-8").strip())
        return out


class AimFiguresExtension(Extension):
    def __init__(self, **kwargs: Any) -> None:
        self.config = {"folder": ["docs/figures", "Where the figure SVG files live"]}
        super().__init__(**kwargs)

    def extendMarkdown(self, md: Markdown) -> None:
        folder = str(self.getConfig("folder"))
        # Ahead of the fenced-code and reference preprocessors, so a figure is in place before
        # anything else inspects the page.
        md.preprocessors.register(FigurePreprocessor(md, folder), "aim_figures", 50)


def makeExtension(**kwargs: Any) -> AimFiguresExtension:
    return AimFiguresExtension(**kwargs)
