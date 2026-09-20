---
title: "Designing Target Motion"
description: >-
  How a target moves decides what a scenario trains. Choosing between a path you can learn and one
  you have to read.
tags:
  - tracking
  - switching
related:
  - page: wiki/making-scenarios/designing-around-a-weakness.md
    why: picking the demand this motion is supposed to create.
  - page: wiki/making-scenarios/kovaaks/where-settings-live.md
    why: the profile and tab each of these choices is set on.
  - page: wiki/categories/tracking.md
    why: the category motion design affects most.
---

!!! warning "Draft"
    Written from public sources, pending review.

Motion is the single biggest design decision in a scenario. Target size changes how hard a shot is.
Motion changes which skill the shot belongs to.

- **Readable and unreadable train different things.** Pick one on purpose.[^REF-15]
- **A learnable path becomes recall.** That is useful, and it is not reading.[^REF-15]
- **Mixed behavior costs comparability.** Weighted evenly, a run's difficulty is luck.[^REF-82]
- **Travel time is motion too.** A projectile has to be led. Hitscan does not.[^REF-86]

## Readable against unreadable

**A fixed path can be ridden.** Run the same route enough times and you stop reacting to it. You
recall it, and your crosshair leads the target because you know where it goes.

**A reacting target cannot be anticipated.** It answers your movement, so the only way through is
to read it as it happens.[^REF-15]

<figure class="aim-figure">
<!-- aim:figure reactive -->
<figcaption>The left path is a prediction you can ride. The right one is only a record of what
already happened.</figcaption>
</figure>

Both are worth training. The failure is building one and believing you built the other, which is
what happens when a path is nearly repeatable.

A half-predictable target teaches guessing. Guessing works until the pattern shifts, and then it
collapses all at once.[^REF-15]

## Deciding how much the target notices you

Whether a target reacts is a design choice with a setting behind it: Waypoint Logic decides how
much attention a bot pays to the route it was given.[^REF-91]

| If you want | Choose |
| --- | --- |
| A route the target repeats, ignoring you entirely | Seek Waypoint[^REF-91] |
| A route it abandons the moment it finds you | Seek Combat[^REF-91] |
| A route it walks while tracking you | Seek Target[^REF-91] |
| No route at all, just dodging | Ignore[^REF-91] |

<figure class="aim-figure">
<!-- aim:figure waypoints -->
<figcaption>The same three waypoints, two settings. One loops forever. The other abandons the route
on contact.</figcaption>
</figure>

Seek Waypoint is the setting for a repeatable tracking drill. Seek Combat turns the same map into a
scenario about the moment contact happens.

## Mixed behavior costs you comparability

**A bot can carry several dodge profiles, each with a weighting.**[^REF-82] That is how a target
mostly does one thing and occasionally does another.

Weight it heavily and runs stay comparable, because nearly every rep is the same rep. Weight it
evenly and which drill you got is decided after you pressed play.

<figure class="aim-figure">
<!-- aim:figure weights -->
<figcaption>Weighted hard one way, a run repeats. Weighted evenly, the difficulty of a run is
luck.</figcaption>
</figure>

Neither is wrong, but only one of them gives you a score you can read across sessions.

## Travel time is part of the motion

**A projectile weapon turns every shot into a lead.**[^REF-86] Where the target will be matters more
than where it is, and that is a different skill from putting a crosshair on a thing.

<figure class="aim-figure">
<!-- aim:figure travel -->
<figcaption>Down the sights of each. The projectile player's crosshair is not on the
target, and that is the point.</figcaption>
</figure>

Match this to the game you play. Training leads for a hitscan game adds a skill you never use.
Training hitscan for a projectile game leaves out the one that decides fights.

## Common mistakes

- Building a path you meant to be unpredictable, then learning it within a week.
- Stacking dodge profiles at similar weights and wondering why scores jump around.[^REF-82]
- Setting an elaborate route and leaving Waypoint Logic on Ignore, so nothing follows it.[^REF-91]
- Training projectile leads for a game where every gun is hitscan.[^REF-86]

## In practice

**Decide first whether the target should be readable.** A tracking drill usually wants a repeatable
path. A reaction drill wants one you cannot anticipate.

**Do this next.** Open a tracking scenario you play, find its dodge profile, and set Waypoint Logic
to Seek Waypoint so the target stops reacting to you.

## Resources

- [Tracking](../categories/tracking.md): the category motion design affects most.
- [KovaaK's](../resources/trainers/kovaaks.md): the trainer these settings belong to.
