"""The Edit Scenario window's five tabs, one line per field.

These are rules and numbers rather than motion, so almost none of the profile shapes apply. A kind
ending "-inv" means the higher value shows less of the effect, which is true of every Disable switch
on the Challenge tab: checking one removes something the reader was being shown.
"""
from fields import Field

MAIN: tuple[Field, ...] = (
    ("Scenario Name", "What the scenario is called. It is what a reader searches for and what "
     "their score is filed under.", "label", "unnamed", "named"),
    ("Player Characters", "The character profiles a player may use in this scenario. Adding one "
     "makes it available; it does not put it into a challenge run.",
     "slot", "none added", "a character"),
    ("Bots", "The bot profiles this scenario may spawn. Same rule: this is the inventory, not the "
     "rules.", "slot", "none added", "a bot"),
)

UNPACK: tuple[Field, ...] = (
    ("Unpack", "Extracts the scenario's profiles back out as files you can edit. It is how you "
     "undo a change to a profile, and how you take one piece out of someone else's scenario.",
     "unpack", "it stays packed", "profiles written out"),
)

CHALLENGE: tuple[Field, ...] = (
    ("Map Scale", "Scales the whole map. It changes every distance in the scenario at once, so a "
     "flick that was comfortable stops being one.", "worldscale", "a small room", "a large one"),
    ("Time Scale", "Speeds the whole scenario up or slows it down, targets included.",
     "timescale", "normal", "fast"),
    ("Target Speed", "A multiplier on how fast targets move, applied over whatever their dodge "
     "profiles already do.", "dodgepace", "the same path, slowly", "the same path, fast"),
    ("Target Speed Mode", "Static holds the speed where you set it. Adapt moves it with your "
     "performance, so the difficulty stops being a constant you control.",
     "adaptmode", "static", "adapt"),
    ("Target Size", "A multiplier on target size. The cleanest difficulty dial the window has.",
     "targetscale", "as the profile set it", "scaled up from it"),
    ("Target Size Mode", "Static or adapt again. An adapting scenario is harder to read across "
     "sessions, because a rise no longer means what it used to.",
     "adaptmode", "static", "adapt"),
    ("Time Limit", "How long a run lasts. A length you repeat is worth more than a length you "
     "optimize.", "runlength", "a short run", "a long one"),
    ("Time Regained Per Kill", "Seconds added back to the clock for each kill. Above zero, a good "
     "run lasts longer than a bad one, so two scores no longer share a clock.",
     "clockadd", "the clock only falls", "a kill buys time"),
    ("End After Kills", "Stops the run at a kill count. Set alongside a time limit it is a race: "
     "whichever fires first ends the run.", "endtally", "the run ends early", "it runs a long time"),
    ("End After Damage", "Stops the run once a damage total is reached. The third runner in the "
     "same race.", "endtally", "the run ends early", "it runs a long time"),
    ("Lock Hipfire FOV", "Clamps the field of view targets are seen at. Unclamped, a target's "
     "angular size differs per reader and your scenario is not quite the one they play.",
     "fovclamp", "a different drill each", "the same for everyone"),
    ("Locked FOV Range", "The field of view the clamp holds readers to. It only matters once the "
     "lock above is on.", "fovclamp", "left open", "held to a range"),
    ("Force Particle Effects", "Forces the scenario's particle effects on, whatever the reader's "
     "own settings say.", "particle", "reader's choice", "forced on"),
    ("Disable Projectile Predictors", "Removes the lead indicator drawn ahead of a moving target. "
     "Without it you have to judge the lead yourself.",
     "predictor", "the lead is drawn", "no lead shown"),
    ("Disable Cheats", "Stops a weapon's Cheat tab applying. It is what keeps an aimbot or a "
     "trigger bot out of a scored run.", "lock-inv", "cheats apply", "cheats are off"),
    ("Disable Health Bars", "Removes the health bar above a target, so you cannot see how close "
     "it is to dying.", "healthbar", "health is shown", "no bar"),
    ("Disable Hit Markers", "Removes the marker that confirms a hit landed. It makes the drill "
     "closer to a game and harder to learn from.",
     "hitmarker", "the hit is marked", "nothing marks it"),
    ("Disable Hit Sounds", "Removes the hit sound. Keep it on while you are learning a drill and "
     "turn it off only when the point is practicing without the crutch.",
     "hitsound", "the hit is heard", "silent"),
)

SCORING: tuple[Field, ...] = (
    ("Score To Win", "The score a run has to reach. It is the bar the rest of this tab is "
     "measured against.", "wintarget", "reached early", "a long way up"),
    ("Score Per Damage", "Points for each point of damage dealt. Paying per damage rewards "
     "landing shots rather than finishing targets.",
     "paydamage", "a little", "a lot"),
    ("Score Per Hit", "Points for each hit that lands, whatever it did. A model paying only for "
     "hits trains volume.", "payhit", "a little", "a lot"),
    ("Enable Over Damage", "Whether damage past what was needed to kill still counts. Off, the "
     "surplus from an overkill is thrown away.",
     "overdamage", "the surplus is wasted", "the surplus pays"),
    ("Score Per Kill", "Points for each kill. Paying per kill rewards finishing a target rather "
     "than chipping at it.", "paykill", "a little", "a lot"),
    ("Score Per Midair Direct", "Points for a direct hit on a target that is off the ground. It "
     "is how a scenario asks for a specific shot rather than any shot.",
     "paymidair", "a little", "a lot"),
    ("Score Per Any Direct", "Points for a direct hit, airborne or not.",
     "paydirect", "a little", "a lot"),
    ("Score Per Time Left", "Points for each second still on the clock when the run ends. It pays "
     "for finishing early, which is a speed drill rather than an accuracy one.",
     "paytime", "a little", "a lot"),
    ("Score Per Distance Traveled", "Points for moving. It turns a scenario into a movement drill "
     "with shooting attached.", "movescore", "moving pays nothing", "distance pays"),
    ("Enable Movement Based Scoring", "Turns the movement block on at all. Left off, nothing in "
     "it applies however it is filled in.",
     "movescore", "movement is ignored", "movement counts"),
    ("Score Loss Per Damage Taken", "Points subtracted when you are hit. It trains staying alive "
     "alongside aiming, which is a different drill.",
     "penaltydamage", "a small cost", "a heavy one"),
    ("Score Loss Per Death", "Points subtracted when you die. Set high it makes the scenario "
     "about survival first.", "penaltydeath", "a small cost", "a heavy one"),
    ("Accuracy Multiplier", "Multiplies the subtotal by your accuracy, so misses charge against "
     "everything you earned.", "multaccuracy", "unchanged", "accuracy takes a cut"),
    ("Square Root Accuracy Multiplier", "Multiplies by the square root of accuracy instead. It "
     "softens how much one bad stretch swings the final score.",
     "multsqrt", "unchanged", "a gentler cut"),
    ("Damage Efficiency Multiplier", "Multiplies by damage landed against damage fired. The "
     "editor recommends not checking this and Accuracy, because the same misses are charged "
     "twice.", "multdamage", "unchanged", "efficiency takes a cut"),
    ("Kill Efficiency Multiplier", "Multiplies by kills against shots. It rewards finishing "
     "targets with as little spent as possible.",
     "multkill", "unchanged", "efficiency takes a cut"),
)

TAGS: tuple[Field, ...] = (
    ("Tags", "The words the browser searches on. Empty, the scenario is unfindable however good "
     "it is.", "findable", "nobody finds it", "it turns up"),
    ("Difficulty", "The rating shown beside the scenario. It sets what a reader expects before "
     "they load it.", "difficulty", "gentle", "hard"),
    ("Description", "What the scenario is for. Write it as the weakness it isolates, not as what "
     "it looks like: a reader hunting for a drill searches by what it fixes.",
     "label", "blank", "written"),
    ("Aim Type", "The broad skill the drill trains. It feeds the browser's filters, so this is "
     "how the right reader reaches it.", "slot", "unset", "clicking or tracking"),
    ("Aim Sub Type", "The narrower skill under that type. It is the difference between a "
     "scenario found by the person who needs it and one found by nobody.",
     "slot", "unset", "a sub type"),
    ("Flicking", "Marks the scenario as a flicking drill: one correction onto the target rather "
     "than a slide onto it.", "flick", "a slide onto it", "one snap"),
    ("Thumbnail", "The picture shown in the browser. It is the only thing a reader sees before "
     "deciding whether to try the scenario.", "thumbnail", "an empty tile", "a picture"),
)
