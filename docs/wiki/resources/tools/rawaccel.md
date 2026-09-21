---
title: "Raw Accel"
description: >-
  The mouse acceleration driver, what it does, and why most players should leave it alone.
tags:
  - tool
  - sensitivity
related:
  - page: wiki/getting-started/sensitivity.md
    why: the sensitivity it scales, and cm/360 for comparing settings.
  - page: wiki/getting-started/setup.md
    why: acceleration settings in games, mouse software and Windows, which this replaces with one curve.
---

<!-- aim:sources checked -->

**Links:** [GitHub](https://github.com/RawAccelOfficial/rawaccel) · [Guide](https://github.com/RawAccelOfficial/rawaccel/blob/master/doc/Guide.md)

## What it is

A free, open-source Windows 10 and 11 x86-64 driver that applies mouse acceleration and sensitivity
curves you define, before any game sees the input.[^REF-62] The driver is signed, and settings take
a one-second delay to apply, which the developers say is there to limit abuse.[^REF-62]

## Who it suits

Players who want acceleration as a deliberate, repeatable setting instead of turning it off. It also
covers people who want one curve that behaves the same in every game.

## What it covers

- **Curve modes**: Synchronous, Linear, Classic, Power, Natural, Jump, and a lookup table for
  drawing your own.[^REF-63]
- **Caps and offsets**: where acceleration starts, and the most it can add.[^REF-63]
- **Horizontal and vertical**: one curve for all movement, or separate ones per direction.[^REF-63]
- **Per-device settings**: DPI normalization and turning it off for individual mice.[^REF-63]
- **Live graph**: can overlay your recent mouse movements onto the curve.[^REF-63]

## Key content

- [Raw Accel guide](https://github.com/RawAccelOfficial/rawaccel/blob/master/doc/Guide.md): every
  mode and setting, explained by the developers.

## Our take

Download it only from GitHub releases. The project states it has no other official site, and
lookalike sites such as rawaccel.net are not affiliated.[^REF-62]

[Setup](../../getting-started/setup.md) recommends acceleration off as the starting point.
Acceleration is a separate choice some players make on purpose, and this is the tool for making it
consistently. Change one setting at a time, and give each change several sessions before judging it.
