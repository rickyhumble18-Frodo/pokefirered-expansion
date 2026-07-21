#!/usr/bin/env python3
"""Kaizo difficulty pass over src/data/trainers.party.

Subcommands:
  ai    Phase A - raise every trainer's AI to a smart baseline; bosses get
        switching intelligence, the Elite Four and Champion also get Omniscient.
  bulk  Phase B - per-segment level bands, team padding and held items for
        route trainers. Segments and pools live in tools/kaizo_segments.json;
        pre-pass levels are captured into tools/kaizo_baseline.json on first
        run so re-runs recompute from the originals instead of compounding.
  wilds Scale wild encounter levels in src/data/wild_encounters.json so each
        map's strongest wild lands at ~65% of its segment's band ceiling
        (proportional per slot; levels are never lowered). Maps with wild
        tables but no trainers take their segment from wild_only_maps.

All subcommands are idempotent: running them twice produces the same file.
Use --dry-run to print a unified diff instead of rewriting the file.
"""

import argparse
import difflib
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kaizo_pools as kp_pools

REPO_ROOT = Path(__file__).resolve().parent.parent
PARTY_FILE = REPO_ROOT / "src/data/trainers.party"
SEGMENTS_FILE = REPO_ROOT / "tools/kaizo_segments.json"
BASELINE_FILE = REPO_ROOT / "tools/kaizo_baseline.json"
SCRIPT_FILES = [REPO_ROOT / "data/scripts/trainers.inc"] + \
    sorted((REPO_ROOT / "data/maps").glob("*/scripts.inc"))
WILD_FILE = REPO_ROOT / "src/data/wild_encounters.json"
WILD_FRACTION = 0.65  # wild ceiling as a share of the local trainer band ceiling

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


def name_to_species(name):
    """Party display name -> SPECIES_ constant, mirroring trainerproc's
    fprint_constant (alnum kept, lowercase upper-cased, apostrophe dropped,
    everything else -> '_')."""
    out = []
    for c in name.strip():
        if c.isascii() and (c.isalnum()):
            out.append(c.upper())
        elif c == "'":
            continue
        else:
            out.append("_")
    tok = "".join(out)
    return tok if tok.startswith("SPECIES_") else "SPECIES_" + tok


def species_to_name(species):
    """SPECIES_ constant -> a display name that round-trips back through
    name_to_species. Title-cased with underscores as spaces."""
    return species[len("SPECIES_"):].title().replace("_", " ")


def with_species(mon_para, species, level):
    """A minimal mon paragraph for a (possibly changed) species: name + level
    + standard IVs, dropping any prior custom moves/ability that no longer
    apply. Moves auto-generate from the level-up learnset."""
    return [f"{species_to_name(species)}\n",
            f"Level: {level}\n",
            "IVs: 20 HP / 20 Atk / 20 Def / 20 SpA / 20 SpD / 20 Spe\n"]


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
    if trainer.klass in BULK_SKIP_CLASSES or trainer.id in AI_SKIP_TRAINERS:
        return None  # bosses/rivals are hand-anchored; facility brains stay scripted
    map_name = trainer_maps.get(trainer.id)
    if map_name is None and VARIANT_RE.search(trainer.id):
        # VS Seeker rematch party: uplift onto the base trainer's segment so
        # rematch cycles stay level with the first fight (+2/win stacks on top).
        map_name = trainer_maps.get(VARIANT_RE.sub("", trainer.id))
    return map_segments.get(map_name) if map_name else None


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
    # Variety tracking across the whole pass: global usage steers selection
    # toward less-used species; per-map usage caps any species to <=2 trainers.
    global_usage = Counter()
    map_usage = Counter()
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

        # Capture pre-pass levels + original authored species once; later runs
        # recompute from these (the first team_size mons are the authored ones,
        # padding is appended after and this pass rebuilds it every run).
        if trainer.id not in baseline:
            baseline[trainer.id] = {"levels": [level_of(m) for m in mons][:len(mons)],
                                    "team_size": len(mons)}
        base = baseline[trainer.id]
        orig_count = base["team_size"]
        if "species" not in base:
            base["species"] = [name_to_species(species_of(m)) for m in mons[:orig_count]]

        # 1. Level curve: rescale recorded pre-pass levels onto the band.
        band_lo, band_hi = seg["level_band"]
        seg_lo, seg_hi = seg_range[seg_name]
        span = max(1, seg_hi - seg_lo)
        scaled = [min(band_hi, max(band_lo,
                  band_lo + ((lv - seg_lo) * (band_hi - band_lo) + span // 2) // span))
                  for lv in base["levels"]]
        pad_level = min(scaled) if scaled else band_lo

        # 2. Type + evolution-stage constraints.
        map_name = trainer_maps.get(trainer.id)
        gym_type = kp_pools.GYM_TYPE.get(map_name)
        tier = kp_pools.SEGMENT_STAGE.get(seg_name, kp_pools.STAGE_NONE)

        def stage_pool(types):
            pool = []
            for t in (types or []):
                pool += kp_pools.TYPE_POOLS.get(t, [])
            legal = [s for s in dict.fromkeys(pool) if kp_pools.stage_legal(s, tier)]
            return legal or [s for s in kp_pools.GENERAL_POOL if kp_pools.stage_legal(s, tier)]

        def pick(pool, team, seed):
            # prefer species under the per-map cap and least globally used;
            # deterministic tie-break by seed so re-runs are identical.
            cand = [s for s in pool if s not in team and map_usage[(map_name, s)] < 2]
            if not cand:
                cand = [s for s in pool if s not in team] or list(pool)
            best = min(global_usage[s] for s in cand)
            tied = sorted(s for s in cand if global_usage[s] == best)
            return tied[stable_hash(seed) % len(tied)]

        # One type context for the whole trainer: the gym type, else the class
        # theme, else the union of the authored mons' own types, else general.
        if gym_type:
            ctx_types = [gym_type]
        elif trainer.klass in kp_pools.CLASS_THEME:
            ctx_types = [kp_pools.CLASS_THEME[trainer.klass]]
        else:
            at = [t for s in base["species"] if s in kp_pools.DATA
                  for t in kp_pools.types_of(s)]
            ctx_types = list(dict.fromkeys(at)) or None
        ctx_pool = stage_pool(ctx_types)

        # Rebuild authored mons. Gym interiors force the gym type; every segment
        # past gym 3/6 forces the stage rule; and the per-map cap (<=2) plus
        # no-dupe-in-team applies to authored mons too, so an over-used species
        # gets diversified. A mon kept exactly as authored preserves its custom
        # moves/items; any changed mon is rebuilt minimally (species+level+IVs).
        new_mons, team = [], set()
        for i in range(orig_count):
            orig_sp = base["species"][i]
            target = orig_sp
            if orig_sp in kp_pools.DATA:
                if gym_type and gym_type not in kp_pools.types_of(orig_sp):
                    target = pick(ctx_pool, team, trainer.id + f"fix{i}")
                else:
                    target = kp_pools.stage_fix(orig_sp, tier)
                    if gym_type and gym_type not in kp_pools.types_of(target):
                        target = pick(ctx_pool, team, trainer.id + f"fix{i}")
                # variety: diversify a within-team dupe or an over-cap species
                if target in team or map_usage[(map_name, target)] >= 2:
                    target = pick(ctx_pool, team, trainer.id + f"var{i}")
            elif target in team:
                target = pick(ctx_pool, team, trainer.id + f"var{i}")
            if target != orig_sp:
                new_mons.append(with_species(mons[i], target, scaled[i]))
            else:
                new_mons.append(with_level(mons[i], scaled[i]))
            team.add(target)
            global_usage[target] += 1
            map_usage[(map_name, target)] += 1
        mons = new_mons

        # 3. Padding from the same type context, stage-legal, cap-respecting.
        padded = False
        while len(mons) < seg["min_team"]:
            pk = pick(ctx_pool, team, trainer.id + f"pad{len(mons)}")
            mons.append([f"{species_to_name(pk)}\n", f"Level: {pad_level}\n"])
            team.add(pk)
            global_usage[pk] += 1
            map_usage[(map_name, pk)] += 1
            padded = True

        # 4. Held item on the last mon of padded teams.
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


def map_id_to_dirname():
    ids = {}
    for p in (REPO_ROOT / "data/maps").glob("*/map.json"):
        try:
            ids[json.loads(p.read_text())["id"]] = p.parent.name
        except (KeyError, ValueError):
            pass
    return ids


def apply_wilds(dry_run, check):
    config = json.loads(SEGMENTS_FILE.read_text())
    segments = config["segments"]
    seg_of_dir = dict(config["maps"])
    seg_of_dir.update(config.get("wild_only_maps", {}))
    id2dir = map_id_to_dirname()

    old_text = WILD_FILE.read_text()
    data = json.loads(old_text)
    mon_keys = ("land_mons", "water_mons", "rock_smash_mons", "fishing_mons")
    changed, unassigned = [], []
    for group in data["wild_encounter_groups"]:
        if group["label"] != "gWildMonHeaders":
            continue  # frontier facility tables have no overworld map
        for enc in group["encounters"]:
            dirname = id2dir.get(enc["map"])
            seg_name = seg_of_dir.get(dirname)
            if seg_name is None:
                unassigned.append(enc["map"])
                continue
            band_hi = segments[seg_name]["level_band"][1]
            target = max(2, int(band_hi * WILD_FRACTION + 0.5))
            slots = [m for k in mon_keys if k in enc for m in enc[k]["mons"]]
            cur_max = max((m["max_level"] for m in slots), default=0)
            if cur_max == 0 or cur_max >= target:
                continue  # empty table, or already at/above the target: never lower
            before = (min(m["min_level"] for m in slots), cur_max)
            for m in slots:
                for key in ("min_level", "max_level"):
                    m[key] = max(m[key], min(target, int(m[key] * target / cur_max + 0.5)))
                if m["min_level"] > m["max_level"]:
                    m["min_level"] = m["max_level"]
            after = (min(m["min_level"] for m in slots), max(m["max_level"] for m in slots))
            changed.append((dirname, seg_name, before, after))
    if unassigned:
        sys.exit("kaizo_pass wilds: no segment for wild maps: " + ", ".join(sorted(set(unassigned))))

    new_text = json.dumps(data, indent=2) + "\n"
    if new_text == old_text:
        print("no changes")
        return 0
    if check:
        print("kaizo_pass: wild_encounters.json is not up to date", file=sys.stderr)
        return 1
    for dirname, seg_name, before, after in changed:
        print(f"  {dirname:<36} {seg_name:<16} {before[0]}-{before[1]} -> {after[0]}-{after[1]}")
    if dry_run:
        print(f"dry-run: {len(changed)} wild tables would change")
        return 0
    WILD_FILE.write_text(new_text)
    print(f"rewrote {WILD_FILE} ({len(changed)} tables)")
    return 0


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
    parser.add_argument("command", choices=["ai", "bulk", "wilds"])
    parser.add_argument("--dry-run", action="store_true", help="print a diff instead of rewriting")
    parser.add_argument("--check", action="store_true", help="exit 1 if the file would change (CI mode)")
    args = parser.parse_args()

    if args.command == "wilds":
        return apply_wilds(args.dry_run, args.check)

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
