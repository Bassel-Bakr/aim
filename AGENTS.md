# Agent guide

Instructions for AI coding agents working in this repository. Human contributors should read
[CONTRIBUTING.md](CONTRIBUTING.md) instead — this file points at the same rules and adds nothing
that contradicts them.

## What this repository is

A static documentation site about aim training, built with [Zensical](https://zensical.org) from
Markdown in `docs/`. Content is prose, not code. Most changes are edits to Markdown files plus a
matching `nav` entry in `zensical.toml`.

## Setup

Python 3.10 or later. See [README.md](README.md#run-the-site-locally) for the full walkthrough.

```bash
python -m venv .venv
```

Activate the environment (`.venv\Scripts\Activate.ps1` on Windows PowerShell, `source
.venv/bin/activate` on macOS or Linux), then:

```bash
pip install -r requirements.txt
```

## Commands

Preview the site locally with live reload on <http://localhost:8000>:

```bash
zensical serve
```

Verify a change before committing. Both commands must finish without errors, and the same checks
run on every pull request via `.github/workflows/check.yml`:

```bash
python scripts/check_pages.py
```

```bash
zensical build --clean
```

`scripts/check_pages.py` enforces four content rules: every `tags:` value is on the allowed list,
each concept page and each resource page carries a `related:` list in front matter where every
entry has a real reason, every citation names an ID in `references.yml` and runs together with
any other citation on the same claim, and every page carries a `description:` of 50 to 160
characters that no other page uses. It also checks that every myth block's title matches a heading on
`docs/wiki/myths.md` and links there as "Evidence", that each entry on that page is a heading
with `{ .aim-myth-title }` over an untitled myth block holding its verdict, that a myth block
elsewhere repeats that verdict word for word, and enforces the readability rules in
[CONTRIBUTING.md](CONTRIBUTING.md#readability). It reports the same readability rules for articles
under a separate heading, as advice rather than failures: the limits are worth meeting there too, but
an article is signed, so how it reads is its author's call. Pass `--drafts` to also require the draft
banner on every page. Name pages after the flags to check only those.
`zensical build` catches broken internal links and missing nav targets. The build no longer runs
with `--strict`, so link problems appear as warnings rather than failures — read the build output,
do not rely on the exit code alone.

External links are checked separately by lychee, on a weekly schedule rather than per pull request,
so a dead outbound link will not show up in the checks you run locally.

Colours are checked separately, because they change rarely and the check is about the palette rather
than the pages:

```bash
python scripts/check_contrast.py
```

It reads the tokens from `docs/assets/stylesheets/aim.css`, resolves them for both schemes, and
reports the contrast of every pair a reader reads, against WCAG AAA: 7:1 for text, 4.5:1 for large
text. Run it after changing any colour token, and read the whole report rather than the exit code,
since a pair can drop below AAA in one scheme while the other is fine. It is not part of the pull
request checks while known pairs are still below the line.

## Layout

| Path | Contents |
| --- | --- |
| `docs/index.md` | Site landing page. Not a wiki page. |
| `docs/wiki/` | All wiki pages, grouped by section. Sourced, open to contributions. |
| `docs/articles/` | Signed first-person pages. Not wiki pages, not open — see below. |
| `docs/assets/` | Favicon, `stylesheets/aim.css`, which documents each page component it defines, `javascripts/aim-theme.js`, the colour picker, and `javascripts/aim-stats.js`, which counts the landing page's stats up from 0. |
| `overrides/` | Theme template overrides. `main.html` loads the colour picker script in `<head>`, the Google Search Console verification tag from `extra.google_site_verification`, and the GoatCounter script from `extra.goatcounter_code`, both in `zensical.toml` and each left out while empty. It also builds every page's share card tags and its structured data from the page's `title:` and `description:`. Note that this template engine is not full Jinja: it has no `split`, `namespace` or `rstrip`, and does not set `page.is_homepage`. |
| `docs/robots.txt` | Tells crawlers everything is open and points them at `sitemap.xml`. Copied to the site root by the build. |
| `includes/abbreviations.md` | Abbreviation definitions shown as tooltips site-wide. |
| `references.yml` | Every source the wiki cites, once, under a stable `REF-<number>` ID. |
| `extensions/aim_related.py` | Markdown extension that writes the Related section from a page's `related:` front matter, adding bare links back from pages of the same kind that list it. Its helpers are shared by the checker and `scripts/suggest_related.py`. |
| `extensions/aim_stats.py` | Markdown extension that replaces `<!-- aim:stats -->` on the landing page with counts of wiki pages, cited sources and guides, each linking to the page it counts, so the hero's numbers follow the content. |
| `extensions/aim_references.py` | Markdown extension that turns `[^REF-<number>]` citations into footnotes and builds the References page. Installed by `pyproject.toml` through `requirements.txt`. |
| `templates/` | Page templates. Not published. |
| `specs/` | Design documents. Not published. |
| `scripts/` | Repository checks, `suggest_related.py`, `move_page.py`, which moves a page and repoints every link, related entry, nav entry and redirect to it, and `figures/`, the code that draws a page's diagrams and renders. Regenerate a page's figures with its `build.py` rather than editing them by hand. `figures/social/build.py` is the exception: it draws one card for the whole site, `docs/assets/images/social-card.png`, which every page's share tags point at. Rerun it after changing the wordmark or the tagline. |
| `zensical.toml` | Site config and the `nav` tree. |

## Python

Everything under `scripts/` and `extensions/` carries type annotations: parameters, return types, and
the empty collections whose element type is otherwise invisible. Keep them on code you add or
change. Nothing enforces this — no checker runs in CI — so a missing annotation shows up only when
someone reads the function. Run `mypy scripts extensions --ignore-missing-imports` locally if you
want them verified; `bpy` and `zensical` ship no stubs, which is what that flag is for.

Shapes that repeat have an alias rather than being spelled out at each use: `Meta` for a page's front
matter and `Element` for a metaball, among others. Import the alias instead of writing the shape
again, so the two places that read it cannot drift apart.

## Page components

`docs/assets/stylesheets/aim.css` defines a handful of classes that Markdown pages opt into. Each
one is documented above its own rules in the stylesheet, with the Markdown that produces it. Read
that before using one, and add a new component only when a page actually needs it.

| Class | What it does |
| --- | --- |
| `.aim-hero` | Landing-page opener. A page with a hero has the theme's generated title hidden, so the hero has to carry the title itself. |
| `.aim-cards` | Turns a list of links into a card grid. The whole card is the link, so each item needs exactly one link, written as its title. A second link in the same item ends up under the stretched hit area and cannot be clicked. |
| `.aim-steps` | Turns an ordered list into a numbered route. |
| `.aim-category` | Inline badge on a link naming a skill, with `.aim-category--clicking`, `--tracking` or `--switching` alongside it. |
| `.aim-table-stack` | Wraps a table whose last column should drop onto its own line below 38em instead of squeezing. |
| `.aim-figure` | A `<figure>` holding an inline SVG diagram or an image render, with a caption. Diagram colours come from its `fig-` classes, so they follow the scheme and picked colour. |
| `.aim-figure-credit` | A `<span>` at the end of a figure's caption naming a third-party asset the figure uses, its author and its licence. |

All of these except `.aim-category` are wrappers:

```markdown
<div class="aim-cards" markdown>

- **[Categories](wiki/categories/index.md)**: what the section covers.

</div>
```

The `markdown` attribute and the blank lines around the content are both required, or the Markdown
inside the wrapper is passed through as literal text. `.aim-category` goes on the link itself with
`attr_list`: `[Clicking](clicking.md){ .aim-category .aim-category--clicking }`.

Colour tokens in `aim.css` are also written by `docs/assets/javascripts/aim-theme.js` when a reader
picks a colour. A new scheme-dependent colour token has to be added to `derive` there as well, or it
keeps its default colour under every picked colour, and no test catches that.

## Rules that are easy to get wrong

Read [CONTRIBUTING.md](CONTRIBUTING.md) in full before adding a page. These are the constraints
agents most often miss:

1. Start from a template in `templates/` — `concept.md` for explanations, `resource.md` for
   communities, trainers and tools.
2. Page titles come from the `title:` field in front matter. Do not add an `#` heading in the body.
   Every page also carries a `description:`, one folded line of 50 to 160 characters saying what the
   page answers. It becomes the page's meta description, its search result text and its share card
   blurb, no two pages may share one, and `scripts/check_pages.py` rejects a page without it. See
   [CONTRIBUTING.md](CONTRIBUTING.md#describe-the-page).
3. Every new page needs a `nav` entry in `zensical.toml` and at least one inbound link from a related
   page.
4. Use only the tags listed in [CONTRIBUTING.md](CONTRIBUTING.md#tags). Do not invent new ones.
5. Write in your own words, and note that reusing a source's sentence with a few words changed is
   still copying — restate the claim from scratch, or quote and attribute it. Cite each fact with its
   source's ID from `references.yml` as a footnote marker, `[^REF-15]`, and never define it on the
   page: `extensions/aim_references.py` adds the definition. Where a sentence rests on several
   sources, run the markers together with nothing between them, `[^REF-77][^REF-74]`. Add a missing
   source to the registry with the next unused ID; never renumber one. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full
   rule and its two exceptions. Outside those exceptions, do not name the source in the sentence
   ("Aimlabs puts…", "a coach recommends…"): state the claim and let the footnote say who.
   Never copy guides, tables, or images from other sites — content here is CC BY-SA 4.0 and the
   sources are not. Third-party assets a figure is built from are the one exception; see
   [Third-party assets](#third-party-assets).
6. Do not assert a claim you cannot verify from a public source. Leave it out, or mark it with
   `<!-- REVIEW: what needs checking -->`.
7. A page written from research but not yet fact-checked keeps the draft banner at the top, exactly
   as shown in [CONTRIBUTING.md](CONTRIBUTING.md).
8. New abbreviations go in both `docs/wiki/glossary.md` and `includes/abbreviations.md`.
9. Every wiki page follows the readability rules in
   [CONTRIBUTING.md](CONTRIBUTING.md#readability): 45-word paragraphs, 25-word sentences, and on
   concept pages three to five answer bullets up top and a `**Do this next.**` paragraph at the end.
   Run `python scripts/check_pages.py <page>` on any page you write or edit.
10. When restructuring an existing page, run `python scripts/check_rewrite.py <base> <page>` before
    committing, where `<base>` is the commit before you started. It must print
    `Invariants unchanged`. A rewrite that drops a link or renames a heading breaks pages that link
    to it, and the build does not always say so.
11. When you add or edit a page's `related:` list, run `python scripts/suggest_related.py <page>`.
    Draft a reason for each suggestion worth keeping from what both pages actually say, and drop the
    rest. A reason names how the other page connects to this one; do not invent a connection the
    pages do not support. Do the same for any bare link back the build shows on the other page.
12. Move or rename a page only with `python scripts/move_page.py <old> <new>`, never with a plain
    `git mv`. Review the other mentions it lists, then run `zensical build --clean`.

## Third-party assets

A figure may be built from someone else's model or texture where its licence allows it, which is
how `scripts/figures/tension/` renders a mouse and a forearm. Only a licence that permits reuse and
modification, such as CC BY 4.0, and only with the credit that licence asks for. The credit lives
in four places at once, and dropping any of them breaks the licence:

1. The file's own `license.txt`, kept beside it under `scripts/figures/<page>/models/<name>/`.
2. A `MODEL_CREDIT` constant in that page's `build.py`, naming each author, the asset and its
   licence.
3. The render's own metadata, written from that constant into EXIF `Artist`, `Copyright` and
   `ImageDescription`, and into XMP, so a copied file still carries it.
4. A visible `<span class="aim-figure-credit">` at the end of the figure's caption on the page.

CC BY also requires saying that the asset was changed. The credit line says so where the render
poses, recolours or cuts up the original, which it always does here.

## Articles are not wiki pages

`docs/articles/` is a separate part of the site at `/articles`, and none of the rules above apply to
it. Articles are signed opinion written from the maintainer's own experience: they use
`templates/article.md`, carry a `!!! info "Written by <name>"` byline instead of the draft banner,
take no tags, and do not require footnotes. `scripts/check_pages.py` enforces that.

Never write or edit an article on your own initiative. A byline names a real person as
accountable for every claim on the page, so its content is theirs to decide. Fix a typo or a dead
link if asked; send anything touching the argument itself back to the author.

## Deployment

`.github/workflows/deploy.yml` builds and publishes to GitHub Pages on a push to `main`, unless the
push touches nothing the site is built from: its `paths-ignore` list skips guides, `specs/`,
`templates/` and `scripts/`, which cannot change a published byte. Add a path there only if that
holds, and never one the build reads. Run the workflow by hand from the Actions tab to publish
anyway. Do not commit the `site/` directory; it is generated and ignored.
