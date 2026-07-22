#!/usr/bin/env python3
"""Populate the Standard (DIFFICULTY_NORMAL) and Hard (DIFFICULTY_HARD) columns
of src/data/trainers.party from a single Hard source.

The current trainers.party holds the uplifted "Hard" curve. This pass leaves
those levels as the Hard tier and adds a Standard tier that is identical in every
respect (species, moves, abilities, items, EVs/IVs, team size) except levels,
which come from the pre-uplift game:

  * exact per-slot pre-uplift levels for trainers in tools/standard_levels.json
    (gym leaders, Elite Four, Champion, superboss, and most route trainers),
  * the base variant's pre-uplift levels for rematch variants (TRAINER_..._2..6)
    whose team size changed after the uplift,
  * otherwise a rescale of the trainer's Hard levels from its segment's
    level_band onto standard_band (the VS-Seeker roster added after the uplift).

A trainer whose Standard levels equal its Hard levels (frontier brains, empty
parties, anything the uplift never touched) is emitted once with no Difficulty
key, so the engine serves it to both tiers via the DIFFICULTY_NORMAL fallback.
A trainer whose levels differ is emitted twice: a `Difficulty: Normal` block with
Standard levels and a `Difficulty: Hard` block with the current levels.

Idempotent: re-running treats the `Difficulty: Hard` block (or a keyless block on
the first run) as the canonical Hard source and regenerates the Standard block.
Use --dry-run for a diff, --check for CI.
"""
import argparse
import difflib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kaizo_pass as kp

REPO = Path(__file__).resolve().parent.parent
PARTY = REPO / "src/data/trainers.party"
STD_LEVELS = REPO / "tools/standard_levels.json"
SEGMENTS = REPO / "tools/kaizo_segments.json"
VARIANT_RE = re.compile(r"_[2-6]$")


def blocks(lines):
    """Yield (trainer_id, [block lines]) in file order; a block spans a
    '=== TRAINER_X ===' header through the line before the next header."""
    start, tid = None, None
    for i, line in enumerate(lines):
        if line.startswith("=== ") and line.rstrip().endswith(" ==="):
            if start is not None:
                yield tid, lines[start:i]
            start, tid = i, line.strip().strip("= ").strip()
    if start is not None:
        yield tid, lines[start:len(lines)]


def difficulty_of(block):
    for line in block:
        if line.startswith("Difficulty:"):
            return line.split(":", 1)[1].strip().lower()
    return None


def strip_difficulty(block):
    return [l for l in block if not l.startswith("Difficulty:")]


def mon_levels(block):
    return [int(l[len("Level: "):]) for l in block if l.startswith("Level: ")]


def set_levels(block, levels):
    """Return block with each 'Level: N' line replaced in order by levels[]."""
    out, k = [], 0
    for l in block:
        if l.startswith("Level: "):
            out.append(f"Level: {levels[k]}\n")
            k += 1
        else:
            out.append(l)
    return out


def insert_difficulty(block, value):
    """Insert 'Difficulty: <value>' after the Name: line (present on every
    trainer); fall back to just after the header."""
    out, done = [], False
    for i, l in enumerate(block):
        out.append(l)
        if not done and l.startswith("Name:"):
            out.append(f"Difficulty: {value}\n")
            done = True
    if not done:  # no Name line: put it right after the header
        out = [block[0], f"Difficulty: {value}\n"] + block[1:]
    return out


def rescale(levels, src, dst):
    """Map each level from band src=[lo,hi] onto dst=[lo,hi], preserving
    relative position, clamped to dst."""
    slo, shi = src
    dlo, dhi = dst
    span = max(1, shi - slo)
    out = []
    for lv in levels:
        v = dlo + round((lv - slo) * (dhi - dlo) / span)
        out.append(max(dlo, min(dhi, v)))
    return out


def build_standard(tid, hard_levels, std_levels, trainer_maps, segments, map_seg):
    """Standard levels for a trainer, same length as hard_levels."""
    if not hard_levels:
        return hard_levels
    exact = std_levels.get(tid)
    if exact is not None and len(exact) == len(hard_levels):
        return exact
    # Rematch variant whose size changed: borrow the base variant's curve.
    base = VARIANT_RE.sub("", tid)
    if base != tid:
        base_levels = std_levels.get(base)
        if base_levels:
            n = len(hard_levels)
            if n <= len(base_levels):
                return base_levels[:n]
            return base_levels + [base_levels[-1]] * (n - len(base_levels))
    # New trainer (VS-Seeker roster): rescale Hard levels onto the Standard band.
    seg_name = map_seg.get(trainer_maps.get(tid) or trainer_maps.get(base))
    if seg_name:
        seg = segments[seg_name]
        return rescale(hard_levels, seg["level_band"], seg["standard_band"])
    # Last resort (no segment): roughly halve, never below 2.
    return [max(2, round(lv * 0.5)) for lv in hard_levels]


def transform(lines):
    std_levels = json.loads(STD_LEVELS.read_text())
    config = json.loads(SEGMENTS.read_text())
    segments, map_seg = config["segments"], config["maps"]
    trainer_maps = kp.trainer_to_map(kp.SCRIPT_FILES)

    # Canonical Hard block per trainer, in first-seen order (prefer an explicit
    # 'Difficulty: Hard' block; a keyless block counts as canonical on run 1).
    canonical, order = {}, []
    for tid, block in blocks(lines):
        diff = difficulty_of(block)
        if diff == "normal":
            continue  # regenerated from the Hard block
        if tid not in canonical or diff == "hard":
            if tid not in canonical:
                order.append(tid)
            canonical[tid] = strip_difficulty(block)

    out = []
    for tid in order:
        hard = canonical[tid]
        hard_levels = mon_levels(hard)
        std_lv = build_standard(tid, hard_levels, std_levels,
                                trainer_maps, segments, map_seg)
        # Standard is the easier tier: never let a computed level exceed Hard.
        std_lv = [min(s, h) for s, h in zip(std_lv, hard_levels)]
        if std_lv == hard_levels:
            out.extend(hard)  # identical in both tiers: one keyless block
        else:
            normal = insert_difficulty(set_levels(hard, std_lv), "Normal")
            hard_block = insert_difficulty(hard, "Hard")
            out.extend(normal)
            out.extend(hard_block)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    old = PARTY.read_text().splitlines(keepends=True)
    new = transform(old)
    if new == old:
        print("no changes")
        return 0
    if args.check:
        print("difficulty_split: trainers.party is not up to date", file=sys.stderr)
        return 1
    if args.dry_run:
        sys.stdout.writelines(difflib.unified_diff(
            old, new, fromfile="trainers.party", tofile="trainers.party (split)"))
        return 0
    PARTY.write_text("".join(new))
    print(f"rewrote {PARTY}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
