"""The dodge profile's four tabs, one line per field.

Every field here is about a strafe, so most of them draw one. A kind ending "-inv" means the higher
value shows less of the effect, which is true of a chance to ignore something, a cooldown that
blocks a reaction, and a threshold that has to be cleared before anything happens.
"""
from fields import Field

MAIN: tuple[Field, ...] = (
    ("Profile Name", "What this dodge profile is called. Bot profiles attach it by this name.",
     "label", "unnamed", "named"),
    ("Target Distance Range (min)", "How close the bot is willing to get to its target before it "
     "stops closing.", "standoff", "up close", "held back"),
    ("Target Distance Range (max)", "How far the bot drifts before it closes again. The pair "
     "holds the target at a steady angular size.", "standoff", "kept near", "allowed far"),
    ("Toggle Left/Right", "Whether the bot strafes sideways at all. Unchecked, nothing on this "
     "tab's left and right timing does anything.", "strafeon", "stands still", "strafes"),
    ("Initial Strafe", "Which way the bot goes on its first strafe. Set it when you want a drill "
     "that always opens the same way.", "firstturn", "left first", "right first"),
    ("Initial Strafe On", "When that first direction is applied: only on the first spawn, or "
     "again on every respawn.", "everyspawn", "first spawn only", "every spawn"),
    ("Toggle L/R Time Min", "Shortest time the bot keeps going one way before turning. The floor "
     "of the strafe rhythm.", "strafe", "turns quickly", "runs longer"),
    ("Toggle L/R Time Max", "Longest time before turning. Close to the minimum this is a "
     "metronome; far from it the next turn cannot be read.", "evenness", "predictable",
     "unreadable"),
    ("Left Strafe Time Multiplier", "Multiplies how long the bot continues once it starts going "
     "left.", "biasleft", "short lefts", "long lefts"),
    ("Right Strafe Time Multiplier", "The same for the right. Set the two differently and the "
     "target lives on one side of its track.", "bias", "short rights", "long rights"),
    ("Strafe Swap Pause Min", "Shortest hold at a direction change. This is the instant your "
     "crosshair either stays on target or sails past.", "swappause", "no pause", "a real pause"),
    ("Strafe Swap Pause Max", "Longest hold at a direction change. A range here means you cannot "
     "time the resume.", "variance", "same every turn", "varies"),
    ("Toggle Forward/Back", "Whether the bot also moves toward and away from you, which changes "
     "target size while you track.", "depth", "holds distance", "in and out"),
    ("Toggle F/B Time Min", "Shortest run toward or away before reversing.",
     "depthrate", "quick reversal", "long approach"),
    ("Toggle F/B Time Max", "Longest run toward or away. Widen the gap and depth changes stop "
     "being learnable.", "variance", "same every time", "varies"),
    ("Profile Change Time Min", "Shortest time on this dodge profile before the bot may swap to "
     "another one attached to it.", "profileclock", "swaps early", "stays put"),
    ("Profile Change Time Max", "Longest time before a swap. A scenario with one dodge profile "
     "ignores both of these.", "profileclock", "swaps often", "rarely swaps"),
    ("Waypoint Logic", "How much attention the bot pays to a route on the map. Ignore, Seek "
     "Combat, Seek Target and Seek Waypoint.", "waypointlogic", "walks the route",
     "breaks off at you"),
    ("Waypoint Turn Rate", "How sharply the bot corners when it follows a route. Low reads as a "
     "vehicle; high reads as a right angle.", "turnrate", "wide corners", "sharp corners"),
    ("Cooldown Time", "How long before this dodge profile can be used again. Zero means no "
     "cooldown at all.", "cooldown", "no cooldown", "locked out"),
)

REACT: tuple[Field, ...] = (
    ("Target Strafe Reaction", "Whether the bot mimics your movement, opposes it, or ignores it. "
     "Mimic and Oppose both make the target answer you.", "reactmode", "opposes you",
     "mimics you"),
    ("Strafe Reaction Delay Min", "Shortest gap between your movement and the bot answering it.",
     "reactlag", "instant", "a beat late"),
    ("Strafe Reaction Delay Max", "Longest gap. A wide range is what stops a reactive target "
     "from being timed.", "variance", "same lag", "varies"),
    ("Taking Damage Toggles L/R", "Whether a hit makes the bot swap strafe direction. This is the "
     "field that punishes a landed shot with a harder next shot.", "hit", "keeps going",
     "swaps on hit"),
    ("Taking Damage Toggles F/B", "Whether a hit makes the bot reverse its approach instead.",
     "hitdepth", "holds depth", "reverses on hit"),
    ("Chance To Ignore Damage", "How often a hit provokes no reaction at all. Anything between "
     "the extremes means the same hit sometimes does nothing.", "ignorehit",
     "always reacts", "usually ignores"),
    ("Damage Reaction Delay Min", "Shortest gap between the hit and the reaction to it.",
     "hitlag", "immediate", "delayed"),
    ("Damage Reaction Delay Max", "Longest gap. Keep the pair tight if you want to compare runs.",
     "variance", "same every hit", "varies"),
    ("Damage Reaction Cooldown", "How long after one damage reaction before another can fire. It "
     "stops a burst weapon from pinballing the bot.", "cooldown", "reacts to every hit", "reacts rarely"),
    ("Damage Threshold", "How much damage has to land before a reaction triggers at all.",
     "threshold", "one hit is enough", "takes several", "bar"),
    ("Damage Reset Time", "How long accumulated damage is remembered. Past it the threshold "
     "starts over from nothing.", "decay", "forgets at once", "remembers", "bar"),
    ("Triggers Profile Change", "Whether a damage reaction throws the bot out of this dodge "
     "profile. It prefers one set to Ignore, else picks at random.", "swapout", "stays in this profile", "ejected elsewhere"),
    ("Trigger On Blocking Collision", "Whether hitting an obstacle fires a counter strafe, rather "
     "than the bot grinding along the wall.", "wall", "grinds along it", "counter strafes"),
    ("Blocked Speed Percent", "How slow the bot has to be going before the game counts it as "
     "blocked.", "wall-inv", "counts as blocked", "has to stop dead"),
    ("Blocked Reaction Time", "How long the bot presses into the obstacle before giving up on "
     "that direction. Zero reads as unnaturally sharp.", "wallpress", "turns instantly", "pushes a while"),
    ("Self Destruct", "Whether the bot kills itself when it sees a target. It is how a scenario "
     "makes a target vanish on sight instead of fighting.", "vanish", "stays and fights",
     "dies on sight"),
)

MOVE: tuple[Field, ...] = (
    ("Alternate Jump/Crouch Input", "Switches the tab between two approaches. Unchecked, jump and "
     "crouch are separate habits; checked, the bot alternates holding one then the other.",
     "altinput", "each on its own", "strictly alternating"),
    ("Jumping Frequency", "How often the bot presses and holds jump. Vertical motion is a "
     "correction most aim benchmarks leave out on purpose.", "jump", "stays down",
     "jumps often"),
    ("Jump Time Min", "Shortest hold on jump. On a flying character profile this is how far up "
     "it gets.", "jump", "a hop", "a climb"),
    ("Jump Time Max", "Longest hold on jump. A wide range makes the height of each jump "
     "unreadable.", "jumpvary", "same height", "varies"),
    ("Crouching Frequency", "What share of the time the bot holds crouch. Zero never crouches and "
     "one holds it permanently, so it is a percentage rather than a rate.",
     "crouch", "stands", "crouches"),
    ("Crouch Time Min", "Shortest hold on crouch. On a flying profile, holding crouch flies "
     "down.", "crouch", "a dip", "a long duck"),
    ("Crouch Time Max", "Longest hold on crouch. Widen the pair and the target's height stops "
     "being predictable.", "crouchvary", "same depth", "varies"),
)

PLAYBACK: tuple[Field, ...] = (
    ("Playback Profile Name", "Which recording this profile replays. Captured in the editor "
     "and played back instead of the bot's own dodging.", "record", "no recording", "a recording"),
    ("Override Movement", "The recording drives where the bot goes, rather than the strafe "
     "settings on the Main tab.", "record", "own strafe", "recorded path"),
    ("Override Rotation", "The recording drives where the bot looks.",
     "record", "own aim", "recorded aim"),
    ("Override Weapon Input", "The recording drives the trigger.",
     "record", "own trigger", "recorded trigger"),
    ("Override Ability Input", "The recording drives ability presses.",
     "record", "own abilities", "recorded abilities"),
    ("Loop Upon Completion", "Whether the recording restarts when it reaches the end, or "
     "the bot falls back to its own logic.", "record", "plays once", "loops"),
    ("Playback Mode", "Input Only replays keystrokes, so knockback pushes the bot off "
     "course. Absolute Position matches the recorded location and cannot be pushed. Moveable "
     "Absolute Position drops to Input Only once something hits it.",
     "record", "pushed off course", "path survives"),
)
