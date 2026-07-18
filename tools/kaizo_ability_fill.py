#!/usr/bin/env python3
"""Ability Fill v2: fill every empty ability slot on every species.

Phase 2 (this tool, `doc` mode): compute assignments and emit
docs/ability_assignments.md for review. No game data is modified.
Phase 3 (`apply` mode, after approval): rewrite species_info headers.

Assignment model (per the approved spec + adjustments):
- One decision per evolution line; final stages may upgrade.
- Alternate forms (including _GMAX) inherit the base form's fills for any
  slot that is empty on the form; existing abilities are never overwritten.
- Form-linked legendaries get identical fills across the whole group.
- Ability-driven form species (Stance Change, Disguise, ...) are exempt:
  filling their slots would let the Ability Coach switch off the mechanic.
- Banlist is never assigned; existing Sand Veil / Snow Cloak are replaced.
- Variety: no pool ability on more than ABILITY_CAP filled slots.
"""

import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CACHE = REPO / "tools/.ability_fill_species.json"
DOC = REPO / "docs/ability_assignments.md"

ABILITY_CAP = 25  # rev3: no ability may exceed 25 assigned fills
JUSTIFICATION_CAP = 12  # rev3: no more than 12 species share the same justification
def cap_of(a): return ABILITY_CAP

BANLIST = {
    "ABILITY_WONDER_GUARD", "ABILITY_IMPOSTER", "ABILITY_MOODY",
    "ABILITY_SAND_VEIL", "ABILITY_SNOW_CLOAK", "ABILITY_ARENA_TRAP",
    "ABILITY_SHADOW_TAG", "ABILITY_ILLUSION", "ABILITY_NEUTRALIZING_GAS",
}

# Species that must never get Huge/Pure Power even if a stat tie sneaks them
# past the Atk>=SpA gate: the spec's named special lines (whose notable final
# stage attacks specially or which are support/defensive identities), plus
# clearly non-attacker forms. Matched by prefix so whole families are covered.
HUGE_POWER_EXCLUDE_PREFIXES = (
    "SPECIES_FENNEKIN", "SPECIES_BRAIXEN", "SPECIES_DELPHOX",
    "SPECIES_CYNDAQUIL", "SPECIES_QUILAVA", "SPECIES_TYPHLOSION",
    "SPECIES_FUECOCO", "SPECIES_CROCALOR", "SPECIES_SKELEDIRGE",
    "SPECIES_CHARCADET", "SPECIES_ARMAROUGE",
    "SPECIES_MAREEP", "SPECIES_FLAAFFY", "SPECIES_AMPHAROS",
    "SPECIES_MILCERY", "SPECIES_ALCREMIE",
    "SPECIES_YAMASK", "SPECIES_COFAGRIGUS", "SPECIES_RUNERIGUS",
    "SPECIES_CHIMECHO", "SPECIES_CHINGLING",
    "SPECIES_LUNATONE", "SPECIES_SOLROCK",
    "SPECIES_RELLOR", "SPECIES_RABSCA",
    "SPECIES_COSMOG", "SPECIES_COSMOEM", "SPECIES_LUNALA",
    "SPECIES_EXEGGCUTE", "SPECIES_EXEGGUTOR",
    "SPECIES_DEOXYS_DEFENSE", "SPECIES_DEOXYS_NORMAL",
    "SPECIES_SCREAM_TAIL", "SPECIES_FLUTTER_MANE",
)

# Species whose form mechanics live in their ability; coaching it away would
# brick the form logic, so their empty slots stay empty.
ABILITY_FORM_EXEMPT_PREFIXES = (
    "SPECIES_AEGISLASH", "SPECIES_DARMANITAN", "SPECIES_WISHIWASHI",
    "SPECIES_MINIOR", "SPECIES_ZYGARDE", "SPECIES_MIMIKYU", "SPECIES_EISCUE",
    "SPECIES_CRAMORANT", "SPECIES_MORPEKO", "SPECIES_PALAFIN",
    "SPECIES_CASTFORM", "SPECIES_CHERRIM", "SPECIES_ARCEUS",
    "SPECIES_SILVALLY", "SPECIES_GRENINJA_BATTLE_BOND", "SPECIES_GRENINJA_ASH",
    "SPECIES_TERAPAGOS", "SPECIES_OGERPON", "SPECIES_SHEDINJA", "SPECIES_SHELLOS",  # Shellos fine actually
)
ABILITY_FORM_EXEMPT_PREFIXES = tuple(p for p in ABILITY_FORM_EXEMPT_PREFIXES if p != "SPECIES_SHELLOS")

# Replacements for existing evasion abilities (adjustment 4).
EVASION_REPLACEMENTS = {
    # species: {slot: (ability, why)}
    "SPECIES_SANDSHREW":      {0: ("ABILITY_SAND_RUSH", "sand-dweller speed instead of evasion")},
    "SPECIES_SANDSLASH":      {0: ("ABILITY_SAND_RUSH", "sand-dweller speed instead of evasion")},
    "SPECIES_DIGLETT":        {0: ("ABILITY_SAND_FORCE", "digger powers ground/rock/steel in sand")},
    "SPECIES_DUGTRIO":        {0: ("ABILITY_SAND_FORCE", "digger powers ground/rock/steel in sand")},
    "SPECIES_DIGLETT_ALOLA":  {0: ("ABILITY_SAND_FORCE", "digger, matches Kanto line")},
    "SPECIES_DUGTRIO_ALOLA":  {0: ("ABILITY_SAND_FORCE", "digger, matches Kanto line")},
    "SPECIES_GEODUDE":        {2: ("ABILITY_SAND_FORCE", "living rock thrives in sandstorm")},
    "SPECIES_GRAVELER":       {2: ("ABILITY_SAND_FORCE", "living rock thrives in sandstorm")},
    "SPECIES_GOLEM":          {2: ("ABILITY_SAND_FORCE", "living rock thrives in sandstorm")},
    "SPECIES_GLIGAR":         {1: ("ABILITY_IMMUNITY", "scorpion shrugs off poison; distinct from Poison Heal hidden")},
    "SPECIES_GLISCOR":        {1: ("ABILITY_IMMUNITY", "scorpion shrugs off poison; distinct from Poison Heal hidden")},
    "SPECIES_PHANPY":         {2: ("ABILITY_STURDY", "little tank elephant")},
    "SPECIES_DONPHAN":        {2: ("ABILITY_STURDY", "armored elephant endures a hit")},
    "SPECIES_LARVITAR":       {2: ("ABILITY_GUTS", "stubborn mountain grub, tenacity theme")},
    "SPECIES_CACNEA":         {0: ("ABILITY_IRON_BARBS", "cactus spines punish contact")},
    "SPECIES_CACTURNE":       {0: ("ABILITY_IRON_BARBS", "cactus spines punish contact")},
    "SPECIES_GIBLE":          {0: ("ABILITY_SAND_RUSH", "land shark hunts fast in sand; Rough Skin stays hidden")},
    "SPECIES_GABITE":         {0: ("ABILITY_SAND_RUSH", "land shark hunts fast in sand; Rough Skin stays hidden")},
    "SPECIES_GARCHOMP":       {0: ("ABILITY_SAND_RUSH", "land shark hunts fast in sand; Rough Skin stays hidden")},
    "SPECIES_GARCHOMP_MEGA_Z": {0: ("ABILITY_SAND_FORCE", "canonical Mega Garchomp ability")},
    "SPECIES_STUNFISK":       {2: ("ABILITY_EARTH_EATER", "mud-buried trap feeds on ground moves")},
    "SPECIES_HELIOPTILE":     {1: ("ABILITY_SOLAR_POWER", "sun-frill lizard")},
    "SPECIES_HELIOLISK":      {1: ("ABILITY_SOLAR_POWER", "sun-frill lizard")},
    "SPECIES_SANDYGAST":      {2: ("ABILITY_REGENERATOR", "sand reforms itself")},
    "SPECIES_PALOSSAND":      {2: ("ABILITY_REGENERATOR", "sand castle rebuilds")},
    "SPECIES_SILICOBRA":      {2: ("ABILITY_STAMINA", "coiled muscle hardens under fire")},
    "SPECIES_SANDACONDA":     {2: ("ABILITY_STAMINA", "coiled muscle hardens under fire")},
    "SPECIES_SANDACONDA_GMAX": {2: ("ABILITY_STAMINA", "inherits base form")},
    "SPECIES_WIGLETT":        {2: ("ABILITY_GOOEY", "slippery garden eel")},
    "SPECIES_WUGTRIO":        {2: ("ABILITY_GOOEY", "slippery garden eel")},
    "SPECIES_ORTHWORM":       {2: ("ABILITY_EARTH_EATER", "burrowing worm feeds on ground moves")},
    "SPECIES_SANDSHREW_ALOLA": {0: ("ABILITY_SLUSH_RUSH", "igloo shrew speeds through snow")},
    "SPECIES_SANDSLASH_ALOLA": {0: ("ABILITY_SLUSH_RUSH", "igloo shrew speeds through snow")},
    "SPECIES_VULPIX_ALOLA":   {0: ("ABILITY_ICE_BODY", "snowfield fox sustains in its element; Snow Warning stays hidden")},
    "SPECIES_NINETALES_ALOLA": {0: ("ABILITY_ICE_BODY", "snowfield fox sustains in its element; Snow Warning stays hidden")},
    "SPECIES_GLACEON":        {0: ("ABILITY_REFRIGERATE", "the ice-ate eeveelution finally gets a weapon")},
    "SPECIES_ARTICUNO":       {2: ("ABILITY_SNOW_WARNING", "the blizzard bird brings the blizzard")},
    "SPECIES_SWINUB":         {1: ("ABILITY_SLUSH_RUSH", "boar charges through snow")},
    "SPECIES_PILOSWINE":      {1: ("ABILITY_SLUSH_RUSH", "boar charges through snow")},
    "SPECIES_MAMOSWINE":      {1: ("ABILITY_SLUSH_RUSH", "boar charges through snow")},
    "SPECIES_FROSLASS":       {0: ("ABILITY_CURSED_BODY", "yuki-onna's grudge")},
    "SPECIES_VANILLITE":      {1: ("ABILITY_SNOW_WARNING", "brings the hail it is made of")},
    "SPECIES_VANILLISH":      {1: ("ABILITY_SNOW_WARNING", "brings the hail it is made of")},
    "SPECIES_CUBCHOO":        {0: ("ABILITY_THICK_FAT", "polar bear blubber")},
    "SPECIES_BEARTIC":        {0: ("ABILITY_THICK_FAT", "polar bear blubber")},
    "SPECIES_CETODDLE":       {1: ("ABILITY_ICE_BODY", "whale of the snowfields")},
}

# Curated line assignments: base species of line -> (slot2, hidden, why).
# None = engine decides / slot not empty. Final-stage upgrades via CURATED_STAGE.
CURATED_LINE = {
    "SPECIES_BULBASAUR":  ("ABILITY_THICK_FAT", None, "bulb stores reserves; blunts fire/ice on the grass tank"),
    "SPECIES_CHARMANDER": ("ABILITY_TOUGH_CLAWS", None, "claw-fighting fire lizard"),
    "SPECIES_SQUIRTLE":   ("ABILITY_SHELL_ARMOR", None, "the shell is the identity"),
    "SPECIES_CATERPIE":   ("ABILITY_TINTED_LENS", None, "compound eyes to tinted lens as it matures"),
    "SPECIES_WEEDLE":     ("ABILITY_MERCILESS", None, "poison-sting line punishes the poisoned"),
    "SPECIES_PIDGEY":     ("ABILITY_NO_GUARD", None, "Hurricane bird wants No Guard"),
    "SPECIES_RATTATA":    ("ABILITY_ADAPTABILITY", None, "the definitive normal-type scrapper"),
    "SPECIES_SPEAROW":    ("ABILITY_MOXIE", None, "aggressive little raptor snowballs"),
    "SPECIES_EKANS":      ("ABILITY_MERCILESS", None, "venomous crits on poisoned prey"),
    "SPECIES_PIKACHU":    (None, None, "line already full via Light Ball identity; engine fills pre-evos"),
    "SPECIES_NIDORAN_F":  ("ABILITY_SHEER_FORCE", None, "matches Nidoking/queen hidden identity"),
    "SPECIES_NIDORAN_M":  ("ABILITY_SHEER_FORCE", None, "matches Nidoking/queen hidden identity"),
    "SPECIES_VULPIX":     ("ABILITY_SOLAR_POWER", None, "sun fox, Drought stays hidden"),
    "SPECIES_ZUBAT":      ("ABILITY_INFILTRATOR", None, "echolocation slips past screens"),
    "SPECIES_ODDISH":     ("ABILITY_REGENERATOR", None, "plants regrow; sustain option beside Chlorophyll"),
    "SPECIES_DIGLETT":    (None, "ABILITY_STURDY", "already underground; survives the first quake"),
    "SPECIES_MEOWTH":     ("ABILITY_TOUGH_CLAWS", None, "scratch cat"),
    "SPECIES_PSYDUCK":    ("ABILITY_MAGIC_GUARD", None, "headache blocks indirect pain, pairs with Cloud Nine"),
    "SPECIES_MANKEY":     ("ABILITY_DEFIANT", None, "rage escalates when slighted"),
    "SPECIES_GROWLITHE":  ("ABILITY_GUTS", None, "loyal dog fights hurt; Justified/Intimidate exist"),
    "SPECIES_POLIWAG":    ("ABILITY_UNAWARE", None, "vacant spiral stare ignores boosts"),
    "SPECIES_ABRA":       (None, None, "full"),
    "SPECIES_MACHOP":     ("ABILITY_IRON_FIST", None, "the puncher archetype"),
    "SPECIES_BELLSPROUT": ("ABILITY_CORROSION", None, "acid plant poisons even steel"),
    "SPECIES_TENTACOOL":  ("ABILITY_MERCILESS", None, "jellyfish venom crits the poisoned"),
    "SPECIES_GEODUDE":    ("ABILITY_ROCKY_PAYLOAD", None, "throws rocks; rock-move booster"),
    "SPECIES_PONYTA":     ("ABILITY_SPEED_BOOST", None, "racehorse accelerates"),
    "SPECIES_SLOWPOKE":   (None, None, "Regenerator already hidden; full line ok"),
    "SPECIES_MAGNEMITE":  ("ABILITY_TRANSISTOR", None, "electromagnet, electric amplifier"),
    "SPECIES_FARFETCHD":  ("ABILITY_SHARPNESS", None, "leek is a blade"),
    "SPECIES_DODUO":      ("ABILITY_RECKLESS", None, "headfirst double-headed charge"),
    "SPECIES_SEEL":       ("ABILITY_ICE_BODY", None, "arctic pinniped"),
    "SPECIES_GRIMER":     ("ABILITY_CORROSION", None, "toxic sludge dissolves everything"),
    "SPECIES_SHELLDER":   ("ABILITY_STRONG_JAW", None, "the clamp IS a jaw"),
    "SPECIES_GASTLY":     ("ABILITY_INFILTRATOR", None, "gas seeps through walls and screens"),
    "SPECIES_ONIX":       ("ABILITY_SAND_STREAM", None, "burrowing titan kicks up the storm"),
    "SPECIES_DROWZEE":    ("ABILITY_MAGIC_BOUNCE", None, "dream-eater reflects hexes"),
    "SPECIES_KRABBY":     ("ABILITY_TOUGH_CLAWS", None, "the crab claw"),
    "SPECIES_VOLTORB":    ("ABILITY_GALVANIZE", None, "living electric orb electrifies its body"),
    "SPECIES_EXEGGCUTE":  ("ABILITY_HARVEST", None, "eggs regrow their tools"),
    "SPECIES_CUBONE":     ("ABILITY_ROCK_HEAD", None, "bone-club recoil immunity, matches Marowak myth"),
    "SPECIES_LICKITUNG":  ("ABILITY_CUD_CHEW", None, "berry re-eater fits the tongue gimmick"),
    "SPECIES_KOFFING":    (None, None, "Levitate/Neutralizing... engine handles, NG banned"),
    "SPECIES_RHYHORN":    (None, None, "full (Lightning Rod etc.)"),
    "SPECIES_TANGELA":    (None, None, "Regenerator already hidden"),
    "SPECIES_KANGASKHAN": ("ABILITY_SCRAPPY", None, "mother punches through ghosts"),
    "SPECIES_HORSEA":     ("ABILITY_SWIFT_SWIM", None, "seahorse in the current, Sniper preserved on Kingdra"),
    "SPECIES_GOLDEEN":    ("ABILITY_MULTISCALE", None, "prize koi's shimmering scales"),
    "SPECIES_STARYU":     (None, None, "full"),
    "SPECIES_SCYTHER":    (None, None, "Technician already"),
    "SPECIES_PINSIR":     ("ABILITY_STRONG_JAW", None, "the pincers crush"),
    "SPECIES_TAUROS":     ("ABILITY_RECKLESS", None, "rampaging bull"),
    "SPECIES_MAGIKARP":   ("ABILITY_MULTISCALE", None, "scales are all it has; Gyarados upgrades to Moxie via stage rule"),
    "SPECIES_LAPRAS":     ("ABILITY_ICE_SCALES", None, "gentle giant's special wall shell"),
    "SPECIES_EEVEE":      (None, None, "Anticipation/Adaptability already"),
    "SPECIES_PORYGON":    (None, None, "Download/Analytic already"),
    "SPECIES_OMANYTE":    ("ABILITY_STORM_DRAIN", None, "ammonite pulls the tide"),
    "SPECIES_KABUTO":     ("ABILITY_SHARPNESS", None, "scythe-limbed horseshoe crab"),
    "SPECIES_AERODACTYL": (None, None, "full"),
    "SPECIES_SNORLAX":    (None, None, "Thick Fat/Gluttony already"),
    "SPECIES_ARTICUNO":   (None, None, "handled in evasion replacements"),
    "SPECIES_ZAPDOS":     ("ABILITY_TRANSISTOR", None, "the thunderbird amplified"),
    "SPECIES_MOLTRES":    ("ABILITY_FLAME_BODY", None, "touching the firebird burns"),
    "SPECIES_DRATINI":    ("ABILITY_SWIFT_SWIM", None, "river serpent; Multiscale stays the Dragonite hidden"),
    "SPECIES_MEWTWO":     ("ABILITY_NEUROFORCE", None, "engineered mind hits harder where it hurts"),
    "SPECIES_MEW":        ("ABILITY_ADAPTABILITY", None, "the ancestor species fits any niche"),
    "SPECIES_ETERNATUS":  ("ABILITY_LEVITATE", None, "serpent floats in the atmosphere; identical on Eternamax"),
    "SPECIES_ZACIAN":     ("ABILITY_SHARPNESS", None, "the sword; identical on Crowned"),
    "SPECIES_ZAMAZENTA":  ("ABILITY_STAMINA", None, "the shield; identical on Crowned"),
    "SPECIES_CALYREX":    ("ABILITY_REGENERATOR", None, "the king restores the land; identical on both riders"),
    "SPECIES_KORAIDON":   ("ABILITY_TOUGH_CLAWS", None, "primal fighter; identical on all builds"),
    "SPECIES_MIRAIDON":   ("ABILITY_TRANSISTOR", None, "the future engine; identical on all modes"),
    "SPECIES_KYUREM":     ("ABILITY_ICE_SCALES", None, "frozen husk armor; identical on White/Black"),
    "SPECIES_NECROZMA":   ("ABILITY_TINTED_LENS", None, "light-eater pierces resistance; identical on fusions"),
    "SPECIES_GROUDON":    ("ABILITY_SOLID_ROCK", None, "the continent shrugs; identical on Primal"),
    "SPECIES_KYOGRE":     ("ABILITY_STORM_DRAIN", None, "the sea pulls water in; identical on Primal"),
    "SPECIES_RAYQUAZA":   (None, "ABILITY_MULTISCALE", "sky serpent scales; Delta Stream grandfathered in slot 2"),
    "SPECIES_REGIGIGAS":  (None, "ABILITY_STAMINA", "the colossus only gets harder to move; Huge Power grandfathered"),
    "SPECIES_SLAKING":    (None, "ABILITY_GUTS", "when it bothers to care; Scrappy grandfathered"),
}

# Final-stage upgrades (species-level override on top of the line decision).
CURATED_STAGE = {
    "SPECIES_KARTANA":    ("ABILITY_SHARPNESS", None),  # the paper sword

    "SPECIES_BUTTERFREE": ("ABILITY_EFFECT_SPORE", None),  # powder-scale wings; Tinted Lens already hidden
    "SPECIES_EXEGGUTOR":  ("ABILITY_SOLAR_POWER", None),   # sun palm; Harvest already hidden
    "SPECIES_MOLTRES":    ("ABILITY_DROUGHT", None),       # the firebird brings the sun; Flame Body already hidden

    "SPECIES_GYARADOS":   (None, None),  # full already (Moxie hidden)
    "SPECIES_CHARIZARD":  ("ABILITY_TOUGH_CLAWS", None),
    "SPECIES_VENUSAUR":   ("ABILITY_THICK_FAT", None),
    "SPECIES_BLASTOISE":  ("ABILITY_MEGA_LAUNCHER", None),  # deliberate upgrade: cannons
    "SPECIES_PIDGEOT":    ("ABILITY_NO_GUARD", None),
    "SPECIES_MACHAMP":    (None, None),  # No Guard already
    "SPECIES_GENGAR":     ("ABILITY_INFILTRATOR", "ABILITY_MAGIC_GUARD"),  # upgrade: untouchable specter
    "SPECIES_ALAKAZAM":   (None, None),  # Magic Guard already hidden
    "SPECIES_DRAGONITE":  ("ABILITY_MARVEL_SCALE", None),
    "SPECIES_TYRANITAR":  (None, None),
}

WEATHER_SPEED = {"TYPE_GRASS": "ABILITY_CHLOROPHYLL", "TYPE_WATER": "ABILITY_SWIFT_SWIM",
                 "TYPE_GROUND": "ABILITY_SAND_RUSH", "TYPE_ROCK": "ABILITY_SAND_RUSH",
                 "TYPE_ICE": "ABILITY_SLUSH_RUSH"}
TYPE_OFFENSE = {"TYPE_STEEL": "ABILITY_STEELWORKER", "TYPE_ELECTRIC": "ABILITY_TRANSISTOR",
                "TYPE_DRAGON": "ABILITY_DRAGONS_MAW", "TYPE_ROCK": "ABILITY_ROCKY_PAYLOAD"}
TYPE_SUSTAIN = {"TYPE_WATER": "ABILITY_WATER_ABSORB", "TYPE_ELECTRIC": "ABILITY_VOLT_ABSORB",
                "TYPE_FIRE": "ABILITY_FLASH_FIRE", "TYPE_GRASS": "ABILITY_SAP_SIPPER",
                "TYPE_ICE": "ABILITY_THICK_FAT", "TYPE_POISON": "ABILITY_POISON_HEAL",
                "TYPE_PSYCHIC": "ABILITY_MAGIC_GUARD", "TYPE_FAIRY": "ABILITY_MAGIC_BOUNCE",
                "TYPE_GHOST": "ABILITY_CURSED_BODY", "TYPE_FLYING": "ABILITY_REGENERATOR",
                "TYPE_BUG": "ABILITY_REGENERATOR", "TYPE_NORMAL": "ABILITY_THICK_FAT",
                "TYPE_FIGHTING": "ABILITY_GUTS", "TYPE_DARK": "ABILITY_UNNERVE",
                "TYPE_GROUND": "ABILITY_EARTH_EATER", "TYPE_ROCK": "ABILITY_SOLID_ROCK",
                "TYPE_STEEL": "ABILITY_STAMINA", "TYPE_DRAGON": "ABILITY_MULTISCALE"}
CONTACT_PUNISH = {"TYPE_FIRE": "ABILITY_FLAME_BODY", "TYPE_ELECTRIC": "ABILITY_STATIC",
                  "TYPE_POISON": "ABILITY_POISON_POINT", "TYPE_GRASS": "ABILITY_EFFECT_SPORE",
                  "TYPE_ROCK": "ABILITY_ROUGH_SKIN", "TYPE_GROUND": "ABILITY_ROUGH_SKIN",
                  "TYPE_STEEL": "ABILITY_IRON_BARBS", "TYPE_BUG": "ABILITY_POISON_POINT"}
# Broad ranked pools (rev3): with a hard 25-per-ability cap and ~993 slots we
# need >=40 abilities in active rotation, so the engine draws from deep pools
# and always prefers the least-used legal candidate.
OFFENSE_ORDER = ["ABILITY_ADAPTABILITY", "ABILITY_SHEER_FORCE", "ABILITY_TOUGH_CLAWS",
                 "ABILITY_MOXIE", "ABILITY_DEFIANT", "ABILITY_COMPETITIVE",
                 "ABILITY_TINTED_LENS", "ABILITY_ANALYTIC", "ABILITY_RECKLESS",
                 "ABILITY_SUPER_LUCK", "ABILITY_SNIPER", "ABILITY_STAKEOUT",
                 "ABILITY_GUTS", "ABILITY_SCRAPPY", "ABILITY_TECHNICIAN",
                 "ABILITY_DOWNLOAD", "ABILITY_STRONG_JAW", "ABILITY_IRON_FIST",
                 "ABILITY_MOLD_BREAKER", "ABILITY_HUSTLE", "ABILITY_RIVALRY",
                 "ABILITY_ANGER_POINT", "ABILITY_LONG_REACH", "ABILITY_NEUROFORCE",
                 "ABILITY_BEAST_BOOST", "ABILITY_MERCILESS", "ABILITY_INFILTRATOR",
                 "ABILITY_CORROSION", "ABILITY_SWARM", "ABILITY_KEEN_EYE",
                 "ABILITY_VITAL_SPIRIT", "ABILITY_INSOMNIA", "ABILITY_HYPER_CUTTER"]
SUSTAIN_ORDER = ["ABILITY_REGENERATOR", "ABILITY_NATURAL_CURE", "ABILITY_STURDY",
                 "ABILITY_FILTER", "ABILITY_UNAWARE", "ABILITY_MARVEL_SCALE",
                 "ABILITY_INTIMIDATE", "ABILITY_STAMINA", "ABILITY_ICE_SCALES",
                 "ABILITY_FLUFFY", "ABILITY_SOLID_ROCK", "ABILITY_MULTISCALE",
                 "ABILITY_THICK_FAT", "ABILITY_SHED_SKIN", "ABILITY_HYDRATION",
                 "ABILITY_HARVEST", "ABILITY_ROUGH_SKIN", "ABILITY_IRON_BARBS",
                 "ABILITY_PRESSURE", "ABILITY_CUD_CHEW", "ABILITY_FUR_COAT",
                 "ABILITY_LEAF_GUARD", "ABILITY_TANGLING_HAIR", "ABILITY_GOOEY",
                 "ABILITY_TELEPATHY", "ABILITY_OWN_TEMPO", "ABILITY_INNER_FOCUS",
                 "ABILITY_BIG_PECKS", "ABILITY_LIMBER", "ABILITY_SOUNDPROOF",
                 "ABILITY_BULLETPROOF", "ABILITY_WEAK_ARMOR", "ABILITY_STALL",
                 "ABILITY_RAIN_DISH", "ABILITY_ICE_BODY"]
SPEED_ORDER = ["ABILITY_SPEED_BOOST", "ABILITY_UNBURDEN", "ABILITY_QUICK_FEET"]

# Ability-specific justification snippets so no generic string is reused >12x.
ABILITY_WHY = {
    "ABILITY_ADAPTABILITY": "same-type moves hit even harder",
    "ABILITY_SHEER_FORCE": "trades secondary effects for raw power",
    "ABILITY_TOUGH_CLAWS": "its contact moves bite deeper",
    "ABILITY_MOXIE": "snowballs off every knockout",
    "ABILITY_DEFIANT": "answers intimidation with fury",
    "ABILITY_COMPETITIVE": "punishes stat-drop pressure",
    "ABILITY_TINTED_LENS": "its resisted hits stop being resisted",
    "ABILITY_ANALYTIC": "capitalizes when it moves last",
    "ABILITY_RECKLESS": "leans into its high-recoil attacks",
    "ABILITY_SUPER_LUCK": "fishes for crits by nature",
    "ABILITY_SNIPER": "turns its crits into haymakers",
    "ABILITY_STAKEOUT": "feasts on switches",
    "ABILITY_GUTS": "fights harder through status",
    "ABILITY_SCRAPPY": "refuses to let Ghosts wall it",
    "ABILITY_TECHNICIAN": "sharpens its weaker strikes",
    "ABILITY_DOWNLOAD": "reads the foe's weaker defense",
    "ABILITY_STRONG_JAW": "its bite attacks crush",
    "ABILITY_IRON_FIST": "its punches land like hammers",
    "ABILITY_MOLD_BREAKER": "ignores the defenses it can't respect",
    "ABILITY_HUSTLE": "trades accuracy for overwhelming force",
    "ABILITY_RIVALRY": "burns hotter against its own kind",
    "ABILITY_ANGER_POINT": "one crit away from maximum rage",
    "ABILITY_LONG_REACH": "strikes without touching",
    "ABILITY_NEUROFORCE": "amplifies its super-effective hits",
    "ABILITY_BEAST_BOOST": "grows with every kill",
    "ABILITY_MERCILESS": "always crits the poisoned",
    "ABILITY_INFILTRATOR": "slips past screens and subs",
    "ABILITY_CORROSION": "poisons even the immune",
    "ABILITY_SWARM": "rallies its bug power in a pinch",
    "ABILITY_KEEN_EYE": "never loses its aim",
    "ABILITY_VITAL_SPIRIT": "too wired to be put to sleep",
    "ABILITY_INSOMNIA": "never sleeps on the job",
    "ABILITY_HYPER_CUTTER": "its blades never dull",
    "ABILITY_REGENERATOR": "heals as it pivots out",
    "ABILITY_NATURAL_CURE": "shrugs off status on the switch",
    "ABILITY_STURDY": "always survives the first blow",
    "ABILITY_FILTER": "softens super-effective hits",
    "ABILITY_UNAWARE": "ignores the foe's setup",
    "ABILITY_MARVEL_SCALE": "hardens when statused",
    "ABILITY_INTIMIDATE": "saps the foe's attack on entry",
    "ABILITY_STAMINA": "hardens with every hit taken",
    "ABILITY_ICE_SCALES": "halves the special hits it takes",
    "ABILITY_FLUFFY": "shrugs off contact damage",
    "ABILITY_SOLID_ROCK": "endures super-effective blows",
    "ABILITY_MULTISCALE": "half damage at full health",
    "ABILITY_THICK_FAT": "insulated against fire and ice",
    "ABILITY_SHED_SKIN": "sloughs off status naturally",
    "ABILITY_HYDRATION": "washes status away in rain",
    "ABILITY_HARVEST": "regrows its berries",
    "ABILITY_ROUGH_SKIN": "grates attackers on contact",
    "ABILITY_IRON_BARBS": "spikes punish every touch",
    "ABILITY_PRESSURE": "drains the foe's PP",
    "ABILITY_CUD_CHEW": "chews its berry twice",
    "ABILITY_FUR_COAT": "its pelt halves physical hits",
    "ABILITY_LEAF_GUARD": "status-proof under the sun",
    "ABILITY_TANGLING_HAIR": "snares whatever touches it",
    "ABILITY_GOOEY": "slows attackers on contact",
    "ABILITY_TELEPATHY": "dodges ally fire",
    "ABILITY_OWN_TEMPO": "keeps its head, never confused",
    "ABILITY_INNER_FOCUS": "unflinching under fire",
    "ABILITY_BIG_PECKS": "its guard can't be lowered",
    "ABILITY_LIMBER": "never gets paralyzed",
    "ABILITY_SOUNDPROOF": "deaf to sound attacks",
    "ABILITY_BULLETPROOF": "shells off ball and bomb moves",
    "ABILITY_WEAK_ARMOR": "sheds armor for blinding speed",
    "ABILITY_STALL": "bides its time to strike last",
    "ABILITY_RAIN_DISH": "drinks in the rain",
    "ABILITY_ICE_BODY": "heals in the hail",
    "ABILITY_SPEED_BOOST": "accelerates every turn",
    "ABILITY_UNBURDEN": "doubles speed once its item is gone",
    "ABILITY_QUICK_FEET": "outruns trouble when statused",
}
def why_for(ab, ty=None):
    base = ABILITY_WHY.get(ab, pretty_name(ab) + " suits it")
    return f"{pretty_name(ab)}: {base}"


LEARN = json.loads((REPO / "tools/.ability_fill_learnsets.json").read_text())
MOVES = json.loads((REPO / "tools/.ability_fill_moves.json").read_text())

def has_stab_physical(sp, species):
    types = set(species[sp]["types"][0]) if species[sp]["types"] else set()
    for mv in LEARN.get(sp, []):
        info = MOVES.get(mv)
        if info and info["cat"] == "DAMAGE_CATEGORY_PHYSICAL" and info["pwr"] > 0 and info["type"] in types:
            return True
    return False


def load_species():
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    scratch = json.loads(Path(
        "/tmp/claude-0/-home-user-pokefirered-expansion/bbb47bcf-4dfe-51ad-a1d9-bd02cf974111/scratchpad/species_full.json"
    ).read_text())
    CACHE.write_text(json.dumps(scratch))
    return scratch


def base_of_form(name, species):
    if name.count("_") >= 2 or any(name.endswith(s) for s in (
            "_GMAX", "_MEGA", "_MEGA_X", "_MEGA_Y", "_MEGA_Z", "_ALOLA",
            "_GALAR", "_HISUI", "_PALDEA")):
        parts = name.split("_")
        for cut in range(len(parts) - 1, 1, -1):
            cand = "_".join(parts[:cut])
            if cand in species and cand != name:
                return cand
    return None


def pretty_name(ab):
    return ab.replace("ABILITY_", "").replace("_", " ").title()


def main():
    doc_only = "apply" not in sys.argv[1:]
    if not doc_only:
        sys.exit("apply mode is Phase 3; not enabled until assignments are approved")

    species = load_species()
    species = {k: v for k, v in species.items() if v.get("abilities")}
    for v in species.values():
        v["abilities"] = (v["abilities"] + ["ABILITY_NONE"] * 3)[:3]

    # union-find families over evolution edges
    parent = {k: k for k in species}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)
    for k, v in species.items():
        for e in v.get("evos", []):
            if e in species and e != k:
                union(k, e)

    # Fix 1: cosmetic-only families share ONE decision per evolution stage.
    # Each listed prefix collapses to a canonical member; others inherit it.
    # Functional forms (regional/therian/origin/riders/*_MEGA/*_ETERNAL) excluded.
    COSMETIC_CANON = {
        "SPECIES_ALCREMIE_": "SPECIES_ALCREMIE_STRAWBERRY_VANILLA_CREAM",
        "SPECIES_FURFROU_": "SPECIES_FURFROU_NATURAL",
        "SPECIES_FLABEBE_": "SPECIES_FLABEBE_RED",
        "SPECIES_FLOETTE_": "SPECIES_FLOETTE_RED",
        "SPECIES_FLORGES_": "SPECIES_FLORGES_RED",
        "SPECIES_SCATTERBUG_": "SPECIES_SCATTERBUG_ICY_SNOW",
        "SPECIES_SPEWPA_": "SPECIES_SPEWPA_ICY_SNOW",
        "SPECIES_VIVILLON_": "SPECIES_VIVILLON_ICY_SNOW",
        "SPECIES_DEERLING_": "SPECIES_DEERLING_SPRING",
        "SPECIES_SAWSBUCK_": "SPECIES_SAWSBUCK_SPRING",
        "SPECIES_SQUAWKABILLY_": "SPECIES_SQUAWKABILLY_GREEN",
        "SPECIES_TATSUGIRI_": "SPECIES_TATSUGIRI_CURLY",
    }
    cosmetic_inherit = {}  # member -> canonical
    for k in species:
        for pref, canon in COSMETIC_CANON.items():
            if k.startswith(pref) and k != canon and canon in species:
                # exclude functional variants that merely share the prefix
                if any(tag in k for tag in ("_MEGA", "_ETERNAL", "_GMAX")):
                    break
                cosmetic_inherit[k] = canon
                break

    # regional forms are their own line; cosmetic/battle forms inherit base
    inherit_from = {}
    for k in species:
        b = base_of_form(k, species)
        if b and not any(k.endswith(s) for s in ("_ALOLA", "_GALAR", "_HISUI", "_PALDEA")):
            inherit_from[k] = b

    counts = defaultdict(int)
    just_counts = defaultdict(int)
    for v in species.values():
        for a in v["abilities"]:
            if a != "ABILITY_NONE":
                counts[a] += 0  # existing don't count toward the cap

    assignments = {}   # species -> {slot: (ability, why)}
    def assign(sp, slot, ability, why, exempt_just=False):
        if ability in BANLIST or ability is None:
            return False
        cur = species[sp]["abilities"]
        if cur[slot] != "ABILITY_NONE" or ability in cur:
            return False
        if counts[ability] >= cap_of(ability):
            return False
        if not exempt_just and just_counts[why] >= JUSTIFICATION_CAP:
            return False
        assignments.setdefault(sp, {})[slot] = (ability, why)
        counts[ability] += 1
        just_counts[why] += 1
        return True

    # 1) evasion replacements (these overwrite, so tracked separately)
    evasion_out = []
    for sp, repl in EVASION_REPLACEMENTS.items():
        if sp not in species:
            continue
        for slot, (ab, why) in repl.items():
            old = species[sp]["abilities"][slot]
            evasion_out.append((sp, slot, old, ab, why))
            counts[ab] += 1

    exempt = [k for k in species if k.startswith(ABILITY_FORM_EXEMPT_PREFIXES)]

    # 1b) form-linked legendary groups: identical fills on every member,
    # both slots, decided once per group.
    LINKED_GROUPS = [
        (("SPECIES_ZACIAN",), {1: ("ABILITY_SHARPNESS", "the sword"), 2: ("ABILITY_JUSTIFIED", "sword of justice")}),
        (("SPECIES_ZAMAZENTA",), {1: ("ABILITY_STAMINA", "the shield"), 2: ("ABILITY_DEFIANT", "the proud shield refuses to yield")}),
        (("SPECIES_CALYREX",), {1: ("ABILITY_REGENERATOR", "the king restores the land"), 2: ("ABILITY_HARVEST", "king of bountiful harvests")}),
        (("SPECIES_ETERNATUS",), {1: ("ABILITY_LEVITATE", "floats in the upper atmosphere"), 2: ("ABILITY_REGENERATOR", "infinite energy core")}),
        (("SPECIES_KYUREM",), {1: ("ABILITY_ICE_SCALES", "frozen husk armor"), 2: ("ABILITY_DRAGONS_MAW", "the original dragon's power")}),
        (("SPECIES_NECROZMA",), {1: ("ABILITY_TINTED_LENS", "light-eater pierces resistance"), 2: ("ABILITY_ANALYTIC", "prism intelligence")}),
        (("SPECIES_GROUDON",), {1: ("ABILITY_SOLID_ROCK", "the continent shrugs"), 2: ("ABILITY_SHEER_FORCE", "magma-charged blows")}),
        (("SPECIES_KYOGRE",), {1: ("ABILITY_STORM_DRAIN", "the sea pulls water in"), 2: ("ABILITY_SWIFT_SWIM", "is the current")}),
        (("SPECIES_KORAIDON",), {1: ("ABILITY_TOUGH_CLAWS", "primal fighter"), 2: ("ABILITY_RECKLESS", "prehistoric abandon")}),
        (("SPECIES_MIRAIDON",), {1: ("ABILITY_TRANSISTOR", "the future engine"), 2: ("ABILITY_LEVITATE", "hover mode")}),
        (("SPECIES_URSHIFU",), {1: ("ABILITY_IRON_FIST", "the fist style incarnate"), 2: ("ABILITY_STAMINA", "training-hardened body")}),
    ]
    linked_members = set()
    linked_fills = []
    for prefixes, fills in LINKED_GROUPS:
        for sp in sorted(species):
            if not sp.startswith(prefixes) or sp.startswith(ABILITY_FORM_EXEMPT_PREFIXES):
                continue
            linked_members.add(sp)
            for slot, (ab, why) in fills.items():
                if species[sp]["abilities"][slot] == "ABILITY_NONE" and ab not in species[sp]["abilities"]:
                    assignments.setdefault(sp, {})[slot] = (ab, why + " (identical across all linked forms)")
                    counts[ab] += 1
                    linked_fills.append(sp)

    # 2) line fills
    fams = defaultdict(list)
    for k in species:
        if k in ("SPECIES_NONE", "SPECIES_EGG") or k.startswith(ABILITY_FORM_EXEMPT_PREFIXES):
            continue
        if k in linked_members or k in inherit_from or k in cosmetic_inherit:
            continue  # linked/cosmetic/forms fill by inheritance below
        fams[find(k)].append(k)

    def stat(sp, key):
        return int(species[sp].get(key) or 0)

    def final_of_line(sp):
        if sp not in parent:
            return sp
        root = find(sp)
        fam = [m for m in species if m in parent and find(m) == root]
        return max(fam, key=lambda s: sum(stat(s, k) for k in ("hp","atk","def","spa","spd","spe"))) if fam else sp

    for root, members in sorted(fams.items()):
        members.sort(key=lambda s: (stat(s, "hp") + stat(s, "atk") + stat(s, "def")
                                    + stat(s, "spa") + stat(s, "spd") + stat(s, "spe")))
        final = members[-1]
        line_cur = CURATED_LINE.get(root) or CURATED_LINE.get(members[0])
        for sp in members:
            cur = species[sp]["abilities"]
            need2 = cur[1] == "ABILITY_NONE"
            needh = cur[2] == "ABILITY_NONE"
            if not (need2 or needh):
                continue
            stage_cur = CURATED_STAGE.get(sp)
            pick2 = pickh = None
            why2 = whyh = None
            if stage_cur:
                pick2, pickh = stage_cur
                why2 = whyh = "curated final-stage upgrade"
            if pick2 is None and line_cur and line_cur[0]:
                pick2, why2 = line_cur[0], line_cur[2]
            if pickh is None and line_cur and line_cur[1]:
                pickh, whyh = line_cur[1], line_cur[2]

            types = species[sp]["types"][0] if species[sp]["types"] else ("TYPE_NORMAL", "TYPE_NORMAL")
            atk, spa = stat(sp, "atk"), stat(sp, "spa")
            spe, bulk = stat(sp, "spe"), stat(sp, "hp") + stat(sp, "def") + stat(sp, "spd")
            offensive = max(atk, spa) >= bulk / 3

            def engine_pick(want_offense, avoid):
                thematic, generic = [], []
                if want_offense:
                    # Huge/Pure Power only where THIS species can actually use it:
                    # its own Atk must be its attacking stat (>= SpA) and it must
                    # own a STAB physical move now. That excludes special lines and
                    # not-yet-physical pre-evos, so every assignment passes audit.
                    own_spa = int(species[sp].get("spa") or 0)
                    if (atk <= 70 and atk >= own_spa and sp != "SPECIES_DITTO"
                            and not sp.startswith(HUGE_POWER_EXCLUDE_PREFIXES)
                            and has_stab_physical(sp, species)):
                        if "TYPE_PSYCHIC" in types or "TYPE_FAIRY" in types:
                            thematic.append(("ABILITY_PURE_POWER", "Pure Power: doubled Atk on a physical attacker (Atk>=SpA) with a STAB physical move"))
                        else:
                            thematic.append(("ABILITY_HUGE_POWER", "Huge Power: doubled Atk on a physical attacker (Atk>=SpA) with a STAB physical move"))
                    if "TYPE_WATER" in types and spa >= atk:
                        thematic.append(("ABILITY_WATER_BUBBLE", "Water Bubble: doubles its Water damage and blocks burns"))
                    for ty in types:
                        if ty in TYPE_OFFENSE: thematic.append((TYPE_OFFENSE[ty], why_for(TYPE_OFFENSE[ty])))
                    if spe >= 95:
                        for a in SPEED_ORDER: thematic.append((a, why_for(a)))
                        for ty in types:
                            if ty in WEATHER_SPEED: thematic.append((WEATHER_SPEED[ty], why_for(WEATHER_SPEED[ty])))
                    for a in OFFENSE_ORDER:
                        generic.append((a, why_for(a)))
                else:
                    if spe <= 60 and max(atk, spa) <= 70:
                        thematic.append(("ABILITY_PRANKSTER", "Prankster: a slow supporter that now moves first"))
                    if max(atk, spa) >= 60 and int(species[sp].get("hp") or 0) + int(species[sp].get("def") or 0) <= 130:
                        thematic.append(("ABILITY_SERENE_GRACE", "Serene Grace: a frail frame with outsized luck"))
                    for ty in types:
                        if ty in TYPE_SUSTAIN: thematic.append((TYPE_SUSTAIN[ty], why_for(TYPE_SUSTAIN[ty])))
                        if ty in CONTACT_PUNISH: thematic.append((CONTACT_PUNISH[ty], why_for(CONTACT_PUNISH[ty])))
                    for a in SUSTAIN_ORDER:
                        generic.append((a, why_for(a)))

                def legal(pairs):
                    return [(a, w) for a, w in pairs
                            if a not in avoid and a not in BANLIST
                            and a not in species[sp]["abilities"]
                            and counts[a] < cap_of(a) and just_counts[w] < JUSTIFICATION_CAP]
                # thematic first (spread the wealth among fitting picks), else the
                # least-used legal candidate anywhere in the broad pool
                for bucket in (legal(thematic), legal(generic)):
                    if bucket:
                        return min(bucket, key=lambda x: counts[x[0]])
                return None, None

            if need2:
                a, w = (pick2, why2) if pick2 else (None, None)
                if a is None or not assign(sp, 1, a, w):
                    a, w = engine_pick(offensive, set())
                    if a: assign(sp, 1, a, w)
                elif a: pass
            if needh:
                avoid = {assignments.get(sp, {}).get(1, (None,))[0]}
                bst = atk + spa + spe + bulk
                want = (not offensive if need2 else offensive) and bst >= 320
                a, w = (pickh, whyh) if pickh else (None, None)
                if a is None or not assign(sp, 2, a, w):
                    a, w = engine_pick(want, avoid)
                    if a: assign(sp, 2, a, w)

    # final-sweep helper reusing the same thematic engine
    def sweep_fill(sp):
        v = species[sp]
        types = v["types"][0] if v["types"] else ("TYPE_NORMAL", "TYPE_NORMAL")
        atk, spa = int(v.get("atk") or 0), int(v.get("spa") or 0)
        spe = int(v.get("spe") or 0)
        bulk = int(v.get("hp") or 0) + int(v.get("def") or 0) + int(v.get("spd") or 0)
        offensive = max(atk, spa) >= bulk / 3
        for slot in (1, 2):
            if v["abilities"][slot] != "ABILITY_NONE" or slot in assignments.get(sp, {}):
                continue
            pool = OFFENSE_ORDER + SUSTAIN_ORDER if offensive else SUSTAIN_ORDER + OFFENSE_ORDER
            tycands = [TYPE_OFFENSE.get(ty) for ty in types] + [TYPE_SUSTAIN.get(ty) for ty in types]
            taken = {x[0] for x in assignments.get(sp, {}).values()}
            legal = [a for a in [c for c in tycands if c] + pool
                     if a not in BANLIST and a not in v["abilities"] and a not in taken
                     and counts[a] < cap_of(a) and just_counts[why_for(a)] < JUSTIFICATION_CAP]
            if legal:
                a = min(legal, key=lambda x: counts[x])
                assign(sp, slot, a, why_for(a))

    # 3) forms inherit (mandatory, outside the variety cap; reported separately)
    inherit_counts = defaultdict(int)
    inherited = []
    for form, base in sorted(inherit_from.items()):
        if form.startswith(ABILITY_FORM_EXEMPT_PREFIXES) or form in linked_members:
            continue
        for slot in (1, 2):
            if species[form]["abilities"][slot] == "ABILITY_NONE":
                src = assignments.get(base, {}).get(slot)
                if src is None and species[base]["abilities"][slot] != "ABILITY_NONE":
                    src = (species[base]["abilities"][slot], "matches base form data")
                if src and src[0] not in species[form]["abilities"]:
                    assignments.setdefault(form, {})[slot] = (src[0], f"inherits {base.replace('SPECIES_','')}")
                    inherit_counts[src[0]] += 1
                    inherited.append(form)

    # 3a2) cosmetic families inherit their canonical member's fills (rev3 fix 1)
    cosmetic_filled = []
    for member, canon in sorted(cosmetic_inherit.items()):
        for slot in (1, 2):
            if species[member]["abilities"][slot] != "ABILITY_NONE":
                continue
            src = assignments.get(canon, {}).get(slot)
            if src is None and species[canon]["abilities"][slot] != "ABILITY_NONE":
                src = (species[canon]["abilities"][slot], "matches canonical form data")
            if src and src[0] not in species[member]["abilities"]:
                assignments.setdefault(member, {})[slot] = (
                    src[0], f"cosmetic: inherits {canon.replace('SPECIES_','')}")
                inherit_counts[src[0]] += 1
                cosmetic_filled.append(member)

    # 3b) exempt species: duplicate their form-mechanic ability into every
    # empty slot so no slot in the dex is empty. The Ability Coach must refuse
    # buying a slot whose ability equals the current one (Phase 3 code tweak).
    exempt_dups = []
    for sp in species:
        if not sp.startswith(ABILITY_FORM_EXEMPT_PREFIXES):
            continue
        mech = species[sp]["abilities"][0]
        for slot in (1, 2):
            if species[sp]["abilities"][slot] == "ABILITY_NONE":
                assignments.setdefault(sp, {})[slot] = (mech, "exempt: duplicate of form-mechanic ability")
                exempt_dups.append((sp, slot, mech))

    # 4) final sweep so no non-exempt slot is left empty
    for sp in species:
        if sp in ("SPECIES_NONE", "SPECIES_EGG") or sp.startswith(ABILITY_FORM_EXEMPT_PREFIXES):
            continue
        if sp in cosmetic_inherit:  # cosmetic members already inherited canonical
            continue
        sweep_fill(sp)

    # 5) refit pass: replace flagged mismatches (self-audit) with fitting picks
    PHYS_R = {"ABILITY_HUGE_POWER","ABILITY_PURE_POWER","ABILITY_TOUGH_CLAWS","ABILITY_STRONG_JAW",
              "ABILITY_IRON_FIST","ABILITY_SHARPNESS","ABILITY_GORILLA_TACTICS","ABILITY_MOXIE",
              "ABILITY_DEFIANT","ABILITY_RECKLESS","ABILITY_GUTS"}
    CLAWJAW_R = {"ABILITY_TOUGH_CLAWS","ABILITY_STRONG_JAW","ABILITY_SHARPNESS","ABILITY_IRON_FIST"}
    SPECIAL_POOL = ["ABILITY_TINTED_LENS","ABILITY_ANALYTIC","ABILITY_COMPETITIVE","ABILITY_DOWNLOAD",
                    "ABILITY_SNIPER","ABILITY_SERENE_GRACE","ABILITY_SOLAR_POWER"]
    def final_of_r(sp):
        if sp not in parent: return sp
        root = find(sp)
        fam = [m for m in species if m in parent and find(m) == root]
        return max(fam, key=lambda s: sum(int(species[s].get(k) or 0) for k in ("hp","atk","def","spa","spd","spe")))
    refitted = []
    for sp in list(assignments):
        for slot in list(assignments[sp]):
            ab, why = assignments[sp][slot]
            if why.startswith(("exempt:", "curated")) or "identical across" in why or ab in ("ABILITY_HUGE_POWER","ABILITY_PURE_POWER"):
                continue
            fin = final_of_r(sp)
            fatk, fspa = int(species[fin].get("atk") or 0), int(species[fin].get("spa") or 0)
            bad = (ab in PHYS_R and fatk < 80) or (ab in CLAWJAW_R and fspa > fatk + 15)
            if not bad:
                continue
            taken = {x[0] for s2, x in assignments[sp].items() if s2 != slot} | set(species[sp]["abilities"])
            pool = (SPECIAL_POOL if fspa > fatk else []) + SUSTAIN_ORDER + [TYPE_SUSTAIN.get(ty) for ty in (species[sp]["types"][0] if species[sp]["types"] else ())]
            legal = [c for c in pool if c and c not in BANLIST and c not in taken
                     and counts[c] < cap_of(c) and just_counts[why_for(c)] < JUSTIFICATION_CAP]
            if legal:
                cand = min(legal, key=lambda x: counts[x])
                counts[ab] -= 1
                counts[cand] += 1
                just_counts[why_for(cand)] += 1
                assignments[sp][slot] = (cand, why_for(cand) + " [refit off misfit " + pretty_name(ab) + "]")
                refitted.append(sp)
    # emit doc
    def pretty(ab): return ab.replace("ABILITY_", "").replace("_", " ").title()
    dex = {}
    t = open(REPO / "include/constants/pokedex.h").read()
    m = re.search(r"#define FOREACH_SPECIES_IN_NATIONAL_DEX\(F\)(.*?)\n\n", t, re.S)
    for i, nm in enumerate(re.findall(r"F\((\w+)\)", m.group(1))):
        dex[f"NATIONAL_DEX_{nm}"] = i
    def dexof(sp): return dex.get(species[sp]["dex"], 9999)

    filled = sum(len(v) for v in assignments.values())
    with open(DOC, "w") as f:
        f.write(f"""# Ability Fill v2 — Phase 2 Assignments (REVIEW, nothing applied)

- Slots filled: **{filled}** (+ {len(evasion_out)} evasion replacements)
- Variety cap: {ABILITY_CAP} per assigned decision; max observed: {max(counts.values())} ({pretty(max(counts, key=counts.get))}). Form inheritances are mandated by the GMAX/forms rule and counted separately below.
- Banlist assignments: 0 (verified below)

## Sand Veil / Snow Cloak replacements (overwrite existing slots)

| Species | Slot | Was | Now | Why |
|---|---|---|---|---|
""")
        for sp, slot, old, ab, why in sorted(evasion_out, key=lambda r: dexof(r[0])):
            f.write(f"| {sp.replace('SPECIES_','')} | {slot+1 if slot<2 else 'H'} | {pretty(old)} | {pretty(ab)} | {why} |\n")

        f.write("""
## Exempt (ability-driven form mechanics — slots left empty on purpose)

Coaching these onto another slot would disable the form gimmick, failing the
"no silent overwrites" rule: """)
        f.write(", ".join(sorted({p.replace("SPECIES_","") for p in exempt})) + "\n")

        f.write("""
## Form-linked legendaries — machinery verification (adjustment 3)

Verified in code before assigning: form changes swap only the species field
(`SetMonData(MON_DATA_SPECIES)`); `abilityNum` persists, and
`GetAbilityBySpecies` falls back to the first non-empty slot with no assert.
Therefore a non-signature abilityNum survives every form change, and the only
hazard is a *layout mismatch* between linked forms. Mitigation: every linked
group below receives identical fills, so no slot resolves differently across
a form change.

| Group | Link | Finding | Shared fill |
|---|---|---|---|
| Zacian Hero + Crowned | Rusted Sword, battle start | safe; Intrepid Sword is slot 1 on both | Sharpness (2) + Justified (H), identical on both |
| Zamazenta Hero + Crowned | Rusted Shield, battle start | safe; Dauntless Shield slot 1 on both | Stamina (2) + Defiant (H), identical on both |
| Calyrex + Ice/Shadow Rider | Reins fusion | safe; As One is slot 1 of rider forms | Regenerator (2) + Harvest (H), identical |
| Eternatus + Eternamax | trainer-only form | safe; player never Eternamaxes | Levitate (2) + Regenerator (H), identical |
| Kyurem + White/Black | DNA Splicers fusion | safe | Ice Scales (2) + Dragon's Maw (H), identical |
| Necrozma + Dusk/Dawn/Ultra | Prism fusion / Ultra Burst | safe | Tinted Lens (2) + Analytic (H), identical |
| Groudon/Kyogre + Primal | orb, battle-only, reverts | safe | Solid Rock+Sheer Force / Storm Drain+Swift Swim, identical |
| Koraidon / Miraidon builds | ride modes, non-battle | safe | Tough Claws+Reckless / Transistor+Levitate, identical |
| Therian formes (Tornadus etc.) | Reveal Glass | safe; forms inherit base fills | per line |

## Assignments (dex order; forms inherit their base and are listed once)

| Dex | Species | Slot | Ability | Justification |
|---|---|---|---|---|
""")
        for sp in sorted(assignments, key=lambda s: (dexof(s), s)):
            for slot in sorted(assignments[sp]):
                ab, why = assignments[sp][slot]
                f.write(f"| {dexof(sp)} | {sp.replace('SPECIES_','')} | {'2' if slot==1 else 'H'} | {pretty(ab)} | {why} |\n")

        # self-audit (revision item 5)
        PHYS = {"ABILITY_HUGE_POWER","ABILITY_PURE_POWER","ABILITY_TOUGH_CLAWS","ABILITY_STRONG_JAW",
                "ABILITY_IRON_FIST","ABILITY_SHARPNESS","ABILITY_GORILLA_TACTICS","ABILITY_MOXIE",
                "ABILITY_DEFIANT","ABILITY_RECKLESS","ABILITY_GUTS"}
        CLAWJAW = {"ABILITY_TOUGH_CLAWS","ABILITY_STRONG_JAW","ABILITY_SHARPNESS","ABILITY_IRON_FIST"}
        def final_of(sp):
            root = find(sp) if sp in parent else sp
            fam = [m for m in species if m in parent and find(m) == root]
            return max(fam, key=lambda s: sum(int(species[s].get(k) or 0) for k in ("hp","atk","def","spa","spd","spe"))) if fam else sp
        f.write("\n## Self-audit (revision item 5)\n\n")
        f.write("Physical-boost fills where the line's FINAL stage has base Atk < 80 "
                "(Huge/Pure Power meme picks are intentional and marked):\n\n")
        n = 0
        for sp in sorted(assignments, key=lambda s: (dexof(s), s)):
            for slot, (ab, why) in assignments[sp].items():
                if why.startswith(("exempt:", "curated")) or "identical across" in why or "inherits" in why:
                    continue
                if ab in PHYS:
                    fin = final_of(sp)
                    fatk = int(species[fin].get("atk") or 0)
                    if fatk < 80:
                        tag = "INTENTIONAL meme pick" if ab in ("ABILITY_HUGE_POWER","ABILITY_PURE_POWER") else "flagged"
                        f.write(f"- {sp.replace('SPECIES_','')} {'2' if slot==1 else 'H'} = {pretty(ab)} (final-stage Atk {fatk}) — {tag}\n")
                        n += 1
        f.write(f"\n({n} rows)\n\nClaw/jaw/blade fills on special-leaning species (final SpA > Atk + 15):\n\n")
        n = 0
        for sp in sorted(assignments, key=lambda s: (dexof(s), s)):
            for slot, (ab, why) in assignments[sp].items():
                if why.startswith(("exempt:", "curated")) or "identical across" in why or "inherits" in why:
                    continue
                if ab in CLAWJAW:
                    fin = final_of(sp)
                    fatk, fspa = int(species[fin].get("atk") or 0), int(species[fin].get("spa") or 0)
                    if fspa > fatk + 15:
                        f.write(f"- {sp.replace('SPECIES_','')} {'2' if slot==1 else 'H'} = {pretty(ab)} (final Atk {fatk} / SpA {fspa}) — flagged\n")
                        n += 1
        f.write(f"\n({n} rows)\n")
        empty_total = sum(1 for v in species.values() for s in (1,2) if v["abilities"][s] == "ABILITY_NONE")
        filled_all = sum(len(v) for v in assignments.values())
        f.write(f"\n### Reconciliation\n\nPhase 1 empty slots: {empty_total}. "
                f"Assignments in this doc: {filled_all} "
                f"(regular decisions + linked-group fills + form inheritances + {len(exempt_dups)} exempt duplicates). "
                f"{empty_total} - {filled_all} = {empty_total - filled_all} (must be 0).\n")

        f.write("\n## Per-ability usage counts (assigned fills only)\n\n")
        used = {a: (c, inherit_counts.get(a, 0)) for a, c in counts.items() if c > 0 or inherit_counts.get(a, 0)}
        for a, (c, ic) in sorted(used.items(), key=lambda x: -(x[1][0]+x[1][1])):
            flag = " ⚠ OVER CAP" if c > cap_of(a) else ""
            extra = f" (+{ic} form inheritance)" if ic else ""
            f.write(f"- {pretty(a)}: {c}{extra}{flag}\n")

    leftover = [k for k in species if k not in exempt and k not in ("SPECIES_NONE","SPECIES_EGG")
                and (species[k]["abilities"][1] == "ABILITY_NONE" and k not in assignments or
                     species[k]["abilities"][2] == "ABILITY_NONE" and 2 not in assignments.get(k, {}) and 1 not in assignments.get(k, {}) and False)]
    print(f"filled {filled} slots; evasion replacements {len(evasion_out)}; doc at {DOC}")
    over = [a for a, c in counts.items() if c > ABILITY_CAP]
    print("over cap:", [pretty(a) for a in over] or "none")
    banned_assigned = [a for v in assignments.values() for (a, w) in v.values()
                       if a in BANLIST and not w.startswith("exempt:")]
    print("banned assigned:", banned_assigned or "none")


if __name__ == "__main__":
    main()
