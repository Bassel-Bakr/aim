"""The aim profile's one tab and the ability profile's tabs, one line per field.

An aim profile field is about a second crosshair: where the bot thinks you are, how fast it gets
there, and how far off it lands. An ability field is about charges and the conditions that release
them. A kind ending "-inv" means the higher value shows less of the effect.
"""
from fields import Field

AIM: tuple[Field, ...] = (
    ("Profile Name", "What this aim profile is called. Bot profiles attach it per weapon slot.",
     "label", "unnamed", "named"),
    ("Aiming Style", "Which aiming model the bot runs. It sets the shape of everything below.",
     "slot", "unset", "a style"),
    ("Reaction Time Min", "Shortest gap between the bot's estimates of where you are. It is a "
     "sampling rate rather than a delay: estimate rarely and it aims where you were.",
     "sampletarget", "the guess keeps up", "it aims at an old guess"),
    ("Reaction Time Max", "Longest gap between estimates. A wide pair makes the bot's lag "
     "different every time you fight it.", "variance", "the same lag", "varies"),
    ("Self Movement Fix Time Min", "Shortest gap between the bot's estimates of its own position. "
     "Long, and it compensates for its own movement against a stale reading.",
     "sampleself", "it knows where it is", "a stale idea of itself"),
    ("Self Movement Fix Time Max", "Longest gap between those readings.",
     "variance", "the same lag", "varies"),
    ("Flick FOV", "How far off-center a target can be and still get a flick rather than a track.",
     "flickfov", "you are outside it", "it flicks to you"),
    ("Flick Speed", "How fast the bot snaps to the estimated location, measured relative to its "
     "reaction time.", "flickspeed", "it is still arriving", "it is already there"),
    ("Flick Error", "How far a flick may land from where it was aimed. Set to zero this is an "
     "aimbot, which is useful for checking a scenario's geometry and nothing else.",
     "flickerror", "near perfect", "wide misses"),
    ("Track Speed", "How fast the bot's crosshair follows a target it is already on.",
     "trackspeed", "it trails behind", "glued to it"),
    ("Track Error", "Random error added to tracking, from zero up to this, multiplied by the "
     "mousepad penalty and then clamped at Max Aiming Error.",
     "trackerror", "it stays on you", "it wanders off you"),
    ("Max Aiming Error", "The ceiling on error after every penalty is applied. However hard the "
     "bot is turning, it never misses by more than this.",
     "errorceiling", "clamped tight", "a loose ceiling"),
    ("Max Turn On Mousepad", "How many degrees from the center of the bot's mousepad before an "
     "aiming penalty starts. It is the field that makes a bot feel like a player running out of "
     "desk.", "desklimit", "it runs out early", "a lot of desk"),
    ("Mouse Re-center Time Min", "Shortest time the bot takes to lift and reset to the middle of "
     "its pad.", "recenter", "back in the middle", "a slow reset"),
    ("Mouse Re-center Time Max", "Longest reset. The pair decides how long the bot spends at a "
     "disadvantage after a hard turn.", "variance", "the same every time", "varies"),
    ("Optimal Aim FOV", "The cone the bot aims well inside. Outside it, the outer penalty takes "
     "over.", "optimalcone", "outside, it aims worse", "you are in its best cone"),
    ("Outer Aim Penalty Multiplier", "How much worse the bot aims outside that cone. It is the "
     "setting that makes a scenario about angles rather than about reflexes.",
     "outerpenalty", "barely a penalty", "the penalty bites"),
    ("Shoot FOV", "How close the bot has to be aiming before it fires at all. Narrow, and it "
     "holds fire while it corrects.", "shootfov", "it holds fire", "it fires from here"),
    ("Vertical Aim Offset", "Where on the target the bot aims. High puts it on the head box, low "
     "puts it on the body.", "aimoffset", "it aims low", "it aims high"),
    ("Tolerable Spread", "How wide the bot's own spread may be before it will still fire. "
     "Tolerant, it shoots through a bloomed crosshair rather than waiting.",
     "spreadtol", "it waits for a tight one", "it fires anyway"),
    ("Distance Spread Factor", "How much distance loosens that tolerance. One means distance "
     "plays no part at all.", "distancespread", "distance plays no part", "distance loosens it"),
)

ABILITY_MAIN: tuple[Field, ...] = (
    ("Profile Name", "What this ability is called. Character profiles hold up to four by name.",
     "label", "unnamed", "named"),
    ("Max Charges", "The ceiling on stored uses. It decides how many times a run can be "
     "interrupted by something that is not aiming.", "chargebar", "two", "four"),
    ("Charges On Spawn", "How many are ready when the run starts, which is not always the "
     "maximum.", "chargespawn", "one ready", "all ready"),
    ("Charge Timer", "How long one charge takes to come back.",
     "chargerefill", "a long wait", "it comes back fast"),
    ("Charges Refunded On Kill", "Charges handed back for a kill. It ties ability uptime to how "
     "well the run is going.", "refund", "a kill refunds nothing", "the kill refunds one"),
    ("Delay Between Uses", "The gap enforced between two uses, separate from the charge timer.",
     "usegap", "back to back", "spaced out"),
    ("Fully Auto", "Whether the ability can be held down to keep using it rather than pressed per "
     "use.", "holduse", "one press, one use", "one hold, many uses"),
    ("Weapon To Shoot", "Which weapon profile the ability fires, if it fires one.",
     "slot", "nothing chosen", "a weapon"),
    ("Block Attack Timer", "How long after using the ability before attacking is allowed again.",
     "blockattack", "a short block", "a long one"),
    ("Blocked When Attacking", "Whether attacking blocks the ability, rather than the other way "
     "round.", "blockwhenattack", "usable either way", "blocked while attacking"),
    ("Ammo Per Shot", "Ammo the ability takes from the selected weapon each time it fires.",
     "ammobite", "one per use", "several", "round"),
)

ABILITY_AI: tuple[Field, ...] = (
    ("Uses On Ground", "Whether bots use the ability while standing on something.",
     "useground", "never on the ground", "it uses it on the ground"),
    ("Uses In Air", "Whether bots use it while airborne. A movement ability used off the ground "
     "reads very differently from one used on it.",
     "useair", "never off the ground", "it uses it off the ground"),
    ("Uses In Combat", "Whether bots use it while they have a target.",
     "usecombat", "never with a target", "it uses it with a target"),
    ("Uses Out Of Combat", "Whether bots use it with nobody to fight, which is how a bot crosses "
     "a map rather than waits on it.",
     "useoutcombat", "never with nobody around", "it uses it with nobody around"),
    ("Reuse Timer", "How long a bot waits before considering the ability again.",
     "chancetick", "chance after chance", "long gaps between"),
    ("Self Health Range (min)", "The lowest health a bot may have and still use it.",
     "selfhealth", "only when it is hurt", "at almost any health"),
    ("Self Health Range (max)", "The highest. Narrow the pair and the bot only reaches for it "
     "when hurt, which reads as a player rather than a script.",
     "selfhealth", "only when it is hurt", "at almost any health"),
    ("Target Health Range (min)", "The lowest health you may have for the bot to use it on you.",
     "targethealth", "only when you are hurt", "at almost any health"),
    ("Target Health Range (max)", "The highest. Set narrow, the bot saves it for a finish.",
     "targethealth", "only when you are hurt", "at almost any health"),
    ("Target Distance Range (min)", "How close you have to be before the bot will use it.",
     "standoff", "it closes right in", "it keeps its distance"),
    ("Target Distance Range (max)", "How far away it will still use it.",
     "standoff", "kept near", "allowed far"),
    ("Maximum FoV To Target", "Using the ability in combat, the bot has to be aiming within this "
     "many degrees of you.", "aimgate", "not aimed close enough", "the ability is allowed"),
    ("Taking Damage Activates", "Whether being hit makes the bot use the ability. It is what "
     "turns a landed shot into a harder next shot.",
     "hit", "the hit changes nothing", "the hit triggers it"),
    ("Chance To Ignore Damage", "How often a hit produces no reaction. Anything between the "
     "extremes means the same hit sometimes does nothing.",
     "ignorehit", "always reacts", "usually ignores"),
    ("Reaction Delay Min", "Shortest gap between the hit and the ability firing. At zero the bot "
     "answers instantly, which no human does.", "abilityanswer", "it answers at once", "it answers late"),
    ("Reaction Delay Max", "Longest gap. Give it a range and the fight becomes winnable.",
     "variance", "the same lag", "varies"),
    ("Damage Reaction Cooldown", "How long before another damage reaction can fire.",
     "cooldown", "reacts to every hit", "reacts rarely"),
    ("Damage Threshold", "How much damage has to land before the reaction triggers at all.",
     "threshold", "one hit is enough", "takes several", "bar"),
    ("Damage Reset Time", "How long accumulated damage is remembered before the threshold starts "
     "over.", "decay", "forgets at once", "remembers", "bar"),
)

ABILITY_MOVEMENT: tuple[Field, ...] = (
    ("H-Box", "A movement ability's own hurtbox: a volume that damages or knocks back whatever it "
     "passes through. Only a movement ability has this tab.",
     "hurtbox", "it barely touches", "a wide hurtbox"),
    ("Input", "Which of the player's inputs still work while the movement ability is running. "
     "Also a movement-only tab.",
     "inputlock", "everything still works", "most inputs locked out"),
)
