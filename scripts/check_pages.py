"""Check wiki pages against the rules in CONTRIBUTING.md.

Usage:
    python scripts/check_pages.py                          # tags, sections, and readability
    python scripts/check_pages.py --drafts                 # also require the sourcing marker
    python scripts/check_pages.py docs/wiki/glossary.md    # check named pages only
"""
import re
import sys
from collections.abc import Iterator, Sequence
from pathlib import Path

import yaml
from markdown.extensions.toc import slugify
from aim_related import CONCEPT_DIRS, PLACEHOLDER, Meta, kind

DOCS = Path(__file__).resolve().parent.parent / "docs"
WIKI = DOCS / "wiki"
EXEMPT_FROM_BANNER = {"index.md", "wiki/tags.md"}
ALLOWED_TAGS = {
    "community", "trainer", "tool",
    "clicking", "tracking", "switching",
    "benchmarks", "routines", "sensitivity", "beginner",
    "myth",
}
BANNER = '<!-- aim:sources'
# Every page describes itself in one line. overrides/main.html puts that line in the page's meta
# description, its share card and its structured data, so a page without one is listed under the
# site's own description instead of its subject. Search engines cut the line off around 160
# characters, and one shorter than 50 says too little to be worth showing.
DESCRIPTION_MIN = 50
DESCRIPTION_MAX = 160
# Articles live outside docs/wiki/ because they run on a different trust model: signed opinion
# written from experience, carrying the author's name instead of a citation trail. They are not
# wiki pages and do not follow wiki rules.
ARTICLES = DOCS / "articles"
BYLINE = '!!! info "Written by '
# A myth block elsewhere names its myth: its title must match a heading on wiki/myths.md word for
# word, and its one link, "Evidence", goes to that heading's anchor. On the hub itself each entry
# heading carries .aim-myth-title and is the title bar of an untitled myth block holding its verdict,
# with no link; a myth block elsewhere repeats that verdict word for word.
MYTH_BLOCK = re.compile(r'^!!! myth "([^"]*)"[ \t]*\n((?:(?:[ ]{4}.*)?\n)*)', re.M)
MYTH_LINK = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
MYTH_LINK_TEXT = "Evidence"
MYTH_HEADING = re.compile(r"^## (.+?)(?:\s*\{[^}]*\})?\s*$", re.M)
HUB_ENTRY = re.compile(r'^## (.+?)(\s*\{ \.aim-myth-title \})?[ \t]*\n\s*\n(!!! myth "")?', re.M)
HUB_VERDICT = re.compile(r'^## (.+?) \{ \.aim-myth-title \}[ \t]*\n\s*\n!!! myth ""[ \t]*\n((?:[ ]{4}.*\n)+)', re.M)
# Sources live once in references.yml and pages cite them by ID; see extensions/aim_references.py.
REGISTRY = DOCS.parent / "references.yml"
REFERENCE_ID = re.compile(r"^REF-[1-9]\d*$")
REFERENCE_CITATION = re.compile(r"\[\^(REF-[1-9]\d*)\](?!:)")
REFERENCE_DEFINITION = re.compile(r"^\[\^(REF-[^\]]*)\]:", re.M)
REFERENCE_MARKER = re.compile(r"\[\^(REF-[^\]]*)\](?!:)")
# Several sources for one claim sit together, [^REF-1][^REF-2], the way an encyclopedia stacks
# them: a comma or "and" between the markers reads as part of the sentence.
REFERENCE_RUN = re.compile(r"\[\^REF-[1-9]\d*\]([\s,;]+(?:and\s+)?)(?=\[\^REF-[1-9]\d*\])")
REFERENCES_HEADING = re.compile(r"^## References\s*$", re.M)
REFERENCE_FIELDS = {"id", "author", "title", "url", "type", "tier", "publication", "notes"}
REFERENCE_REQUIRED = {"id", "author", "title", "url", "type", "tier"}
REFERENCE_TYPES = {"article", "document", "documentation", "encyclopedia", "post", "repository", "study", "video", "website"}
# How much weight a source carries, which decides how strongly a claim may be worded.
# See CONTRIBUTING.md#source-tiers.
REFERENCE_TIERS = {"research", "testing", "practitioner", "vendor", "reference"}
# Related pages are listed in front matter and written out by extensions/aim_related.py.
RELATED_HEADING = re.compile(r"^## Related( pages)?\s*$", re.M)
RELATED_FIELDS = {"page", "why"}


def registry_ids() -> tuple[set[str], list[str]]:
    """Validate references.yml and return its IDs, with any problems found."""
    errors: list[str] = []
    entries = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or []
    ids: set[str] = set()
    urls: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"references.yml entry {index + 1}: not a mapping")
            continue
        where = f"references.yml {entry.get('id', f'entry {index + 1}')}"
        for field in sorted(REFERENCE_REQUIRED - entry.keys()):
            errors.append(f"{where}: missing '{field}'")
        for field in sorted(entry.keys() - REFERENCE_FIELDS):
            errors.append(f"{where}: unknown field '{field}'")
        ref_id, url = entry.get("id", ""), entry.get("url", "")
        if not REFERENCE_ID.match(str(ref_id)):
            errors.append(f"{where}: id must look like REF-1, with no leading zeros")
        if ref_id in ids:
            errors.append(f"{where}: duplicate id")
        if url in urls:
            errors.append(f"{where}: duplicate url {url}")
        if not str(url).startswith("https://"):
            errors.append(f"{where}: url must start with https://")
        if entry.get("type") not in REFERENCE_TYPES:
            errors.append(f"{where}: type '{entry.get('type')}' is not one of {', '.join(sorted(REFERENCE_TYPES))}")
        if entry.get("tier") not in REFERENCE_TIERS:
            errors.append(f"{where}: tier '{entry.get('tier')}' is not one of {', '.join(sorted(REFERENCE_TIERS))}")
        ids.add(ref_id)
        urls.add(url)
    return ids, errors


# A key block marks the one point a reader should leave a page with. Two on a page means neither
# is the one.
KEY_BLOCK = re.compile(r'^!!! key "', re.M)

# Readability. Most readers skim and many read with ADHD, so a page has to survive being read in
# passes: short paragraphs, short sentences, the answer first, and a way out at the end. See
# specs/2026-09-13-readability-design.md for where these numbers come from.
PARAGRAPH_LIMIT = 45
SENTENCE_LIMIT = 25
ANSWER_BULLETS = range(3, 6)
NEXT_ACTION = "**Do this next.**"
WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’/-]*")
# A sentence ends at . ! ? : or ; followed by a capital or digit. Abbreviations and decimals are
# shielded first so "e.g. Voltaic" and "0.27 sensitivity" do not end one.
ABBREVIATION = re.compile(r"\b(?:e\.g|i\.e|vs|etc|approx|cf)\.")
DECIMAL = re.compile(r"(\d)\.(\d)")
SENTENCE_END = re.compile(r"(?<=[.!?:;])[\"”’)]*\s+(?=[A-Z0-9\"“(\[])")
# The site writes US English, like its sources. Footnote definitions are exempt: they quote titles.
BRITISH = re.compile(
    r"\b(practis(?:e|ed|es|ing)|organis(?:e|ed|es|ing|ation)|behaviours?|colour(?:ed|ing|s)?"
    r"|centres?|analys(?:e|ed|ing)|labour|favourites?|defence|recognis(?:e|ed|es|ing)"
    r"|realis(?:e|ed|es|ing)|minimis(?:e|ed|es|ing)|optimis(?:e|ed|es|ing|ation))\b",
    re.I,
)


def front_matter(text: str) -> Meta:
    match = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not match:
        return {}
    return yaml.safe_load(match.group(1)) or {}


def myth_headings() -> dict[str, str | None]:
    """Each heading on wiki/myths.md, mapped to the verdict in the myth block under it, if any."""
    text = (WIKI / "myths.md").read_text(encoding="utf-8")
    verdicts = {heading: " ".join(block.split()) for heading, block in HUB_VERDICT.findall(text)}
    return {heading: verdicts.get(heading) for heading in MYTH_HEADING.findall(text)}


def related_errors(rel: str, meta: Meta) -> list[str]:
    """Problems with a page's related list."""
    related = meta.get("related")
    if related is None:
        return []
    if not isinstance(related, list):
        return [f"{rel}: 'related' must be a list of pages"]
    errors: list[str] = []
    seen: set[str] = set()
    for index, entry in enumerate(related):
        where = f"{rel}: related entry {index + 1}"
        if not isinstance(entry, dict) or entry.keys() != RELATED_FIELDS:
            errors.append(f"{where}: expected exactly 'page' and 'why'")
            continue
        page, why = entry["page"], entry["why"]
        if not isinstance(why, str) or not why.strip() or why.strip() == PLACEHOLDER:
            errors.append(f"{where}: 'why' must say how {page} connects to this page")
        if not isinstance(page, str) or not page.startswith("wiki/") or not page.endswith(".md"):
            errors.append(f"{where}: 'page' must be a docs-relative wiki page, like wiki/training/routines.md")
            continue
        if not (DOCS / page).is_file():
            errors.append(f"{where}: {page} does not exist")
            continue
        if page == rel:
            errors.append(f"{where}: a page cannot list itself")
        if page in seen:
            errors.append(f"{where}: {page} is listed twice")
        seen.add(page)
    return errors


def description_errors(rel: str, meta: Meta) -> list[str]:
    """Problems with the one-line description a page is listed under."""
    description = meta.get("description")
    if description is None:
        return [f"{rel}: missing a 'description' in front matter, the line search results show"]
    if not isinstance(description, str):
        return [f"{rel}: 'description' must be one line of text"]
    text = " ".join(description.split())
    if text != description.strip():
        return [f"{rel}: 'description' runs to several lines; write it as one, folded with '>-'"]
    if not DESCRIPTION_MIN <= len(text) <= DESCRIPTION_MAX:
        return [
            f"{rel}: description of {len(text)} characters, "
            f"expected {DESCRIPTION_MIN} to {DESCRIPTION_MAX}"
        ]
    return []


def body(text: str) -> str:
    """The page without its front matter, comments, or fenced code."""
    text = re.sub(r"\A---\r?\n.*?\r?\n---\r?\n", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return re.sub(r"```.*?```", "", text, flags=re.S)


def prose_blocks(text: str) -> Iterator[str]:
    """Paragraphs and lists that readers read as prose, with markup a reader never sees removed.

    Headings, tables, footnote definitions, and HTML are skipped: none of them is a run of prose.
    Admonitions are skipped too, except myth and key blocks, whose bodies are read like any
    paragraph because readers read them first.
    """
    for block in re.split(r"\n\s*\n", body(text)):
        stripped = block.strip()
        if stripped.startswith(("!!! myth ", "!!! key ")):
            content = "\n".join(line.strip() for line in stripped.split("\n")[1:])
            if content:
                yield content
            continue
        if not stripped or block.startswith("    "):
            continue
        if stripped.startswith(("#", "|", "[^", "<", "!!!", "???")):
            continue
        yield stripped


def plain(text: str) -> str:
    text = re.sub(r"\[\^[^\]]+\]", "", text)
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)(\{[^}]*\})?", r"\1", text)
    return " ".join(re.sub(r"[*_`]", "", text).split())


def units(block: str) -> list[tuple[bool, str]]:
    """A list yields one unit per item; a prose block yields itself as one paragraph."""
    if re.match(r"([-*]|\d+\.)\s", block):
        items = re.split(r"\n\s*(?:[-*]|\d+\.)\s+", "\n" + block)
        return [(False, plain(item)) for item in items if item.strip()]
    return [(True, plain(block))]


def sentences(text: str) -> list[str]:
    shielded = DECIMAL.sub(r"\1§\2", ABBREVIATION.sub(lambda m: m.group(0).replace(".", "§"), text))
    return [part.replace("§", ".") for part in SENTENCE_END.split(shielded) if part.strip()]


def words(text: str) -> int:
    return len(WORD.findall(text))


def excerpt(text: str) -> str:
    return text if len(text) <= 70 else text[:67] + "..."


def readability(rel: str, text: str, concept: bool) -> list[str]:
    errors: list[str] = []
    for block in prose_blocks(text):
        for is_paragraph, unit in units(block):
            # A list item is read as a paragraph, so it gets the same limit.
            if words(unit) > PARAGRAPH_LIMIT:
                kind = "paragraph" if is_paragraph else "list item"
                errors.append(
                    f"{rel}: {kind} of {words(unit)} words (limit {PARAGRAPH_LIMIT}): "
                    f'"{excerpt(unit)}"'
                )
            for sentence in sentences(unit):
                if words(sentence) > SENTENCE_LIMIT:
                    errors.append(
                        f"{rel}: sentence of {words(sentence)} words (limit {SENTENCE_LIMIT}): "
                        f'"{excerpt(sentence)}"'
                    )
    prose = re.sub(r"^\[\^[^\]]+\]:.*$", "", body(text), flags=re.M)
    related = front_matter(text).get("related")
    if isinstance(related, list):
        prose += "\n" + "\n".join(str(entry.get("why", "")) for entry in related if isinstance(entry, dict))
    for spelling in sorted({match.lower() for match in BRITISH.findall(prose)}):
        errors.append(f"{rel}: British spelling '{spelling}', the site writes US English")
    if concept:
        lead = body(text).split("\n## ", 1)[0]
        bullets = len(re.findall(r"^- ", lead, flags=re.M))
        if bullets not in ANSWER_BULLETS:
            errors.append(
                f"{rel}: opens with {bullets} bullets before its first heading, expected 3 to 5"
            )
        # The Related section is written directly above Resources, so this keeps the action above both.
        before_resources = text.split("\n## Resources", 1)[0]
        if NEXT_ACTION not in before_resources:
            errors.append(f"{rel}: missing a '{NEXT_ACTION}' paragraph before Resources")
    return errors


def check(path: Path, drafts: bool, headings: dict[str, str | None],
          known_ids: set[str]) -> tuple[list[str], list[str]]:
    """Problems that fail the check, and advice that does not."""
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(DOCS).as_posix()
    # Wiki pages live under docs/wiki/; their section is the first segment below that.
    in_wiki = path.is_relative_to(WIKI)
    section = path.relative_to(WIKI).as_posix().split("/")[0] if in_wiki else ""
    in_articles = path.is_relative_to(ARTICLES)
    is_index = path.name == "index.md"
    errors: list[str] = []
    advice: list[str] = []

    for tag in front_matter(text).get("tags") or []:
        if tag not in ALLOWED_TAGS:
            errors.append(f"{rel}: tag '{tag}' is not allowed")
    meta = front_matter(text)
    if kind(rel) and not is_index and not meta.get("related"):
        errors.append(f"{rel}: missing a 'related' list in front matter")
    if in_wiki and RELATED_HEADING.search(text):
        errors.append(f"{rel}: remove the Related heading; list related pages in front matter instead")
    errors += related_errors(rel, meta)
    errors += description_errors(rel, meta)
    # References are the sources for claims on this page; they sit under their own heading, apart
    # from Resources, which point readers to material for learning more.
    cited = set(REFERENCE_CITATION.findall(text))
    if in_wiki and REFERENCES_HEADING.search(text):
        errors.append(f"{rel}: remove '## References'; the references extension adds it")
    for marker in sorted(set(REFERENCE_MARKER.findall(text)) - cited):
        errors.append(f"{rel}: [^{marker}] is not a valid reference ID; use REF-1 style, no leading zeros")
    if REFERENCE_RUN.search(text):
        errors.append(f"{rel}: citations for one claim run together as [^REF-1][^REF-2]; remove what separates them")
    for ref_id in sorted(cited - known_ids):
        errors.append(f"{rel}: cites {ref_id}, which is not in references.yml")
    for label in REFERENCE_DEFINITION.findall(text):
        errors.append(f"{rel}: defines [^{label}] on the page; references are defined only in references.yml")
    if in_articles:
        # A byline replaces the draft banner: articles are signed, not pending review.
        if not is_index:
            if BYLINE not in text:
                errors.append(f'{rel}: missing byline, expected \'{BYLINE}<name>"\'')
            if "\n## Further resources" not in text:
                errors.append(f"{rel}: missing '## Further resources' section")
        if front_matter(text).get("tags"):
            errors.append(f"{rel}: articles do not carry tags")
        # An article's paragraphs are read by the same person who reads the wiki, so the length
        # limits are worth meeting here too. They are advice rather than a rule: an article is signed
        # by its author, and how it reads is the author's call in a way a wiki page's never is.
        advice += readability(rel, text, False)
    elif drafts and rel not in EXEMPT_FROM_BANNER and BANNER not in text:
        errors.append(f"{rel}: missing draft banner")
    if in_wiki:
        if rel == "wiki/myths.md":
            entries = HUB_ENTRY.findall(text)
            for heading, marked, block in entries:
                if not marked or not block:
                    errors.append(
                        f"{rel}: entry '{heading}' needs '{{ .aim-myth-title }}' on its heading and an "
                        f'untitled \'!!! myth ""\' block holding the claim directly below it'
                    )
            if len(MYTH_BLOCK.findall(text)) != len(entries):
                errors.append(f"{rel}: every myth block on this page sits directly under an entry heading")
        for title, block in MYTH_BLOCK.findall(text):
            links = MYTH_LINK.findall(block)
            if rel == "wiki/myths.md":
                if title:
                    errors.append(f"{rel}: myth block '{title}' must be untitled here; its heading is the title")
                if links:
                    errors.append(f"{rel}: myth block under an entry links out; on this page the answer follows it")
                continue
            if title not in headings:
                errors.append(
                    f"{rel}: myth block title '{title}' has no matching heading on wiki/myths.md"
                )
            # The correction reads the same wherever the myth appears: the hub entry's verdict.
            verdict = " ".join(MYTH_LINK.sub("", block).replace("{ .aim-myth-more }", "").split())
            if headings.get(title) and verdict != headings[title]:
                errors.append(
                    f"{rel}: myth block '{title}' must say exactly its verdict on wiki/myths.md: "
                    f'"{headings[title]}"'
                )
            anchor = "myths.md#" + slugify(title, "-")
            if len(links) != 1 or links[0][0] != MYTH_LINK_TEXT or not links[0][1].endswith(anchor):
                errors.append(f"{rel}: myth block '{title}' needs one link, [{MYTH_LINK_TEXT}](.../{anchor})")
        errors += readability(rel, text, section in CONCEPT_DIRS and not is_index)
        keys = len(KEY_BLOCK.findall(text))
        if keys > 1:
            errors.append(f"{rel}: {keys} key blocks, a page carries at most one")
    return errors, advice


def duplicate_descriptions(paths: Sequence[Path]) -> list[str]:
    """Two pages listed under the same line give a search engine no reason to show both."""
    seen: dict[str, list[str]] = {}
    for path in paths:
        meta = front_matter(path.read_text(encoding="utf-8"))
        description = meta.get("description")
        if not isinstance(description, str) or not description.strip():
            continue
        seen.setdefault(" ".join(description.split()), []).append(path.relative_to(DOCS).as_posix())
    return [
        f"{' and '.join(pages)}: share one description; each page describes its own subject"
        for pages in seen.values()
        if len(pages) > 1
    ]


def figure_files(paths: Sequence[Path]) -> list[str]:
    """Every figure file is cited, and every citation has a file.

    The aim_figures extension already fails the build on a marker with no file. The other way round
    is quieter: a renamed figure leaves its old SVG on disk, where nothing renders it and nothing
    complains, until someone wonders which of the two is live.
    """
    folder = DOCS / "figures"
    if not folder.is_dir():
        return []
    # Every page, not just the ones being checked: the editor hook lints one page at a time, and a
    # citation map built from that one page would call all the other figures orphans.
    cited: dict[str, list[str]] = {}
    for path in sorted(DOCS.rglob("*.md")):
        for name in re.findall(r"<!--\s*aim:figure\s+([A-Za-z0-9_-]+)\s*-->",
                               path.read_text(encoding="utf-8")):
            cited.setdefault(name, []).append(path.relative_to(DOCS).as_posix())
    on_disk = {svg.stem for svg in folder.glob("*.svg")}
    errors = [f"docs/figures/{name}.svg: no page cites this figure"
              for name in sorted(on_disk - set(cited))]
    errors += [f"{pages[0]}: cites figure {name}, which has no file in docs/figures"
               for name, pages in sorted(cited.items()) if name not in on_disk]
    errors += [f"{' and '.join(pages)}: both cite the figure {name}; a figure belongs to one page"
               for name, pages in sorted(cited.items()) if len(pages) > 1]
    return errors


def main() -> int:
    args = sys.argv[1:]
    drafts = "--drafts" in args
    named = [Path(arg).resolve() for arg in args if not arg.startswith("--")]
    paths = named or sorted(DOCS.rglob("*.md"))
    headings = myth_headings()
    known_ids, errors = registry_ids()
    advice: list[str] = []
    for path in paths:
        page_errors, page_advice = check(path, drafts, headings, known_ids)
        errors += page_errors
        advice += page_advice
    errors += duplicate_descriptions(paths)
    errors += figure_files(paths)
    for error in errors:
        print(error)
    if advice:
        print("Readability, strongly recommended but not required:")
        for note in advice:
            print(f"  {note}")
    print(f"{len(errors)} problem(s) found" if errors else "All pages OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
