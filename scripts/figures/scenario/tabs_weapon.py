"""The weapon profile's twelve tabs, one line per field.

Same shape as the character tabs: name, what the editor says it does, the demonstration kind, and
the two state labels. A kind ending "-inv" means the higher value shows less of the effect.

Charge, Burst and Projectile appear only once their switch on the Main tab is set, so their fields
are listed with the switch that reveals them rather than as tabs of their own.
"""
from fields import Field

MAIN: tuple[Field, ...] = (
    ("Weapon Name", "What this weapon profile is called.", "label", "unnamed", "named"),
    ("Type", "Hitscan is instantaneous damage at a distance. Projectile is a physical object with "
     "travel time, so every shot becomes a lead.", "hitscan", "hitscan", "projectile"),
    ("Category", "Semi automatic fires once per press; full automatic keeps firing while held.",
     "burst", "semi auto", "full auto"),
    ("Burst Fire", "Each press fires a fixed burst, configured on a tab of its own.",
     "burst", "single", "a burst"),
    ("Damage Per Shot", "How much damage one round does.", "shotbite", "a small bite", "a big one", "bar"),
    ("Bullets Per Click", "How many rounds leave per press, as a shotgun does.",
     "burst", "one", "several"),
    ("Time Between Shots", "The floor on your fire rate. For a click-timing drill this floor is "
     "the drill.", "firefloor", "a fast weapon", "a slow one", "round"),
    ("Origin Offset", "Where the shot leaves from, as X, Y and Z from the camera.",
     "muzzleoffset", "it leaves from the eye", "off to one side", "round"),
    ("Max Hitscan Range", "How far a hitscan shot reaches before it stops.",
     "traceend", "the shot never reaches", "it carries all the way"),
    ("Headshot Capable", "Whether this weapon can register a headshot at all. It pairs with the "
     "head box on the character's Boxes tab.", "head", "no", "yes"),
    ("Headshot Factor", "How much a headshot multiplies damage by.", "headmult", "a headshot counts the same", "it hits far harder", "bar"),
    ("Damage Falloff", "The start and stop distances over which damage tapers off.",
     "falloffband", "it tapers close in", "full damage far out"),
    ("Damage At Max Range", "What a shot still does once falloff is complete.",
     "rangefloor", "almost nothing at range", "it still hurts", "bar"),
    ("Switch Time Reduction", "Allows swapping to another weapon before this one is ready to fire "
     "again. Set equal to time between shots and the swap is instant.",
     "earlyswap", "it waits its turn", "it comes up early", "round"),
)

EFFECTS: tuple[Field, ...] = (
    ("Delay Before Shot", "A wind-up between pressing and firing.",
     "shotwindup", "it fires at once", "a long wind-up", "round"),
    ("Delay After Shooting", "A recovery after firing before anything else may happen.",
     "shotrecovery", "ready again at once", "a long recovery", "round"),
    ("Piercing", "Lets hitscan weapons go through targets and damage more than one thing.",
     "hitscan", "stops at one", "passes through"),
    ("Hitscan Radius", "Widens what counts as a hit, independently of the target's size.",
     "scatter", "a point", "a wide shot"),
    ("Ground Knockback Factor", "When the target is on the ground, damage is multiplied by this "
     "and applied as knockback.", "groundshove", "it barely moves", "it is thrown"),
    ("Air Knockback Factor", "The same, for a target that is airborne.",
     "airshove", "it barely moves", "it is thrown"),
    ("Flat Horizontal Knockback", "A fixed sideways shove, drawn between a minimum and a maximum.",
     "flatshove", "a nudge", "a shove"),
    ("Flat Vertical Knockback", "A fixed upward shove, drawn between a minimum and a maximum.",
     "jump", "small", "large"),
    ("Accel Speed Modifier", "While this weapon is held, the character's acceleration is "
     "multiplied by this amount.", "rampslow", "it makes you sluggish", "it barely slows you"),
    ("Max Speed Modifier", "While this weapon is held, top speed is multiplied by this amount.",
     "speedcap", "this weapon slows you", "it barely slows you"),
    ("Stun Duration", "How long a hit target is stunned for.", "stunfreeze", "a flinch", "a long freeze"),
    ("Tagging Duration", "How long a hit target is slowed for.", "tagdrag", "it shrugs it off", "it crawls a while"),
    ("Aim Punch Amount", "How far a hit knocks the target's own aim off.",
     "climb", "steady", "punched"),
)

AMMO: tuple[Field, ...] = (
    ("Magazine Max", "How many rounds before a reload. Large enough never to reload keeps a drill "
     "continuous.", "magsize", "four rounds", "twelve", "round"),
    ("Ammo Per Shot", "How much ammo each press consumes.", "ammobite", "one per press", "several", "round"),
    ("Incremental Reload", "Reloads a round at a time rather than the whole magazine.",
     "head", "all at once", "one at a time"),
    ("Empty Reload Time", "How long a reload takes from empty.", "emptyreload", "a quick reload", "a long one", "round"),
    ("Partial Reload Time", "How long a reload takes with rounds still in the magazine.",
     "partialreload", "a quick top-up", "a long one", "round"),
    ("Ammo Reloaded Per Kill", "Rounds returned for each kill.", "killammo", "the kill returns one", "it returns several", "round"),
    ("Reload Before Shot Recovery", "Allows the reload to begin before the post-shot recovery has "
     "finished.", "overlapreload", "it waits its turn", "it starts early", "round"),
)

GRAPHICS: tuple[Field, ...] = (
    ("View Model Animation", "Which first-person animation set the weapon uses.",
     "view", "primary", "another"),
    ("Third Person Model", "The weapon others see you holding.", "view", "none", "a model"),
    ("Third Person Skin", "Which skin that model wears.", "view", "default", "another"),
    ("Hitscan Trace Particle", "The trail drawn along a hitscan shot. Worth setting: a readable "
     "trace tells you where a miss went.", "particle", "none", "a trace"),
    ("Hitscan Visual Duration", "How long that trail stays on screen.",
     "tracerlife", "gone at once", "it lingers"),
    ("Hitscan Visual Radius", "How thick the trail is.", "tracerwidth", "a hairline trail", "a fat one"),
    ("Beam Tracks Crosshair", "The beam follows the crosshair rather than staying where it was "
     "fired.", "hitscan", "stays put", "follows"),
    ("Hitscan Visual Offset", "Where the trail is drawn from, as X, Y and Z.",
     "traceorigin", "it follows the shot", "it starts elsewhere"),
    ("Muzzle Flash Particle", "The flash at the barrel.", "particle", "none", "a flash"),
    ("Muzzle Flash Particle Scale", "How large that flash is.", "muzzlescale", "you can see past it", "it covers the target"),
    ("Wall Impact Particle", "What appears where a shot hits the world.",
     "particle", "none", "an impact"),
    ("Wall Impact Particle Scale", "How large that impact is.", "wallburst", "easy to miss", "impossible to miss"),
    ("Body Impact Particle", "What appears where a shot hits a character.",
     "particle", "none", "an impact"),
    ("Body Impact Particle Scale", "How large that impact is.", "bodyburst", "easy to miss", "impossible to miss"),
    ("Wall Hit Decal", "The mark left behind on the world.", "particle", "none", "a mark"),
    ("Decal Size", "How large that mark is.", "decalmark", "small marks", "the wall fills up"),
)

EXPLOSIVES: tuple[Field, ...] = (
    ("Explodes", "Rounds detonate on impact. Splash damage rewards being near the target, which "
     "is the opposite of most aim drills.", "particle", "no", "yes"),
    ("Explosion Radius", "How far the blast reaches.", "scatter", "tight", "wide"),
    ("Area Damage", "How much damage the blast does away from the point of impact.",
     "blastedge", "the edge barely stings", "the edge still kills", "bar"),
    ("Self Damage Multiplier", "How much of that blast damage comes back to you.",
     "blastback", "it barely touches you", "it takes you too", "bar"),
    ("Explosion Blocked By World", "Walls stop the blast instead of letting it through.",
     "particle", "passes", "blocked"),
    ("Clear Attackers On Self Damage", "Self damage clears who last hurt you.",
     "view", "kept", "cleared"),
)

SPREAD: tuple[Field, ...] = (
    ("Firing Type", "Which firing state this block of spread settings applies to, such as "
     "standing hipfire.", "pattern", "one state", "another"),
    ("Circular Spread", "Unchecked, the spread is square instead. A square reaches further at its "
     "corners than along its edges.", "scatter", "square", "circular"),
    ("Stationary Velocity", "The speed below which you count as standing still for spread.",
     "stillgate", "moving opens the cone", "it counts as still"),
    ("Spread Decay Delay", "How long after firing before spread begins recovering.",
     "spreadhold", "it closes at once", "it stays open"),
    ("Spread Increase per Shot", "How much each shot widens the cone.",
     "scatter", "holds tight", "opens fast"),
    ("Spread Decrease per Second", "How fast the cone closes again.",
     "scatter-inv", "closes slowly", "closes fast"),
    ("Spread Minimum", "The tightest the cone can ever be reduced to.",
     "scatter", "pinpoint", "never tight"),
    ("Spread Maximum", "The widest the cone can ever reach.", "scatter", "capped", "wide open"),
)

PBS: tuple[Field, ...] = (
    ("Use Per Bullet Spread", "A fixed pattern of offsets rather than a random cone, which is "
     "what a shotgun wants. A fixed pattern is learnable.",
     "pattern", "random cone", "fixed pattern"),
    ("Pattern Offsets", "Where each pellet lands relative to the crosshair.",
     "scatter", "tight pattern", "wide pattern"),
    ("Pattern Count", "How many entries the pattern holds.", "pelletlist", "a two-shot pattern", "a six-shot one", "mark"),
)

RECOIL: tuple[Field, ...] = (
    ("Vertical Recoil", "How much to move the crosshair up, drawn at random between a minimum and "
     "a maximum.", "climb", "barely rises", "climbs hard"),
    ("Horizontal Recoil", "How much to move the crosshair sideways, drawn between a minimum and a "
     "maximum.", "swerve", "it climbs straight", "it wanders sideways"),
    ("First Shot Multiplier", "How much the first shot of a burst is scaled by.",
     "climb", "same as the rest", "punishes the first"),
    ("Time To Peak", "How long in seconds the recoil takes to reach its maximum.",
     "recoilpeak", "it tops out at once", "it climbs slowly", "mark"),
    ("Auto Reset", "The crosshair returns on its own once firing stops.",
     "hitscan", "stays up", "returns"),
    ("Time To Reset", "How long after the peak before the crosshair is home. Peak plus reset "
     "should come to less than Time Between Shots.", "recoilreset", "home before the next shot", "still high", "mark"),
    ("Allow Manual Negation", "Lets the player pull down against the recoil themselves.",
     "hitscan", "fixed", "controllable"),
    ("Crouch Scale", "Scales recoil while crouched. 1 is the same as normal.",
     "climb-inv", "same as standing", "tamer crouched"),
    ("ADS Scale", "Scales recoil while aiming down sights. 1 is the same as normal.",
     "climb-inv", "same as hipfire", "tamer zoomed"),
)

PSR: tuple[Field, ...] = (
    ("Use Per Shot Recoil", "For weapons whose recoil follows a pre-determined pattern over the "
     "magazine, the kind a player learns.", "pattern", "random", "a pattern"),
    ("Time Per Shot", "How long each instance of recoil takes to play. Automatic reset is blocked "
     "while it runs, so set it above Time Between Shots.", "shotrecoil", "a short clip", "a long one", "mark"),
    ("Restore Rate", "How quickly the crosshair and the center of shots return to normal.",
     "climb-inv", "slow to settle", "settles fast"),
    ("Loop Start Index", "Which shot the pattern jumps back to once it reaches the end of the "
     "list.", "patternloop", "it loops the whole list", "the tail only", "mark"),
)

ADS: tuple[Field, ...] = (
    ("Can Aim Down Sight", "Whether the weapon has a zoom at all.", "zoom", "no", "yes"),
    ("Zoom FOV", "The field of view while zoomed. Games handle FOV differently, so match the "
     "number to the game you are training for.", "zoom", "slight", "strong"),
    ("Allow User Override", "Lets the reader pick their own zoom field of view.",
     "hitscan", "fixed", "their choice"),
    ("Zoom Time", "How long the zoom animation takes.", "zoomramp", "it snaps in", "a slow zoom", "box"),
    ("Zoom Start Delay", "A delay in seconds before the zoom animation begins.",
     "zoomwait", "it starts at once", "it hangs first", "box"),
    ("Zoom Sensitivity Factor", "How much your sensitivity changes while zoomed.",
     "zoomsens", "the view keeps up", "the same hand moves less"),
    ("ADSing Resets Charge", "Going in or out of sights interrupts weapon charging.",
     "pattern", "charge kept", "charge lost"),
    ("Zoom Blocked In Air", "Jumping or falling drops out of, or prevents, aiming down sights.",
     "aircrouch", "allowed", "blocked"),
    ("Third Person Camera Offset", "Shifts the camera while a third-person character is aiming "
     "down sights.", "tpscamera", "it sits behind you", "it swings out wide"),
)

ALSO_SHOOT: tuple[Field, ...] = (
    ("Also Shoot Profiles", "Other weapon profiles fired at the same time as this one. Ammo, "
     "recoil and spread all follow the original profile.", "burst", "one weapon", "several"),
    ("Zoomed Override", "While zoomed, the weapon obeys the other profile's Also Shoot tab "
     "instead of this one.", "aircrouch", "this tab", "the other tab"),
)

CHEATS: tuple[Field, ...] = (
    ("Aimbot Mode", "How the lock behaves, including whether it ignores your fire input.",
     "lock", "off", "locking"),
    ("Target Preference", "What decides priority when several targets are available.",
     "lock", "nearest", "another rule"),
    ("Disable On Kill", "Whether a lock may move to a new target once it has one.",
     "lock", "moves on", "stays"),
    ("Lock Strength", "How hard the lock pulls the crosshair toward the target.",
     "lockpull", "it tugs a little", "it drags you on target"),
    ("Lock Max Speed", "The fastest the lock may move your aim.", "lockrate", "it crawls across", "it crosses at once"),
    ("Lock FOV", "How far off target the lock will still engage.", "lockcone", "only dead ahead", "it grabs from far off"),
    ("Lock Deadzone", "The distance from the target at which the lock stops tracking. This is "
     "what turns an aimbot from unbeatable into a building tool.",
     "lockdead", "it holds you on target", "it lets go early"),
    ("Lock Needs LOS", "The lock requires line of sight to the target.",
     "lock", "through walls", "needs sight"),
    ("Lock Horizontal", "The lock corrects sideways.", "lock", "no", "yes"),
    ("Lock Vertical", "The lock corrects up and down.", "lock", "no", "yes"),
    ("Lock Vertical Offset", "How far up or down the lock aims when locking vertically.",
     "lockheight", "it parks on the body", "over the head"),
    ("Lock Blocks Mouse", "The lock takes your mouse input away while engaged.",
     "lock", "you still aim", "it takes over"),
    ("Lock Auto Off Timer", "How long before the lock releases on its own.",
     "lockhold", "it lets go quickly", "it holds on", "box"),
    ("Lock Re-Engage Timer", "How long before a released lock may grab again.",
     "lockregrab", "it grabs again at once", "a long wait", "box"),
    ("Sticky Lock", "The lock resists letting go once it has a target.",
     "lock", "lets go", "sticks"),
    ("Head Lock", "The lock aims at the head rather than the body.",
     "head", "body", "head"),
    ("Trigger Bot", "Fires for you the moment a target crosses the crosshair.",
     "lock", "you fire", "it fires"),
    ("Trigger Bot Delay", "How long it waits before firing for you.",
     "triggerwait", "it fires as you cross", "it hesitates", "box"),
)
