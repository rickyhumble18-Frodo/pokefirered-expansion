#!/usr/bin/env python3
"""Type pools, evolution-stage rules and gym typing for the Phase B trainer pass.

Consumes tools/kaizo_species_data.json (built by build_kaizo_species_data.py).
Pure data + helpers; kaizo_pass.py drives selection and idempotency.
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = json.loads((REPO / "tools/kaizo_species_data.json").read_text())

SKIP_SPECIES = {"SPECIES_NONE", "SPECIES_EGG"}

# --- evolution graph -------------------------------------------------------
_EVOS = {sp: v["evos"] for sp, v in DATA.items()}
_PRE = {}
for _sp, _es in _EVOS.items():
    for _e in _es:
        _PRE.setdefault(_e, []).append(_sp)


def types_of(sp):
    return DATA.get(sp, {}).get("types", ["TYPE_NORMAL"])


def is_first(sp):
    return sp not in _PRE


def is_final(sp):
    return not _EVOS.get(sp)


def _roots(sp, seen=None):
    seen = seen if seen is not None else set()
    if sp in seen or sp not in _PRE:
        return {sp}
    seen.add(sp)
    out = set()
    for p in _PRE[sp]:
        out |= _roots(p, seen)
    return out or {sp}


def _depth(sp, seen=None):
    seen = seen if seen is not None else set()
    children = [c for c in _EVOS.get(sp, []) if c not in seen]
    if not children:
        return 1
    seen = seen | {sp}
    return 1 + max(_depth(c, seen) for c in children)


def line_length(sp):
    return max(_depth(r) for r in _roots(sp))


def first_of_three_plus(sp):
    """First stage of a 3+ stage line (Charmander, Abra, Dratini, Pichu...)."""
    return is_first(sp) and line_length(sp) >= 3


def _canonical_branch(children):
    canon = [c for c in children if DATA.get(c, {}).get("canonical")] or children
    return sorted(canon)[0]


def evolve_once(sp):
    """One step forward along a canonical branch; sp itself if final."""
    return _canonical_branch(_EVOS[sp]) if _EVOS.get(sp) else sp


def final_form(sp):
    """Walk to a terminal along canonical branches."""
    cur = sp
    seen = set()
    while _EVOS.get(cur) and cur not in seen:
        seen.add(cur)
        cur = _canonical_branch(_EVOS[cur])
    return cur


# --- stage tiers by segment ------------------------------------------------
# before gym 3 (Vermilion): anything. after gym 3 through gym 6 (Fuchsia): no
# first-stage-of-3 lines. after gym 6: fully evolved (single-stage counts).
STAGE_NONE, STAGE_NO_BABIES, STAGE_FINAL = 0, 1, 2
SEGMENT_STAGE = {
    "early": STAGE_NONE,
    "brock_misty": STAGE_NONE,
    "misty_surge": STAGE_NONE,
    "surge_erika": STAGE_NO_BABIES,
    "erika_koga": STAGE_NO_BABIES,
    "koga_sabrina": STAGE_FINAL,
    "sabrina_blaine": STAGE_FINAL,
    "blaine_giovanni": STAGE_FINAL,
    "victory_road": STAGE_FINAL,
}


def stage_legal(sp, tier):
    if tier == STAGE_NONE:
        return True
    if tier == STAGE_NO_BABIES:
        return not first_of_three_plus(sp)
    return is_final(sp)  # STAGE_FINAL; single-stage is final


def stage_fix(sp, tier):
    """Evolve sp to the nearest stage-legal form of its own line."""
    if stage_legal(sp, tier):
        return sp
    if tier == STAGE_NO_BABIES:
        cand = evolve_once(sp)
        return cand if stage_legal(cand, tier) else final_form(sp)
    return final_form(sp)  # STAGE_FINAL


# --- gym typing ------------------------------------------------------------
GYM_TYPE = {
    "PewterCity_Gym": "TYPE_ROCK",
    "CeruleanCity_Gym": "TYPE_WATER",
    "VermilionCity_Gym": "TYPE_ELECTRIC",
    "CeladonCity_Gym": "TYPE_GRASS",
    "FuchsiaCity_Gym": "TYPE_POISON",
    "SaffronCity_Gym": "TYPE_PSYCHIC",
    "CinnabarIsland_Gym": "TYPE_FIRE",
    "ViridianCity_Gym": "TYPE_GROUND",
}

# --- route trainer class -> preferred padding type -------------------------
CLASS_THEME = {
    "Bug Catcher": "TYPE_BUG",
    "Swimmer M": "TYPE_WATER", "Swimmer F": "TYPE_WATER",
    "Fisherman": "TYPE_WATER", "Sailor": "TYPE_WATER", "Tuber F": "TYPE_WATER",
    "Tuber M": "TYPE_WATER",
    "Hiker": "TYPE_ROCK", "Ruin Maniac": "TYPE_ROCK",
    "Biker": "TYPE_POISON", "Team Rocket": "TYPE_POISON",
    "Rocker": "TYPE_ELECTRIC", "Engineer": "TYPE_ELECTRIC",
    "Psychic": "TYPE_PSYCHIC",
    "Black Belt": "TYPE_FIGHTING", "Cue Ball": "TYPE_FIGHTING",
    "Crush Girl": "TYPE_FIGHTING", "Crush Kin": "TYPE_FIGHTING",
    "Bird Keeper": "TYPE_FLYING",
    "Channeler": "TYPE_GHOST",
    "Burglar": "TYPE_FIRE",
    "Aroma Lady": "TYPE_GRASS", "Pkmn Ranger": "TYPE_GRASS",
    "Beauty": "TYPE_NORMAL",
}


def type_pool(t):
    """Canonical, non-legendary species of type t (base forms only)."""
    return [sp for sp, v in DATA.items()
            if sp not in SKIP_SPECIES and v["canonical"] and not v["legendary"]
            and t in v["types"]]


# precompute once
TYPE_POOLS = {t: sorted(type_pool(t)) for t in {
    "TYPE_NORMAL", "TYPE_FIRE", "TYPE_WATER", "TYPE_ELECTRIC", "TYPE_GRASS",
    "TYPE_ICE", "TYPE_FIGHTING", "TYPE_POISON", "TYPE_GROUND", "TYPE_FLYING",
    "TYPE_PSYCHIC", "TYPE_BUG", "TYPE_ROCK", "TYPE_GHOST", "TYPE_DRAGON",
    "TYPE_DARK", "TYPE_STEEL", "TYPE_FAIRY",
}}
GENERAL_POOL = sorted({sp for pool in TYPE_POOLS.values() for sp in pool})
