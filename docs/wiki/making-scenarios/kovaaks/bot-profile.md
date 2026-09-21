---
title: "Bot Profile"
description: >-
  The three tabs of a KovaaK's bot profile, how it wires a character to a dodge, and the switches
  that keep a target from being scored.
tags:
  - routines
related:
  - page: wiki/making-scenarios/kovaaks/character-profile.md
    why: the body a bot wears, and where its size and spawn live.
  - page: wiki/making-scenarios/kovaaks/dodge-profile.md
    why: the profile that decides how this bot moves.
  - page: wiki/making-scenarios/designing-target-motion.md
    why: choosing what the motion these settings produce should train.
---

# Bot Profile

!!! warning "Draft"
    Written from public sources, pending review.

!!! note "Read from the editor"
    Field names, tooltip text and defaults here were read from the KovaaK's scenario editor in
    September 2026. The official wiki documents tabs rather than fields.

A bot profile is wiring, not content. It names a character, decides whether that character shoots,
and attaches the dodges that make it move.

- **It holds almost no settings of its own.** It points at other profiles.
- **Three tabs.** Main, Weapon, Dodge.[^REF-82]
- **Two switches change scoring.** Disable Scoring and Untargetable.
- **Weapons come from the character.** Not from this profile.

## Tabs

### Main

Profile name and the character profile the bot wears. Spawn group, a bot X-ray switch, ability use
timer and ability usage as a frequency with a min and max. A laser pointer switch. Then use minimum
respawn time, disable scoring and untargetable.[^REF-82]

**The character profile is the important line.** Everything about the target's size, health and
spawn behavior comes from there, not from here.

<figure class="aim-figure">
<!-- aim:figure wiring -->
<figcaption>A bot profile is a junction box. Note that weapons hang off the character, not off the bot.</figcaption>
</figure>

**Disable Scoring and Untargetable are design tools.** A bot that cannot be targeted or scored can
stand in a scenario as scenery, a distraction, or a thing to avoid shooting.

That is how you build a drill about target selection rather than target acquisition: put something
in the scene that punishes a careless click.

Spawn Group ties the bot to a spawn point group on the map, which is how different bots start in
different places.

**One switch is about performance, not behavior.** Checking it removes all dodging and movement
logic from the bot, which helps when a scenario wants a great many simple targets.

Ability Usage is a frequency rather than a schedule. Every interval between its minimum and maximum
the bot re-evaluates whether it may use abilities at all.

Untargetable means other bots cannot target it, which matters only in scenarios where bots fight
each other.

<figure class="aim-figure">
<!-- aim:figure bot-main-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>

### Weapon

A no aiming or shooting switch, a fire weapons switch, and a weapon switch timer. Then a row per
weapon slot pairing an aim profile with a frequency.[^REF-82]

The panel notes that the weapons listed come from the character profile chosen on the Main
tab.

**Two switches, three behaviors.** No Aiming/Shooting strips the aiming logic out entirely. Fire
Weapons left unchecked keeps the aim but holds the trigger.

Unchecked, the bot still aims at its target and simply fires nothing. That is a target that
watches you, which reads very differently from one that ignores you.

<figure class="aim-figure">
<!-- aim:figure fire-modes -->
<figcaption>Ignores you, watches you, or shoots back. Two switches cover all three.</figcaption>
</figure>

**Most aim drills want one of the first two.** A target that never shoots back is a target you can
study, and most pure aim scenarios use exactly that.

The aim column names which aim profile the bot uses per weapon, and the frequency column weights
how often each is chosen.

<figure class="aim-figure">
<!-- aim:figure bot-weapon-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>

### Dodge

Attaches dodge profiles, each with a weighting.[^REF-82] This is where a target's motion comes from.

**Weighting decides whether runs are comparable.** Heavily weighted one way and nearly every rep is
the same rep. Weighted evenly and which drill you got is luck.

<figure class="aim-figure">
<!-- aim:figure bot-dodge-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>

## Common mistakes

- Editing the bot to change target size. Size is on its character profile.
- Building a dodge profile and never attaching it here.[^REF-82]
- Stacking several dodges at similar weights, then wondering why scores jump.[^REF-82]
- Leaving bots shooting in a drill that is only about your own aim.

## In practice

**Treat it as a junction box.** If a target is wrong, the fix is almost always in the profile this
one points at, not in this one.

**Do this next.** Open a bot profile in a scenario you play and note which character and which dodge
it names. Those two are what you would actually edit.

## Resources

- [Bot Profiles](https://wiki.kovaaks.com/en/home/KovaaK's/ScenarioCreation/BotProfiles): the
  official page for this editor.
- [Designing Target Motion](../designing-target-motion.md): what to do with the dodges you attach.
