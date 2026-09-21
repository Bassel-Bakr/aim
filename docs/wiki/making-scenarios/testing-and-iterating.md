---
title: "Testing a Scenario"
description: >-
  How to tell whether a scenario you built trains what you meant, using a known scenario as a
  reference and changing one thing at a time.
tags:
  - routines
related:
  - page: wiki/making-scenarios/tuning-difficulty.md
    why: the dials you move between one test and the next.
  - page: wiki/training/progress-and-plateaus.md
    why: reading a trend rather than a single run.
  - page: wiki/making-scenarios/kovaaks/making-a-scenario.md
    why: the build this testing loop follows.
---

!!! warning "Draft"
    Written from public sources, pending review.

A new scenario has no leaderboard, no benchmark and no history. Your score on it means nothing until
you give it something to mean something against.

- **Test without saving.** Profile changes apply from the pause menu.[^REF-79]
- **Session Manager is a sandbox.** Nothing you set there survives a save.[^REF-84]
- **Anchor to a scenario you know.** A familiar drill in the same session is your reference.
- **One run proves nothing.** Two or three reps give a fuller read.[^REF-8]

## The fast loop

**You do not have to save to test.** With the scenario editor open, clicking Play on the pause menu
applies profile changes immediately.[^REF-79]

That makes the edit-and-play loop short enough to tune by feel. Save once the version is worth
keeping, not after every change.

**The Session Manager is for the test run only.** It swaps the player character, adds or removes
bots, changes bot profiles, sets teams and toggles invincibility. It also changes the map, the map
scale and the time scale.[^REF-84]

None of it is saved into the scenario. To make a change stick, set it in the scenario editor's
Challenge tab instead.[^REF-84]

<figure class="aim-figure">
<!-- aim:figure test-loop -->
<figcaption>Both loops feel the same while you are in them. Only one of them survives the save.</figcaption>
</figure>

Time scale is the most useful of these for design work. Slowing a scenario down shows you what the
motion actually does, without rebuilding it slower.

## Give the score a reference

**Play a scenario you already know in the same session.** Your own score history on a familiar drill
tells you what kind of day you are having, which a new scenario cannot.

<figure class="aim-figure">
<!-- aim:figure anchor -->
<figcaption>The known scenario is the reading. Without it a bad first session on a new drill means nothing.</figcaption>
</figure>

Without that anchor, a bad first session on a new scenario is unreadable. It could be the design, or
it could be you.

**A single run does not settle anything.** Two or three reps give a fuller read than one.[^REF-8]
Scores also move from day to day.[^REF-9]

<figure class="aim-figure">
<!-- aim:figure noise -->
<figcaption>Any two neighbouring runs disagree. The trend only exists once all of them are on screen.</figcaption>
</figure>

## Ask what the run actually demanded

**Watch a run back, or check the stats.** Closing a session by looking at what happened turns
repetitions into feedback you can act on.[^REF-51]

For a scenario you built, the question is narrower than usual: did you fail in the way the design
intended? Failing for some other reason means the drill is measuring something else.

**A drill that is comfortable immediately is usually mis-set.** Either the difficulty is too low, or
a shortcut exists and you have already found it.

<figure class="aim-figure">
<!-- aim:figure comfortable -->
<figcaption>Nine clean reps is not a drill working. It is a drill asking nothing, one way or the other.</figcaption>
</figure>

## When to stop changing it

**Freeze the scenario once it reads clearly.** A drill you keep editing has no history, so it can
never show improvement.

<figure class="aim-figure">
<!-- aim:figure freeze -->
<figcaption>Every edit restarts the history. Three short climbs are not a trend.</figcaption>
</figure>

Retire it when the weakness it was built for stops being your weakness, rather than when you get
bored. A scenario played into the ground measures the scenario.

## Common mistakes

- Saving after every small change, which fills your list with near-identical scenarios.
- Tuning in the Session Manager, then saving and losing the change.[^REF-84]
- Judging a new scenario on its first session, with nothing to compare against.
- Editing a scenario you also train on, so its score history means nothing.

## In practice

**Separate the building session from the training session.** Build and tune in one sitting, then
leave the scenario alone and train on it in the next.

**Do this next.** Take a scenario you built, play it in the same session as one you know well, and
write down both scores before you change anything.

## Resources

- [Progress and Plateaus](../training/progress-and-plateaus.md): what a trend looks like against
  noise.
- [Routines](../training/routines.md): fitting a scenario you built into a session.
