---
title: "Dodge Profile"
description: >-
  The four tabs of a KovaaK's dodge profile, the settings that decide whether a target's path can be
  learned, and what waypoint logic does.
tags:
  - tracking
  - switching
related:
  - page: wiki/making-scenarios/designing-target-motion.md
    why: the design decisions these settings carry out.
  - page: wiki/making-scenarios/kovaaks/bot-profile.md
    why: the bot that attaches this profile, and at what weight.
  - page: wiki/making-scenarios/kovaaks/where-settings-live.md
    why: the shorter lookup this page is the long form of.
---

# Dodge Profile

!!! warning "Draft"
    Written from public sources, pending review.

The dodge profile is the most important editor in the game for aim training. It decides how a target
moves, which decides which skill your scenario trains.

- **Strafe timing is the core.** Toggle times and swap pauses set the rhythm.[^REF-33]
- **React makes a target unlearnable.** It answers you instead of repeating.[^REF-33][^REF-83]
- **Waypoint Logic decides whether a route runs.** Four settings.[^REF-91]
- **Playback replaces motion with a recording.** A fixed path, every run.[^REF-33]

## Tabs

### Main

Target distance as a min and max. Toggle Left/Right, with an initial strafe direction and a trigger
for it.

Toggle L/R time as a min and max, a strafe time multiplier per side, and a strafe swap pause. Then
toggle forward and back, and a profile change time.

Waypoint logic, waypoint turn rate and cooldown time close the tab.[^REF-33][^REF-83]

**Toggle L/R Time is the strafe rhythm.** A narrow min and max makes a metronome you can learn. A
wide one makes a target you have to read.

That single pair moves a scenario between a tracking drill you can groove and a reaction drill you
cannot. Set it deliberately.

<figure class="aim-figure">
<!-- aim:figure rhythm -->
<figcaption>Same distance, same speed. Evenly spaced direction changes can be learned. Irregular ones cannot.</figcaption>
</figure>

**Strafe Swap Pause is the hardest setting in the profile.** A pause at the direction change is the
moment your crosshair either stays on target or sails past.

**Strafe Time Multiplier biases one side.** It multiplies how long the bot keeps going once it
starts strafing that way.[^REF-33]

Set the two sides differently and the target spends more time on one side of its track. That turns
an even drill into one about a direction you are worse at.

<figure class="aim-figure">
<!-- aim:figure strafe-multiplier -->
<figcaption>Same base timing, one side doubled. The target lives on the right.</figcaption>
</figure>

Cooldown Time is how long before this dodge profile can be used again, with zero meaning no
cooldown at all.[^REF-33]

Target Distance keeps the bot within a range of you. That is how a scenario holds a consistent
angular size instead of letting the target drift near and far.

**Waypoint Logic decides how much attention the bot pays to its route.** Ignore, Seek Combat, Seek
Target and Seek Waypoint.[^REF-91]

Seek Waypoint is the setting for a repeatable tracking drill: the target walks its path and never
reacts to you.

<figure class="aim-figure">
<!-- aim:figure dodge-main-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>

### React

Target Strafe Reaction, with a strafe reaction delay as a min and max.[^REF-33][^REF-83]

Then a damage reaction block. Whether taking damage toggles left/right or forward/back, and a
chance to ignore damage. A delay, a cooldown, a threshold and a reset time. Finally, whether it
triggers a profile change.

A blocked movement checks block follows, including trigger on blocking collision.[^REF-33]

**This tab is what makes a target unlearnable.** Target Strafe Reaction set to mimic means the bot
answers your movement rather than running its own pattern.

Chance to Ignore Damage is the subtle one. At anything below certain, the same hit sometimes
provokes a dodge and sometimes does not, so you cannot learn the response.

That is useful for a reaction drill and ruinous for a scenario you want to compare across sessions.

**Triggers Profile Change ejects the bot entirely.** Under Mimic or Oppose, a damage reaction
pushes it out of this dodge profile.[^REF-33]

It then looks for a dodge profile set to Ignore. If none exists, it picks one at
random.[^REF-33] A scenario with one dodge profile therefore behaves differently from one with
several.

<figure class="aim-figure">
<!-- aim:figure profile-swap -->
<figcaption>Under Mimic or Oppose, damage throws the bot out of this profile and into another.</figcaption>
</figure>

**Blocked movement is its own reaction.** Trigger On Blocking Collision fires a counter strafe when
the bot hits something that would stop it.[^REF-33]

The reaction time beside it sets how long the bot presses into the obstacle before turning
around.[^REF-33] At zero it turns instantly, which reads as unnaturally sharp.

<figure class="aim-figure">
<!-- aim:figure blocked -->
<figcaption>Reaction time is how long the bot presses into the wall before it gives up on that direction.</figcaption>
</figure>

<figure class="aim-figure">
<!-- aim:figure dodge-react-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>

### Move

Alternate jump and crouch input, jump frequency, jump time, crouching frequency and crouch
time.[^REF-33][^REF-83]

**Two approaches, chosen by one switch.** With Alternate Jump/Crouch Input unchecked you set how
often the bot presses and holds jump or crouch.[^REF-33]

Checked, the bot alternates between holding jump and holding crouch instead. That mode is meant for
character profiles where holding jump flies up and holding crouch flies down.[^REF-33]

Crouching Frequency is a percentage of time rather than a rate: zero never crouches, one holds
crouch permanently.[^REF-33]

**Vertical motion is a different demand.** A jumping target adds a vertical correction that most
aim benchmarks deliberately leave out.

Add it when your game has jump fights worth training. Leave it off when the drill is about
horizontal tracking.

<figure class="aim-figure">
<!-- aim:figure dodge-move-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>

### Playback

Profile name, override movement, override rotation, override weapon input, override ability input,
loop upon completion, and a playback mode.[^REF-33]

**Playback replaces the dodge with a recording.** The target repeats a captured path exactly, every
run, which is the most repeatable motion the editor can produce.

**Playback Mode decides what a knockback does to that recording.** Three options, and the difference
only shows once something hits the bot.[^REF-33]

Input Only replays the keyboard inputs from wherever the bot happens to be, so knockback takes
effect and pushes it off course.[^REF-33]

Absolute Position matches the recorded location at all times. The bot teleports to the start of the
path, and knockback or obstructions cannot pull it off.[^REF-33]

Moveable Absolute Position uses Absolute Position until something knocks it, then falls back to
Input Only for the rest of the playback.[^REF-33]

<figure class="aim-figure">
<!-- aim:figure playback-mode -->
<figcaption>Same recording, same shove. Only the mode decides whether the path survives it.</figcaption>
</figure>

For a drill you want identical every run, Absolute Position is the setting. The other two let a
scenario drift once contact happens.

Use it when you want a fixed path with no variance at all. It is the opposite end of the scale from
the React tab.

<figure class="aim-figure">
<!-- aim:figure dodge-playback-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>

## Common mistakes

- Building a route on the map and leaving Waypoint Logic on Ignore.[^REF-91]
- Setting a wide Toggle L/R range for a drill you meant to be repeatable.[^REF-33]
- Leaving Chance to Ignore Damage below certain in a scenario you score across sessions.[^REF-33]
- Editing the bot or character profile to change motion. It lives here.[^REF-82][^REF-83]

## In practice

**Decide readable or unreadable first, then set two fields.** Toggle L/R time for the rhythm, and
Target Strafe Reaction for whether the target answers you.

**Do this next.** Open the dodge profile of a tracking scenario you play and look at its Toggle L/R
time range. That range is why the scenario feels the way it does.

## Resources

- [Dodge Profiles](https://wiki.kovaaks.com/en/home/KovaaK's/ScenarioCreation/DodgeProfiles): the
  official page for this editor.
- [Designing Target Motion](../designing-target-motion.md): what to aim these settings at.
