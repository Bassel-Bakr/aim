---
title: "Making Scenarios"
description: >-
  Designing your own aim trainer scenarios: choosing what one should demand, tuning it, and telling
  whether it trains what you meant.
tags:
  - routines
---

!!! warning "Draft"
    Written from public sources, pending review.

KovaaK's documents its own editor field by field, and keeps it current.[^REF-79] This section does
not repeat that.

It covers the part no editor manual answers: what a scenario should demand, and how to tell whether
yours does.

Make one only when nothing that already exists isolates the thing you keep losing. A custom scenario
has no leaderboard and no history, so it costs you context a known scenario gives away free.

Two facts shape the rest. A scenario always starts as a copy, because no blank one is
offered.[^REF-79][^REF-85] A map is the exception: the map creator starts you with an empty
one.[^REF-91]

<figure class="aim-figure">
<svg viewBox="0 0 760 280" class="fig-fit" role="img" aria-labelledby="fig-copying-title"><title id="fig-copying-title">An existing scenario on the left. Unpacking it produces a character profile, a bot profile and a dodge profile, which appear one after another. Replacing one of them produces your own scenario on the right.</title><defs><marker id="fig-copy-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 Z" class="fig-grid-fill"/></marker></defs><metadata><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#"><cc:Work rdf:about=""><dc:creator>Bassel Bakr</dc:creator><dc:source>https://github.com/Bassel-Bakr/aim</dc:source><cc:license rdf:resource="https://creativecommons.org/licenses/by-sa/4.0/"/></cc:Work></rdf:RDF></metadata><style>@keyframes aimCopyIn{0%{opacity:0}6%{opacity:1}100%{opacity:1}}.aim-copy-step{opacity:0;animation-name:aimCopyIn;animation-iteration-count:infinite;animation-duration:6.0s}@keyframes aimCopySwap{0%{opacity:0}66%{opacity:0}72%{opacity:1}100%{opacity:1}}.aim-copy-swap{opacity:0;animation-name:aimCopySwap;animation-iteration-count:infinite;animation-duration:6.0s}@media (prefers-reduced-motion:reduce){.aim-copy-step,.aim-copy-swap{opacity:1;animation:none!important}}</style><rect x="12" y="46" width="736" height="208" rx="12" class="fig-panel"/><text x="32" y="30"><tspan font-size="16" font-weight="700" class="fig-ink fig-name">Every scenario starts as a copy</tspan><tspan dx="10" font-size="13" font-weight="500" class="fig-muted fig-note">the editor offers no blank one</tspan></text><rect x="44" y="110" width="150" height="66" rx="10" class="fig-grid-stroke" stroke-width="2" fill="none"/><text x="119" y="138" class="fig-ink" text-anchor="middle" font-size="14" font-weight="700">Existing</text><text x="119" y="160" class="fig-muted" text-anchor="middle" font-size="12" font-weight="500">scenario</text><path d="M202 143H262" class="fig-grid-stroke" stroke-width="2" marker-end="url(#fig-copy-arrow)"/><text x="232" y="124" class="fig-muted" text-anchor="middle" font-size="12" font-weight="500">unpack</text><g class="aim-copy-step" style="animation-delay:0.50s"><rect x="276" y="96" width="150" height="32" rx="8" class="fig-panel fig-grid-stroke" stroke-width="2"/><text x="351" y="112" class="fig-muted" text-anchor="middle" font-size="13" font-weight="600" dominant-baseline="central">character</text></g><g class="aim-copy-step" style="animation-delay:1.00s"><rect x="276" y="136" width="150" height="32" rx="8" class="fig-panel fig-grid-stroke" stroke-width="2"/><text x="351" y="152" class="fig-muted" text-anchor="middle" font-size="13" font-weight="600" dominant-baseline="central">bot</text></g><g class="aim-copy-step" style="animation-delay:1.50s"><rect x="276" y="176" width="150" height="32" rx="8" class="fig-panel fig-grid-stroke" stroke-width="2"/><text x="351" y="192" class="fig-muted" text-anchor="middle" font-size="13" font-weight="600" dominant-baseline="central">dodge</text></g><path d="M436 143H496" class="fig-grid-stroke" stroke-width="2" marker-end="url(#fig-copy-arrow)"/><text x="466" y="124" class="fig-muted" text-anchor="middle" font-size="12" font-weight="500">replace</text><g class="aim-copy-swap"><rect x="510" y="110" width="176" height="66" rx="10" class="fig-panel fig-accent-stroke" stroke-width="2.4"/><text x="598" y="138" class="fig-accent-text" text-anchor="middle" font-size="14" font-weight="700">Your scenario</text><text x="598" y="160" class="fig-muted" text-anchor="middle" font-size="12" font-weight="500">one profile changed</text></g></svg>
<figcaption>Copy, unpack, replace one profile. That is the whole shape of making a scenario.</figcaption>
</figure>

## Design it

<div class="aim-cards" markdown>

- **[Making Your Own Scenario](making-a-scenario.md)**: the whole build, as decisions rather than
  clicks.
- **[Designing Around a Weakness](designing-around-a-weakness.md)**: turning a named gap into a
  drill that isolates it.
- **[Designing Target Motion](designing-target-motion.md)**: readable paths against reactive ones,
  and which trains what.

</div>

## Make it measure something

<div class="aim-cards" markdown>

- **[Tuning Difficulty](tuning-difficulty.md)**: which settings move difficulty, and how far to
  push them.
- **[Keeping the Score Readable](keeping-the-score-readable.md)**: stripping the randomness you
  added by accident.
- **[Testing a Scenario](testing-and-iterating.md)**: telling whether it trains what you intended.

</div>

## Look it up, then ship it

- [Where Each Setting Lives](where-settings-live.md): a map from the demand you want to the tab
  that controls it.
- [Sharing to the Workshop](sharing-to-the-workshop.md): uploading, updating, and what is worth
  publishing.
