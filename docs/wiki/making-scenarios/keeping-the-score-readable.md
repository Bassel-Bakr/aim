---
title: "Keeping the Score Readable"
description: >-
  Every source of randomness in a scenario you built adds noise to its score. What to strip out so a
  bad run means something.
tags:
  - routines
related:
  - page: wiki/making-scenarios/testing-and-iterating.md
    why: reading a score once the noise in it is under control.
  - page: wiki/making-scenarios/tuning-difficulty.md
    why: difficulty that is hard on purpose rather than hard by accident.
  - page: wiki/training/progress-and-plateaus.md
    why: what score movement looks like when nothing has actually changed.
---

!!! warning "Draft"
    Written from public sources, pending review.

A scenario you built is a measuring instrument. Every random element in it is noise on the reading,
and noise you added yourself is the kind you can remove.

- **Randomness hides what you did.** A score that moves on its own teaches nothing.
- **Weapons are the usual source.** Spread and recoil both have random forms.[^REF-86]
- **The score model is a second instrument.** What it counts is what you will practice.
- **Strip first, then judge.** Remove the noise before concluding anything about your aim.

## Noise you added by accident

**A random cone is noise, not difficulty.** Spread is the cone a shot may land in. Per bullet
spread is a fixed pattern instead.[^REF-86]

The difference decides whether a miss was yours. With a cone, two identical inputs give two
different outcomes, so a bad run may be the weapon rather than the aim.

<figure class="aim-figure">
<!-- aim:figure spread -->
<figcaption>Two volleys each. Spread lands somewhere new. Per bullet spread repeats itself exactly.</figcaption>
</figure>

**Recoil has the same split.** Recoil sets vertical and horizontal kick. Per shot recoil gives a
consistent, learnable pattern.[^REF-86]

A learnable pattern is a skill. A random one is a tax on every run, paid unevenly.

<figure class="aim-figure">
<!-- aim:figure recoil -->
<figcaption>Two bursts each. Only the per-shot pattern climbs the same way twice, which is what makes it learnable.</figcaption>
</figure>

## What to strip and what to keep

Anything not under test should be as quiet as it can be. That is not the same as making the drill
easy: the demand you built the scenario for stays exactly where it was.

| Source | Keep it when | Strip it when |
| --- | --- | --- |
| Weapon spread | The drill is about spray control | The drill is about where you pointed |
| Random recoil | Never, for a drill you score | Always, for a drill you score |
| Reactive bots | You are training reading | You are training a repeatable motion |
| Wide spawn scatter | Distance variation is the point | You are isolating one distance |
| Several dodge profiles | You want mixed behavior | You want comparable runs |

Strip in one pass, then leave the scenario alone. A measuring instrument you keep adjusting has no
history, and history is the only thing that makes a score mean anything.

## The score model counts too

**Whatever the scoring rewards is what you will practice.** A model that pays for hits and never
charges for misses trains volume. One that subtracts for misses trains restraint.

Neither is wrong. Inheriting one by accident from the scenario you copied is, because then the
drill is teaching something nobody chose.

<figure class="aim-figure">
<!-- aim:figure scoring -->
<figcaption>The same nine shots, scored two ways. The run did not change. What it was worth did.</figcaption>
</figure>

That is the speed-against-accuracy trade-off with a price attached. Push the pace and accuracy
falls. The score model decides whether that trade pays.[^REF-17]

## Common mistakes

- Reading a score from a scenario with random spread as a measure of aim.[^REF-86]
- Removing randomness and also removing the demand, leaving a drill that is merely easy.
- Keeping the copied scenario's scoring without checking what it pays for.
- Changing the noise and the difficulty in the same edit, so neither result is readable.

## In practice

**Ask what else could have moved that number.** If the answer is anything other than you, the
scenario is measuring two things.

**Do this next.** Open the weapon profile of a scenario you built and check for spread. If it has
any, make a copy without it and compare a session on each.

## Resources

- [How Aim Works](../fundamentals/how-aim-works.md): the trade-off a score model puts a price on.
- [Progress and Plateaus](../training/progress-and-plateaus.md): telling real movement from noise.
