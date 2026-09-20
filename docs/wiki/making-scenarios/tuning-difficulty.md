---
title: "Tuning Difficulty"
description: >-
  Which settings actually move a scenario's difficulty, how far to push them, and why harder is not
  the same as more useful.
tags:
  - routines
related:
  - page: wiki/making-scenarios/kovaaks/where-settings-live.md
    why: the tab that holds each setting named here.
  - page: wiki/fundamentals/how-aim-works.md
    why: the speed-accuracy trade-off behind every difficulty dial.
  - page: wiki/making-scenarios/designing-around-a-weakness.md
    why: deciding what the scenario should be hard at before making it hard.
---

!!! warning "Draft"
    Written from public sources, pending review.

Difficulty is not one slider. A scenario has several, they do different things, and turning them all
up produces a drill that teaches nothing.

- **Size and distance are the core pair.** Both follow the same trade-off.[^REF-27]
- **Speed buys itself with accuracy.** The exchange is measurable.[^REF-17]
- **Aim for hard, not survivable.** A run you barely survive gives no usable feedback.
- **Move one dial per version.** Two changes at once explain nothing.

## The dials, and what each one does

| Dial | Where it lives | What it changes |
| --- | --- | --- |
| Target size | Character profile, Boxes[^REF-81] | Precision demanded per shot |
| Spawn spread | Character profile, Spawn[^REF-81] | Distance between targets |
| Dodge speed | Dodge profile[^REF-83] | Correction rate demanded |
| Reactivity | Dodge profile, React[^REF-83] | Whether the path can be learned |
| Bot count | Edit Scenario, Challenge[^REF-80] | Target selection pressure |
| Time limit | Edit Scenario, Challenge[^REF-80] | Pace, and tolerance for a reset |

**Size and distance are one relationship, not two.** The time a movement takes grows with how far
it travels and how small the target is.[^REF-27]

That means shrinking a target and spreading spawns further apart push on the same thing. Doing both
at once doubles a change you may have meant to make once.

<figure class="aim-figure">
<!-- aim:figure spawns -->
<figcaption>Offsets at zero stack every target on the marker. Widened, the same marker covers an area.</figcaption>
</figure>

<figure class="aim-figure">
<!-- aim:figure dials -->
<figcaption>Two different settings, one raised demand. Change both and you have moved difficulty
twice.</figcaption>
</figure>

## Pushing speed

**Speed and accuracy trade against each other.** The exchange is measurable rather than a matter of
discipline, so a speed increase has a predictable accuracy cost.[^REF-17]

<figure class="aim-figure">
<!-- aim:figure tradeoff -->
<figcaption>Pace is cheap until it is not. The band is where accuracy is still worth building.</figcaption>
</figure>

Build accuracy at a pace you can hit, then raise speed. Chasing speed before accuracy is solid
builds habits that are harder to undo than they were to avoid.[^REF-17]

**Slower variants are not a waste of a session.** Running a scenario at a pace where the crosshair
lands cleanly builds the technique that survives when difficulty goes back up.[^REF-17]

<figure class="aim-figure">
<!-- aim:figure slower -->
<figcaption>Same distance, two paces. One lands. The other overshoots and saws back onto the target.</figcaption>
</figure>

## How hard is hard enough

**A scenario should be uncomfortable and readable at once.** If every run is noise, nothing in the
score tells you what to fix next time.

Practice that works gets harder as you improve, rather than starting at the ceiling.[^REF-36] A
drill pinned above your level has nowhere left to go.

**Skill level changes what difficulty should do.** Early on, a learner needs conditions that let the
movement come together at all. Later, the useful work is at the edge.[^REF-28]

<figure class="aim-figure">
<!-- aim:figure stage -->
<figcaption>The useful band moves along the scale as the skill becomes yours.</figcaption>
</figure>

<figure class="aim-figure">
<!-- aim:figure health -->
<figcaption>Health is the dial that changes the question, not just the answer: acquire once, or acquire and stay.</figcaption>
</figure>

## Change one thing

**Keep the version you started from.** Two scenarios differing in one setting tell you what that
setting does. Two differing in five tell you nothing.

<figure class="aim-figure">
<!-- aim:figure versions -->
<figcaption>One dial moved is an experiment. Five moved is a new scenario with no explanation.</figcaption>
</figure>

Name versions so the difference is visible without opening them. A name carrying the changed dial
and its value beats a version number.

## Common mistakes

- Raising size, speed and spread together, then wondering which one broke the drill.
- Building at your ceiling, where every run is noise.
- Treating a slow variant as a wasted session.[^REF-17]
- Judging a change on one run. A single day's result moves too much to prove
  anything.[^REF-29]

## In practice

**Tune until the failure is specific.** A good difficulty setting makes you fail in one identifiable
way, not in a general blur.

**Do this next.** Take a scenario you made, copy it, change one dial by a small step, and play both
in the same session.

## Resources

- [How Aim Works](../fundamentals/how-aim-works.md): the trade-off every dial here sits on.
- [Progress and Plateaus](../training/progress-and-plateaus.md): judging a change across runs.
