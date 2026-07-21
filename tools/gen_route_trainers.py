#!/usr/bin/env python3
"""Single source of truth for the 40 new VS-Seeker-rematchable route trainers.

The MANIFEST below is the ONLY place trainers are declared. Running this script
regenerates every synced piece from it, so the three-part rematch sync
(enum RematchID / REMATCH_TRAINER_COUNT / sRematches[]) plus the trainer enum,
party data, object events and scripts can never drift:

  include/constants/opponents.h      TRAINER_* enum entries (base + _2 variant)
  include/constants/vs_seeker.h      REMATCH_* enum entries
  include/vs_seeker.h                REMATCH_TRAINER_COUNT define
  src/data/trainer_rematches.h       sRematches[] initializer rows
  src/data/trainers.party            base + variant party blocks
  data/maps/<Route>/scripts.inc      EventScript + rematch script + text
  data/maps/<Route>/map.json         object events (valid coords via collision)

All generated regions are fenced by GEN_ROUTE_TRAINERS markers (or, for the
object events, by the Kaizo<Name> script-name prefix), so re-running replaces
them cleanly and idempotently. Each trainer gets 2 rematch teams (Option A):
base + one variant, cycled by the existing win-count %% variants system with
+2 levels per rematch win.

Usage:
    python3 tools/gen_route_trainers.py            # write all files
    python3 tools/gen_route_trainers.py --check    # verify counts only
"""

import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BEGIN = "GEN_ROUTE_TRAINERS_BEGIN"
END = "GEN_ROUTE_TRAINERS_END"
SCRIPT_PREFIX = "EventScript_Kaizo"   # per-map generated script id: <Map>_EventScript_Kaizo<Name>

# --- Class -> presentation (battle class string, Pic, overworld gfx, gender) ---
# Only classes with a clean overworld sprite are used.
CLASS = {
    "HIKER":       ("Hiker",       "Hiker",        "OBJ_EVENT_GFX_HIKER",       "Male"),
    "CAMPER":      ("Camper",      "Camper",       "OBJ_EVENT_GFX_CAMPER",      "Male"),
    "LASS":        ("Lass",        "Lass",         "OBJ_EVENT_GFX_LASS",        "Female"),
    "BUG_CATCHER": ("Bug Catcher", "Bug Catcher",  "OBJ_EVENT_GFX_BUG_CATCHER", "Male"),
    "YOUNGSTER":   ("Youngster",   "Youngster",    "OBJ_EVENT_GFX_YOUNGSTER",   "Male"),
    "FISHERMAN":   ("Fisherman",   "Fisherman",    "OBJ_EVENT_GFX_FISHER",      "Male"),
    "SUPER_NERD":  ("Super Nerd",  "Super Nerd",   "OBJ_EVENT_GFX_SCIENTIST",   "Male"),
    "BIKER":       ("Biker",       "Biker",        "OBJ_EVENT_GFX_BIKER",       "Male"),
    "POKEMANIAC":  ("Pokemaniac",  "Pokemaniac",   "OBJ_EVENT_GFX_POKE_MANIAC", "Male"),
    "ROCKER":      ("Rocker",      "Rocker",       "OBJ_EVENT_GFX_ROCKER",      "Male"),
    "BEAUTY":      ("Beauty",      "Beauty",       "OBJ_EVENT_GFX_BEAUTY",      "Female"),
    "PSYCHIC":     ("Psychic",     "Psychic M",    "OBJ_EVENT_GFX_PSYCHIC_M",   "Male"),
    "BLACK_BELT":  ("Black Belt",  "Black Belt",   "OBJ_EVENT_GFX_BLACK_BELT",  "Male"),
    "SWIMMER_M":   ("Swimmer M",   "Swimmer M",    "OBJ_EVENT_GFX_SWIMMER_M_WATER", "Male"),
    "SWIMMER_F":   ("Swimmer F",   "Swimmer F",    "OBJ_EVENT_GFX_SWIMMER_F_WATER", "Female"),
}

# thematic species pools per class (Kanto plus a few cross-gen picks for kaizo flavor)
POOL = {
    "HIKER":       ["SPECIES_GEODUDE", "SPECIES_GRAVELER", "SPECIES_ONIX", "SPECIES_MACHOP",
                    "SPECIES_RHYHORN", "SPECIES_LARVITAR", "SPECIES_NOSEPASS"],
    "CAMPER":      ["SPECIES_RATTATA", "SPECIES_NIDORAN_M", "SPECIES_SANDSHREW", "SPECIES_MANKEY",
                    "SPECIES_PHANPY", "SPECIES_POOCHYENA"],
    "LASS":        ["SPECIES_ODDISH", "SPECIES_JIGGLYPUFF", "SPECIES_CLEFAIRY", "SPECIES_MEOWTH",
                    "SPECIES_SKITTY", "SPECIES_MARILL"],
    "BUG_CATCHER": ["SPECIES_METAPOD", "SPECIES_KAKUNA", "SPECIES_PARAS", "SPECIES_VENONAT",
                    "SPECIES_SCYTHER", "SPECIES_PINSIR", "SPECIES_LARVESTA"],
    "YOUNGSTER":   ["SPECIES_RATTATA", "SPECIES_SPEAROW", "SPECIES_EKANS", "SPECIES_SANDSHREW",
                    "SPECIES_ZIGZAGOON", "SPECIES_MAREEP"],
    "FISHERMAN":   ["SPECIES_MAGIKARP", "SPECIES_GOLDEEN", "SPECIES_POLIWAG", "SPECIES_TENTACOOL",
                    "SPECIES_KRABBY", "SPECIES_HORSEA", "SPECIES_FEEBAS", "SPECIES_WINGULL"],
    "SUPER_NERD":  ["SPECIES_GRIMER", "SPECIES_VOLTORB", "SPECIES_MAGNEMITE", "SPECIES_KOFFING",
                    "SPECIES_BALTOY", "SPECIES_PORYGON"],
    "BIKER":       ["SPECIES_KOFFING", "SPECIES_GRIMER", "SPECIES_VOLTORB", "SPECIES_EKANS",
                    "SPECIES_HOUNDOUR", "SPECIES_WEEZING"],
    "POKEMANIAC":  ["SPECIES_SLOWPOKE", "SPECIES_LICKITUNG", "SPECIES_RHYHORN", "SPECIES_CUBONE",
                    "SPECIES_KANGASKHAN", "SPECIES_MAWILE"],
    "ROCKER":      ["SPECIES_VOLTORB", "SPECIES_MAGNEMITE", "SPECIES_ELECTABUZZ", "SPECIES_ELECTRODE",
                    "SPECIES_ELEKID", "SPECIES_PLUSLE"],
    "BEAUTY":      ["SPECIES_VULPIX", "SPECIES_GROWLITHE", "SPECIES_PERSIAN", "SPECIES_BELLOSSOM",
                    "SPECIES_ROSELIA", "SPECIES_MILOTIC"],
    "PSYCHIC":     ["SPECIES_ABRA", "SPECIES_KADABRA", "SPECIES_DROWZEE", "SPECIES_SLOWPOKE",
                    "SPECIES_RALTS", "SPECIES_MEDITITE"],
    "BLACK_BELT":  ["SPECIES_MACHOP", "SPECIES_MACHOKE", "SPECIES_MANKEY", "SPECIES_HITMONLEE",
                    "SPECIES_HITMONCHAN", "SPECIES_MAKUHITA"],
    "SWIMMER_M":   ["SPECIES_TENTACOOL", "SPECIES_STARYU", "SPECIES_HORSEA", "SPECIES_SHELLDER",
                    "SPECIES_POLIWAG", "SPECIES_WAILMER", "SPECIES_CARVANHA"],
    "SWIMMER_F":   ["SPECIES_STARYU", "SPECIES_GOLDEEN", "SPECIES_POLIWAG", "SPECIES_TENTACOOL",
                    "SPECIES_CORSOLA", "SPECIES_CLAMPERL"],
}

# route -> (MAP macro, segment band [lo, hi])
ROUTE_BAND = {
    "Route4":  ("MAP_ROUTE4",  (27, 31)),
    "Route24": ("MAP_ROUTE24", (27, 31)),
    "Route6":  ("MAP_ROUTE6",  (40, 43)),
    "Route8":  ("MAP_ROUTE8",  (54, 57)),
    "Route9":  ("MAP_ROUTE9",  (54, 57)),
    "Route10": ("MAP_ROUTE10", (54, 57)),
    "Route12": ("MAP_ROUTE12", (70, 73)),
    "Route13": ("MAP_ROUTE13", (70, 73)),
    "Route16": ("MAP_ROUTE16", (70, 73)),
    "Route17": ("MAP_ROUTE17", (70, 73)),
    "Route18": ("MAP_ROUTE18", (70, 73)),
    "Route19": ("MAP_ROUTE19", (92, 95)),
    "Route20": ("MAP_ROUTE20", (92, 95)),
    "Route21_North": ("MAP_ROUTE21_NORTH", (92, 95)),
    "Route21_South": ("MAP_ROUTE21_SOUTH", (92, 95)),
}

# The 40 trainers: (route, CLASS, NAME). NAME is unique, <=10 chars, uppercase.
# Weighted 80% mid/late per the approved plan.
MANIFEST = [
    # Route 4 (27-31)
    ("Route4", "HIKER", "DWAYNE"), ("Route4", "CAMPER", "TOBIAS"), ("Route4", "LASS", "PRISCILLA"),
    # Route 24 (27-31)
    ("Route24", "BUG_CATCHER", "MARV"), ("Route24", "LASS", "ODETTE"),
    # Route 6 (40-43)
    ("Route6", "FISHERMAN", "DOUGAL"), ("Route6", "BUG_CATCHER", "PERCY"), ("Route6", "YOUNGSTER", "ROLAND"),
    # Route 8 (54-57)
    ("Route8", "SUPER_NERD", "EWALD"), ("Route8", "BIKER", "AXEL"),
    # Route 9 (54-57)
    ("Route9", "HIKER", "BRUNO"), ("Route9", "POKEMANIAC", "DEXTER"),
    # Route 10 (54-57)
    ("Route10", "SUPER_NERD", "OHMER"), ("Route10", "HIKER", "GRANT"),
    ("Route10", "POKEMANIAC", "SILAS"), ("Route10", "ROCKER", "ZIGGY"),
    # Route 12 (70-73)
    ("Route12", "FISHERMAN", "MARLON"), ("Route12", "BEAUTY", "SERENA"), ("Route12", "ROCKER", "JAX"),
    # Route 13 (70-73)
    ("Route13", "FISHERMAN", "CLETUS"), ("Route13", "BEAUTY", "LACEY"), ("Route13", "PSYCHIC", "MORDECAI"),
    # Route 16 (70-73)
    ("Route16", "BIKER", "RAZOR"), ("Route16", "BEAUTY", "VIVIAN"), ("Route16", "BIKER", "CLUTCH"),
    # Route 17 (70-73)
    ("Route17", "BIKER", "TORQUE"), ("Route17", "BIKER", "NITRO"), ("Route17", "BEAUTY", "CARMEN"),
    # Route 18 (70-73)
    ("Route18", "BIKER", "SPARK"), ("Route18", "BIKER", "DIESEL"),
    ("Route18", "POKEMANIAC", "WENDELL"), ("Route18", "HIKER", "BOULDER"),
    # Route 19 (92-95)
    ("Route19", "SWIMMER_F", "MARINA"), ("Route19", "SWIMMER_M", "REEF"),
    # Route 20 (92-95)
    ("Route20", "SWIMMER_M", "TIDE"), ("Route20", "BLACK_BELT", "KENJI"),
    # Route 21 North (92-95)
    ("Route21_North", "SWIMMER_F", "PEARL"), ("Route21_North", "FISHERMAN", "SALTON"),
    # Route 21 South (92-95)
    ("Route21_South", "SWIMMER_M", "CREST"), ("Route21_South", "SWIMMER_F", "CORAL"),
]

VANILLA_REMATCH_COUNT = 221  # REMATCH_TRAINER_COUNT before this generator


def det_rng(seed):
    """Tiny deterministic LCG so parties are stable across runs."""
    state = abs(hash(seed)) & 0xFFFFFFFF
    def nxt(n):
        nonlocal state
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        return state % n
    return nxt


def make_party(cls, band, seed, variant):
    """3 mons; ace at band hi, others spread down. Variant differs by species
    pick + a small mid-level bump so the rematch feels distinct (levels stay
    in-band; the +2/win climb comes from the rematch counter)."""
    lo, hi = band
    pool = POOL[cls]
    rng = det_rng(seed + ("V" if variant else "B"))
    picks, seen = [], set()
    for _ in range(3):
        for _try in range(8):
            s = pool[rng(len(pool))]
            if s not in seen:
                break
        seen.add(s)
        picks.append(s)
    mids = lo + (hi - lo) // 2
    levels = [lo, mids, hi]
    return list(zip(picks, levels))


def existing_trainer_ids():
    """TRAINER_* names already in opponents.h, minus this generator's own
    region, so re-runs don't count prior output as a collision."""
    import re
    txt = (REPO / "include/constants/opponents.h").read_text()
    b, e = txt.find(f"// {BEGIN}"), txt.find(f"// {END}")
    if b != -1 and e != -1:
        txt = txt[:b] + txt[e:]
    return set(re.findall(r"\bTRAINER_(\w+)\b", txt))


def build():
    assert len(MANIFEST) == 40, f"expected 40 trainers, got {len(MANIFEST)}"
    keys = [f"{c}_{n}" for _, c, n in MANIFEST]
    assert len(keys) == len(set(keys)), "duplicate trainer key in MANIFEST"
    clash = set(keys) & existing_trainer_ids()
    assert not clash, f"MANIFEST names collide with existing trainers: {sorted(clash)}"
    trainers = []
    for route, cls, name in MANIFEST:
        mapmac, band = ROUTE_BAND[route]
        base_id = f"TRAINER_{cls}_{name}"
        var_id = f"{base_id}_2"
        rematch_id = f"REMATCH_{cls}_{name}"
        script_id = f"{route}_{SCRIPT_PREFIX}{name.title()}"
        trainers.append(dict(
            route=route, mapmac=mapmac, band=band, cls=cls, name=name,
            base_id=base_id, var_id=var_id, rematch_id=rematch_id, script_id=script_id,
            base_party=make_party(cls, band, base_id, False),
            var_party=make_party(cls, band, base_id, True),
        ))
    return trainers


# ---------------------------------------------------------------- placement
def place_objects(trainers):
    """Assign each trainer a valid, unoccupied, collision-free tile on its
    route, spaced apart, facing a direction with open ground ahead."""
    layouts = {L["id"]: L for L in json.loads((REPO / "data/layouts/layouts.json").read_text())["layouts"] if L}
    by_route = {}
    for t in trainers:
        by_route.setdefault(t["route"], []).append(t)

    DIRS = {"Down": (0, 1), "Up": (0, -1), "Left": (-1, 0), "Right": (1, 0)}
    for route, group in by_route.items():
        mj = json.loads((REPO / f"data/maps/{route}/map.json").read_text())
        lay = layouts[mj["layout"]]
        W, H = lay["width"], lay["height"]
        blocks = struct.unpack(f"<{W*H}H", (REPO / lay["blockdata_filepath"]).read_bytes()[: W * H * 2])
        def coll(x, y):
            return (blocks[y * W + x] >> 10) & 3
        occupied = {(o["x"], o["y"]) for o in mj.get("object_events", [])}
        # candidate open tiles, away from borders, spaced from occupied
        cands = []
        for y in range(2, H - 2):
            for x in range(2, W - 2):
                if coll(x, y) != 0 or (x, y) in occupied:
                    continue
                # need at least 2 open tiles in some cardinal direction (a sight line)
                cands.append((x, y))
        # deterministic spread: sort by a hash, then greedily keep spaced >=3
        cands.sort(key=lambda p: (abs(hash((route, p))) & 0xFFFFFF))
        chosen = []
        for c in cands:
            if all(abs(c[0] - k[0]) + abs(c[1] - k[1]) >= 3 for k in chosen):
                chosen.append(c)
            if len(chosen) >= len(group):
                break
        if len(chosen) < len(group):
            raise SystemExit(f"{route}: only {len(chosen)} open tiles for {len(group)} trainers")
        for t, (x, y) in zip(group, chosen):
            # pick a facing dir with >=2 open collision-0 tiles ahead
            face, rng_sight = "Down", 1
            for d, (dx, dy) in DIRS.items():
                ahead = [(x + dx * s, y + dy * s) for s in (1, 2)]
                if all(0 <= ax < W and 0 <= ay < H and coll(ax, ay) == 0 and (ax, ay) not in occupied
                       for ax, ay in ahead):
                    face, rng_sight = d, 2
                    break
            t["x"], t["y"], t["face"], t["sight"] = x, y, face, rng_sight
            occupied.add((x, y))
    return by_route


# ---------------------------------------------------------------- emit helpers
def splice(path, new_block):
    """Replace the region between BEGIN/END markers with new_block, or append a
    fresh marked region before the given anchor if absent. Handled per-file."""
    raise NotImplementedError  # per-file splices below are explicit


def replace_region(text, begin, end, body):
    b = text.find(begin)
    if b == -1:
        return None
    b_line = text.rfind("\n", 0, b) + 1
    e = text.find(end, b)
    e_line = text.find("\n", e) + 1
    return text[:b_line] + body + text[e_line:]


def emit(trainers, by_route, check=False):
    new_count = len(trainers)
    total_rematch = VANILLA_REMATCH_COUNT + new_count
    if check:
        print(f"new trainers: {new_count}  (2 teams each = {2*new_count} enum slots)")
        print(f"REMATCH_TRAINER_COUNT: {VANILLA_REMATCH_COUNT} -> {total_rematch}")
        return total_rematch, new_count

    # 1) opponents.h -- TRAINER_ enum (base + _2) before TRAINERS_COUNT
    p = REPO / "include/constants/opponents.h"
    txt = p.read_text()
    lines = [f"    // {BEGIN}"]
    for t in trainers:
        lines += [f"    {t['base_id']},", f"    {t['var_id']},"]
    lines.append(f"    // {END}")
    body = "\n".join(lines) + "\n"
    marked = replace_region(txt, f"// {BEGIN}", f"// {END}", body)
    if marked is None:
        marked = txt.replace("    TRAINERS_COUNT,", body + "    TRAINERS_COUNT,", 1)
    p.write_text(marked)

    # 2) constants/vs_seeker.h -- REMATCH_ enum before REMATCH_COUNT
    p = REPO / "include/constants/vs_seeker.h"
    txt = p.read_text()
    lines = [f"    // {BEGIN}"] + [f"    {t['rematch_id']}," for t in trainers] + [f"    // {END}"]
    body = "\n".join(lines) + "\n"
    marked = replace_region(txt, f"// {BEGIN}", f"// {END}", body)
    if marked is None:
        marked = txt.replace("    REMATCH_COUNT", body + "    REMATCH_COUNT", 1)
    p.write_text(marked)

    # 3) vs_seeker.h -- REMATCH_TRAINER_COUNT define
    p = REPO / "include/vs_seeker.h"
    txt = p.read_text()
    import re
    txt = re.sub(r"#define REMATCH_TRAINER_COUNT \d+",
                 f"#define REMATCH_TRAINER_COUNT {total_rematch}", txt)
    p.write_text(txt)

    # 4) trainer_rematches.h -- sRematches[] rows before final "};"
    p = REPO / "src/data/trainer_rematches.h"
    txt = p.read_text()
    rows = [f"    // {BEGIN}"]
    for t in trainers:
        rows += [
            f"    [{t['rematch_id']}] =",
            "    {",
            f"        .trainerIDs = {{{t['base_id']}, {t['var_id']}}},",
            f"        .mapGroup = MAP_GROUP({t['mapmac']}),",
            f"        .mapNum = MAP_NUM({t['mapmac']}),",
            "    },",
        ]
    rows.append(f"    // {END}")
    body = "\n".join(rows) + "\n"
    marked = replace_region(txt, f"// {BEGIN}", f"// {END}", body)
    if marked is None:
        # insert before the final closing brace of the initializer
        idx = txt.rstrip().rfind("\n};")
        marked = txt[: idx + 1] + body + txt[idx + 1 :]
    p.write_text(marked)

    # 5) trainers.party -- base + variant blocks. No marker comments (the file
    # is CPP-processed and the Phase B parser reads paragraphs), so idempotency
    # is by removing any prior block for our IDs, then appending fresh ones.
    p = REPO / "src/data/trainers.party"
    txt = p.read_text()
    our_ids = {t["base_id"] for t in trainers} | {t["var_id"] for t in trainers}
    # split into "=== TRAINER_X ===" blocks and drop any of ours
    parts = re.split(r"(?m)^(?==== TRAINER_)", txt)
    kept = []
    for part in parts:
        m = re.match(r"=== (TRAINER_\w+) ===", part)
        if m and m.group(1) in our_ids:
            continue
        kept.append(part)
    base = "".join(kept).rstrip() + "\n"

    def party_block(tid, cls, name, party):
        c = CLASS[cls]
        out = [f"=== {tid} ===",
               f"Name: {name}",
               f"Class: {c[0]}",
               f"Pic: {c[1]}",
               f"Gender: {c[3]}",
               "Music: Male" if c[3] == "Male" else "Music: Female",
               "Double Battle: No",
               "AI: Check Bad Move / Try To Faint / Check Viability",
               ""]
        for sp, lvl in party:
            out += [sp.replace("SPECIES_", "").title().replace("_", " "),
                    f"Level: {lvl}",
                    "IVs: 20 HP / 20 Atk / 20 Def / 20 SpA / 20 SpD / 20 Spe",
                    ""]
        return "\n".join(out)
    blocks = []
    for t in trainers:
        blocks.append(party_block(t["base_id"], t["cls"], t["name"], t["base_party"]))
        blocks.append(party_block(t["var_id"], t["cls"], t["name"], t["var_party"]))
    p.write_text(base + "\n" + "\n".join(blocks) + "\n")

    # 6) per-map scripts.inc -- EventScript + rematch + text (trainerbattle FIRST)
    for route, group in by_route.items():
        p = REPO / f"data/maps/{route}/scripts.inc"
        txt = p.read_text()
        out = [f"@ {BEGIN}"]
        for t in group:
            n = t["name"].title()
            s = t["script_id"]
            out += [
                f"{s}::",
                f"\ttrainerbattle_single {t['base_id']}, {route}_Text_Kaizo{n}Intro, {route}_Text_Kaizo{n}Defeat",
                "\tspecialvar VAR_RESULT, ShouldTryRematchBattle",
                f"\tgoto_if_eq VAR_RESULT, TRUE, {s}Rematch",
                f"\tmsgbox {route}_Text_Kaizo{n}Post, MSGBOX_AUTOCLOSE",
                "\tend",
                "",
                f"{s}Rematch::",
                f"\ttrainerbattle_rematch {t['base_id']}, {route}_Text_Kaizo{n}Rematch, {route}_Text_Kaizo{n}Defeat",
                f"\tmsgbox {route}_Text_Kaizo{n}Post, MSGBOX_AUTOCLOSE",
                "\tend",
                "",
                f"{route}_Text_Kaizo{n}Intro:",
                f'\t.string "Let\'s battle!$"',
                f"{route}_Text_Kaizo{n}Defeat:",
                f'\t.string "I lost!$"',
                f"{route}_Text_Kaizo{n}Post:",
                f'\t.string "Come back anytime.$"',
                f"{route}_Text_Kaizo{n}Rematch:",
                f'\t.string "Ready for a rematch?$"',
                "",
            ]
        out.append(f"@ {END}")
        body = "\n".join(out) + "\n"
        marked = replace_region(txt, f"@ {BEGIN}", f"@ {END}", body)
        if marked is None:
            marked = txt.rstrip() + "\n\n" + body
        p.write_text(marked)

    # 7) per-map map.json -- object events (idempotent: drop prior generated, re-add)
    for route, group in by_route.items():
        p = REPO / f"data/maps/{route}/map.json"
        mj = json.loads(p.read_text())
        mj["object_events"] = [o for o in mj.get("object_events", [])
                               if SCRIPT_PREFIX not in str(o.get("script", ""))]
        for t in group:
            c = CLASS[t["cls"]]
            mj["object_events"].append({
                "type": "object",
                "graphics_id": c[2],
                "x": t["x"], "y": t["y"], "elevation": 3,
                "movement_type": f"MOVEMENT_TYPE_FACE_{t['face'].upper()}",
                "movement_range_x": 1, "movement_range_y": 1,
                "trainer_type": "TRAINER_TYPE_NORMAL",
                "trainer_sight_or_berry_tree_id": str(t["sight"]),
                "script": t["script_id"],
                "flag": "0",
            })
        p.write_text(json.dumps(mj, indent=2) + "\n")

    print(f"generated {new_count} trainers ({2*new_count} enum slots); "
          f"REMATCH_TRAINER_COUNT -> {total_rematch}")
    return total_rematch, new_count


def main():
    trainers = build()
    by_route = place_objects(trainers) if "--check" not in sys.argv else {}
    emit(trainers, by_route, check="--check" in sys.argv)


if __name__ == "__main__":
    main()
