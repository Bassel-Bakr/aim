"""One figure per tab, built from the field lists in the tabs_* modules.

build.py resolves a figure name against diagrams.py first and this module second, so a bespoke
figure and a generated field sheet are placed on a page the same way.
"""
import fields
import tabs
import tabs_char
import tabs_aim
import tabs_bot
import tabs_dodge
import tabs_scenario
import tabs_weapon


def movefields() -> str:
    return fields.sheet("movefields", "Move tab, every field",
                        "What each one varies, and which way it runs.", tabs.MOVE)


def mainfields() -> str:
    return fields.sheet("mainfields", "Main tab, every field",
                        "Identity, health, and the respawn timing.", tabs_char.MAIN)


def boxfields() -> str:
    return fields.sheet("boxfields", "Boxes tab, every field",
                        "Both hitboxes, and the head the other tabs depend on.", tabs_char.BOXES)


def colorfields() -> str:
    return fields.sheet("colorfields", "Colors tab, every field",
                        "Four colors, every one of which a reader may override.",
                        tabs_char.COLORS)


def abilityslotfields() -> str:
    return fields.sheet("abilityslotfields", "Abilities tab, every field",
                        "Four slots and the two timers that gate them.", tabs_char.ABILITIES)


def spawnfields() -> str:
    return fields.sheet("spawnfields", "Spawn tab, every field",
                        "Where targets appear, and what plays when they do.", tabs_char.SPAWN)


def effectfields() -> str:
    return fields.sheet("effectfields", "Effects tab, every field",
                        "Knockback, invincibility, regen, and the build-time switches.",
                        tabs_char.EFFECTS)


def wmainfields() -> str:
    return fields.sheet("wmainfields", "Main tab, every field",
                        "Type, category, damage and fire rate.", tabs_weapon.MAIN)


def weffectfields() -> str:
    return fields.sheet("weffectfields", "Effects tab, every field",
                        "What a hit does beyond damage.", tabs_weapon.EFFECTS)


def wammofields() -> str:
    return fields.sheet("wammofields", "Ammo tab, every field",
                        "Magazine, reloads and what refills them.", tabs_weapon.AMMO)


def wgraphicsfields() -> str:
    return fields.sheet("wgraphicsfields", "Graphics tab, every field",
                        "Cosmetic, except for the ones that tell you where a shot went.", tabs_weapon.GRAPHICS)


def wexplosivefields() -> str:
    return fields.sheet("wexplosivefields", "Explosives tab, every field",
                        "Blast radius, damage and what stops it.", tabs_weapon.EXPLOSIVES)


def wspreadfields() -> str:
    return fields.sheet("wspreadfields", "Spread tab, every field",
                        "The random cone, and how fast it opens and closes.", tabs_weapon.SPREAD)


def wpbsfields() -> str:
    return fields.sheet("wpbsfields", "Per bullet spread, every field",
                        "A fixed pattern instead of a random cone.", tabs_weapon.PBS)


def wrecoilfields() -> str:
    return fields.sheet("wrecoilfields", "Recoil tab, every field",
                        "The climb, and the timing rule the editor states.", tabs_weapon.RECOIL)


def wpsrfields() -> str:
    return fields.sheet("wpsrfields", "Per shot recoil, every field",
                        "A learnable pattern, with its own timing trap.", tabs_weapon.PSR)


def wadsfields() -> str:
    return fields.sheet("wadsfields", "Aim down sights, every field",
                        "The zoom, and what it does to your sensitivity.", tabs_weapon.ADS)


def walsofields() -> str:
    return fields.sheet("walsofields", "Also Shoot, every field",
                        "Firing other weapon profiles alongside this one.", tabs_weapon.ALSO_SHOOT)


def wcheatfields() -> str:
    return fields.sheet("wcheatfields", "Cheats tab, every field",
                        "The lock, its limits, and the trigger bot.", tabs_weapon.CHEATS)


def dmainfields() -> str:
    return fields.sheet("dmainfields", "Dodge Main tab, every field",
                        "The strafe: how far, how long, and how evenly.", tabs_dodge.MAIN)


def dreactfields() -> str:
    return fields.sheet("dreactfields", "React tab, every field",
                        "What the bot answers, and how reliably.", tabs_dodge.REACT)


def dmovefields() -> str:
    return fields.sheet("dmovefields", "Dodge Move tab, every field",
                        "Jump and crouch, under one switch.", tabs_dodge.MOVE)


def dplayfields() -> str:
    return fields.sheet("dplayfields", "Dodge Playback tab, every field",
                        "A recording instead of a strafe.", tabs_dodge.PLAYBACK)


def bmainfields() -> str:
    return fields.sheet("bmainfields", "Bot Main tab, every field",
                        "What this bot points at, and what it is worth.", tabs_bot.MAIN)


def bweaponfields() -> str:
    return fields.sheet("bweaponfields", "Bot Weapon tab, every field",
                        "Whether it aims, whether it fires, and with what.", tabs_bot.WEAPON)


def bdodgefields() -> str:
    return fields.sheet("bdodgefields", "Bot Dodge tab, every field",
                        "The dodges attached, and at what weight.", tabs_bot.DODGE)


def smainfields() -> str:
    return fields.sheet("smainfields", "Scenario Main tab, every field",
                        "The inventory: what may appear, not what does.", tabs_scenario.MAIN)


def sunpackfields() -> str:
    return fields.sheet("sunpackfields", "Unpack tab, every field",
                        "Getting the profiles back out as files.", tabs_scenario.UNPACK)


def schallengefields() -> str:
    return fields.sheet("schallengefields", "Challenge tab, every field",
                        "The rules of a run, and what you are shown during it.",
                        tabs_scenario.CHALLENGE)


def sscoringfields() -> str:
    return fields.sheet("sscoringfields", "Scoring tab, every field",
                        "What a run is worth, which is what you practice.",
                        tabs_scenario.SCORING)


def stagsfields() -> str:
    return fields.sheet("stagsfields", "Tags tab, every field",
                        "Whether anyone ever finds the scenario.", tabs_scenario.TAGS)


def aimfields() -> str:
    return fields.sheet("aimfields", "AI Aim Profile, every field",
                        "Where the bot thinks you are, and how far off it lands.",
                        tabs_aim.AIM)


def abmainfields() -> str:
    return fields.sheet("abmainfields", "Ability Main tab, every field",
                        "Charges, and what releases them.", tabs_aim.ABILITY_MAIN)


def abaifields() -> str:
    return fields.sheet("abaifields", "AI Use tab, every field",
                        "When a bot reaches for it, rather than what it does.",
                        tabs_aim.ABILITY_AI)


def abmovefields() -> str:
    return fields.sheet("abmovefields", "Movement ability, the two extra tabs",
                        "A hurtbox, and what you may still press.",
                        tabs_aim.ABILITY_MOVEMENT)
