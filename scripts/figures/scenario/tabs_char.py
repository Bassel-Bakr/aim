"""The character profile's other seven tabs, one line per field.

Split from tabs.py so no single file has to hold every editor. Same shape: name, what the editor
says it does, the demonstration kind, and the two state labels. A kind ending "-inv" means the
higher value shows less of the effect, which is true of every field where raising a number removes
a behavior rather than adding one.
"""
from fields import Field

MAIN: tuple[Field, ...] = (
    ("Profile Name", "What this character profile is called. Bots and players both wear one.",
     "label", "unnamed", "named"),
    ("Health", "How much damage the character takes before dying. One hit makes a scenario about "
     "acquisition; more makes it about staying on target.", "hitpoints", "one shot and it drops", "several shots"),
    ("Min Respawn Delay", "Delay until respawn is possible. Bots always use this; players may "
     "press fire or jump during it.", "respawnmin", "back at once", "held down a while"),
    ("Max Respawn Delay", "Delay after death until the player is forced to respawn.",
     "respawnmax", "forced up at once", "you may lie there"),
    ("Respawn Anim Duration", "How long the respawn animation runs before control returns.",
     "respawnanim", "control returns at once", "a long animation"),
    ("Headshot Only", "If checked, body shots do no damage. It uses the head box from the Boxes "
     "tab.", "head", "body counts", "head only"),
    ("Camera Height Offset", "Vertical shift of the eyes. With a head box 0 is the middle of the "
     "head; without one it is the middle of the body.", "eyeline", "it sees from the chest", "it sees from the head"),
    ("Hide Third Person Weapon", "Hides the weapon on the third-person model.",
     "view", "shown", "hidden"),
    ("Third Person Camera", "Plays the character from behind rather than through its eyes.",
     "view", "first person", "third person"),
)

BOXES: tuple[Field, ...] = (
    ("Character Model", "Which mesh the character is drawn with.", "view", "none", "a model"),
    ("Bounding Box Type", "The shape of the main hitbox, which collides with the world and takes "
     "both hitscan and projectile fire.", "view", "cylinder", "another shape"),
    ("Has Head", "Adds a separate head box. Headshot Only and the camera offset both depend on "
     "whether one exists.", "head", "no head", "has head"),
    ("Body Height", "How tall the main bounding box is.", "boxheight", "a short box", "a tall one"),
    ("Body Radius", "How wide the main bounding box is. The cleanest difficulty dial in the "
     "editor.", "boxwidth", "a narrow box", "a wide one"),
    ("Projectile Box Type", "The shape of the second hitbox, which passes through the world and "
     "takes projectile fire only.", "head", "cylinder", "another shape"),
    ("Hide Bounding Box", "Draws the projectile box or leaves it invisible.",
     "head", "visible", "hidden"),
    ("Projectile Has Head", "Whether the projectile box carries a head of its own.",
     "head", "no head", "has head"),
    ("Projectile Body Height", "How tall the projectile hitbox is.", "projheight", "a short second box", "a tall one"),
    ("Projectile Body Radius", "How wide the projectile hitbox is. This is how a projectile "
     "weapon is given a more forgiving target than a hitscan one.", "projwidth", "a narrow second box", "a wide one"),
)

COLORS: tuple[Field, ...] = (
    ("Enemy Head Color", "Head color for enemies. The convention is head for the character and "
     "body for the team.", "head", "default", "set"),
    ("Enemy Body Color", "Body color for enemies.", "swatch", "default", "set"),
    ("Team Head Color", "Head color for teammates.", "swatch", "default", "set"),
    ("Team Body Color", "Body color for teammates. Readers can override all four in their own "
     "Visuals settings.", "swatch", "default", "set"),
)

ABILITIES: tuple[Field, ...] = (
    ("Global Cooldown", "One cooldown shared across every ability this character holds.",
     "sharedcool", "free again at once", "all four wait together"),
    ("Block Ability for Duration on Challenge Start", "Abilities are unavailable for this long "
     "once the challenge begins.", "startblock", "usable at once", "shut for a while"),
    ("Ability 1", "The first of four ability slots.", "swatch", "empty", "filled"),
    ("Ability 2", "The second ability slot.", "slot", "empty", "filled"),
    ("Ability 3", "The third ability slot.", "slot", "empty", "filled"),
    ("Ability 4", "The fourth ability slot.", "slot", "empty", "filled"),
)

SPAWN: tuple[Field, ...] = (
    ("Spawn Offset Minimum", "The near corner of the box a character may appear in, as X, Y and "
     "Z.", "spawnnear", "it can appear on top of you", "it is pushed out"),
    ("Spawn Offset Maximum", "The far corner of that box. Widening it turns a holding drill into "
     "a repositioning one.", "spawnfar", "a tight spawn area", "it can appear anywhere"),
    ("Blocked Self Spawn Radius", "Keeps bots from spawning too near one another, so one flick "
     "cannot cover two targets.", "spawnapart", "one flick covers both", "two separate flicks"),
    ("Block Other Spawn FOV", "Blocks spawns you are already looking at. The editor recommends "
     "15 to 30 degrees.", "spawnangle", "only dead ahead", "a wide wedge"),
    ("Invert Block Other Spawn FOV Logic", "Flips the rule, so spawns prefer to fall inside your "
     "view rather than outside it.", "slot", "kept out", "kept in"),
    ("Block Other Spawn Distance", "Which spawns the rule considers. Left at 0 the field of view "
     "is never checked at all.", "spawnreach", "the rule barely reaches", "it reaches far out"),
    ("Playback Profile Name", "A recording of inputs, captured in the editor with F1, replayed "
     "when the character spawns.", "record", "none", "a recording"),
    ("Override Movement", "The recording drives movement instead of the character's own logic.",
     "record", "its own", "the recording"),
    ("Override Rotation", "The recording drives where the character looks.",
     "record", "its own", "the recording"),
    ("Override Weapon Input", "The recording drives firing.",
     "record", "its own", "the recording"),
    ("Override Ability Input", "The recording drives ability use.",
     "record", "its own", "the recording"),
    ("Loop Upon Completion", "The recording restarts when it reaches the end.",
     "record", "plays once", "loops"),
    ("Playback Mode", "Input Only replays keystrokes and can be knocked off course. Absolute "
     "Position cannot. Moveable Absolute is the second until it is hit.",
     "record", "input only", "absolute"),
)

EFFECTS: tuple[Field, ...] = (
    ("Damage Knockback Factor", "How far damage pushes the character.",
     "groundshove", "it barely moves", "it is thrown"),
    ("Respawn Invincibility Timer", "Above 0 the character is invincible for that many seconds, "
     "or until it shoots.", "spawnguard", "hittable at once", "safe for a while"),
    ("Block Self Damage", "The character cannot hurt itself.", "shield", "can", "cannot"),
    ("Block Team Damage", "Teammates cannot hurt each other.", "shield", "can", "cannot"),
    ("Invincible Player", "The player cannot be killed. A building tool, not a scenario setting.",
     "shield", "mortal", "invincible"),
    ("Invincible Bots", "Bots cannot be killed, which lets you inspect a scenario without "
     "clearing it.", "shield", "mortal", "invincible"),
    ("Disable Character Collision", "Characters pass through one another instead of shoving.",
     "pass", "they collide", "they pass"),
    ("Health Regained On Kill", "Health returned for each kill.", "killheal", "a trickle back", "a real top-up"),
    ("Health Regen Per Sec", "Health returned every second.", "regentick", "a trickle back", "a real top-up"),
    ("Ammo Awarded On Death", "Ammo handed to whoever made the kill. Usually a thing to put on "
     "bot characters.", "ammodrop", "a couple of rounds", "a full magazine"),
    ("Landing View Bob Time", "How long the view bobs after landing.", "land", "steady", "bobs"),
    ("Lifesteal", "The percentage of damage dealt that comes back as health.",
     "lifesteal", "a trickle back", "a real top-up"),
)
