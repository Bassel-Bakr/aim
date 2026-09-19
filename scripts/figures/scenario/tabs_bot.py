"""The bot profile's three tabs, one line per field.

A bot profile is wiring, so several of its fields point at another profile rather than setting a
number. Those draw the thing they point at. A kind ending "-inv" means the higher value shows less
of the effect.
"""
from fields import Field

MAIN: tuple[Field, ...] = (
    ("Profile Name", "What this bot profile is called. The scenario's bot list attaches it by "
     "this name.", "label", "unnamed", "named"),
    ("Character Profile", "Which character this bot wears. Size, health, spawn behavior and the "
     "weapons it can hold all come from there, not from here.",
     "slot", "nothing chosen", "a character"),
    ("Spawn Group", "Which group of spawn points on the map this bot starts from. It is how "
     "different bots begin in different places.", "slot", "anywhere", "one group"),
    ("Bot X-Ray", "Draws the bot through walls. It makes a target readable in a scenario that has "
     "cover in it.", "xray", "hidden by cover", "seen through it"),
    ("Ability Use Timer", "How long the bot waits between chances to use an ability.",
     "chancetick", "chance after chance", "long gaps between"),
    ("Ability Usage Frequency", "How likely the bot is to use an ability when it gets a chance.",
     "usechance", "it rarely takes one", "it takes most"),
    ("Ability Usage Min", "Shortest interval before the bot re-evaluates whether it may use "
     "abilities at all.", "permitcheck", "it rethinks often", "it rarely rethinks"),
    ("Ability Usage Max", "Longest interval between those checks. A wide pair makes ability use "
     "impossible to anticipate.", "variance", "steady", "unreadable"),
    ("Laser Pointer", "Draws a beam from the bot showing where it is aiming. It turns an "
     "invisible threat into a readable one.", "pointer", "nothing shown", "a visible beam"),
    ("Use Minimum Respawn Time", "Whether the bot obeys the minimum respawn delay from its "
     "character profile, or comes back as soon as it can.",
     "respawnwait", "comes back at once", "waits the minimum", "box"),
    ("Disable Scoring", "Stops hits on this bot from counting. It is how you put something in a "
     "scene that a careless click should not reward.", "noscore", "the hit scores", "scores nothing"),
    ("Untargetable", "Stops other bots from targeting this one. It matters only in scenarios "
     "where bots fight each other.", "notarget", "a valid target", "ignored"),
    ("No Dodging/Movement", "Removes all dodging and movement logic from the bot. It is a "
     "performance switch, for scenarios that want a lot of simple bots.",
     "strafeon-inv", "moves", "stands still"),
)

WEAPON: tuple[Field, ...] = (
    ("No Aiming/Shooting", "Strips the aiming logic out entirely. The bot neither tracks you nor "
     "fires, which is what most pure aim drills want.", "botaim", "tracks you", "ignores you"),
    ("Fire Weapons", "Unchecked, the bot still aims at its target but fires nothing. A target "
     "that watches you reads very differently from one that ignores you.",
     "botfire", "holds fire", "shoots back"),
    ("Weapon Switch Timer", "How long the bot keeps a weapon before swapping to another one its "
     "character profile carries.", "weaponhold", "it swaps constantly", "it keeps one"),
    ("Slot Aim Profile", "Which AI aim profile the bot uses for this weapon slot. It decides how "
     "accurate and how fast the bot is.", "slot", "nothing chosen", "an aim profile"),
    ("Slot Frequency", "How often this slot is chosen when the bot swaps. The column weights the "
     "slots against each other.", "weight", "one slot, mostly", "a coin flip"),
)

DODGE: tuple[Field, ...] = (
    ("Dodge Profile", "Which dodge profile this bot may use. This is where all of a target's "
     "motion comes from.", "slot", "nothing chosen", "a dodge profile"),
    ("Dodge Weighting", "How often this dodge is picked against the others attached here. "
     "Weighted evenly, which drill you get is luck.", "weight", "one dodge, mostly",
     "a coin flip"),
)
