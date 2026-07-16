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
