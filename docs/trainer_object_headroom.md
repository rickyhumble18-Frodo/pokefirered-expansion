# FireRed Kaizo — Trainer & Object Headroom Report

All figures below were confirmed by compiling the actual constants (not grep
counts) against `include/`, and cross-checked with `git blame` to distinguish
this fork's changes from upstream. Numbers current as of the audit.

## 1. Object Event Caps — unchanged from vanilla

```
OBJECT_EVENTS_COUNT           16    (include/constants/global.h:87)
OBJECT_EVENT_TEMPLATES_COUNT  64    (include/constants/global.h:88)
```

Neither was raised by this fork — both trace to the initial import commit, no
later override.

- **64 templated objects per map** — the hard per-map file limit (NPCs +
  trainers + items + signs combined).
- **16 active runtime slots** — a single global pool (`gObjectEvents[16]`), NOT
  per-map. The player permanently occupies one slot, leaving **15** for
  everything else loaded near the player at once. The engine streams objects
  in/out by proximity, so a map may *template* far more than 15; only ~15 are
  ever live simultaneously. Vanilla FRLG already depends on this, so it is not a
  practical constraint for adding trainers.

## 2. Per-Map Object Counts (of the 64 template cap)

| Map | Objects | Slack |
|---|---|---|
| Route 24 | 8 | 56 |
| Route 25 | 13 | 51 |
| Cerulean Cave 1F | 9 | 55 |
| Cerulean Cave 2F | 13 | 51 |
| Cerulean Cave B1F | 13 | 51 |
| Victory Road 1F | 7 | 57 |
| Victory Road 2F | 13 | 51 |
| Victory Road 3F | 12 | 52 |

**Whole-ROM context:** busiest single map is One Island Kindle Road at
**29/64**; median across all 481 maps is **3**. Every map has massive slack —
adding trainers is never object-cap-bound in practice.

## 3. Trainer ID Enum — appendable, large headroom

`enum TrainerID` (`include/constants/opponents.h`) is a plain sequential enum
with a trailing `TRAINERS_COUNT` sentinel. `gTrainers[DIFFICULTY_COUNT][TRAINERS_COUNT]`
and related arrays auto-size off it, so appending a `TRAINER_*` entry is free at
the enum/array level.

Compiled values:

```
TRAINERS_COUNT      = 675     (current trainers defined)
MAX_TRAINERS_COUNT  = 768     (trainer-defeated flag space: TRAINER_FLAGS_START..END)
HEADROOM            = 93      trainers before flag space overflows
```

The header comment beside `MAX_TRAINERS_COUNT` previously claimed "only space
for 25 additional trainers" — that was stale (predated this hack's additions)
and has been corrected to derive from `MAX_TRAINERS_COUNT - TRAINERS_COUNT`.
Exceeding 93 overflows the trainer-defeated flags into `SYS_FLAGS`; recoverable
by raising `MAX_TRAINERS_COUNT`, but it costs saveblock space and requires
re-verifying flag ranges (`include/constants/flags.h`).

## 4. Fixed-Size Structures Indexed by Trainer/Rematch Count — the real constraints

| Structure | Location | Sizing | Auto-scales? | Risk |
|---|---|---|---|---|
| `rematchWinCounts[REMATCH_COUNT]` (saveblock) | `include/global.h:1046` | `REMATCH_COUNT` = **221** (enum sentinel) | **Yes** | None — grows automatically with the `enum RematchID` sentinel. |
| `sRematches[REMATCH_TRAINER_COUNT]` (VS Seeker table) | `src/data/trainer_rematches.h` | `REMATCH_TRAINER_COUNT` = **221** (manual `#define`, `include/vs_seeker.h:7`) | **No** | **The one real trap.** Kept in sync only by `STATIC_ASSERT(REMATCH_TRAINER_COUNT == REMATCH_COUNT)` in `src/rematch_scaling.c`. Forgetting the bump = loud compile error (safe). But bumping the define and forgetting the `[REMATCH_NEW] = {...}` entry = **silent** zero-init to `TRAINER_NONE` -> broken rematch chain, no error. |
| `sBossRematches[]` (boss rotation) | `src/rematch_scaling.c:32` | Unsized `[]`, linear scan via `ARRAY_COUNT` | **Yes** | None on total entries. Only fixed value is `MAX_BOSS_VARIANTS = 3` (rotation slots per boss); FRODO already uses all 3. |
| Trainer-defeated flags | `TRAINER_FLAGS_START..END` (`include/constants/flags.h`) | `MAX_TRAINERS_COUNT` = 768 | via section 3 | 93 headroom. |
| `sizeof(struct SaveBlock1)` | `STATIC_ASSERT`, `src/save.c:82` | `<= SAVEBLOCK1_SIZE` | compile-checked | Currently passing (slack exists); only relevant if a saveblock array grows by hundreds of entries. |

## Bottom Line

- **Object slots and the trainer-ID enum are effectively unconstrained** at this
  project's scale (93 trainer-flag headroom, 35+ free object slots on the
  busiest relevant map).
- **The single place needing disciplined editing is a new VS-Seeker-rematchable
  route trainer**, which requires all three of: (1) `enum RematchID` entry,
  (2) `REMATCH_TRAINER_COUNT` bump, (3) `sRematches[]` designated-initializer
  entry. Miss #3 and it fails silently rather than at compile time.
- **Bosses, one-off statics, and non-rematchable trainers have no such trap** —
  append and go.
