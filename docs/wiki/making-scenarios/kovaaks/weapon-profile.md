---
title: "Weapon Profile"
description: >-
  Every tab of the KovaaK's weapon profile, which settings add noise to a score, and why the cheat
  tab is a building tool.
tags:
  - clicking
related:
  - page: wiki/making-scenarios/keeping-the-score-readable.md
    why: the randomness this profile is the usual source of.
  - page: wiki/making-scenarios/kovaaks/character-profile.md
    why: the character that carries up to eight of these.
  - page: wiki/making-scenarios/kovaaks/where-settings-live.md
    why: the shorter lookup this page is the long form of.
---

# Weapon Profile

!!! warning "Draft"
    Written from public sources, pending review.

The weapon decides what a click costs. It is also where most of a score's noise comes from. For a
drill about aim, the job here is mostly taking things out.

- **Two tabs add randomness.** Spread and Recoil, unless you use their patterned forms.[^REF-33]
- **Type changes the skill.** Hitscan points. Projectile leads.[^REF-33][^REF-86]
- **Cheats are a building tool.** Not something to leave on.[^REF-86]
- **Most tabs are cosmetic.** Graphics and Explosives change nothing about aiming.[^REF-33]

## Tabs

### Main

Weapon name, type, category and a burst switch. Damage per shot, bullets per click and time between
shots. Origin offset, max hitscan range, headshot capable and factor. Damage falloff, damage at max
range, and switch time reduction.[^REF-33][^REF-86]

**Type is the decision on this page.** Hitscan resolves where you pointed. Projectile takes time to
arrive, so every shot becomes a lead, which is a different skill.

Category sets semi or full automatic, and time between shots sets the floor on your fire rate. For
a click-timing drill that floor is the drill.

Headshot Capable and Headshot Factor pair with the head box on the character's Boxes tab. Together
they make a smaller high-value area without shrinking the target.


**Every field on the tab.**

<figure class="aim-figure">
<!-- aim:figure weapon-main-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>
### Effects

Delay before shot, delay after shooting, piercing, hitscan radius, ground and air knockback, flat
knockback, speed modifiers, stun, tagging and aim punch.[^REF-33]

**Hitscan Radius is worth knowing about.** It widens what counts as a hit, independently of target
size, so a drill can be made forgiving without redrawing the target.

**Piercing lets one shot reach several targets.** The editor describes it as allowing hitscan
weapons to go through targets and damage more than one thing.[^REF-33]

That changes what a line of targets asks for. Without it, a row is a selection problem. With it, a
row is one shot taken at the right angle.

<figure class="aim-figure">
<!-- aim:figure piercing -->
<figcaption>Without piercing a row of targets is a selection problem. With it, it is one shot.</figcaption>
</figure>

<figure class="aim-figure">
<!-- aim:figure hit-radius -->
<figcaption>Two ways to make the same miss count. One you can see coming. The other you cannot.</figcaption>
</figure>

The knockback and stun fields shape fights, not aim. Leave them alone for a drill.


**Every field on the tab.**

<figure class="aim-figure">
<!-- aim:figure weapon-effect-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>
### Ammo

Magazine max, ammo per shot, incremental reload, empty and partial reload times, ammo reloaded per
kill, and reload before shot recovery.[^REF-33][^REF-86]

**Reloads interrupt a drill.** For most aim scenarios a magazine large enough never to reload keeps
the run continuous.


**Every field on the tab.**

<figure class="aim-figure">
<!-- aim:figure weapon-ammo-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>
### Graphics

View and third-person models and skins. Hitscan trace particle, visual duration, radius and offset,
and beam tracking. Muzzle flash, wall and body impact particles, decals and decal size.[^REF-33]

Cosmetic, with one exception. A trace or impact particle that reads clearly tells you where the shot
went, which matters when you are diagnosing a miss.


**Every field on the tab.**

<figure class="aim-figure">
<!-- aim:figure weapon-graphics-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>
### Explosives

Explodes, radius, area damage, self damage multiplier, explosion blocked by world, and clear
attackers on self damage.[^REF-33]

**Skip this for an aim drill.** Splash damage rewards being near the target, which is the opposite
of the demand you are building.


**Every field on the tab.**

<figure class="aim-figure">
<!-- aim:figure weapon-explosive-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>
### Spread

Firing type, circular spread, stationary velocity and spread decay delay. Then a block per firing
state: spread increase per shot, decrease per second, and a min and max.[^REF-33][^REF-86]

**This is the main source of noise in a score.** With spread, two identical inputs give two
different outcomes, so a bad run may be the weapon rather than your aim.

**Circular Spread decides the shape of the cone.** Unchecked, the spread is square
instead.[^REF-33]

A square reaches further at its corners than along its edges, so the same setting is less forgiving
on the diagonals. The min and max are the lowest the spread can be reduced to and the highest it
can reach.[^REF-33]

<figure class="aim-figure">
<!-- aim:figure spread-shape -->
<figcaption>The same spread value. A square reaches further at its corners than a circle ever does.</figcaption>
</figure>

Set it to zero for any drill you intend to read. Keep it only when the drill is about controlling a
spraying weapon.


**Every field on the tab.**

<figure class="aim-figure">
<!-- aim:figure weapon-spread-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>
### PBS

Per bullet spread: a fixed pattern of offsets rather than a random cone, which is what a shotgun
wants.[^REF-33][^REF-86]

A fixed pattern is learnable, so it is a skill rather than a tax. That is the whole difference from
the Spread tab.


**Every field on the tab.**

<figure class="aim-figure">
<!-- aim:figure weapon-per-bullet-spread-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>
### Recoil

Vertical and horizontal recoil, each as a min and max. First shot multiplier, time to peak, auto
reset and time to reset. Manual negation, crouch scale and ADS scale.[^REF-33][^REF-86]

**Random recoil is noise like spread is noise.** Two bursts climb differently, so your score moves
for reasons that are not you.

Vertical Recoil is how far the crosshair moves up, drawn at random between the min and the
max.[^REF-33] Crouch Scale and ADS Scale multiply the whole thing in those two states, with one
meaning no change.[^REF-33]

**The timing fields have a rule, and the editor states it.** Time To Peak is how long the recoil
takes to reach maximum. Time To Reset is how long after that before the crosshair returns.[^REF-33]

The tooltip recommends that peak plus reset comes to less than the Main tab's Time Between
Shots.[^REF-33] Break that and the crosshair never gets home between shots, so the climb
accumulates.

<figure class="aim-figure">
<!-- aim:figure recoil-timing -->
<figcaption>Peak plus reset has to fit inside the gap between shots, or the climb never comes home.</figcaption>
</figure>


**Every field on the tab.**

<figure class="aim-figure">
<!-- aim:figure weapon-recoil-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>
### PSR

Per shot recoil: a fixed climb, the kind a Counter-Strike player learns.[^REF-33][^REF-86] The
editor describes it as for weapons where the recoil follows a pre-determined pattern over the
magazine.[^REF-33]

Use this when recoil control is the point of the drill.

**It has its own timing trap.** The per-shot time is how long each instance of recoil takes to
play, and the automatic reset is blocked while it runs.[^REF-33]

The tooltip recommends setting it above the Main tab's Time Between Shots, so that rapidly tapped
shots still trigger recoil at all.[^REF-33]

A loop start index decides which shot the pattern jumps back to once it reaches the end of the
list.[^REF-33]


**Every field on the tab.**

<figure class="aim-figure">
<!-- aim:figure weapon-per-shot-recoil-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>
### ADS

Whether the weapon can aim down sights, and the zoom FOV. Whether the user may override that FOV.
Zoom time, start delay and sensitivity factor. Blocking rules while zoomed, and a third-person
camera offset.[^REF-33][^REF-86]

Relevant only if your game has an ADS you want to practice through. It changes your effective
sensitivity while zoomed, so treat a zoomed drill as a separate scenario.


**Every field on the tab.**

<figure class="aim-figure">
<!-- aim:figure weapon-ads-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>
### Also Shoot

Attaches other weapon profiles to fire alongside this one.[^REF-33] Useful for building a weapon out
of parts, and not something an aim drill needs.


**Every field on the tab.**

<figure class="aim-figure">
<!-- aim:figure weapon-also-shoot-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>
### Cheats

Aimbot mode, target preference and disable on kill. Lock strength, max speed, FOV and deadzone.
Line-of-sight and axis rules, lock offsets, auto-off and re-engage timers. Sticky lock, head lock,
trigger bot and its delay.[^REF-33][^REF-86]

**This tab is a building tool.** An aimbot takes your own aim out of the picture. That is what you
want when checking whether a scenario's geometry, spawns and motion behave as intended.

Cheats can be disabled through the challenge properties, and are freely available in free
play.[^REF-86] Turn them off before the scenario becomes something you score.

**Lock Deadzone is the field that makes an aimbot useful.** It is the distance from the target at
which the lock stops tracking.[^REF-33]

At zero the lock rides the target's center and nothing you do matters. Set it and the lock brings
the crosshair close, then lets go.

That is a far better way to check whether a scenario's spawns and motion behave as intended.

<figure class="aim-figure">
<!-- aim:figure lock-deadzone -->
<figcaption>A deadzone is what turns a lock from an unbeatable opponent into a building tool.</figcaption>
</figure>

Target Preference decides priority when several targets are available.[^REF-33] Disable On Kill
decides whether a lock may move to a new target once it has one.[^REF-33]

Lock Vertical Offset shifts how far up or down the lock aims when locking vertically.[^REF-33]


**Every field on the tab.**

<figure class="aim-figure">
<!-- aim:figure weapon-cheats-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>
## Common mistakes

- Reading a score from a weapon with spread as a measure of aim.[^REF-33]
- Leaving a cheat enabled after testing.[^REF-86]
- Editing Charge or Burst settings without enabling them on Main.[^REF-86]
- Building a magazine small enough that reloads break the drill.

## In practice

**Strip first, then judge.** For a drill about aim, a weapon with no spread, no random recoil and no
reload keeps the score about where you pointed.

**Do this next.** Open the weapon profile of a scenario you play and check its Spread tab. If it has
any, copy the scenario with spread at zero and compare a session on each.

## Resources

- [Weapon Profiles](https://wiki.kovaaks.com/en/home/KovaaK's/ScenarioCreation/WeaponProfiles):
  the official page for this editor.
- [Keeping the Score Readable](../keeping-the-score-readable.md): why the randomness here matters.
