"""Regenerates the figures on docs/wiki/scenarios/making-a-scenario.md.

    python scripts/figures/scenario/build.py

Each diagram is rewritten in place inside the page, matched by its <svg>'s aria-labelledby id, so
edit the drawing code in diagrams.py and never the SVG in the page. The page keeps whatever caption
sits under each figure.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SECTION = ROOT / "docs" / "wiki" / "scenarios"
sys.path.insert(0, str(HERE))
import diagrams as d  # noqa: E402
import sheets  # noqa: E402

# Which diagrams belong to which page of the section, by the id each <svg> is matched on.
PAGES: dict[str, tuple[str, ...]] = {
    "index.md": ("copying",),
    "making-a-scenario.md": ("profiles", "spawn", "decisions"),
    "designing-around-a-weakness.md": ("weakest", "deliberate", "isolate", "shortcut"),
    "designing-target-motion.md": ("waypoints", "weights", "reactive", "travel"),
    "tuning-difficulty.md": ("dials", "spawns", "tradeoff", "slower", "health", "stage",
                             "versions"),
    "keeping-the-score-readable.md": ("spread", "recoil", "scoring"),
    "testing-and-iterating.md": ("testloop", "anchor", "noise", "comfortable", "freeze"),
    "where-settings-live.md": ("twotabs",),
    "sharing-to-the-workshop.md": ("upload", "loweffort"),
    "scenario-editor.md": ("smainfields", "sunpackfields", "endconditions", "timeregained",
                           "lockfov", "adapt", "feedback", "schallengefields", "multipliers",
                           "sscoringfields", "stagsfields"),
    "character-profile.md": ("hitboxes", "friction", "speedbias", "stepup",
                             "crouchbox", "movefields", "headbox", "selfradius",
                             "spawnfov", "mainfields", "boxfields",
                             "colorfields", "abilityslotfields", "spawnfields",
                             "effectfields"),
    "weapon-profile.md": ("hitradius", "piercing", "spreadshape", "recoiltiming",
                          "lockdeadzone", "wmainfields", "weffectfields",
                          "wammofields", "wgraphicsfields", "wexplosivefields",
                          "wspreadfields", "wpbsfields", "wrecoilfields",
                          "wpsrfields", "wadsfields", "walsofields",
                          "wcheatfields"),
    "bot-profile.md": ("wiring", "bmainfields", "firemodes", "bweaponfields",
                       "bdodgefields"),
    "dodge-profile.md": ("rhythm", "strafemult", "dmainfields", "profileswap", "blocked",
                         "dreactfields", "dmovefields", "playbackmode", "dplayfields"),
    "aim-profile.md": ("estimating", "mousepad", "aimcone", "aimfields"),
    "ability-profile.md": ("charges", "interrupt", "abmainfields", "abmovefields",
                           "abaifields"),
}


def main() -> None:
    for filename, names in PAGES.items():
        page = SECTION / filename
        text = page.read_text(encoding="utf-8")
        for name in names:
            # Bespoke figures live in diagrams.py; per-field sheets are generated
            # from tabs.py. A page names either the same way.
            maker = getattr(d, name, None) or getattr(sheets, name)
            svg = maker()
            pattern = re.compile(r'<svg [^>]*aria-labelledby="fig-%s-title".*?</svg>' % name, re.S)
            text, count = pattern.subn(lambda _: svg, text)
            if count != 1:
                sys.exit(f"expected one fig-{name} diagram in {filename}, found {count}")
        page.write_text(text, encoding="utf-8", newline="\n")
        print(f"diagrams written to {page.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
