"""Move the fields that still used a generic slider onto a shape with a subject in it.

`reach`, `delay` and `angle` draw a marker on a dashed track. For a plain magnitude that is honest.
For a distance measured from you, a pause at a turn, a profile lockout or the gap between a hit and
the answer to it, it is not: those have a subject, and the slider left it out.

Run it once; it reports anything it could not find so a typo cannot pass silently.
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

# field name -> (kind, low label, high label)
RETAG: dict[str, tuple[str, str, str]] = {
    "Target Distance Range (min)": ("standoff", "it closes right in", "it keeps its distance"),
    "Target Distance Range (max)": ("standoff", "kept near", "allowed far"),
    "Strafe Swap Pause Min": ("swappause", "no pause at the turn", "it waits at the turn"),
    "Profile Change Time Min": ("profileclock", "it swaps out early", "it stays a long while"),
    "Profile Change Time Max": ("profileclock", "swaps often", "rarely swaps"),
    "Waypoint Turn Rate": ("turnrate", "it swings wide", "it corners sharply"),
    "Cooldown Time": ("cooldown", "usable again at once", "a long lockout"),
    "Strafe Reaction Delay Min": ("reactlag", "it answers at once", "it answers late"),
    "Damage Reaction Delay Min": ("hitlag", "it answers at once", "it answers late"),
    "Damage Reaction Cooldown": ("cooldown-inv", "it reacts to every hit", "a long lockout"),
    "Blocked Reaction Time": ("wallpress", "it gives up at once", "it leans in a while"),
}

FILES = ("tabs.py", "tabs_char.py", "tabs_weapon.py", "tabs_dodge.py", "tabs_bot.py",
         "tabs_scenario.py", "tabs_aim.py")


def main() -> None:
    changed: set[str] = set()
    present: set[str] = set()
    for name in FILES:
        path = HERE / name
        text = path.read_text(encoding="utf-8")
        for field in RETAG:
            if f'("{field}",' in text:
                present.add(field)
        for field, (kind, low, high) in RETAG.items():
            # The kind and the two state labels are the last three quoted strings of the spec.
            pattern = re.compile(
                r'(\("' + re.escape(field) + r'",.*?)"[a-z-]+",\s*"[^"]*",\s*"[^"]*"', re.S)
            text, count = pattern.subn(
                lambda m: f'{m.group(1)}"{kind}", "{low}", "{high}"', text, count=1)
            if count:
                changed.add(field)
        path.write_text(text, encoding="utf-8", newline="\n")
    print(f"retagged {len(changed)} fields")
    missing = sorted(set(RETAG) - present)
    if missing:
        raise SystemExit("no such field, check the spelling: " + ", ".join(missing))


if __name__ == "__main__":
    main()
