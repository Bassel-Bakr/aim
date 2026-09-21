---
title: "Character Profile"
description: >-
  Every tab of the KovaaK's character profile, which of its settings change what a scenario trains,
  and which exist for other kinds of scenario.
tags:
  - routines
related:
  - page: wiki/making-scenarios/kovaaks/where-settings-live.md
    why: the shorter lookup this page is the long form of.
  - page: wiki/making-scenarios/tuning-difficulty.md
    why: how far to move the settings this profile holds.
  - page: wiki/making-scenarios/kovaaks/making-a-scenario.md
    why: the build this profile is one step of.
---

# Character Profile

!!! warning "Draft"
    Written from public sources, pending review.

!!! note "Read from the editor"
    Field names, tooltip text and defaults here were read from the KovaaK's scenario editor in
    September 2026. The official wiki documents tabs rather than fields.

A character profile is a body: the player's, or a target's. Four of its eight tabs do nothing for an
aim drill. This page says which four, so you can stop reading them.

- **Two tabs carry almost everything.** Boxes and Spawn.[^REF-81]
- **Move is for movement scenarios.** Not for aim drills.[^REF-81]
- **The same profile dresses player and bot.** One body, two roles.[^REF-79]
- **Health changes the question.** One hit, or acquire and stay.

## Tabs

### Main

Holds the profile name, health, the respawn delays and animation duration, a headshot-only switch,
a camera height offset, and two third-person options.[^REF-81]

**Health is the one that matters.** At one hit a scenario is pure acquisition: find it, click it,
find the next. Raise it and the drill asks you to stay on the target after the first hit lands.

That single number moves a scenario between two categories, so set it deliberately rather than
inheriting it from whatever you copied.

Respawn delays decide the pace between targets. Long delays give reset time and make the drill
about the shot. Short ones keep pressure on and make it about recovery.

**Headshot Only narrows the target without resizing it.** It uses the head box from the Boxes tab
rather than the body, which is a different demand from shrinking the whole character.


**Every field on the tab.**

<figure class="aim-figure">
<!-- aim:figure character-main-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>
### Weapon

Eight weapon slots.[^REF-81] What each weapon does lives in its own profile, not here.

Use it to strip a drill down: a weapon with no spread and no recoil keeps the score about where you
pointed.

### Move

Thirty fields of movement physics: run speed, friction, jump velocity, air control, crouch
behavior, and a Quake or Source movement switch.

**Most of it is Unreal Engine, renamed.** The editor says so itself: the Scaling Friction tooltip
notes that "UE4 internally calls this 'Ground Friction'".

That is worth knowing, because it means these fields behave the way engine movement fields behave,
not the way an aim trainer invented them to.

**Skip this tab for an aim drill.** It shapes how the character moves through a map, which matters
for a movement scenario and not for one where you stand and shoot.

The exception is a scenario built to practice aiming while strafing. Four fields decide how hard
your own movement makes the aiming.

Strafe Speed Multiplier is the speed multiplier while strafing and not moving forward.

**Forward Speed Bias has a precise default.** At 1 a diagonal input moves you at 45 degrees to
where you are looking.

Larger numbers move you forward and back more than to the sides. Smaller ones move you to the side
more than forward and back.

<figure class="aim-figure">
<!-- aim:figure speed-bias -->
<figcaption>Where a diagonal input actually sends you, relative to where you are looking.</figcaption>
</figure>

**Three fields are called friction and none of them do the same job.** Scaling Friction is how fast
you change direction, and is the one the editor maps to Unreal's Ground Friction.

Let Off Friction is the braking drag, applied whenever acceleration is zero or the character is
over its maximum speed. That one sets how far you slide after releasing a key.

Aerial Friction pulls horizontal speed back toward run speed while airborne. The tooltip warns a
little goes a long way, and that even 0.3 is strong.

<figure class="aim-figure">
<!-- aim:figure friction -->
<figcaption>Three fields named friction, doing three different jobs.</figcaption>
</figure>

For a strafe-aiming drill the first two are what make counter-strafing feel sharp or mushy, which
is the thing you are actually training against.

**Two switches change what jumping is.** Fly On Jump And Crouch sends a crouched character airborne
instead of just cancelling the crouch. Can Pogo Jump lets a held jump key keep
bouncing.

**Step Up Height is the one that breaks a map quietly.** At zero the character has to jump at every
step. Set huge, it warps on top of obstacles.

<figure class="aim-figure">
<!-- aim:figure step-up -->
<figcaption>Too low and it jumps at every step. Too high and it warps up them.</figcaption>
</figure>

Match it to the smallest ledge in your map and neither failure happens.

**Crouching is two settings.** Crouch Height Multiplier scales the bounding box height, so a
crouched target is a smaller target.

Crouch Animation Rate sets how fast that happens, in seconds: 1 is 0.3, 2 is 0.15. A fast
duck is a target that shrinks before your correction lands.

<figure class="aim-figure">
<!-- aim:figure crouch-box -->
<figcaption>The same crouched height, reached at two speeds. One of them beats your correction.</figcaption>
</figure>

Can Crouch has one gotcha worth knowing: crouching does not work at all if the character is a
sphere shape.

**Every field on the tab, in order.** Thirty of them, with what each one varies and which way it
runs.

<figure class="aim-figure">
<!-- aim:figure character-move-fields -->
<figcaption>The Move tab in full. Each strip names a field, says what it does, and shows a low and
a high state side by side.</figcaption>
</figure>

### Boxes

The tab that sets target size. A character model, then two bounding boxes, each with a type, a head
switch, and proportions for body height and body radius.[^REF-81]

**This is the cleanest difficulty dial in the editor.** Body radius changes how precise each shot
has to be without changing anything else about the drill.

The second box is the projectile one. It can be hidden, and it exists so a projectile weapon can be
given a more forgiving target than a hitscan one.[^REF-81]

**Has Head changes two other settings.** With a head box, Headshot Only becomes meaningful: body
shots do no damage at all.

It also moves where the character's eyes sit. Camera Height Offset measures from the middle of the
head when there is one, and from the middle of the body when there is not.

<figure class="aim-figure">
<!-- aim:figure head-box -->
<figcaption>A head box moves the eye line and gives Headshot Only something to mean.</figcaption>
</figure>

A head is therefore not decoration. It creates a smaller high-value area and shifts the viewpoint
you play the scenario from.

<figure class="aim-figure">
<!-- aim:figure hitboxes -->
<figcaption>The main box stops at the world. The projectile box does not, which is what makes it the more forgiving target.</figcaption>
</figure>


**Every field on the tab.**

<figure class="aim-figure">
<!-- aim:figure character-box-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>
### Colors

Head and body colors for enemies and for teams. They only apply where the reader has not
overridden colors in their own Visuals settings.[^REF-81]

Worth one minute: a target color that separates cleanly from your map is one less thing between
you and the shot.


**Every field on the tab.**

<figure class="aim-figure">
<!-- aim:figure character-color-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>
### Abilities

A global cooldown, a switch that blocks abilities for a duration at challenge start, and four
ability slots.[^REF-81]

**Skip this for an aim drill.** Abilities are for scenarios about using them.


**Every field on the tab.**

<figure class="aim-figure">
<!-- aim:figure ability-slot-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>
### Spawn

Where targets appear, and the tab that turns one marker into an area.[^REF-81]

Spawn Offset Minimum and Maximum take an X, Y and Z each. Widening them scatters targets further
apart, which is how a holding drill becomes a repositioning one.

**Blocked Self Spawn Radius stops targets clustering.** Without it two targets can land close
enough that one flick covers both, which quietly turns a switching drill into a single-target
one.[^REF-81]

<figure class="aim-figure">
<!-- aim:figure self-spawn-radius -->
<figcaption>Without the radius, two targets can land inside one flick. The rule spaces them.</figcaption>
</figure>

**Block Other Spawn FOV keeps targets out of your view.** Spawns you are already looking at, within
the given field of view and distance, are blocked where possible.

The editor recommends a field of view around 15 to 30 degrees. These two apply to the
player's character rather than to bots, and work independently of the blocked self radius
above.

An invert switch flips the rule, so targets prefer to appear inside your view instead of outside
it.

**The distance field is a trap.** It selects which spawns the rule considers: a large number
affects all of them, a small one only those near the player.

Left at zero, the field of view is never checked at all. A carefully chosen FOV with the
distance still at zero does nothing, which is easy to miss.

<figure class="aim-figure">
<!-- aim:figure spawn-fov -->
<figcaption>Set the distance or the field of view is never consulted, however carefully you chose it.</figcaption>
</figure>

**Playback On Spawn runs a recording when the character appears.** A playback profile is a recording
of inputs, captured in the scenario editor with a key press, F1 by default.

Profiles used here run on spawn and apply to bots and player characters alike. The same recordings
can drive bots periodically from the dodge profile editor instead.

The override switches beside it decide which inputs the recording takes over: movement, rotation,
weapon and ability.


**Every field on the tab.**

<figure class="aim-figure">
<!-- aim:figure character-spawn-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>
### Effects

Knockback, respawn invincibility, damage blocking, invincibility for player or bots, collision,
health regen, ammo on death, view bob and lifesteal.

**Two are useful while building.** Invincible Bots lets you inspect a scenario's geometry without
killing anything, and Disable Character Collision stops targets pushing each other around.

Respawn Invincibility Timer makes a character invincible for a set number of seconds, or until it
shoots. Ammo Awarded On Death hands ammo to whoever made the kill, which the editor notes
is usually a thing to put on bots.

Lifesteal is the percentage of damage dealt that comes back as health.

Turn both off before the scenario becomes something you train on.


**Every field on the tab.**

<figure class="aim-figure">
<!-- aim:figure character-effect-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>
## Common mistakes

- Hunting for a size slider. Size is body radius on the Boxes tab.
- Changing this profile and expecting bots to follow. The bot names which character it
  wears.[^REF-82]
- Tuning movement physics for a drill where you never move.
- Leaving a build-time switch such as Invincible Bots on in a scenario you score.

## In practice

**Two tabs, then stop.** Boxes and Spawn between them set what a target costs to hit and how far
you travel to reach it. That is most of an aim scenario.

**Do this next.** Open a bot's character profile, note its body radius, then change only that and
run the scenario beside the original.

## Resources

- [Character Profiles](https://wiki.kovaaks.com/en/home/KovaaK's/ScenarioCreation/CharacterProfiles):
  the official page for this editor.
- [Where Each Setting Lives](where-settings-live.md): the same ground as a lookup table.
