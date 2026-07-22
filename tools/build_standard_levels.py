#!/usr/bin/env python3
"""Recover per-slot pre-uplift trainer levels for the Standard difficulty tier.

The Hard tier is the current src/data/trainers.party. The Standard tier reuses
the *levels* the trainers had before the kaizo level uplift (git commit
74c0f0a7, "Kaizo level uplift"), transplanted onto the current species/moves so
only levels differ between the two tiers.

For every trainer that already existed at 74c0f0a7~1 with the same team size,
this records its pre-uplift level per slot into tools/standard_levels.json. That
covers the gym leaders, Elite Four, Champion, superboss and the bulk of route
trainers. Trainers added later (the VS-Seeker route roster) and rematch variants
whose team size changed are absent here; tools/difficulty_split.py falls back to
each trainer's base variant or its segment's Standard band for those.
"""
import json
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PARTY = REPO / "src/data/trainers.party"
PRE_UPLIFT_REV = "74c0f0a7~1"  # last commit before the kaizo level uplift
OUT = REPO / "tools/standard_levels.json"


def parse_levels(text):
    """trainer id -> [level per party slot], in file order."""
    trainers, cur, levels = {}, None, []
    for line in text.splitlines():
        m = re.match(r"^=== (TRAINER_\S+) ===", line)
        if m:
            if cur is not None:
                trainers[cur] = levels
            cur, levels = m.group(1), []
        elif cur is not None and line.startswith("Level: "):
            levels.append(int(line[len("Level: "):]))
    if cur is not None:
        trainers[cur] = levels
    return trainers


def main():
    cur = parse_levels(PARTY.read_text())
    pre_text = subprocess.run(
        ["git", "show", f"{PRE_UPLIFT_REV}:src/data/trainers.party"],
        cwd=REPO, capture_output=True, text=True, check=True).stdout
    pre = parse_levels(pre_text)

    out = {}
    for tid, cur_levels in cur.items():
        pre_levels = pre.get(tid)
        if pre_levels is not None and len(pre_levels) == len(cur_levels):
            out[tid] = pre_levels
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"wrote {OUT}: {len(out)}/{len(cur)} trainers recovered per-slot "
          f"({len(cur) - len(out)} fall back to base/band)")


if __name__ == "__main__":
    main()
