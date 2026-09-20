---
title: "Ability Profile"
description: >-
  The two tabs of a KovaaK's ability profile, the four kinds of ability, and when an aim scenario has
  any use for one.
tags:
  - routines
related:
  - page: wiki/making-scenarios/kovaaks/character-profile.md
    why: the character that carries up to four abilities and a global cooldown.
  - page: wiki/making-scenarios/kovaaks/where-settings-live.md
    why: the shorter lookup this page is the long form of.
---

# Ability Profile

!!! warning "Draft"
    Written from public sources, pending review.

An ability is a movement, melee, sprint or recall action a character can use.[^REF-87] For a pure
aim drill you will not need one. For a scenario that resembles a real fight, you might.

- **Four kinds.** Movement, melee, sprint and recall.[^REF-87]
- **Two tabs each.** Main for what it does, AI Use for when bots use it.[^REF-87]
- **A character holds four.** Plus one global cooldown across them.[^REF-33]
- **Skip it for a pure aim drill.** It trains using the ability.

## Tabs

### Main

Profile name, max charges, charges on spawn and a charge timer. Charges refunded on kill, delay
between uses, and a fully-auto switch.[^REF-33]

Then the weapon to shoot, a block attack timer, whether the ability is blocked when attacking, and
ammo per shot.[^REF-33]

A movement ability adds two more tabs. H-Box gives it a hurtbox so targets near it take damage or
knockback, and Input controls which inputs are allowed during it.[^REF-87]

**Charges and cooldown set the rhythm.** They decide how often something that is not aiming
interrupts the scenario.

Max Charges is the ceiling, Charges On Spawn is how many are ready at the start, and the charge
timer refills them.[^REF-33]

<figure class="aim-figure">
<!-- aim:figure charges -->
<figcaption>Charges decide how many times a run gets interrupted, and the timer decides how soon again.</figcaption>
</figure>

Fully Auto means the ability can be held down to keep using it, rather than pressed per
use.[^REF-33] Ammo Per Shot takes ammo from the selected weapon.[^REF-33]

For a drill where you want aiming to be continuous, that interruption is the problem. For a drill
about fighting through an ability, it is the point.

<figure class="aim-figure">
<!-- aim:figure interrupt -->
<figcaption>Same sixty seconds. The red stretches are time the drill is not measuring your aim.</figcaption>
</figure>

<figure class="aim-figure">
<!-- aim:figure ability-main-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>

<figure class="aim-figure">
<!-- aim:figure ability-movement-fields -->
<figcaption>The two tabs only a movement ability has.</figcaption>
</figure>

### AI Use

When bots use it, rather than what it does. Uses on ground, in air, in combat and out of combat.
Then a reuse timer.[^REF-33][^REF-87]

Then the conditions. Self health range, target health range and target distance range, each as a
min and max. Maximum FoV to target.[^REF-33]

Then the reactions. Whether taking damage activates the ability, a chance to ignore damage, and a
reaction delay as a min and max.[^REF-33]

A damage reaction block closes the tab with a cooldown, a threshold and a reset time.[^REF-33]

**The ranges are how you make a bot behave plausibly.** A bot that only dashes when hurt, or only
when you are close, reads as a player rather than a script.

Maximum FoV to Target adds a condition of its own. Using the ability in combat, the bot must be
aiming within that many degrees of you.[^REF-33]

**Reaction delay is the honesty setting.** At zero the bot answers instantly, which no human does.
Give it a range and the fight becomes winnable.

<figure class="aim-figure">
<!-- aim:figure ability-ai-use-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>

## Common mistakes

- Building an ability scenario and calling it aim practice.
- Leaving reaction delay at zero, which produces an opponent nobody can beat.[^REF-33]
- Forgetting the character's global cooldown, which caps all four abilities at once.[^REF-33]

## In practice

**Add one only when the fight needs it.** An ability makes a scenario more like a game and less like
a measurement. Both are useful. They are not the same thing.

**Do this next.** If your scenario is about aim, check that your character has no abilities
assigned, so nothing interrupts the run.

## Resources

- [Ability Profiles](https://wiki.kovaaks.com/en/home/KovaaK's/ScenarioCreation/AbilityProfiles):
  the official page for this editor.
- [Transfer to Games](../../fundamentals/transfer-to-games.md): what a game-like scenario buys you.
