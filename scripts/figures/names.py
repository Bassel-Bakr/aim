"""The published name of each figure, where it differs from the function that draws it.

A figure is drawn by a Python function, and a Python identifier cannot contain a hyphen, so a
compound name arrives run together: dmainfields, wcheatfields, lockdeadzone. The file on disk and
the marker in the page are read by people, so they get the hyphenated form and this table is where
the two meet.

Names not listed here are already one word and publish unchanged.
"""

PUBLISHED = {
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


def published(name: str) -> str:
    """The name a figure is written and cited under."""
    return PUBLISHED.get(name, name)
