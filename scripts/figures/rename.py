"""One-shot: give every figure a hyphenated name.

The figures were named after the Python functions that draw them, so a compound name arrived as one
run-together word: dmainfields, wcheatfields, lockdeadzone. A file on disk has no reason to inherit
that, and a marker in a page is read by people.

This renames the files in docs/figures, rewrites the markers in the pages, and records the mapping
in scripts/figures/names.py so each generator can publish under the readable name while its drawing
function keeps the identifier Python allows.

Run once from the repository root:

    python scripts/figures/rename.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
FIGURES = DOCS / "figures"

# Only the names that are more than one word. Everything else already reads as a word and maps to
# itself.
RENAME = {
    "abaifields": "ability-ai-use-fields",
    "abilityslotfields": "ability-slot-fields",
    "abmainfields": "ability-main-fields",
    "abmovefields": "ability-movement-fields",
    "aimcone": "aim-cone",
    "aimfields": "aim-profile-fields",
    "bdodgefields": "bot-dodge-fields",
    "bmainfields": "bot-main-fields",
    "boxfields": "character-box-fields",
    "bweaponfields": "bot-weapon-fields",
    "colorfields": "character-color-fields",
    "crouchbox": "crouch-box",
    "dmainfields": "dodge-main-fields",
    "dmovefields": "dodge-move-fields",
    "dplayfields": "dodge-playback-fields",
    "dreactfields": "dodge-react-fields",
    "effectfields": "character-effect-fields",
    "endconditions": "end-conditions",
    "firemodes": "fire-modes",
    "headbox": "head-box",
    "hitradius": "hit-radius",
    "lockdeadzone": "lock-deadzone",
    "lockfov": "lock-fov",
    "loweffort": "low-effort",
    "mainfields": "character-main-fields",
    "movefields": "character-move-fields",
    "playbackmode": "playback-mode",
    "profileswap": "profile-swap",
    "recoiltiming": "recoil-timing",
    "schallengefields": "scenario-challenge-fields",
    "selfradius": "self-spawn-radius",
    "smainfields": "scenario-main-fields",
    "spawnfields": "character-spawn-fields",
    "spawnfov": "spawn-fov",
    "speedbias": "speed-bias",
    "spreadshape": "spread-shape",
    "sscoringfields": "scenario-scoring-fields",
    "stagsfields": "scenario-tags-fields",
    "stepup": "step-up",
    "strafemult": "strafe-multiplier",
    "sunpackfields": "scenario-unpack-fields",
    "testloop": "test-loop",
    "timeregained": "time-regained",
    "twotabs": "two-tabs",
    "wadsfields": "weapon-ads-fields",
    "walsofields": "weapon-also-shoot-fields",
    "wammofields": "weapon-ammo-fields",
    "wcheatfields": "weapon-cheats-fields",
    "weffectfields": "weapon-effect-fields",
    "wexplosivefields": "weapon-explosive-fields",
    "wgraphicsfields": "weapon-graphics-fields",
    "wmainfields": "weapon-main-fields",
    "wpbsfields": "weapon-per-bullet-spread-fields",
    "wpsrfields": "weapon-per-shot-recoil-fields",
    "wrecoilfields": "weapon-recoil-fields",
    "wspreadfields": "weapon-spread-fields",
}


def main() -> None:
    on_disk = {p.stem for p in FIGURES.glob("*.svg")}
    unknown = sorted(set(RENAME) - on_disk)
    if unknown:
        raise SystemExit("no such figure, check the spelling: " + ", ".join(unknown))
    for old, new in RENAME.items():
        (FIGURES / f"{old}.svg").rename(FIGURES / f"{new}.svg")
    for page in sorted(DOCS.rglob("*.md")):
        text = page.read_text(encoding="utf-8")
        if "aim:figure" not in text:
            continue
        rewritten = re.sub(
            r"<!--\s*aim:figure\s+([A-Za-z0-9_-]+)\s*-->",
            lambda m: f"<!-- aim:figure {RENAME.get(m.group(1), m.group(1))} -->", text)
        if rewritten != text:
            page.write_text(rewritten, encoding="utf-8", newline="\n")
    print(f"{len(RENAME)} figures renamed; "
          f"{len(on_disk) - len(RENAME)} were already single words")


if __name__ == "__main__":
    main()
