#!/usr/bin/env python3
"""Kaizo difficulty pass over src/data/trainers.party.

Subcommands:
  ai    Phase A - raise every trainer's AI to a smart baseline; bosses get
        switching intelligence, the Elite Four and Champion also get Omniscient.

All subcommands are idempotent: running them twice produces the same file.
Use --dry-run to print a unified diff instead of rewriting the file.
"""

import argparse
import difflib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PARTY_FILE = REPO_ROOT / "src/data/trainers.party"

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
    parser.add_argument("command", choices=["ai"])
    parser.add_argument("--dry-run", action="store_true", help="print a diff instead of rewriting")
    parser.add_argument("--check", action="store_true", help="exit 1 if the file would change (CI mode)")
    args = parser.parse_args()

    old_lines = PARTY_FILE.read_text().splitlines(keepends=True)
    if args.command == "ai":
        new_lines = apply_ai(old_lines)
    return finish(old_lines, new_lines, args.dry_run, args.check)


if __name__ == "__main__":
    sys.exit(main())
