"""Regenerates the figures cited by the Making Scenarios pages.

    python scripts/figures/scenario/build.py

Each figure is written to docs/figures, where the marker line on its page picks it up at build
time. Edit the drawing code in diagrams.py, or the field spec in the tabs modules; the page keeps
the caption under each figure.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import diagrams as d  # noqa: E402
import sheets  # noqa: E402
from publish import publish  # noqa: E402

# Which diagrams belong to which page of the section, by the id each <svg> is matched on.
PAGES: dict[str, tuple[str, ...]] = {
    "kovaaks/index.md": ("copying",),
    "kovaaks/making-a-scenario.md": ("profiles", "spawn", "decisions"),
    "designing-around-a-weakness.md": ("weakest", "deliberate", "isolate", "shortcut"),
    "designing-target-motion.md": ("waypoints", "weights", "reactive", "travel"),
    "tuning-difficulty.md": ("dials", "spawns", "tradeoff", "slower", "health", "stage",
                             "versions"),
    "keeping-the-score-readable.md": ("spread", "recoil", "scoring"),
    "testing-and-iterating.md": ("testloop", "anchor", "noise", "comfortable", "freeze"),
    "kovaaks/where-settings-live.md": ("twotabs",),
    "kovaaks/sharing-to-the-workshop.md": ("upload", "loweffort"),
    "kovaaks/edit-scenario.md": ("smainfields", "sunpackfields", "endconditions", "timeregained",
                           "lockfov", "adapt", "feedback", "schallengefields", "multipliers",
                           "sscoringfields", "stagsfields"),
    "kovaaks/character-profile.md": ("hitboxes", "friction", "speedbias", "stepup",
                             "crouchbox", "movefields", "headbox", "selfradius",
                             "spawnfov", "mainfields", "boxfields",
                             "colorfields", "abilityslotfields", "spawnfields",
                             "effectfields"),
    "kovaaks/weapon-profile.md": ("hitradius", "piercing", "spreadshape", "recoiltiming",
                          "lockdeadzone", "wmainfields", "weffectfields",
                          "wammofields", "wgraphicsfields", "wexplosivefields",
                          "wspreadfields", "wpbsfields", "wrecoilfields",
                          "wpsrfields", "wadsfields", "walsofields",
                          "wcheatfields"),
    "kovaaks/bot-profile.md": ("wiring", "bmainfields", "firemodes", "bweaponfields",
                       "bdodgefields"),
    "kovaaks/dodge-profile.md": ("rhythm", "strafemult", "dmainfields", "profileswap", "blocked",
                         "dreactfields", "dmovefields", "playbackmode", "dplayfields"),
    "kovaaks/aim-profile.md": ("estimating", "mousepad", "aimcone", "aimfields"),
    "kovaaks/ability-profile.md": ("charges", "interrupt", "abmainfields", "abmovefields",
                           "abaifields"),
}


def main() -> None:
    figures = {}
    for names in PAGES.values():
        for name in names:
            # Bespoke figures live in diagrams.py; per-field sheets are generated
            # from the tabs modules. A page names either the same way.
            maker = getattr(d, name, None) or getattr(sheets, name)
            figures[name] = maker()
    publish(figures)


if __name__ == "__main__":
    main()
