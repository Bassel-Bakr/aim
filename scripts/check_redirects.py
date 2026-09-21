"""Find registry URLs that have quietly moved.

    python scripts/check_redirects.py
    python scripts/check_redirects.py REF-30 REF-42      # only these

lychee checks for dead links once a week. A link that redirects is not dead, so a source that
changes domain passes every check the repository runs while the citation slowly rots: the redirect
holds until whoever set it up stops paying for the old domain, and then a reference points nowhere.
kova moved from pyvno.xyz to kova.page in September 2026 and nothing here would have noticed.

This is a separate script rather than part of check_pages.py, for the same reason the colour check
is separate: it needs the network, it is slow, and it is about the registry rather than the pages.
Run it when a source feels stale, or on a schedule.

A redirect is only reported when the destination differs in more than a trailing slash or a www
prefix, since those carry no meaning. Read the whole report rather than the exit code: a redirect
can be a rename worth following, a login wall, or a regional edition, and only a person can tell
which.
"""
import sys
import urllib.error
import urllib.request
from typing import NamedTuple
from urllib.parse import urljoin, urlsplit, urlunsplit

import yaml

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
TIMEOUT = 20
MAX_HOPS = 6
REDIRECTS = {301, 302, 303, 307, 308}


class Result(NamedTuple):
    ref_id: str
    url: str
    final: str | None
    status: int | None
    note: str


def canonical(url: str) -> str:
    """The parts of a URL that carry meaning, so a trailing slash is not reported as a move."""
    parts = urlsplit(url)
    host = parts.netloc.lower().removeprefix("www.")
    path = parts.path.rstrip("/")
    return urlunsplit((parts.scheme, host, path, parts.query, ""))


def follow(url: str) -> tuple[str | None, int | None, str]:
    """Walk the redirect chain by hand, so the destination is visible rather than followed silently."""
    here = url
    for _hop in range(MAX_HOPS):
        request = urllib.request.Request(here, headers={"User-Agent": UA}, method="GET")
        try:
            # Redirects are not followed: the handler is removed so the 3xx surfaces as an error.
            opener = urllib.request.build_opener(NoRedirect())
            with opener.open(request, timeout=TIMEOUT) as response:
                return here, response.status, ""
        except urllib.error.HTTPError as error:
            if error.code in REDIRECTS:
                location = error.headers.get("Location")
                if not location:
                    return here, error.code, "redirect without a Location header"
                here = urljoin(here, location)
                continue
            return here, error.code, ""
        except Exception as error:  # noqa: BLE001 - a network failure is a result, not a crash
            return None, None, type(error).__name__
    return here, None, f"more than {MAX_HOPS} redirects"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args: object, **kwargs: object) -> None:
        return None


def check(entries: list[dict[str, str]]) -> list[Result]:
    results: list[Result] = []
    for entry in entries:
        final, status, note = follow(entry["url"])
        results.append(Result(entry["id"], entry["url"], final, status, note))
    return results


def main(argv: list[str]) -> int:
    with open("references.yml", encoding="utf-8") as handle:
        entries = yaml.safe_load(handle) or []
    wanted = {arg.upper() for arg in argv if arg.startswith("REF-")}
    if wanted:
        entries = [entry for entry in entries if entry["id"] in wanted]
    if not entries:
        print("no matching references")
        return 0

    moved: list[Result] = []
    unreachable: list[Result] = []
    for index, result in enumerate(check(entries), start=1):
        print(f"\r{index}/{len(entries)} checked", end="", file=sys.stderr, flush=True)
        if result.final is None:
            unreachable.append(result)
        elif canonical(result.final) != canonical(result.url):
            moved.append(result)
    print("\r", end="", file=sys.stderr)

    if moved:
        print(f"Moved ({len(moved)}), which lychee will not report because the link still works:")
        for result in moved:
            print(f"  {result.ref_id}: {result.url}")
            print(f"    -> {result.final}")
    if unreachable:
        print(f"\nCould not be reached ({len(unreachable)}). A block or a timeout, not necessarily a move:")
        for result in unreachable:
            print(f"  {result.ref_id}: {result.url} ({result.note})")
    if not moved and not unreachable:
        print(f"All {len(entries)} registry URLs resolve to themselves.")
    return 1 if moved else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
