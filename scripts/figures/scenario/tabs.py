"""Every field of every editor tab, one line each.

Each entry is (name, what the editor says it does, demonstration kind, low state, high state).
Where the game's own tooltip explains a field, the note is that explanation restated; where it does
not, the note says only what the field is, and no behavior is invented for it.

fields.py turns each line into a strip with an animated low and high state, and build.py splices
the result into the page. Adding a field is adding a line here.
"""
from fields import Field

# --- character profile: Move ------------------------------------------------
MOVE: tuple[Field, ...] = (
    ("Flies", "The character moves in three dimensions rather than along the ground.",
     "fly", "grounded", "flies"),
    ("Has Jetpack", "Adds a jetpack, and a tab of its own for the jetpack's variables.",
     "fly", "off", "on"),
    ("Run Speed", "The character's ground speed.", "topspeed", "it covers little ground", "it covers a lot"),
    ("Forward Speed Bias", "At 1 a diagonal input moves you at 45 degrees to where you look.",
     "diagbias", "pulled toward forward", "a true diagonal"),
    ("Strafe Speed Multiplier", "Speed multiplier when strafing and not moving forward.",
     "dirmult", "strafing is a crawl", "nearly run speed"),
    ("Back Speed Multiplier", "Speed multiplier when moving backwards.",
     "dirmultback", "backing up is a crawl", "nearly run speed"),
    ("Walking Acceleration", "How fast the character gains speed on the ground.",
     "rampup", "a slow build", "up to speed at once"),
    ("Crouching Acceleration", "How fast the character gains speed when crouched.",
     "rampcrouch", "a slow build", "up to speed at once"),
    ("Scaling Friction", "Affects movement control; higher values allow faster changes in "
     "direction. UE4 calls this Ground Friction.", "turngrip", "it drifts past turns", "it turns on the spot"),
    ("Let Off Friction", "Braking drag, applied whenever acceleration is zero or the character "
     "exceeds max speed.", "letoff", "a long slide", "it stops at once"),
    ("Flat Friction", "A constant friction term applied alongside the scaling one.",
     "flatdrag", "a long slide", "it stops at once"),
    ("Step Up Height", "The height counted as a step. At 0 the character jumps at every step; "
     "huge, it warps on top of obstacles.", "jump-inv", "jumps at steps", "walks up them"),
    ("Fly On Jump And Crouch", "Checked, jumping while crouched sends the character airborne; "
     "unchecked, jump cancels the crouch but stays grounded.", "jump", "stays down", "lifts off"),
    ("Jump Velocity", "How hard the character leaves the ground, drawn between a minimum and a "
     "maximum.", "jump", "low hop", "high jump"),
    ("Aerial Friction", "Pulls horizontal speed back toward run speed in the air. A little goes a "
     "long way; even 0.3 is strong.", "airdrag", "it keeps its speed", "speed bleeds off fast"),
    ("Gravity Scale", "Multiplies gravity for this character.", "fall", "floaty", "heavy"),
    ("Terminal Velocity", "The fastest the character may fall.", "fall", "capped low",
     "capped high"),
    ("Air Control Factor", "How much the movement keys accelerate the character in the air. "
     "1 is the same as ground, 0 is none.", "air", "no steering", "full steering"),
    ("Allow Buffered Jumps", "A jump pressed just before landing is held and fires on touchdown.",
     "jump", "dropped", "buffered"),
    ("Can Pogo Jump", "Hold the jump key down to keep jumping, Minecraft style.",
     "jump", "one jump", "keeps bouncing"),
    ("Can Jump From Crouch", "Whether a crouched character may jump at all.",
     "jump", "blocked", "allowed"),
    ("Aerial Jump Count", "How many extra jumps are available before landing.",
     "jump", "none", "several"),
    ("Can Crouch", "Whether the character may crouch. Crouching does not work at all if the "
     "character is a sphere shape.", "crouch", "cannot", "can"),
    ("Crouch Speed", "Movement speed while crouched.", "crouchpace", "a crawl", "nearly full pace"),
    ("Crouch Height Multiplier", "Multiplier of the bounding box height when crouched.",
     "crouch-inv", "ducks low", "barely ducks"),
    ("Crouch Animation Rate", "How quickly the duck happens: 1 is 0.3 seconds, 2 is 0.15.",
     "crouchrate", "slow duck", "fast duck"),
    ("Can Crouch In Air", "Whether the character may crouch while airborne.",
     "crouch", "grounded only", "in the air too"),
    ("Bounce Off Walls", "The character rebounds from a wall instead of stopping against it.",
     "bounce", "stops dead", "rebounds"),
    ("Landing Speed Penalty Time", "How long the character is slowed after landing.",
     "land", "no penalty", "slowed on landing"),
    ("Enable Quake/Source Movement", "Switches to the movement model those engines use, "
     "bunny hopping included.", "aircrouch", "standard", "Quake or Source"),
)
