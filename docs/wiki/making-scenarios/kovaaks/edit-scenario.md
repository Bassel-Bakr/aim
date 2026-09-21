---
title: "Scenario Editor"
description: >-
  The five tabs of the KovaaK's Edit Scenario window: what unpacking does, the challenge rules, the
  scoring model, and the tags that make a scenario findable.
tags:
  - routines
related:
  - page: wiki/making-scenarios/kovaaks/making-a-scenario.md
    why: the build these tabs sit at the top of.
  - page: wiki/making-scenarios/keeping-the-score-readable.md
    why: what the Scoring tab decides your drill is rewarding.
  - page: wiki/making-scenarios/kovaaks/where-settings-live.md
    why: the shorter lookup this page is the long form of.
---

# Scenario Editor

!!! warning "Draft"
    Written from public sources, pending review.

!!! note "Read from the editor"
    Field names, tooltip text and defaults here were read from the KovaaK's scenario editor in
    September 2026. The official wiki documents tabs rather than fields.

Profiles describe the pieces. This window describes the match: which pieces play, what the rules
are, how a run becomes a number, and whether anyone can find it.

- **Challenge is a separate list.** Profiles on Main do not reach it alone.[^REF-80][^REF-85]
- **Scoring is a training instruction.** Whatever it pays for is what you practice.
- **Two fields end a run.** Time limit, or a kill count.
- **Tags decide whether it exists.** Search runs on them.[^REF-80]

## Tabs

### Main

Scenario name, and the lists of player characters and bots in use.[^REF-80] Each list has
an Add Profile button, and each entry can be removed.

This tab is the inventory, not the rules. Adding a profile here makes it available. It does not put
it into a challenge run.[^REF-85]

<figure class="aim-figure">
<!-- aim:figure scenario-main-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>

### Unpack

Extracts the original profiles out of the scenario.[^REF-80] Worth knowing twice over: for undoing
changes to a profile, and for unpacking selectively rather than everything.

<figure class="aim-figure">
<!-- aim:figure scenario-unpack-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>

### Challenge

Map scale and time scale. Target speed and target size, each with a static or adapt
mode.[^REF-33][^REF-80]

Then the end conditions. Time limit, time regained per kill, end after a number of kills, and end
after a damage amount.

**They are a race, not a menu.** Set more than one and the run stops at whichever fires first.
That is an easy way to build a scenario that never reaches its time limit.

<figure class="aim-figure">
<!-- aim:figure end-conditions -->
<figcaption>Set three end conditions and the run obeys whichever arrives first.</figcaption>
</figure>

**Time Regained per Kill stops the clock being fixed.** A run that goes well lasts longer than one
that does not, so two scores were not measured over the same amount of time.

<figure class="aim-figure">
<!-- aim:figure time-regained -->
<figcaption>Regained time makes a good run longer, so two scores no longer share a clock.</figcaption>
</figure>

For a drill you compare across sessions, leave it at zero and let the time limit be the time limit.

Then lock hipfire FOV with a locked FOV range, and a force particle effects switch.

**Lock Hipfire FOV makes the scenario the same for everyone.** A target's angular size depends on
the field of view you see it at. Unclamped, your scenario is a slightly different drill for every
reader who plays it.

<figure class="aim-figure">
<!-- aim:figure lock-fov -->
<figcaption>Angular size follows field of view. Unclamped, your scenario is not quite the one they play.</figcaption>
</figure>

That matters most for a scenario you intend to share. A score should mean the same thing on
someone else's machine as on yours.

A disable block closes the tab: projectile predictors, cheats, health bars, hit markers and hit
sounds.

**Static against adapt is the interesting pair.** Static holds target speed and size where you set
them. Adapt moves them with your performance.

An adapting scenario is harder to read across sessions, because the difficulty is no longer a
constant you control. For a drill you want to compare, use static.

<figure class="aim-figure">
<!-- aim:figure adapt -->
<figcaption>The same nine runs. Against a fixed bar the rise is improvement. Against a rising one it says much less.</figcaption>
</figure>

**The disable switches are about feedback.** Turning off hit markers and hit sounds removes the
confirmation you normally get, which makes a drill closer to a game and harder to read.

<figure class="aim-figure">
<!-- aim:figure feedback -->
<figcaption>The same shot with and without confirmation. One of them you can learn from.</figcaption>
</figure>

Health bars and projectile predictors go the same way. Each one you disable moves the scenario
toward a game and away from a measurement.

Keep them on while you are learning a drill, and turn them off only when the point is to practice
without the crutch.

Disabling cheats here is what stops a weapon's Cheat tab applying in a scored run.[^REF-86]

**Time Limit sets the run length.** Sixty seconds is the common default, and a length you repeat is
worth more than a length you optimize.

<figure class="aim-figure">
<!-- aim:figure scenario-challenge-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>

### Scoring

Score to win. Then a score-per block: damage, hit, an over-damage switch, kill, midair direct, any
direct, time left and distance traveled.

A movement-based scoring block follows, with its own enable switch. Then a score-loss-per block:
damage taken, death, and more.

Final score multipliers close the tab, including accuracy, square root accuracy, damage efficiency
and kill efficiency.

**Whatever this tab rewards is what you will practice.** A model paying only for hits trains volume.
One that subtracts for misses trains restraint.

Neither is wrong. Inheriting one by accident from the scenario you copied is, because then the drill
teaches something nobody chose.

**Square root accuracy is the subtle one.** It reduces how much accuracy swings the final score, so
a run is judged more on what you did and less on one bad stretch.

**The multipliers stack, and two of them overlap.** They apply to the subtotal the rest of the tab
produces.

The editor recommends not checking both Accuracy and Damage Efficiency, because the same misses are
then charged for twice.

<figure class="aim-figure">
<!-- aim:figure multipliers -->
<figcaption>Accuracy and damage efficiency both punish misses. Checking both charges you twice.</figcaption>
</figure>

Enable Over Damage decides whether damage past what was needed to kill still counts toward the
score.

<figure class="aim-figure">
<!-- aim:figure scenario-scoring-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>

### Tags

Tags, a difficulty rating, a description, an aim type and an aim sub type, a flicking switch, and a
thumbnail.[^REF-80]

**Aim Type and Aim Sub Type are how a drill is found.** They feed the browser's filters, so a
scenario tagged by the skill it trains reaches the person looking for that skill.

Write the description as the weakness it isolates, not as what it looks like. A reader hunting for a
drill is searching by what it fixes.

<figure class="aim-figure">
<!-- aim:figure scenario-tags-fields -->
<figcaption>Every option on this tab, with a low and a high state side by side.</figcaption>
</figure>

## Common mistakes

- Adding a profile on Main and testing in challenge mode, where nothing changed.[^REF-80][^REF-85]
- Leaving target speed or size on adapt in a scenario you want to compare across sessions.
- Keeping the copied scenario's scoring without checking what it pays for.
- Leaving Tags empty, which makes the scenario unsearchable.[^REF-80]

## In practice

**Set the rules before the scoring.** Decide how a run ends, then decide what it was worth. Doing it
the other way round produces a model that rewards the wrong thing.

**Do this next.** Open the Scoring tab of a scenario you play and find what it pays for. That is
what you have been practicing, whether or not you meant to.

## Resources

- [Edit Scenario Window](https://wiki.kovaaks.com/en/home/KovaaK's/ScenarioCreation/EditScenario):
  the official page for this window.
- [Keeping the Score Readable](../keeping-the-score-readable.md): choosing a scoring model on purpose.
