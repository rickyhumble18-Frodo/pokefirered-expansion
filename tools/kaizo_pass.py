#!/usr/bin/env python3
"""Kaizo difficulty pass over src/data/trainers.party.

Subcommands:
  ai    Phase A - raise every trainer's AI to a smart baseline; bosses get
        switching intelligence, the Elite Four and Champion also get Omniscient.
  bulk  Phase B - per-segment level curve, team padding and held items for
        route trainers. Segments and pools live in tools/kaizo_segments.json;
        pre-pass levels are captured into tools/kaizo_baseline.json on first
        run so re-runs recompute from the originals instead of compounding.

All subcommands are idempotent: running them twice produces the same file.
Use --dry-run to print a unified diff instead of rewriting the file.
"""

import argparse
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PARTY_FILE = REPO_ROOT / "src/data/trainers.party"
SEGMENTS_FILE = REPO_ROOT / "tools/kaizo_segments.json"
BASELINE_FILE = REPO_ROOT / "tools/kaizo_baseline.json"
SCRIPT_FILES = [REPO_ROOT / "data/scripts/trainers.inc"] + \
    sorted((REPO_ROOT / "data/maps").glob("*/scripts.inc"))

BASE_AI = "Check Bad Move / Try To Faint / Check Viability"
BOSS_AI_EXTRA = "Smart Switching / Smart Mon Choices"
OMNISCIENT_AI_EXTRA = "Omniscient"

# Classes whose members count as bosses for AI purposes.
BOSS_CLASSES = {
    "Leader",
    "Elite Four",
    "Champion",
    "Boss",          # Rocket boss Giovanni
    "Rival",
    "Rival Early",
    "Rival Late",
}

# Classes that also see the player's sets (E4 tier cruelty).
OMNISCIENT_CLASSES = {"Elite Four", "Champion"}

# Trainers whose AI is controlled at runtime by facility code (frontier
# brains) or scripted demos; leave them alone.
AI_SKIP_TRAINERS = {
    "TRAINER_NONE",
    "TRAINER_MAXIE_MOSSDEEP",
    "TRAINER_ANABEL",
    "TRAINER_TUCKER",
    "TRAINER_SPENSER",
    "TRAINER_GRETA",
    "TRAINER_NOLAND",
    "TRAINER_LUCY",
    "TRAINER_BRANDON",
}


class Trainer:
    def __init__(self, trainer_id, start):
        self.id = trainer_id
        self.start = start          # index of the "=== TRAINER_X ===" line
        self.end = None             # exclusive
        self.klass = None
        self.ai_line_idx = None     # index of the "AI:" line, if any


def parse_trainers(lines):
    trainers = []
    cur = None
    for i, line in enumerate(lines):
        if line.startswith("=== ") and line.rstrip().endswith(" ==="):
            if cur is not None:
                cur.end = i
            cur = Trainer(line.strip().strip("= ").strip(), i)
            trainers.append(cur)
        elif cur is not None:
            if line.startswith("Class: "):
                cur.klass = line[len("Class: "):].strip()
            elif line.startswith("AI: "):
                cur.ai_line_idx = i
    if cur is not None:
        cur.end = len(lines)
    return trainers


def desired_ai(trainer):
    parts = [BASE_AI]
    if trainer.klass in BOSS_CLASSES:
        parts.append(BOSS_AI_EXTRA)
    if trainer.klass in OMNISCIENT_CLASSES:
        parts.append(OMNISCIENT_AI_EXTRA)
    return "AI: " + " / ".join(parts)


def apply_ai(lines):
    out = list(lines)
    for trainer in parse_trainers(lines):
        if trainer.id in AI_SKIP_TRAINERS:
            continue
        new_line = desired_ai(trainer)
        if trainer.ai_line_idx is not None:
            out[trainer.ai_line_idx] = new_line + "\n"
        else:
            # No AI line: insert right after the Class line (every trainer in
            # this file has one; fall back to after the header line).
            insert_at = trainer.start + 1
            for i in range(trainer.start + 1, trainer.end):
                if lines[i].startswith("Class: "):
                    insert_at = i + 1
                    break
            out.insert(insert_at, new_line + "\n")
            # Only safe when processing a single insertion per pass; re-parse.
            return apply_ai(out)
    return out


# ---------------------------------------------------------------------------
# Phase B - bulk level curve / padding / items
# ---------------------------------------------------------------------------

# Never bulk-edit these: bosses and rival fights are hand-authored (Phase C),
# TRAINER_*_2.._6 rematch variants are authored as part of the rematch design.
BULK_SKIP_CLASSES = BOSS_CLASSES | OMNISCIENT_CLASSES
VARIANT_RE = re.compile(r"_[2-6]$")


def trainer_to_map(script_files):
    """Map trainer ids to the map whose scripts battle them, via the
    <MapName>_EventScript_* label prefix."""
    result = {}
    for path in script_files:
        label_map = None
        for line in path.read_text().splitlines():
            m = re.match(r"^(\w+?)_EventScript_\w+::", line)
            if m:
                label_map = m.group(1)
            m = re.search(r"\ttrainerbattle\w*\s+(TRAINER_[A-Z0-9_]+)", line)
            if m and label_map:
                result.setdefault(m.group(1), label_map)
    return result


def split_paragraphs(lines):
    """Split a trainer block body into paragraphs (header first, then mons)."""
    paras, cur = [], []
    for line in lines:
        if line.strip() == "":
            if cur:
                paras.append(cur)
                cur = []
        else:
            cur.append(line)
    if cur:
        paras.append(cur)
    return paras


def species_of(mon_para):
    return mon_para[0].split(" @ ")[0].strip()


def level_of(mon_para):
    for line in mon_para:
        if line.startswith("Level: "):
            return int(line[len("Level: "):])
    raise ValueError(f"mon paragraph without level: {mon_para[0]!r}")


def with_level(mon_para, level):
    return [f"Level: {level}\n" if l.startswith("Level: ") else l for l in mon_para]


def stable_hash(s):
    return int(hashlib.sha1(s.encode()).hexdigest(), 16)


def bulk_segment_of(trainer, trainer_maps, map_segments):
    map_name = trainer_maps.get(trainer.id)
    seg_name = map_segments.get(map_name) if map_name else None
    if (seg_name is None
            or trainer.klass in BULK_SKIP_CLASSES
            or VARIANT_RE.search(trainer.id)
            or trainer.id in AI_SKIP_TRAINERS):
        return None
    return seg_name


def apply_bulk(lines):
    config = json.loads(SEGMENTS_FILE.read_text())
    segments, map_segments = config["segments"], config["maps"]
    baseline = json.loads(BASELINE_FILE.read_text()) if BASELINE_FILE.exists() else {}
    trainer_maps = trainer_to_map(SCRIPT_FILES)

    # Pass 1: pre-pass (vanilla) level range of every segment, so each
    # trainer's baseline can be rescaled onto the segment's level_band while
    # keeping its relative strength within the segment.
    seg_range = {}
    for trainer in parse_trainers(lines):
        seg_name = bulk_segment_of(trainer, trainer_maps, map_segments)
        if seg_name is None:
            continue
        paras = split_paragraphs([l for l in lines[trainer.start:trainer.end]])
        mons = paras[1:]
        if not mons:
            continue
        levels = (baseline.get(trainer.id) or {}).get("levels") \
                 or [level_of(m) for m in mons]
        lo, hi = seg_range.get(seg_name, (999, 0))
        seg_range[seg_name] = (min(lo, min(levels)), max(hi, max(levels)))

    out = []
    for trainer in parse_trainers(lines):
        block = lines[trainer.start:trainer.end]
        seg_name = bulk_segment_of(trainer, trainer_maps, map_segments)
        if seg_name is None:
            out.extend(block)
            continue

        seg = segments[seg_name]
        # Trailing blank lines of the block are re-added at the end.
        body = [l for l in block]
        while body and body[-1].strip() == "":
            body.pop()
        paras = split_paragraphs(body)
        header, mons = paras[0], paras[1:]
        if not mons:
            out.extend(block)
            continue

        # Capture pre-pass levels once; later runs recompute from these.
        if trainer.id not in baseline:
            baseline[trainer.id] = {"levels": [level_of(m) for m in mons][:len(mons)],
                                    "team_size": len(mons)}
        base = baseline[trainer.id]

        # 1. Level curve: rescale the recorded pre-pass levels from the
        # segment's baseline range onto its level_band (anchored ~5-8 below
        # the upcoming gym leader's ace), preserving relative strength.
        band_lo, band_hi = seg["level_band"]
        seg_lo, seg_hi = seg_range[seg_name]
        span = max(1, seg_hi - seg_lo)
        orig_count = base["team_size"]
        scaled = [min(band_hi, max(band_lo,
                  band_lo + ((lv - seg_lo) * (band_hi - band_lo) + span // 2) // span))
                  for lv in base["levels"]]
        for i in range(min(orig_count, len(mons))):
            mons[i] = with_level(mons[i], scaled[i])

        # 2. Team padding, deterministic per trainer, deduped within the team.
        pad_level = min(scaled)
        rng = stable_hash(trainer.id)
        pool = list(seg["pad_pool"])
        padded = False
        while len(mons) < seg["min_team"]:
            team_species = {species_of(m) for m in mons}
            candidates = [s for s in pool if s not in team_species] or pool
            pick = candidates[rng % len(candidates)]
            rng //= len(candidates) or 1
            mons.append([f"{pick}\n", f"Level: {pad_level}\n"])
            padded = True

        # 3. Held item on the last mon of padded teams.
        if padded and " @ " not in mons[-1][0]:
            items = seg["item_pool"]
            item = items[-1] if stable_hash(trainer.id + "item") % 4 == 0 else items[0]
            mons[-1][0] = mons[-1][0].rstrip("\n") + f" @ {item}\n"

        out.extend(header)
        for mon in mons:
            out.append("\n")
            out.extend(mon)
        out.append("\n")

    return out, baseline


def finish(old_lines, new_lines, dry_run, check):
    if new_lines == old_lines:
        print("no changes")
        return 0
    if check:
        print("kaizo_pass: trainers.party is not up to date; run the script and commit the result", file=sys.stderr)
        return 1
    if dry_run:
        sys.stdout.writelines(difflib.unified_diff(old_lines, new_lines,
                                                   fromfile="trainers.party",
                                                   tofile="trainers.party (kaizo)"))
        return 0
    PARTY_FILE.write_text("".join(new_lines))
    print(f"rewrote {PARTY_FILE}")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["ai", "bulk"])
    parser.add_argument("--dry-run", action="store_true", help="print a diff instead of rewriting")
    parser.add_argument("--check", action="store_true", help="exit 1 if the file would change (CI mode)")
    args = parser.parse_args()

    old_lines = PARTY_FILE.read_text().splitlines(keepends=True)
    if args.command == "ai":
        new_lines = apply_ai(old_lines)
    else:
        new_lines, baseline = apply_bulk(old_lines)
        if not args.dry_run and not args.check:
            BASELINE_FILE.write_text(json.dumps(baseline, indent=1, sort_keys=True) + "\n")
    return finish(old_lines, new_lines, args.dry_run, args.check)


if __name__ == "__main__":
    sys.exit(main())
