"""Say what each magnitude field is actually about.

The magnitude kinds slide a marker along a track. Left to themselves they slid a target, which is
right for a spawn offset and wrong for a reload timer, a decal, a muzzle flash or a round of ammo.
This maps those fields onto the glyph that matches their subject, and appends it as a sixth entry
on the spec.

Fields not listed here keep the target, which is correct: they really are about where a character
or a target ends up.
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

SUBJECT = {
    # ammunition and magazines
    "Ammo Per Shot": "round",
    "Magazine Max": "round",
    "Ammo Reloaded Per Kill": "round",
    "Ammo Awarded On Death": "round",
    "Empty Reload Time": "round",
    "Partial Reload Time": "round",
    "Reload Before Shot Recovery": "round",
    # damage and health, which are quantities rather than bodies
    "Damage Per Shot": "bar",
    "Headshot Factor": "bar",
    "Damage At Max Range": "bar",
    "Area Damage": "bar",
    "Self Damage Multiplier": "bar",
    "Health": "bar",
    "Health Regained On Kill": "bar",
    "Health Regen Per Sec": "bar",
    "Lifesteal": "bar",
    # visual effects left on the world
    "Muzzle Flash Particle Scale": "spark",
    "Wall Impact Particle Scale": "spark",
    "Body Impact Particle Scale": "spark",
    "Hitscan Visual Radius": "spark",
    "Hitscan Visual Duration": "spark",
    "Decal Size": "decal",
    "Hitscan Visual Offset": "decal",
    # timers that belong to the weapon, not to a character
    "Delay Before Shot": "round",
    "Delay After Shooting": "round",
    "Time Between Shots": "round",
    "Switch Time Reduction": "round",
    "Zoom Time": "box",
    "Zoom Start Delay": "box",
    "Time To Peak": "mark",
    "Time To Reset": "mark",
    "Time Per Shot": "mark",
    "Loop Start Index": "mark",
    # the pattern and origin fields describe where a shot comes from
    "Origin Offset": "round",
    "Pattern Count": "mark",
    # timers that belong to the scenario rather than to a body
    "Min Respawn Delay": "box",
    "Max Respawn Delay": "box",
    "Respawn Anim Duration": "box",
    "Global Cooldown": "box",
    "Block Ability for Duration on Challenge Start": "box",
    "Respawn Invincibility Timer": "box",
    "Lock Auto Off Timer": "box",
    "Lock Re-Engage Timer": "box",
    "Trigger Bot Delay": "box",
    "Stun Duration": "box",
    "Tagging Duration": "box",
}


def main() -> None:
    seen: set[str] = set()
    present: set[str] = set()
    for name in ("tabs.py", "tabs_char.py", "tabs_weapon.py"):
        path = HERE / name
        text = path.read_text(encoding="utf-8")
        for field, mark in SUBJECT.items():
            if f'("{field}",' in text:
                present.add(field)
            # Append the glyph as a sixth entry, unless one is already there.
            pattern = re.compile(r'(\("' + re.escape(field) +
                                 r'",.*?"[a-z-]+",\s*"[^"]*",\s*"[^"]*")\)', re.S)
            text, count = pattern.subn(lambda m: f'{m.group(1)}, "{mark}")', text, count=1)
            if count:
                seen.add(field)
        path.write_text(text, encoding="utf-8", newline="\n")
    print(f"tagged {len(seen)} fields; {len(present - seen)} already tagged")
    unknown = sorted(set(SUBJECT) - present)
    if unknown:
        raise SystemExit("no such field, check the spelling: " + ", ".join(unknown))


if __name__ == "__main__":
    main()
