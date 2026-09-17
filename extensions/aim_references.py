"""Centralized references for the Aim wiki.

Sources live once, in references.yml, each under a stable ID such as REF-12. A wiki page cites one
with an ordinary footnote marker, [^REF-12], and never defines it: this extension appends the
definition for every REF ID the page cites, built from the registry, under a "References" heading,
so the theme renders them as normal footnotes. It appends only the IDs the page actually cites, because Python-Markdown lists every
defined footnote whether or not the page refers to it.

Footnotes that are not sources, such as a clarifying aside, keep working as before: give them any
label that is not a REF ID and define them on the page.

The References page carries the marker line <!-- aim:references -->, which this extension replaces
with the whole registry, sorted by author and grouped by first letter.

Configured in zensical.toml:

    [project.markdown_extensions.aim_references]
    registry = "references.yml"
"""
import os
import re
from typing import Any

import yaml
from markdown import Markdown
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor
from markdown.preprocessors import Preprocessor
from zensical.extensions.context import ContextPreprocessor

CITATION = re.compile(r"\[\^(REF-[1-9]\d*)\](?!:)")
# Two citations for one claim are written back to back, so their markers render as adjacent
# <sup> elements with nothing between them. CSS cannot tell that pair from two markers with a
# sentence in between — a sibling selector skips text — so the second marker of a real pair is
# tagged here, where the gap is still visible, and aim.css draws the divider on that class.
CITATION_RUN = re.compile(r'</sup><sup id="fnref')
CITATION_RUN_CLASS = "aim-citation-run"
REFERENCES_MARKER = "<!-- aim:references -->"
REFERENCES_PAGE = "wiki/references.md"
# One source as references.yml holds it: id, author, title, url and type, with publication and
# notes where the source has them.
Entry = dict[str, str]
TYPE_LABELS = {
    "article": "Article",
    "document": "Document",
    "documentation": "Documentation",
    "encyclopedia": "Encyclopedia",
    "post": "Post",
    "repository": "Repository",
    "study": "Study",
    "video": "Video",
    "website": "Website",
}


def load_registry(path: str) -> dict[str, Entry]:
    with open(path, encoding="utf-8") as handle:
        entries = yaml.safe_load(handle) or []
    return {entry["id"]: entry for entry in entries}


def anchor(ref_id: str) -> str:
    return ref_id.lower()


def sort_key(entry: Entry) -> tuple[str, str]:
    return (entry["author"].casefold(), entry["title"].casefold())


def source_text(entry: Entry) -> str:
    text = f"{entry['author']}, [{entry['title']}]({entry['url']})"
    if entry.get("publication"):
        text += f", {entry['publication']}"
    return text


class ReferencesPreprocessor(Preprocessor):
    def __init__(self, md: Markdown, registry_path: str) -> None:
        super().__init__(md)
        self.registry_path = registry_path
        self._registry: dict[str, Entry] | None = None

    @property
    def registry(self) -> dict[str, Entry]:
        if self._registry is None:
            self._registry = load_registry(self.registry_path)
        return self._registry

    def run(self, lines: list[str]) -> list[str]:
        if REFERENCES_MARKER in (line.strip() for line in lines):
            lines = [out for line in lines for out in (self.bibliography() if line.strip() == REFERENCES_MARKER else [line])]
        cited: list[str] = []
        fenced = False
        for line in lines:
            if line.lstrip().startswith(("```", "~~~")):
                fenced = not fenced
            if not fenced:
                cited += [ref_id for ref_id in CITATION.findall(line) if ref_id not in cited]
        if not cited:
            return lines
        # Zensical's rendering context names the page, so a footnote can link to its entry on the
        # References page with a correct relative path.
        context = ContextPreprocessor.from_markdown(self.md)
        page = context.page.path.replace("\\", "/") if context else None
        link_base = None
        if page:
            link_base = os.path.relpath(REFERENCES_PAGE, os.path.dirname(page) or ".").replace("\\", "/")
        # The heading is added here, not written on the page, so it appears exactly when there are
        # sources to list and always sits directly above them.
        definitions = ["", "## References", ""]
        for ref_id in cited:
            entry = self.registry.get(ref_id)
            if entry is None:
                definitions.append(f"[^{ref_id}]: **Unknown reference {ref_id}.**")
                continue
            text = source_text(entry)
            if link_base and page != REFERENCES_PAGE:
                text += f" · [{ref_id}]({link_base}#{anchor(ref_id)})"
            definitions.append(f"[^{ref_id}]: {text}")
        return lines + definitions

    def bibliography(self) -> list[str]:
        out: list[str] = []
        letter: str | None = None
        for entry in sorted(self.registry.values(), key=sort_key):
            initial = entry["author"][0].upper()
            # A lone "#" would read as an empty Markdown heading, so digits and symbols group as 0–9.
            initial = initial if initial.isalpha() else "0–9"
            if initial != letter:
                letter = initial
                out += ["", f"## {letter}", ""]
            details = [f"`{entry['id']}`", TYPE_LABELS[entry["type"]]]
            if entry.get("publication"):
                details.append(entry["publication"])
            line = (f'- <span id="{anchor(entry["id"])}"></span>**{entry["author"]}**, '
                    f"[{entry['title']}]({entry['url']}) · " + " · ".join(details))
            if entry.get("notes"):
                line += f"  \n  {entry['notes']}"
            out.append(line)
        return out + [""]


class CitationRunPostprocessor(Postprocessor):
    """Mark every citation marker that follows another with no text between them."""

    def run(self, text: str) -> str:
        return CITATION_RUN.sub(f'</sup><sup class="{CITATION_RUN_CLASS}" id="fnref', text)


class ReferencesExtension(Extension):
    def __init__(self, **kwargs: Any) -> None:
        self.config = {"registry": ["references.yml", "Path to the reference registry, from the project root."]}
        super().__init__(**kwargs)

    def extendMarkdown(self, md: Markdown) -> None:
        md.preprocessors.register(ReferencesPreprocessor(md, self.getConfig("registry")), "aim_references", 25)
        # After the footnotes extension has written the markers, so the pairs are there to find.
        md.postprocessors.register(CitationRunPostprocessor(md), "aim_citation_runs", 25)


def makeExtension(**kwargs: Any) -> ReferencesExtension:
    return ReferencesExtension(**kwargs)
