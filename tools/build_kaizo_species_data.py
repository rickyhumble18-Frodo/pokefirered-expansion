#!/usr/bin/env python3
"""Emit tools/kaizo_species_data.json for the trainer type/stage pass.

Merges the ability-fill species cache (types, evolutions, dex number) with
legendary/mythical/UB/paradox flags parsed from the species_info headers, and
marks one canonical species per national-dex number (the base form, i.e. the
shortest enum name for that dex) so alternate forms stay out of the padding
pools. Committed so tools/kaizo_pass.py and CI don't depend on the cache path.
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CACHE = REPO / "tools/.ability_fill_species.json"
OUT = REPO / "tools/kaizo_species_data.json"
GLOB = "src/data/pokemon/species_info/*_families.h"

LEGENDARY_FLAGS = ("isLegendary", "isSubLegendary", "isMythical", "isUltraBeast",
                   "isRestrictedLegendary", "isParadox", "isTotem")


def parse_legendaries():
    """Set of SPECIES_* that carry any legendary-tier flag."""
    leg = set()
    for f in sorted(REPO.glob(GLOB)):
        text = f.read_text()
        # split into [SPECIES_X] = { ... } blocks
        for m in re.finditer(r"\[(SPECIES_\w+)\]\s*=\s*\{", text):
            sp = m.group(1)
            block = text[m.end(): m.end() + 4000]  # flags live near the top
            block = block[: block.find("\n    },")] if "\n    }," in block else block
            if any(re.search(rf"\.{flag}\s*=\s*TRUE", block) for flag in LEGENDARY_FLAGS):
                leg.add(sp)
    return leg


def main():
    cache = json.loads(CACHE.read_text())
    leg = parse_legendaries()

    # canonical (base) form per dex: shortest enum name, ties alphabetical
    by_dex = {}
    for sp, v in cache.items():
        dex = v.get("dex")
        if not dex or not v.get("types"):
            continue
        by_dex.setdefault(dex, []).append(sp)
    canonical = {min(names, key=lambda s: (len(s), s)) for names in by_dex.values()}

    out = {}
    for sp, v in cache.items():
        if not v.get("types") or not v.get("dex"):
            continue
        types = v["types"][0] if v["types"] else ["TYPE_NORMAL", "TYPE_NORMAL"]
        out[sp] = {
            "types": list(dict.fromkeys(types)),          # dedupe mono-types
            "evos": [e for e in v.get("evos", []) if e in cache],
            "dex": v["dex"],
            "legendary": sp in leg,
            "canonical": sp in canonical,
        }
    OUT.write_text(json.dumps(out, sort_keys=True) + "\n")
    print(f"wrote {OUT}: {len(out)} species, {len(leg)} legendary, "
          f"{sum(1 for x in out.values() if x['canonical'])} canonical")


if __name__ == "__main__":
    main()
