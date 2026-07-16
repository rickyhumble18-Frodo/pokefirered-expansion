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
