"""Check the site's colours against WCAG AAA, in both schemes.

Usage:
    python scripts/check_contrast.py

Reads the tokens out of docs/assets/stylesheets/aim.css, resolves them for the light and the dark
scheme, and reports the contrast of each pair a reader actually reads. AAA wants 7:1 for body text
and 4.5:1 for large text, which is 24px, or 18.7px when bold. Anything a reader only has to see
rather than read, such as a rule or a grid line, is not text and is not checked here.

A pair that names a token this file cannot resolve is reported as unknown rather than passing
quietly: the tokens live in aim.css, but a few come from the theme, and those are listed below with
the value the theme gives them.
"""
import re
import sys
from pathlib import Path

CSS = Path(__file__).resolve().parent.parent / "docs" / "assets" / "stylesheets" / "aim.css"
BLOCK = re.compile(r"(?P<selector>^[^\n{]+)\{(?P<body>[^}]*)\}", re.M)
DECLARATION = re.compile(r"(--[\w-]+)\s*:\s*([^;]+);")
# Tokens the theme sets and aim.css does not, at the values the theme gives them.
THEME = {
    "light": {"--md-default-fg-color": "#000000de", "--md-default-fg-color--light": "#0000008a",
              "--md-default-bg-color": "#ffffff", "--md-code-bg-color": "#f5f5f5",
              "--md-typeset-color": "#000000de"},
    "dark": {"--md-code-bg-color": "#171a21"},
}
AAA_BODY = 7.0
AAA_LARGE = 4.5
# Each pair is (what it is, ink token, background token, the threshold it has to clear).
PAIRS = [
    ("body text", "--md-default-fg-color", "--md-default-bg-color", AAA_BODY),
    ("muted text", "--md-default-fg-color--light", "--md-default-bg-color", AAA_BODY),
    ("links", "--md-typeset-a-color", "--md-default-bg-color", AAA_BODY),
    ("headings", "--aim-heading", "--md-default-bg-color", AAA_LARGE),
    ("code block", "--md-default-fg-color", "--md-code-bg-color", AAA_BODY),
    ("header and footer", "--aim-chrome-fg", "--aim-chrome", AAA_BODY),
    ("header, quieter", "--aim-chrome-fg-light", "--aim-chrome", AAA_BODY),
    ("myth tag", "--aim-tag-ink", "--aim-myth", AAA_BODY),
    ("key tag", "--aim-key-tag-ink", "--aim-key", AAA_BODY),
    ("key title", "--aim-key-ink", "--md-default-bg-color", AAA_LARGE),
    # Figure ink sits on a panel, and its labels are small.
    ("figure: too tense", "--aim-tense", "--md-code-bg-color", AAA_BODY),
    ("figure: too loose", "--aim-loose", "--md-code-bg-color", AAA_BODY),
    ("figure: balanced", "--aim-balanced", "--md-code-bg-color", AAA_BODY),
    ("figure: accent", "--aim-accent", "--md-code-bg-color", AAA_BODY),
    ("category: clicking", "--aim-clicking", "--md-default-bg-color", AAA_BODY),
    ("category: tracking", "--aim-tracking", "--md-default-bg-color", AAA_BODY),
    ("category: switching", "--aim-switching", "--md-default-bg-color", AAA_BODY),
]


def scheme_tokens() -> dict[str, dict[str, str]]:
    """The raw declarations for each scheme, with the shared :root values underneath both."""
    css = CSS.read_text(encoding="utf-8")
    shared: dict[str, str] = {}
    light: dict[str, str] = {}
    dark: dict[str, str] = {}
    for match in BLOCK.finditer(css):
        selector = match.group("selector").strip()
        declarations = dict(DECLARATION.findall(match.group("body")))
        if not declarations:
            continue
        if selector == ":root":
            shared.update(declarations)
        elif selector.startswith('[data-md-color-scheme="default"]'):
            light.update(declarations)
        elif selector.startswith('[data-md-color-scheme="slate"]'):
            dark.update(declarations)
    return {"light": {**THEME["light"], **shared, **light},
            "dark": {**shared, **THEME["dark"], **dark}}


def resolve(token: str, tokens: dict[str, str], seen: set[str] | None = None) -> str | None:
    """A token's colour, following var() references until one lands on a literal."""
    seen = seen or set()
    if token in seen or token not in tokens:
        return None
    seen.add(token)
    value = tokens[token].strip()
    reference = re.fullmatch(r"var\((--[\w-]+)\)", value)
    if reference:
        return resolve(reference.group(1), tokens, seen)
    return value if value.startswith("#") else None


def rgba(value: str) -> tuple[float, float, float, float] | None:
    """A hex colour as red, green, blue and alpha, each 0 to 1."""
    digits = value.lstrip("#")
    if len(digits) in (3, 4):
        digits = "".join(digit * 2 for digit in digits)
    if len(digits) not in (6, 8):
        return None
    parts = [int(digits[i:i + 2], 16) / 255 for i in range(0, len(digits), 2)]
    return (*parts[:3], parts[3] if len(parts) == 4 else 1.0)  # type: ignore[return-value]


def over(ink: tuple[float, float, float, float],
         background: tuple[float, float, float, float]) -> tuple[float, float, float]:
    """Translucent ink composited onto its background, since contrast is about what you see."""
    return tuple(ink[i] * ink[3] + background[i] * (1 - ink[3]) for i in range(3))  # type: ignore[return-value]


def luminance(colour: tuple[float, float, float]) -> float:
    channels = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in colour]
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast(ink: str, background: str) -> float | None:
    ink_rgba, background_rgba = rgba(ink), rgba(background)
    if ink_rgba is None or background_rgba is None:
        return None
    first = luminance(over(ink_rgba, background_rgba))
    second = luminance(over(background_rgba, (1.0, 1.0, 1.0, 1.0)))
    lighter, darker = max(first, second), min(first, second)
    return (lighter + 0.05) / (darker + 0.05)


def main() -> int:
    schemes = scheme_tokens()
    failures: list[str] = []
    unknown: list[str] = []
    for scheme, tokens in schemes.items():
        print(f"{scheme}:")
        for name, ink_token, background_token, threshold in PAIRS:
            ink = resolve(ink_token, tokens)
            background = resolve(background_token, tokens)
            if ink is None or background is None:
                missing = ink_token if ink is None else background_token
                unknown.append(f"{scheme}: {name}: cannot resolve {missing}")
                print(f"  {name:22} ?      {missing} does not resolve to a colour")
                continue
            ratio = contrast(ink, background)
            if ratio is None:
                unknown.append(f"{scheme}: {name}: {ink} or {background} is not a hex colour")
                continue
            mark = "ok " if ratio >= threshold else "AAA"
            print(f"  {name:22} {ratio:5.2f}:1  needs {threshold}:1  {mark}")
            if ratio < threshold:
                failures.append(f"{scheme}: {name} is {ratio:.2f}:1, AAA wants {threshold}:1")
    for line in unknown:
        print(line)
    for line in failures:
        print(line)
    print(f"{len(failures)} pair(s) below AAA" if failures else "Every pair meets AAA")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
