"""Move fields off the generic toggle dot and onto a shape that depicts them.

A third of the editor's fields were drawn as a bobbing dot, which says nothing about a camera, a
hitbox, an aimbot lock or an impact effect. This rewrites those specs in place, one mapping per
field name, and reports anything it could not find so a typo cannot pass silently.
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

# field name -> the kind that actually shows it
REMAP = {
    # which camera you are behind
    "Third Person Camera": "view",
    "Hide Third Person Weapon": "view",
    "Third Person Model": "view",
    "View Model Animation": "view",
    # a head box, and the fields that depend on one
    "Has Head": "head",
    "Projectile Has Head": "head",
    "Headshot Only": "head",
    "Headshot Capable": "head",
    "Head Lock": "head",
    # instant against travel time
    "Type": "hitscan",
    "Piercing": "hitscan",
    "Beam Tracks Crosshair": "hitscan",
    # the aimbot dragging your crosshair
    "Aimbot Mode": "lock",
    "Target Preference": "lock",
    "Disable On Kill": "lock",
    "Lock Needs LOS": "lock",
    "Lock Horizontal": "lock",
    "Lock Vertical": "lock",
    "Lock Blocks Mouse": "lock",
    "Sticky Lock": "lock",
    "Trigger Bot": "lock",
    # airborne, so no floor under it
    "Can Crouch In Air": "aircrouch",
    "Zoom Blocked In Air": "aircrouch",
    # a pattern, not a slide
    "Use Per Bullet Spread": "pattern",
    "Use Per Shot Recoil": "pattern",
    "Firing Type": "pattern",
    # an impact effect that is either there or not
    "Hitscan Trace Particle": "particle",
    "Muzzle Flash Particle": "particle",
    "Wall Impact Particle": "particle",
    "Body Impact Particle": "particle",
    "Wall Hit Decal": "particle",
    "Explodes": "particle",
    "Explosion Blocked By World": "particle",
    # two bodies, colliding or not
    "Disable Character Collision": "pass",
    # the second batch: everything still left on the generic dot
    "Enemy Head Color": "swatch",
    "Enemy Body Color": "swatch",
    "Team Head Color": "swatch",
    "Team Body Color": "swatch",
    "Ability 1": "slot",
    "Ability 2": "slot",
    "Ability 3": "slot",
    "Ability 4": "slot",
    "Playback Profile Name": "record",
    "Override Movement": "record",
    "Override Rotation": "record",
    "Override Weapon Input": "record",
    "Override Ability Input": "record",
    "Loop Upon Completion": "record",
    "Playback Mode": "record",
    "Block Self Damage": "shield",
    "Block Team Damage": "shield",
    "Invincible Player": "shield",
    "Invincible Bots": "shield",
    "Clear Attackers On Self Damage": "shield",
    "Bounding Box Type": "boxshape",
    "Projectile Box Type": "boxshape",
    "Character Model": "boxshape",
    "Hide Bounding Box": "hidden",
    "Incremental Reload": "magazine",
    "Auto Reset": "reset",
    "Allow Manual Negation": "reset",
    "ADSing Resets Charge": "charge",
    "Invert Block Other Spawn FOV Logic": "invertfov",
    "Enable Quake/Source Movement": "movemodel",
    "Profile Name": "label",
    "Weapon Name": "label",
    "Third Person Skin": "label",
    "Allow User Override": "label",
    "Zoomed Override": "slot",
}


def main() -> None:
    # Two different outcomes look the same if you only count rewrites: a field already moved on an
    # earlier run, and a field whose name is misspelled here. The second is a bug and has to be
    # loud, so presence is checked separately from whether anything changed.
    seen: set[str] = set()
    present: set[str] = set()
    for name in ("tabs.py", "tabs_char.py", "tabs_weapon.py"):
        path = HERE / name
        text = path.read_text(encoding="utf-8")
        for field in REMAP:
            if f'("{field}",' in text:
                present.add(field)
        for field, kind in REMAP.items():
            # The kind is the first bare string after the field's note, so match the quoted kind
            # that follows this field's opening tuple.
            pattern = re.compile(r'(\("' + re.escape(field) + r'",.*?)"(toggle(?:-inv)?)"',
                                 re.S)
            text, count = pattern.subn(lambda m: f'{m.group(1)}"{kind}"', text, count=1)
            if count:
                seen.add(field)
        path.write_text(text, encoding="utf-8", newline="\n")
    print(f"rewrote {len(seen)} fields; {len(present - seen)} already done")
    unknown = sorted(set(REMAP) - present)
    if unknown:
        raise SystemExit("no such field, check the spelling: " + ", ".join(unknown))


if __name__ == "__main__":
    main()
