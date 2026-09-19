---
title: "Making Your Own Scenario"
description: >-
  The decisions behind a custom scenario: what it should demand, what to leave alone, and how to
  know when it is finished.
tags:
  - beginner
  - routines
related:
  - page: wiki/scenarios/designing-around-a-weakness.md
    why: choosing the demand before anything else.
  - page: wiki/scenarios/where-settings-live.md
    why: the tab that holds each decision made here.
  - page: wiki/scenarios/testing-and-iterating.md
    why: checking the finished scenario trains what you meant.
  - page: wiki/training/routines.md
    why: where a scenario you made fits into a week of practice.
  - page: wiki/resources/trainers/kovaaks.md
    why: the trainer whose editor this describes.
---

!!! warning "Draft"
    Written from public sources, pending review.

Making a scenario is four decisions and a lot of looking things up. This page is the decisions. The
lookups are on [Where Each Setting Lives](where-settings-live.md), and the field detail is in the
official documentation.[^REF-79]

- **You are editing, not authoring.** Every scenario starts as a copy.[^REF-79][^REF-85]
- **Pick the donor for its shape.** Closest beats most popular.[^REF-85]
- **Decide the demand before the settings.** Otherwise you tune toward nothing.
- **Change one thing.** A version that differs in five ways explains none of them.

## You are always starting from someone else's scenario

**There is no blank scenario.** You download one, unpack it into its profiles, and replace the parts
that matter.[^REF-79][^REF-85]

That makes the first decision a choice of donor. Pick the scenario whose shape is closest to what
you want, not the one you have heard of. A donor that already moves targets the way you need saves
you the hardest edit.

<figure class="aim-figure">
<svg viewBox="0 0 760 300" class="fig-fit" role="img" aria-labelledby="fig-profiles-title"><title id="fig-profiles-title">A scenario holds the challenge rules, the scoring and the tags, and links to a player character and a bot. The bot links to its own character profile, which carries target size, health and spawn, and optionally to a dodge profile, which carries how the target moves.</title><metadata><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#"><cc:Work rdf:about=""><dc:creator>Bassel Bakr</dc:creator><dc:source>https://github.com/Bassel-Bakr/aim</dc:source><cc:license rdf:resource="https://creativecommons.org/licenses/by-sa/4.0/"/></cc:Work></rdf:RDF></metadata><style>@keyframes aimProfIn{0%{opacity:0}5%{opacity:1}100%{opacity:1}}.aim-prof-in{opacity:0;animation-name:aimProfIn;animation-iteration-count:infinite;animation-duration:5.0s}@media (prefers-reduced-motion:reduce){.aim-prof-in{opacity:1;animation:none!important}}</style><defs><marker id="fig-scn-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 Z" class="fig-grid-fill"/></marker></defs><g class="aim-prof-in" style="animation-delay:1.00s"><path d="M380.0 72V91.0H175.0V110" class="fig-grid-stroke" stroke-width="2" fill="none" marker-end="url(#fig-scn-arrow)"/></g><g class="aim-prof-in" style="animation-delay:1.00s"><path d="M380.0 72V91.0H585.0V110" class="fig-grid-stroke" stroke-width="2" fill="none" marker-end="url(#fig-scn-arrow)"/></g><g class="aim-prof-in" style="animation-delay:2.00s"><path d="M585.0 168V188.0H475.0V208" class="fig-grid-stroke" stroke-width="2" fill="none" marker-end="url(#fig-scn-arrow)"/></g><g class="aim-prof-in" style="animation-delay:2.00s"><path d="M585.0 168V188.0H665.0V208" class="fig-grid-stroke" stroke-width="2" fill="none" marker-end="url(#fig-scn-arrow)"/></g><g class="aim-prof-in" style="animation-delay:0.00s"><rect x="300" y="20" width="160" height="52" rx="10" class="fig-panel fig-ink-stroke" stroke-width="2"/><text x="380.0" y="42" class="fig-ink" text-anchor="middle" font-size="16" font-weight="700">Scenario</text><text x="380.0" y="62" class="fig-muted" text-anchor="middle" font-size="13" font-weight="500">Challenge · Scoring · Tags</text></g><g class="aim-prof-in" style="animation-delay:1.00s"><rect x="70" y="110" width="210" height="58" rx="10" class="fig-panel fig-ink-stroke" stroke-width="2"/><text x="175.0" y="132" class="fig-ink" text-anchor="middle" font-size="16" font-weight="700">Player character</text><text x="175.0" y="152" class="fig-muted" text-anchor="middle" font-size="13" font-weight="500">your hitboxes and weapons</text></g><g class="aim-prof-in" style="animation-delay:1.00s"><rect x="480" y="110" width="210" height="58" rx="10" class="fig-panel fig-ink-stroke" stroke-width="2"/><text x="585.0" y="132" class="fig-ink" text-anchor="middle" font-size="16" font-weight="700">Bot</text><text x="585.0" y="152" class="fig-muted" text-anchor="middle" font-size="13" font-weight="500">which character, which dodge</text></g><g class="aim-prof-in" style="animation-delay:2.00s"><rect x="380" y="208" width="190" height="58" rx="10" class="fig-panel fig-ink-stroke" stroke-width="2"/><text x="475.0" y="230" class="fig-ink" text-anchor="middle" font-size="16" font-weight="700">Bot character</text><text x="475.0" y="250" class="fig-muted" text-anchor="middle" font-size="13" font-weight="500">size · health · spawn</text></g><g class="aim-prof-in" style="animation-delay:2.00s"><rect x="590" y="208" width="150" height="58" rx="10" class="fig-panel fig-grid-stroke" stroke-width="2" stroke-dasharray="6 5"/><text x="665.0" y="230" class="fig-muted" text-anchor="middle" font-size="16" font-weight="700">Dodge profile</text><text x="665.0" y="250" class="fig-muted" text-anchor="middle" font-size="13" font-weight="500">how the target moves</text></g><rect x="70" y="278" width="26" height="3" rx="1.5" class="fig-ink-fill"/><text x="106" y="280" class="fig-muted" text-anchor="start" font-size="13" font-weight="500" dominant-baseline="central">required</text><rect x="210" y="278" width="26" height="3" rx="1.5" class="fig-grid-fill"/><text x="246" y="280" class="fig-muted" text-anchor="start" font-size="13" font-weight="500" dominant-baseline="central">optional</text></svg>
<figcaption>What a scenario is made of, and which profile holds each decision.</figcaption>
</figure>

Unpacking writes the scenario's profiles to your machine as separate files, which is why a scenario
is several things rather than one.[^REF-79]

## Four decisions

**What should be hard?** One demand, named in a sentence. If you cannot write the sentence, the
design is not finished, and no amount of editing will finish it.

**How hard?** Hard enough that you fail in one identifiable way. A run that fails for reasons you
cannot name is not measuring anything.

**What should be quiet?** Everything not under test. Random spread, a reacting bot and a cramped map
all add movement to the score that did not come from you.

**How will you know it worked?** Decide the comparison before you build. Usually that is a scenario
you already play, run in the same session.

<figure class="aim-figure">
<svg viewBox="0 0 760 300" class="fig-fit" role="img" aria-labelledby="fig-decisions-title"><title id="fig-decisions-title">Four numbered questions appearing one after another: what should be hard, how hard, what should be quiet, and how will you know it worked. Each carries a one-line note on what answering it means.</title><metadata><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#"><cc:Work rdf:about=""><dc:creator>Bassel Bakr</dc:creator><dc:source>https://github.com/Bassel-Bakr/aim</dc:source><cc:license rdf:resource="https://creativecommons.org/licenses/by-sa/4.0/"/></cc:Work></rdf:RDF></metadata><style>@keyframes aimDecIn{0%{opacity:0;transform:translateX(-10px)}7%{opacity:1;transform:translateX(0)}100%{opacity:1;transform:translateX(0)}}.aim-dec-row{opacity:0;animation-name:aimDecIn;animation-iteration-count:infinite;animation-duration:6.4s}@media (prefers-reduced-motion:reduce){.aim-dec-row{opacity:1;animation:none!important;transform:none!important}}</style><rect x="12" y="46" width="736" height="230" rx="12" class="fig-panel"/><text x="32" y="30"><tspan font-size="16" font-weight="700" class="fig-ink fig-name">Before the editor opens</tspan><tspan dx="10" font-size="13" font-weight="500" class="fig-muted fig-note">four answers, in this order</tspan></text><g class="aim-dec-row" style="animation-delay:0.00s"><circle cx="64" cy="101" r="13" class="fig-accent-stroke" stroke-width="2" fill="none"/><text x="64" y="102" class="fig-accent-text" text-anchor="middle" font-size="12" font-weight="700" dominant-baseline="central">1</text><text x="92" y="96" class="fig-ink" text-anchor="start" font-size="15" font-weight="700">What should be hard?</text><text x="92" y="116" class="fig-muted" text-anchor="start" font-size="12" font-weight="500">one demand, in a sentence</text></g><g class="aim-dec-row" style="animation-delay:0.90s"><circle cx="64" cy="151" r="13" class="fig-accent-stroke" stroke-width="2" fill="none"/><text x="64" y="152" class="fig-accent-text" text-anchor="middle" font-size="12" font-weight="700" dominant-baseline="central">2</text><text x="92" y="146" class="fig-ink" text-anchor="start" font-size="15" font-weight="700">How hard?</text><text x="92" y="166" class="fig-muted" text-anchor="start" font-size="12" font-weight="500">you fail in one nameable way</text></g><g class="aim-dec-row" style="animation-delay:1.79s"><circle cx="64" cy="201" r="13" class="fig-accent-stroke" stroke-width="2" fill="none"/><text x="64" y="202" class="fig-accent-text" text-anchor="middle" font-size="12" font-weight="700" dominant-baseline="central">3</text><text x="92" y="196" class="fig-ink" text-anchor="start" font-size="15" font-weight="700">What should be quiet?</text><text x="92" y="216" class="fig-muted" text-anchor="start" font-size="12" font-weight="500">everything not under test</text></g><g class="aim-dec-row" style="animation-delay:2.69s"><circle cx="64" cy="251" r="13" class="fig-accent-stroke" stroke-width="2" fill="none"/><text x="64" y="252" class="fig-accent-text" text-anchor="middle" font-size="12" font-weight="700" dominant-baseline="central">4</text><text x="92" y="246" class="fig-ink" text-anchor="start" font-size="15" font-weight="700">How will you know?</text><text x="92" y="266" class="fig-muted" text-anchor="start" font-size="12" font-weight="500">the scenario you compare against</text></g></svg>
<figcaption>Four answers, in this order. Each one is only answerable once the one above it is settled.</figcaption>
</figure>

<figure class="aim-figure">
<svg viewBox="0 0 760 330" class="fig-fit" role="img" aria-labelledby="fig-spawn-title"><title id="fig-spawn-title">Two panels showing the same scenario under different settings. On the left a narrow spawn box and a slow dodge keep the target near the crosshair, so the run asks for small corrections. On the right a much wider spawn box and a faster dodge carry the target far past the crosshair, so the run asks for large repositioning.</title><metadata><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#"><cc:Work rdf:about=""><dc:creator>Bassel Bakr</dc:creator><dc:source>https://github.com/Bassel-Bakr/aim</dc:source><cc:license rdf:resource="https://creativecommons.org/licenses/by-sa/4.0/"/></cc:Work></rdf:RDF></metadata><style>@keyframes aimScnStrafe0{0%{transform:translate(-48.0px,0)}20%{transform:translate(-48.0px,0)}22.5%{transform:translate(-47.9px,0)}25%{transform:translate(-44.9px,0)}27.5%{transform:translate(-38.3px,0)}30%{transform:translate(-29.0px,0)}32.5%{transform:translate(-17.6px,0)}35%{transform:translate(-5.1px,0)}37.5%{transform:translate(7.7px,0)}40%{transform:translate(20.0px,0)}42.5%{transform:translate(31.0px,0)}45%{transform:translate(39.9px,0)}47.5%{transform:translate(45.8px,0)}50%{transform:translate(48.0px,0)}70%{transform:translate(48.0px,0)}72.5%{transform:translate(47.9px,0)}75%{transform:translate(44.9px,0)}77.5%{transform:translate(38.3px,0)}80%{transform:translate(29.0px,0)}82.5%{transform:translate(17.6px,0)}85%{transform:translate(5.1px,0)}87.5%{transform:translate(-7.7px,0)}90%{transform:translate(-20.0px,0)}92.5%{transform:translate(-31.0px,0)}95%{transform:translate(-39.9px,0)}97.5%{transform:translate(-45.8px,0)}100%{transform:translate(-48.0px,0)}}.aim-scn-anim0{animation-name:aimScnStrafe0;animation-duration:4.0s}@keyframes aimScnStrafe1{0%{transform:translate(-150.0px,0)}5%{transform:translate(-150.0px,0)}7.5%{transform:translate(-149.0px,0)}10%{transform:translate(-143.0px,0)}12.5%{transform:translate(-132.3px,0)}15%{transform:translate(-117.5px,0)}17.5%{transform:translate(-99.2px,0)}20%{transform:translate(-78.2px,0)}22.5%{transform:translate(-55.1px,0)}25%{transform:translate(-30.5px,0)}27.5%{transform:translate(-5.1px,0)}30%{transform:translate(20.4px,0)}32.5%{transform:translate(45.4px,0)}35%{transform:translate(69.2px,0)}37.5%{transform:translate(91.1px,0)}40%{transform:translate(110.6px,0)}42.5%{transform:translate(126.8px,0)}45%{transform:translate(139.3px,0)}47.5%{transform:translate(147.2px,0)}50%{transform:translate(150.0px,0)}55%{transform:translate(150.0px,0)}57.5%{transform:translate(149.0px,0)}60%{transform:translate(143.0px,0)}62.5%{transform:translate(132.3px,0)}65%{transform:translate(117.5px,0)}67.5%{transform:translate(99.2px,0)}70%{transform:translate(78.2px,0)}72.5%{transform:translate(55.1px,0)}75%{transform:translate(30.5px,0)}77.5%{transform:translate(5.1px,0)}80%{transform:translate(-20.4px,0)}82.5%{transform:translate(-45.4px,0)}85%{transform:translate(-69.2px,0)}87.5%{transform:translate(-91.1px,0)}90%{transform:translate(-110.6px,0)}92.5%{transform:translate(-126.8px,0)}95%{transform:translate(-139.3px,0)}97.5%{transform:translate(-147.2px,0)}100%{transform:translate(-150.0px,0)}}.aim-scn-anim1{animation-name:aimScnStrafe1;animation-duration:2.0s}.aim-scn-anim{animation-timing-function:linear;animation-iteration-count:infinite}@media (prefers-reduced-motion:reduce){.aim-scn-anim{animation-play-state:paused}.aim-scn-anim0{animation-delay:-0.40s!important}.aim-scn-anim1{animation-delay:-1.00s!important}}</style><rect x="12" y="46" width="356" height="270" rx="12" class="fig-panel"/><text x="32" y="30"><tspan font-size="16" font-weight="700" class="fig-ink fig-name">Narrow spawn, slow dodge</tspan><tspan dx="10" font-size="13" font-weight="500" class="fig-muted fig-note">small corrections</tspan></text><rect x="120" y="134" width="140" height="104" rx="8" class="fig-grid-stroke" stroke-width="2" stroke-dasharray="7 6" fill="none"/><text x="190" y="262" class="fig-muted" text-anchor="middle" font-size="13" font-weight="500">Spawn Offset Min and Max</text><path d="M142 186H238" class="fig-grid-stroke" stroke-width="2" stroke-linecap="round" opacity="0.7"/><text x="190" y="118" class="fig-muted" text-anchor="middle" font-size="13" font-weight="500">Dodge profile</text><g class="aim-scn-anim aim-scn-anim0"><circle cx="190" cy="186" r="14" class="fig-target"/></g><circle cx="190" cy="186" r="8" class="fig-ink-stroke" stroke-width="2.2" fill="none"/><path d="M177 186H186M194 186H203M190 173V182M190 190V199" class="fig-ink-stroke" stroke-width="2.2"/><rect x="392" y="46" width="356" height="270" rx="12" class="fig-panel"/><text x="412" y="30"><tspan font-size="16" font-weight="700" class="fig-ink fig-name">Wide spawn, fast dodge</tspan><tspan dx="10" font-size="13" font-weight="500" class="fig-muted fig-note">large repositioning</tspan></text><rect x="398" y="134" width="344" height="104" rx="8" class="fig-grid-stroke" stroke-width="2" stroke-dasharray="7 6" fill="none"/><text x="570" y="262" class="fig-muted" text-anchor="middle" font-size="13" font-weight="500">Spawn Offset Min and Max</text><path d="M420 186H720" class="fig-grid-stroke" stroke-width="2" stroke-linecap="round" opacity="0.7"/><text x="570" y="118" class="fig-muted" text-anchor="middle" font-size="13" font-weight="500">Dodge profile</text><g class="aim-scn-anim aim-scn-anim1"><circle cx="570" cy="186" r="14" class="fig-target"/></g><circle cx="570" cy="186" r="8" class="fig-ink-stroke" stroke-width="2.2" fill="none"/><path d="M557 186H566M574 186H583M570 173V182M570 190V199" class="fig-ink-stroke" stroke-width="2.2"/></svg>
<figcaption>Two settings, one scenario. Spawn spread and dodge speed set what the run demands.</figcaption>
</figure>

## Then do the edit

The mechanics are short, and the official pages carry them in full.[^REF-79][^REF-85] The shape:
download a close scenario, edit it, unpack. Change the profiles holding your demand. Name it on the
Main and Challenge tabs, tag it, and save under a new name.

Two things reliably waste an afternoon. Profiles named only on Main never reach challenge
mode.[^REF-80][^REF-85] Changes made in the Session Manager are never saved.[^REF-84]

You do not have to save to test. With the editor open, Play applies profile changes
immediately.[^REF-79]

## Common mistakes

- Opening the editor before you can say what the scenario should be hard at.
- Picking a famous donor rather than a close one.[^REF-85]
- Changing the demand and the noise in one edit, so the result explains nothing.
- Keeping a scenario after the weakness it was built for stopped being your weakness.

## In practice

**Build in one session, train in the next.** A scenario you keep editing has no history, and
history is what turns a score into information.

**Do this next.** Write one sentence naming what your scenario should be hard at, then find the
existing scenario closest to it.

## Resources

- [Where Each Setting Lives](where-settings-live.md): the lookup table for every decision above.
- [KovaaK's](../resources/trainers/kovaaks.md): the trainer, and its own documentation.
