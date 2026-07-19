# Rematch Scaling (Kaizo)

Every trainer in the game can be rebattled, and every win makes their next
team stronger. There is no level ceiling below the new `MAX_LEVEL` of 255.

## How it works

| Trainer type | Rebattle via | Levels per win | Counter storage |
|---|---|---|---|
| Route trainers | VS Seeker (vanilla flow) | +2 | `gSaveBlock1Ptr->rematchWinCounts[]`, indexed by `enum RematchID` |
| Gym leaders | Talk to the leader again after defeating them | +5 | `VAR_REMATCH_BROCK` … `VAR_REMATCH_GIOVANNI` |
| Elite Four | Re-challenge the league (flags reset after the Hall of Fame, as in vanilla) | +5 | `VAR_REMATCH_LORELEI` … `VAR_REMATCH_LANCE` |
| Champion | Re-challenge the league | +5 | `VAR_REMATCH_CHAMPION` |

Core logic lives in `src/rematch_scaling.c`:

- `GetRematchWinCount()` / `IncrementRematchWinCount()` — counters, keyed to the
  *base* trainer ID (variants map back through `GetBaseTrainerId()`).
- `IsBossTrainer()` — checks the trainer class (`LEADER`, `ELITE_FOUR`,
  `CHAMPION`), so new boss variants automatically get the +5 tier.
- `SetTrainerPartyLevelScaling()` / `GetScaledTrainerMonLevel()` — armed in
  `CreateNPCTrainerParty()` (`src/battle_main.c`), applied to each mon's level
  at party generation, clamped to `MAX_LEVEL`. Only enemy trainer parties are
  scaled; partner, frontier and recorded battles are untouched.
- Counters increment only on the victory paths of `CB2_EndTrainerBattle` /
  `CB2_EndRematchBattle` (`src/battle_setup.c`) — losses and forfeits don't count.

## Team variants

- **Route trainers:** `GetRematchTrainerId()` (`src/vs_seeker.c`) now *cycles*
  through all story-unlocked parties in `sRematches` (`win count % variants`)
  instead of clamping at the last one.
- **Bosses:** `BattleSetup_ConfigureTrainerBattle()` swaps the scripted trainer
  ID for the variant selected by the win count (`GetBossVariantTrainerId()`).
  Gym leaders alternate between their vanilla team and a new `TRAINER_LEADER_*_2`
  team (`src/data/trainers.party`); the Elite Four and Champion alternate
  between their round-1 and vanilla round-2 (`*_2` / `CHAMPION_REMATCH_*`) teams.
  Variant teams keep the same base levels — the climb comes from the win counter.

Giovanni no longer disappears from Viridian Gym after his post-battle dialogue;
the rematch branch intercepts before the vanilla `removeobject` path.

## Level cap

`MAX_LEVEL` is 255 (`include/constants/pokemon.h`). Experience tables extend
past 100 with a linear extension (each level past 100 costs that growth rate's
99→100 step) because the vanilla Erratic formula turns negative past level 160.
The `experience` bitfield was widened to 24 bits using adjacent unused bits;
`metLevel` stays 7 bits and is clamped to 127 on write (nothing catchable
exceeds that).

## Debug / testing

- The expansion overworld debug menu is enabled in all builds (hold the key set
  in `DEBUG_OVERWORLD_HELD_KEYS` — default B — and press Start).
- Boss counters are plain vars: edit `VAR_REMATCH_*` in the debug Vars editor.
- Script specials `Special_GetRematchWinCount` / `Special_SetRematchWinCount`
  read/write any counter: `VAR_0x8004` = trainer ID, `VAR_0x8005` = new count.

### Test plan (in emulator)

1. Beat a route trainer twice via VS Seeker → third fight is base+4 with the
   team cycled.
2. Beat Brock, talk to him again and accept → +5 levels, variant team.
3. Wipe to a rematch → counter must NOT increment on a loss.
4. Set a counter to 200 via debug → levels clamp at 255, no overflow/crash.
5. Save, reset, reload → counters persist.

## Addendum: IVs, EVs and the Effort Coach

- **Perfect IVs**: every Pokémon created on the random-IV path (wild, gift,
  hatched, traded) has 31 in all six IVs (`SetBoxMonIVs`, `src/pokemon.c`).
  Trainer mons keep their `trainers.party` IVs.
- **IV/EV viewer**: the expansion's summary screen pages are enabled
  (`P_SUMMARY_SCREEN_IV_EV_INFO`); press the prompted button on the skills
  page to cycle Stats → IVs → EVs. IVs display as exact numbers.
- **Effort Coach NPC** (Pallet Town, black belt at (8,12)): max a stat's EVs
  to 252, add 100, or wipe all EVs, with the 510 total cap enforced. Partial
  adds near the cap are reported. Backed by `ScrSpecial_ModifyMonEVs`
  (`src/field_specials.c`): `VAR_0x8004` slot, `VAR_0x8005` stat
  (HP/Atk/Def/SpAtk/SpDef/Speed = 0-5), `VAR_0x8006` mode (0 max, 1 add 100,
  2 wipe), returns `VAR_RESULT` ok flag and `VAR_0x8007` EVs actually added.
  Stats recalculate immediately.
- **Nature Coach NPC** (Pallet Town, crush girl at (10,12)): pick the stat to
  raise and the stat to lower (or Neutral → Hardy) and the mon's nature is
  changed through the hidden nature (mint) system — gender, shininess, ability
  slot and form stay untouched, and stats recalculate immediately (battle stat
  calc reads hidden nature). Backed by three specials in
  `src/field_specials.c`: `ScrSpecial_BufferMonNature` (current nature name →
  `STR_VAR_2`), `ScrSpecial_GetNatureFromStatPair` (`VAR_0x8005` raise +
  `VAR_0x8006` lower → nature id, computed from `gNaturesInfo` stat data), and
  `ScrSpecial_SetMonNature` (`VAR_0x8004` slot + `VAR_0x8005` nature id 0-24;
  returns `VAR_RESULT` ok flag, previous nature in `VAR_0x8006`).

## Static difficulty pass (first encounters)

- **Phase A — AI**: every trainer runs Check Bad Move / Try To Faint / Check
  Viability. Bosses (leaders, rival, Rocket boss, E4, Champion) add Smart
  Switching / Smart Mon Choices; the E4 and Champion add Omniscient. Applied
  by `tools/kaizo_pass.py ai`.
- **Phase B — bulk pass** (`tools/kaizo_pass.py bulk`): route/dungeon trainers
  get a segment level curve (×1.15 pre-Brock → ×1.30 late), team padding
  (min 3 / 4 / 5 mons by segment, deduped, deterministic) and a held item on
  the last mon of padded teams. All tunables live in
  `tools/kaizo_segments.json`; pre-pass levels in `tools/kaizo_baseline.json`
  keep re-runs from compounding. CI fails if trainers.party drifts from the
  script output. Bosses, rivals, `TRAINER_*_2..6` variants and frontier
  trainers are never touched by the script.
- **Phase C — bosses**: all 8 gym leaders (both rotation variants), the E4
  round-1 teams and the three Champion first battles are hand-authored:
  6 mons, explicit moves/abilities/natures, EV spreads, held items. Each team
  has a tempo lead, a wallbreaker, a setup threat the player must answer, a
  pivot, coverage for the obvious counter-type, and a Sitrus ace ~+4 over its
  segment's scaled route average (the +5/rematch boost stacks on top).
  The vanilla E4 round-2 and Champion rematch teams are kept as the second
  rotation variant — they can get the same treatment after playtesting.
- **Phase D — global configs** (badge boosts, extra boss healing items) is
  deliberately deferred until after a playtest of A-C, per the spec. E4 and
  Champion currently carry 3 Full Restores each.

Playtest checkpoints (not yet run): Brock AI sanity, a fresh-save run to
Misty counting wipes, and confirming rematch scaling stacks on the new bases.

## Superboss (post-game)

A hidden trainer (FRODO) guards Mewtwo inside Cerulean Cave B1F, appearing
after the first Hall of Fame (gated on FLAG_HIDE_POSTGAME_GOSSIPERS). He
stands at (7,16) — the floor tile at the single opening into Mewtwo's
chamber, verified by collision BFS to cut every walking route from the
floor entry to Mewtwo — so Mewtwo is unreachable until he's beaten once
(the player talks to him from (7,17), (6,16) or (8,16)). On the first win
he steps one tile right to (8,16), leaving the platform approach fully
clear; the position persists across save/reload because the map's
ON_TRANSITION script repositions his object template whenever
VAR_REMATCH_FRODO is at least 1. He rotates three teams
on VAR_REMATCH_FRODO — win count % 3, +5 levels per win like every boss
(Class: Champion), Omniscient AI, 2 Full Restores. Base levels 76/76/77/77/78
with an 82 ace in every variant:

1. TRAINER_SUPERBOSS_FRODO — "The Stat Crimes": Eternatus-Eternamax wall,
   Huge Power Regigigas, Scrappy Band Slaking, Scarf Imposter Ditto, Magic
   Guard Blissey, Mega Mewtwo Y ace (AI mega-evolves via held Mewtwonite Y).
2. TRAINER_SUPERBOSS_FRODO_2 — "Ability Abuse": Prankster Shuckle hazards,
   Wonder Guard Aegislash (replaces Stance Change, so it stays a Shield-forme
   wall), Huge Power Regigigas, Magic Bounce Spiritomb, Scarf Ditto, Delta
   Stream Rayquaza ace.
3. TRAINER_SUPERBOSS_FRODO_3 — "Legendary Apex": Primal Groudon and Kyogre
   (orbs revert on entry), Zacian @ Rusted Sword (crowns on entry, Iron Head
   becomes Behemoth Blade), Dusk Mane Necrozma, Arceus, Eternatus ace.

The illegal abilities are implemented as species_info ability-slot edits for
those species only (Regigigas, Slaking, Blissey, Shuckle, Spiritomb, Rayquaza,
Aegislash-Shield) — wild/player copies of those species can roll them too,
which is acceptable post-game per the design doc.

## Ability Coach (post-game)

A scientist in Pallet Town (6,12), beside the Effort and Nature Coaches, switches a
party mon's ability slot — primary / secondary / hidden — for ¥100,000
(`.set ABILITY_COACH_PRICE` in PalletTown's scripts.inc). Present but refusing
before the first Hall of Fame (FLAG_SYS_GAME_CLEAR). Backed by
`ScrSpecial_SetMonAbilitySlot` (`VAR_0x8004` slot, `VAR_0x8005` target
ability slot 0-2, `VAR_0x8006` 0 = validate / 1 = apply): validation runs
before any money moves and rejects empty slots and the already-active slot,
so failed or cancelled paths never charge. Battle resolution reads
`abilityNum` (`GetAbilityBySpecies` handles hidden = slot 2), and evolution
preserves `abilityNum`, so purchases stick.

Superboss ability-slot edits the coach exposes on player copies (post-game
tradeoff, accepted by design): Regigigas → Huge Power, Slaking → Scrappy,
Blissey → Magic Guard (hidden), Shuckle → Prankster, Spiritomb → Magic
Bounce, Rayquaza → Delta Stream, Aegislash → Wonder Guard. Of these, only
the Chansey line is catchable in vanilla FRLG encounter pools — the rest
matter only if those species become obtainable.
