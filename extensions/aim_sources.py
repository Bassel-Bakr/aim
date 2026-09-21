"""The sourcing note at the top of a wiki page.

A page carries the marker line <!-- aim:sources -->, which this extension replaces with a note
saying which source tiers the page cites and whether anyone has checked it. The tiers are read
from the page's own [^REF-n] markers and the registry, so the note cannot drift from the citations:
add a source to a page and its note follows on the next build.

The marker takes an optional state, and an optional clause appended to the first sentence:

    <!-- aim:sources -->
    <!-- aim:sources checked -->
    <!-- aim:sources checked | plus field names read from the editor in September 2026 -->

The state decides the second sentence, and the three are deliberately different claims:

    (none)    Not yet checked claim by claim.
    checked   Checked against its sources. Not yet reviewed by a person.
    reviewed  (no second sentence)

"checked" means someone compared every claim against the source cited for it. "reviewed" means a
person signed off on the page. A page can be checked and still wrong in ways only a reader who
knows the subject would catch, which is why they are not the same word.

A page that cites nothing carries no marker and gets no note; navigation pages are not making
claims that a tier could describe.

Configured in zensical.toml:

    [project.markdown_extensions.aim_sources]
    registry = "references.yml"
"""
import os
import re
from typing import Any

from markdown import Markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

from aim_references import load_registry

MARKER = re.compile(r"^<!--\s*aim:sources\s*(?P<state>checked|reviewed)?\s*(?:\|\s*(?P<extra>.+?))?\s*-->$")
CITATION = re.compile(r"\[\^(REF-\d+)\]")
TITLE = "How this page is sourced"
WIDTH = 96

# What each tier is called in the note, strongest first. The order is the order they are listed in.
TIERS: dict[str, str] = {
    "research": "research and clinical guidance",
    "testing": "independent measurement",
    "practitioner": "named coaches and communities",
    "vendor": "vendor documentation",
    "reference": "general reference",
}

STATES: dict[str | None, str] = {
    None: "Not yet checked claim by claim.",
    "checked": "Checked against its sources. Not yet reviewed by a person.",
    "reviewed": "",
}


def phrase(parts: list[str]) -> str:
    """A readable list: one item alone, otherwise commas with a final "and"."""
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + ", and " + parts[-1]


def tiers_cited(text: str, registry: dict[str, Any]) -> list[str]:
    """The tiers this page's citations draw on, strongest first."""
    ids = set(CITATION.findall(text))
    found = {registry[ref]["tier"] for ref in ids if ref in registry}
    return [tier for tier in TIERS if tier in found]


def note(tiers: list[str], state: str | None, extra: str | None) -> list[str]:
    """The admonition lines for a page citing `tiers`, wrapped to the repository's width."""
    body = "Sourced from " + phrase([TIERS[tier] for tier in tiers])
    body += f", {extra}." if extra else "."
    tail = STATES[state]
    if tail:
        body += " " + tail
    wrapped: list[str] = []
    line = "   "
    for word in body.split():
        if len(line) + 1 + len(word) > WIDTH:
            wrapped.append(line)
            line = "   "
        line += " " + word
    wrapped.append(line)
    return ["", f'!!! note "{TITLE}"', *wrapped, ""]


class SourcesPreprocessor(Preprocessor):
    def __init__(self, md: Markdown, registry_path: str) -> None:
        super().__init__(md)
        self.registry_path = registry_path

    def run(self, lines: list[str]) -> list[str]:
        marks = [(index, MARKER.match(line.strip())) for index, line in enumerate(lines)]
        marks = [(index, match) for index, match in marks if match]
        if not marks:
            return lines
        registry = load_registry(self.registry_path)
        tiers = tiers_cited("\n".join(lines), registry)
        if not tiers:
            # Nothing cited: drop the marker rather than claim a sourcing the page does not have.
            return [line for index, line in enumerate(lines) if index not in {i for i, _ in marks}]
        out = list(lines)
        for index, match in reversed(marks):
            out[index : index + 1] = note(tiers, match.group("state"), match.group("extra"))
        return out


class SourcesExtension(Extension):
    def __init__(self, **kwargs: Any) -> None:
        self.config = {
            "registry": ["references.yml", "Path to the reference registry, from the project root."]
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md: Markdown) -> None:
        md.preprocessors.register(
            SourcesPreprocessor(md, self.getConfig("registry")), "aim_sources", 28
        )


def makeExtension(**kwargs: Any) -> SourcesExtension:
    return SourcesExtension(**kwargs)
