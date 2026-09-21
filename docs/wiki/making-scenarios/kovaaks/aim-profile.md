---
title: "Aim Profile"
description: >-
  What a KovaaK's aim profile controls, why most aim drills never need one, and how to use it to
  model an opponent's aim.
tags:
  - routines
related:
  - page: wiki/making-scenarios/kovaaks/bot-profile.md
    why: the bot that assigns this profile per weapon.
  - page: wiki/making-scenarios/kovaaks/where-settings-live.md
    why: the shorter lookup this page is the long form of.
---

# Aim Profile

!!! note "How this page is sourced"
    Sourced from vendor documentation, plus field names and tooltips read from the scenario
    editor in September 2026. Not yet checked claim by claim.

An aim profile tells a bot how to aim at you.[^REF-92] It has one tab, and most aim drills never
touch it, because most aim drills use targets that never shoot back.

- **One tab, about twenty fields.**
- **Irrelevant if bots do not fire.** Which covers most aim scenarios.[^REF-79]
- **It models a human, badly or well.** Reaction time, speed and error.
- **It is also how you build an aimbot.** For testing, not for scoring.

## Tabs

### Main

Profile name and an aiming style. Reaction time as a min and max. Self movement fix time as a min
and max.

Then the aim itself: flick FOV, flick speed, flick error, track speed and track error.

Then the limits. Max turn on mousepad, and mouse re-center time as a min and max. Optimal aim FOV
and an outer aim penalty multiplier. Shoot FOV, a vertical aim offset and a tolerable
spread.

**Speed and error are the pair that matter.** Speed sets how fast the bot closes on you. Error sets
how much it misses by, which is what stops it being perfect.

Set error to zero and you have an aimbot. That is genuinely useful while building, because it lets
you check whether a scenario's geometry and spawns work without your own aim in the way.

**Reaction time is a sampling rate, not a delay.** The editor describes it as how often the bot
estimates its opponent's position and its own.

Estimate rarely and the bot aims where you were when it last looked. That is what makes a slow bot
feel beatable rather than merely slow.

<figure class="aim-figure">
<!-- aim:figure estimating -->
<figcaption>A slow bot is not aiming late. It is aiming at an older guess.</figcaption>
</figure>

Flick Speed is defined relative to that reaction time: it is how fast the bot flicks to the
estimated location.

**Reaction time is also how you model a human.** A bot with a short one punishes you for breaking
cover. A long one gives you a window.

**Max Turn On Mousepad is the field that makes a bot feel human.** It is how many degrees from the
bot's mousepad center before an aiming penalty starts.

Track Error is a random value from zero up to the amount you set, multiplied by that mousepad
penalty, then clamped at Max Aiming Error.

<figure class="aim-figure">
<!-- aim:figure mousepad -->
<figcaption>Error climbs once the bot turns past its mousepad, then stops at the ceiling you set.</figcaption>
</figure>

So a bot aiming near its mousepad center is accurate and one turning hard is not. No amount of
turning takes it past the ceiling you set. That is a player running out of desk.

Mouse Re-center Time is how long it takes to lift and reset, which is the other half of the same
idea.

**Optimal Aim FOV and the outer penalty shape where the bot is dangerous.** Inside that cone it aims
well, outside it the penalty multiplier degrades it.

That is the setting for a scenario about angles: stay outside its optimal cone and you are fighting
a worse opponent.

<figure class="aim-figure">
<!-- aim:figure aim-cone -->
<figcaption>The cone is where the bot aims well. Outside it, the penalty multiplier does the work for you.</figcaption>
</figure>

<figure class="aim-figure">
<!-- aim:figure aim-profile-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>

## Common mistakes

- Tuning an aim profile for a scenario whose bots never fire.[^REF-79]
- Leaving error at zero outside of testing, which makes an unbeatable opponent.
- Expecting this profile to change how a bot moves. Motion is a dodge profile.[^REF-83]

## In practice

**Skip it unless your scenario is a duel.** For a target you shoot and it does not shoot back, no
aim profile is needed at all.[^REF-79]

**Do this next.** If you are building a duel scenario, set reaction time and error first and leave
the rest alone. Those two decide how hard the opponent is.

## Resources

- [Aim Profiles](https://wiki.kovaaks.com/en/home/KovaaK's/ScenarioCreation/AimProfiles): the
  official page for this editor.
- [Bot Profile](bot-profile.md): where an aim profile gets attached.
