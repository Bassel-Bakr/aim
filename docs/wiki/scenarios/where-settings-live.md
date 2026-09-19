---
title: "Where Each Setting Lives"
description: >-
  A map from what you want a scenario to demand to the profile and tab that controls it, with the
  traps that cost the most time.
tags:
  - routines
related:
  - page: wiki/scenarios/making-a-scenario.md
    why: the build this map is the lookup table for.
  - page: wiki/scenarios/tuning-difficulty.md
    why: which of these settings are worth changing and how far.
---

!!! warning "Draft"
    Written from public sources, pending review.

This page is a lookup table, not a manual. KovaaK's documents its own editor field by field, and
stays current in a way a third-party page cannot.[^REF-79]

What is missing is the other direction. You know what the scenario should demand. You need to know
where that lives.

- **Start from the demand, not the menu.** Decide what should be hard, then look it up.
- **Settings are spread across profiles.** One scenario, several files.[^REF-79]
- **Two traps cost the most time.** The Challenge tab, and the Session Manager.
- **Read the official pages for fields.** This page does not repeat them.

## From demand to location

| What you want to change | Where it lives |
| --- | --- |
| How precise each shot must be | Character profile, Boxes tab[^REF-81] |
| Whether one hit ends it | Character profile, Main tab, health[^REF-81] |
| How far apart targets appear | Character profile, Spawn tab, offsets[^REF-81] |
| Whether targets crowd each other | Character profile, Spawn tab, blocked radius[^REF-81] |
| Whether a target spawns near your crosshair | Character profile, Spawn tab, spawn FOV[^REF-81] |
| How the target moves | A Dodge profile, attached to the bot[^REF-82][^REF-83] |
| Whether the target reacts to you | Dodge profile, React tab[^REF-83] |
| Whether the target follows a map path | Dodge profile, Waypoint Logic[^REF-91] |
| Whether a shot travels or lands instantly | Weapon profile, Main tab[^REF-86] |
| How much randomness a shot carries | Weapon profile, Spread or PBS tab[^REF-86] |
| Whether recoil is learnable | Weapon profile, Recoil or PSR tab[^REF-86] |
| How many bots, and the rules | Edit Scenario, Challenge tab[^REF-80] |
| What a run is worth | Edit Scenario, Scoring tab[^REF-80] |
| Whether anyone can find it | Edit Scenario, Tags tab[^REF-80] |
| The space it happens in | Edit Map, from the scenario editor[^REF-88] |

## The two traps

**Naming a profile once is not enough.** Adding a character or bot profile on the Main tab does not
change what challenge mode uses. Set it on the Challenge tab as well.[^REF-80][^REF-85]

<figure class="aim-figure">
<svg viewBox="0 0 760 300" class="fig-fit" role="img" aria-labelledby="fig-twotabs-title"><title id="fig-twotabs-title">Two panels, each with a Main box and a Challenge box. On the left the profile appears on Main and the Challenge box stays empty. On the right the profile appears on Main and then on Challenge as well.</title><defs><marker id="fig-tabs-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 Z" class="fig-grid-fill"/></marker></defs><metadata><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#"><cc:Work rdf:about=""><dc:creator>Bassel Bakr</dc:creator><dc:source>https://github.com/Bassel-Bakr/aim</dc:source><cc:license rdf:resource="https://creativecommons.org/licenses/by-sa/4.0/"/></cc:Work></rdf:RDF></metadata><style>@keyframes aimTabsRun{0%{opacity:0}3%{opacity:1}44%{opacity:1}48%{opacity:0}100%{opacity:0}}.aim-tabs-step{opacity:0;animation-name:aimTabsRun;animation-iteration-count:infinite;animation-duration:6.0s}.aim-tabs-00{animation-delay:0.00s}.aim-tabs-10{animation-delay:0.00s}.aim-tabs-11{animation-delay:0.90s}@media (prefers-reduced-motion:reduce){.aim-tabs-step{opacity:1;animation:none!important}}</style><rect x="12" y="46" width="356" height="238" rx="12" class="fig-panel"/><text x="32" y="30"><tspan font-size="16" font-weight="700" class="fig-ink fig-name">Main only</tspan><tspan dx="10" font-size="13" font-weight="500" class="fig-muted fig-note">challenge mode stays empty</tspan></text><rect x="36" y="82" width="308" height="62" rx="10" class="fig-grid-stroke" stroke-width="2" fill="none"/><text x="50" y="100" class="fig-muted" text-anchor="start" font-size="13" font-weight="600">Main</text><g class="aim-tabs-step aim-tabs-00"><rect x="180" y="98" width="132" height="34" rx="8" class="fig-panel fig-accent-stroke" stroke-width="2"/><text x="246" y="115" class="fig-accent-text" text-anchor="middle" font-size="13" font-weight="600" dominant-baseline="central">bot profile</text></g><rect x="36" y="164" width="308" height="62" rx="10" class="fig-grid-stroke" stroke-width="2" fill="none"/><text x="50" y="182" class="fig-muted" text-anchor="start" font-size="13" font-weight="600">Challenge</text><text x="246" y="198" class="fig-muted" text-anchor="middle" font-size="13" font-weight="500">nothing here</text><rect x="392" y="46" width="356" height="238" rx="12" class="fig-panel"/><text x="412" y="30"><tspan font-size="16" font-weight="700" class="fig-ink fig-name">Main, then Challenge</tspan><tspan dx="10" font-size="13" font-weight="500" class="fig-muted fig-note">the profile is used</tspan></text><rect x="416" y="82" width="308" height="62" rx="10" class="fig-grid-stroke" stroke-width="2" fill="none"/><text x="430" y="100" class="fig-muted" text-anchor="start" font-size="13" font-weight="600">Main</text><g class="aim-tabs-step aim-tabs-10"><rect x="560" y="98" width="132" height="34" rx="8" class="fig-panel fig-accent-stroke" stroke-width="2"/><text x="626" y="115" class="fig-accent-text" text-anchor="middle" font-size="13" font-weight="600" dominant-baseline="central">bot profile</text></g><rect x="416" y="164" width="308" height="62" rx="10" class="fig-grid-stroke" stroke-width="2" fill="none"/><text x="430" y="182" class="fig-muted" text-anchor="start" font-size="13" font-weight="600">Challenge</text><g class="aim-tabs-step aim-tabs-11"><rect x="560" y="180" width="132" height="34" rx="8" class="fig-panel fig-accent-stroke" stroke-width="2"/><text x="626" y="197" class="fig-accent-text" text-anchor="middle" font-size="13" font-weight="600" dominant-baseline="central">bot profile</text></g><path d="M570 144V164" class="fig-grid-stroke" stroke-width="2" marker-end="url(#fig-tabs-arrow)"/></svg>
<figcaption>Named on Main alone, challenge mode stays empty. It has to be set on Challenge as well.</figcaption>
</figure>

This is the single most common way an edit appears to do nothing. If your change works in free play
and not in a challenge run, this is why.

**The Session Manager is a sandbox.** It changes the player character, the bots, teams,
invincibility, the map, the map scale and the time scale, and none of it is saved.[^REF-84]

That makes it the right place to try a value and the wrong place to set one.

## What the official pages cover better

Field-level detail belongs where it is maintained. Go there for it:

- [Intro to Scenario Creation](https://wiki.kovaaks.com/en/home/KovaaK's/ScenarioCreation/Intro):
  how profiles link, and how to open the editor.
- [Character Profiles](https://wiki.kovaaks.com/en/home/KovaaK's/ScenarioCreation/CharacterProfiles):
  the nine tabs, the two bounding boxes, the spawn options.
- [Weapon Profiles](https://wiki.kovaaks.com/en/home/KovaaK's/ScenarioCreation/WeaponProfiles):
  fifteen tabs, from ammo to per-shot recoil.
- [KovaaK's Map Creator](https://wiki.kovaaks.com/en/home/KovaaK'sMapCreator/home): brushes, game
  objects and the editor's own key binds.

## Common mistakes

- Hunting for a size slider. Size is a bounding box on the Boxes tab.[^REF-81]
- Editing the bot's character profile to change how it moves. Motion is a dodge
  profile.[^REF-82][^REF-83]
- Building a waypoint path and leaving Waypoint Logic on Ignore, so nothing follows it.[^REF-91]
- Treating this page as current. When it disagrees with the official wiki, the official wiki is
  right.

## In practice

**Look up one setting, change it, play it.** A lookup that does not end in a run you played is just
reading.

**Do this next.** Name the one thing you want your scenario to demand, find its row above, and open
that tab.

## Resources

- [KovaaK's](../resources/trainers/kovaaks.md): the trainer, and its own documentation.
