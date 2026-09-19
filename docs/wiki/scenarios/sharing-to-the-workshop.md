---
title: "Sharing to the Workshop"
description: >-
  What makes a custom scenario worth publishing, and the two facts about workshop uploads that
  surprise people afterwards.
tags:
  - routines
related:
  - page: wiki/scenarios/making-a-scenario.md
    why: the scenario this publishes, and the unique name it needs.
  - page: wiki/scenarios/testing-and-iterating.md
    why: proving the scenario is worth publishing before you publish it.
  - page: wiki/scenarios/where-settings-live.md
    why: the Tags tab that decides whether anyone finds the upload.
---

!!! warning "Draft"
    Written from public sources, pending review.

Uploading is a button. Deciding what deserves uploading is not, and the workshop has an explicit
rule about the difference.

- **A rename is not a contribution.** Low-effort copies are removed.[^REF-85]
- **Publish what you already train on.** Not what you made and never played.
- **Tags decide whether it exists.** An untagged scenario is unfindable.[^REF-80]
- **Edits do not travel.** A local change reaches nobody until you upload again.[^REF-85]

## What is worth publishing

**Low-effort content is removed.** A copy of an existing scenario with nothing changed but the name
is explicitly listed as grounds for removal, and repeat offenders lose upload access.[^REF-85]

<figure class="aim-figure">
<svg viewBox="0 0 760 290" class="fig-fit" role="img" aria-labelledby="fig-loweffort-title"><title id="fig-loweffort-title">Two uploads of the same original scenario. The one that changed only the title is marked removed. The one that added a demand the original lacked is marked as staying.</title><metadata><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#"><cc:Work rdf:about=""><dc:creator>Bassel Bakr</dc:creator><dc:source>https://github.com/Bassel-Bakr/aim</dc:source><cc:license rdf:resource="https://creativecommons.org/licenses/by-sa/4.0/"/></cc:Work></rdf:RDF></metadata><style>@keyframes aimLowIn{0%{opacity:0}6%{opacity:1}100%{opacity:1}}.aim-low-in{opacity:0;animation-name:aimLowIn;animation-iteration-count:infinite;animation-duration:6.0s}@keyframes aimLowVerdict{0%{opacity:0}46%{opacity:0}54%{opacity:1}100%{opacity:1}}.aim-low-verdict{opacity:0;animation-name:aimLowVerdict;animation-iteration-count:infinite;animation-duration:6.0s}@media (prefers-reduced-motion:reduce){.aim-low-in,.aim-low-verdict{opacity:1;animation:none!important}}</style><rect x="12" y="46" width="356" height="218" rx="12" class="fig-panel"/><text x="32" y="30"><tspan font-size="16" font-weight="700" class="fig-ink fig-name">Renamed only</tspan></text><g class="aim-low-in" style="animation-delay:0.00s"><rect x="40" y="88" width="300" height="48" rx="9" class="fig-panel fig-grid-stroke" stroke-width="2"/><text x="190" y="108" class="fig-muted" text-anchor="middle" font-size="12" font-weight="600">the original</text><text x="190" y="126" class="fig-muted" text-anchor="middle" font-size="11" font-weight="500">someone else's work</text></g><g class="aim-low-in" style="animation-delay:0.50s"><rect x="40" y="150" width="300" height="48" rx="9" class="fig-panel fig-grid-stroke" stroke-width="2"/><text x="190" y="170" class="fig-muted" text-anchor="middle" font-size="12" font-weight="600">your upload</text><text x="190" y="188" class="fig-muted" text-anchor="middle" font-size="11" font-weight="500">nothing but the title</text></g><g class="aim-low-verdict"><rect x="120" y="218" width="140" height="36" rx="9" class="fig-panel fig-tense-stroke" stroke-width="2"/><text x="190" y="236" class="fig-tense-fill" text-anchor="middle" font-size="14" font-weight="700" dominant-baseline="central">removed</text></g><rect x="392" y="46" width="356" height="218" rx="12" class="fig-panel"/><text x="412" y="30"><tspan font-size="16" font-weight="700" class="fig-ink fig-name">Actually changed</tspan></text><g class="aim-low-in" style="animation-delay:0.00s"><rect x="420" y="88" width="300" height="48" rx="9" class="fig-panel fig-grid-stroke" stroke-width="2"/><text x="570" y="108" class="fig-muted" text-anchor="middle" font-size="12" font-weight="600">the original</text><text x="570" y="126" class="fig-muted" text-anchor="middle" font-size="11" font-weight="500">someone else's work</text></g><g class="aim-low-in" style="animation-delay:0.50s"><rect x="420" y="150" width="300" height="48" rx="9" class="fig-panel fig-grid-stroke" stroke-width="2"/><text x="570" y="170" class="fig-muted" text-anchor="middle" font-size="12" font-weight="600">your upload</text><text x="570" y="188" class="fig-muted" text-anchor="middle" font-size="11" font-weight="500">a demand the original lacked</text></g><g class="aim-low-verdict"><rect x="500" y="218" width="140" height="36" rx="9" class="fig-panel fig-balanced-stroke" stroke-width="2"/><text x="570" y="236" class="fig-balanced-fill" text-anchor="middle" font-size="14" font-weight="700" dominant-baseline="central">stays</text></g></svg>
<figcaption>Same donor, two uploads. Only the one that added a demand survives.</figcaption>
</figure>

Read that as design advice rather than as a threat. If you cannot say in one sentence what your
version demands that the original did not, it is a local scenario.

**The bar that actually matters is your own routine.** A scenario you have trained on for a week has
been tested by the only method that counts. One you built and admired has not.

**Name the weakness, not the look.** The description and aim type on the Tags tab feed the browser's
search and filters.[^REF-80] A reader hunting for a drill searches by what it fixes.

Workshop content does get browsed and picked up by other players.[^REF-12] A scenario naming the
skill it trains has a real chance of being used.

## Two facts that surprise people

**A local edit is invisible until you upload again.** Changing a scenario you already published
lights the upload control again, and until you use it, other players still have the old
version.[^REF-85]

That includes the map. A map lives inside the scenario, so an edited map only reaches anyone once
the scenario itself is uploaded again.[^REF-91]

<figure class="aim-figure">
<svg viewBox="0 0 760 280" class="fig-fit" role="img" aria-labelledby="fig-upload-title"><title id="fig-upload-title">Three stages in a row: a local copy, the workshop, and a locally edited copy. A token travels from the local copy to the workshop, then on to the edited copy. A return arrow runs from the edited copy back to the workshop, labelled as a re-upload without which the change reaches nobody.</title><defs><marker id="fig-up-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 Z" class="fig-grid-fill"/></marker><marker id="fig-up-arrow-accent" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 Z" class="fig-accent-fill"/></marker></defs><metadata><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#"><cc:Work rdf:about=""><dc:creator>Bassel Bakr</dc:creator><dc:source>https://github.com/Bassel-Bakr/aim</dc:source><cc:license rdf:resource="https://creativecommons.org/licenses/by-sa/4.0/"/></cc:Work></rdf:RDF></metadata><style>@keyframes aimUpMove{0%{opacity:0}4%{opacity:1}26%{opacity:1}30%{opacity:0}100%{opacity:0}}.aim-up-token{opacity:0;animation-name:aimUpMove;animation-iteration-count:infinite;animation-duration:7.0s}@keyframes aimUpSlide0{0%{transform:translate(0,0)}30%{transform:translate(86px,0)}100%{transform:translate(86px,0)}}.aim-up-0{animation-delay:0.00s;animation-name:aimUpMove,aimUpSlide0;animation-duration:7.0s,7.0s}@keyframes aimUpSlide1{0%{transform:translate(0,0)}30%{transform:translate(86px,0)}100%{transform:translate(86px,0)}}.aim-up-1{animation-delay:1.54s;animation-name:aimUpMove,aimUpSlide1;animation-duration:7.0s,7.0s}@media (prefers-reduced-motion:reduce){.aim-up-token{opacity:1;animation:none!important}}</style><rect x="12" y="46" width="736" height="206" rx="12" class="fig-panel"/><text x="32" y="30"><tspan font-size="16" font-weight="700" class="fig-ink fig-name">Upload, edit, upload again</tspan><tspan dx="10" font-size="13" font-weight="500" class="fig-muted fig-note">an edit never travels on its own</tspan></text><rect x="60" y="96" width="140" height="70" rx="10" class="fig-grid-stroke" stroke-width="2" fill="none"/><text x="130" y="124" class="fig-ink" text-anchor="middle" font-size="14" font-weight="700">Local copy</text><text x="130" y="146" class="fig-muted" text-anchor="middle" font-size="12" font-weight="500">yours, editable</text><path d="M208 131H302" class="fig-grid-stroke" stroke-width="2" marker-end="url(#fig-up-arrow)"/><circle cx="212" cy="131" r="8" class="fig-target aim-up-token aim-up-0"/><rect x="310" y="96" width="140" height="70" rx="10" class="fig-grid-stroke" stroke-width="2" fill="none"/><text x="380" y="124" class="fig-ink" text-anchor="middle" font-size="14" font-weight="700">Workshop</text><text x="380" y="146" class="fig-muted" text-anchor="middle" font-size="12" font-weight="500">uploaded, unique name</text><path d="M458 131H552" class="fig-grid-stroke" stroke-width="2" marker-end="url(#fig-up-arrow)"/><circle cx="462" cy="131" r="8" class="fig-target aim-up-token aim-up-1"/><rect x="560" y="96" width="140" height="70" rx="10" class="fig-grid-stroke" stroke-width="2" fill="none"/><text x="630" y="124" class="fig-ink" text-anchor="middle" font-size="14" font-weight="700">Edited locally</text><text x="630" y="146" class="fig-muted" text-anchor="middle" font-size="12" font-weight="500">the arrow lights again</text><path d="M630 174V206H380V174" class="fig-accent-stroke" stroke-width="2" stroke-dasharray="6 5" fill="none" marker-end="url(#fig-up-arrow-accent)"/><text x="435" y="226" class="fig-accent-text" text-anchor="middle" font-size="13" font-weight="600">re-upload, or the change reaches nobody</text></svg>
<figcaption>An edit sits on your machine until you upload again. The workshop copy does not follow
it.</figcaption>
</figure>

**The name has to be unique, and the upload is not instant.** A duplicate title blocks the upload
outright, and a successful one takes a few minutes to propagate before anyone can play it.[^REF-85]

Deleting is done on the Steam Workshop website rather than in the game.[^REF-85]

## Common mistakes

- Publishing a scenario you have never put in a routine.
- Leaving Tags empty, which makes the scenario unsearchable.[^REF-80]
- Editing a map and expecting players to see it without re-uploading.[^REF-91]
- Publishing a lightly-changed copy, which gets removed.[^REF-85]

## In practice

**Let the routine decide.** If it survived a week of your own training, it is worth other people's
time. If it did not, publishing it wastes theirs.

**Do this next.** Take a scenario you built and have trained on for a week, write its Tags
description as the weakness it isolates, then upload it.

## Resources

- [Routines](../training/routines.md): whether the scenario earned its place first.
- [KovaaK's](../resources/trainers/kovaaks.md): the trainer whose workshop this is.
