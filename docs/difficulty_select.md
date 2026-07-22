# New-Game Difficulty Select (Standard / Hard)

After naming, a new game asks the player how tough the adventure should be. The
choice picks one of two coexisting level curves baked into the trainer data:

| Tier | Enum | Curve | Example |
| --- | --- | --- | --- |
| **Standard** | `DIFFICULTY_NORMAL` | pre-uplift, vanilla-ish progression | Brock ace 14, Elite Four low 60s |
| **Hard** | `DIFFICULTY_HARD` | the uplifted kaizo curve | Brock ace 22, Elite Four 118–125, Champion 132, FRODO 150 |

Everything except levels — species, moves, abilities, held items, EVs/IVs, team
size, the 40 VS-Seeker trainers, the coaches, the FRODO superboss and Shadow
Lugia — is shared between the tiers. Only the `Level:` lines differ.

## How the difficulty is stored and read

* `B_VAR_DIFFICULTY` (`include/config/battle.h`) points at `VAR_GAME_DIFFICULTY`
  (`0x40D2`, a formerly unused saveblock1 var).
* The new-game menu (`src/oak_speech.c`) records the choice in
  `gNewGameStartDifficulty`. It is *not* written to the var during the intro,
  because `NewGameInitData` clears every saveblock1 var afterwards; instead
  `NewGameInitData` (`src/new_game.c`) calls `SetCurrentDifficultyLevel` once at
  the very end, so the choice survives into the first save.
* `GetCurrentDifficultyLevel` (`src/difficulty.c`) reads the var. Because the
  menu only ever offers Standard/Hard, an unset var reading `0`
  (`DIFFICULTY_EASY`) can only be a pre-feature save, so outside the test build
  it is mapped to Hard — old saves stay brutal instead of silently dropping to
  Standard. The `#if !TESTING` guard leaves the engine's raw `DIFFICULTY_EASY`
  fallback intact for `test/battle/trainer_control.c`.
* `gTrainers[GetTrainerDifficultyLevel(id)][id]` (`include/data.h`) then serves
  the selected column, and `GetScaledTrainerMonLevel` applies the rematch
  (+2 route / +5 gym) and superboss (+8 FRODO) win-count boosts *on top of*
  whichever base level the chosen tier provides — so scaling stacks on both
  tiers with no extra code.

## How the two columns are generated

`src/data/trainers.party` holds both tiers. Each trainer that differs between
tiers appears twice — a `Difficulty: Normal` block (Standard levels) and a
`Difficulty: Hard` block (current levels) — which `trainerproc` compiles into
`[DIFFICULTY_NORMAL][…]` and `[DIFFICULTY_HARD][…]` entries. A trainer whose
levels match in both tiers (frontier brains, empty parties) is emitted once with
no key and served to both tiers via the `DIFFICULTY_NORMAL` fallback.

The tooling pipeline (all idempotent, all `--check`ed in CI):

1. `tools/kaizo_pass.py ai|bulk` — the existing AI/level/padding passes. They now
   skip `Difficulty: Normal` blocks, treating the Hard block as canonical.
2. `tools/build_standard_levels.py` — recovers each trainer's pre-uplift levels
   per slot from git (`74c0f0a7~1`, the commit before the level uplift) into
   `tools/standard_levels.json`, for every trainer whose team size is unchanged.
3. `tools/difficulty_split.py` — writes the two blocks. Standard levels come
   from, in priority order:
   * exact per-slot pre-uplift levels (`standard_levels.json`) — gym leaders,
     Elite Four, Champion, superboss, and most route trainers;
   * the base variant's pre-uplift levels for rematch variants (`…_2`..`_6`)
     whose team size changed;
   * a rescale of the Hard levels from the segment's `level_band` onto its
     `standard_band` (`tools/kaizo_segments.json`) for the VS-Seeker roster
     added after the uplift.
   A floor guarantees Standard is never harder than Hard on any slot.

## Test plan coverage

1. Standard → Brock ace 14 (his pre-uplift team shifted down two via
   `STANDARD_LEVEL_OVERRIDES` in `difficulty_split.py`). `trainers.h` shows
   `[DIFFICULTY_NORMAL][TRAINER_LEADER_BROCK]` Onix at 14.
2. Hard → Brock ace 22. `[DIFFICULTY_HARD][…]` Onix at 22.
3. Persistence: the var lives in saveblock1 and is set after `NewGameInitData`,
   so it survives save/reload through the endgame.
4. Shared systems: `difficulty_split.py` only rewrites `Level:` lines; a Python
   invariant check confirms species/moves/items/EVs/IVs are identical between
   the two blocks for all 692 split trainers.
5. Scaling stacks: rematch/gym/FRODO boosts apply in `CreateNPCTrainerParty`
   after the tier is selected, so they stack on both bases.
6. Pre-feature save: the var reads 0 and maps to Hard (see above).
