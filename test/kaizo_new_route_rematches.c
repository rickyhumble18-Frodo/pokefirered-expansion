#include "global.h"
#include "event_data.h"
#include "battle_setup.h"
#include "vs_seeker.h"
#include "rematch_scaling.h"
#include "test/test.h"
#include "constants/vs_seeker.h"

// Exercises the exact rematch logic the VS Seeker uses (GetRematchTrainerId,
// GetRematchWinCount / IncrementRematchWinCount, SetTrainerPartyLevelScaling /
// GetScaledTrainerMonLevel) against a sample of the 40 new route trainers,
// on the headless mGBA core. Confirms: a beaten new trainer offers a rematch,
// the 2 teams cycle by win count, and levels climb +2 per win and clamp.

static void ArmNewTrainer(enum TrainerID base)
{
    // Preconditions the VS Seeker relies on: the trainer has been beaten and
    // the player owns the VS Seeker (which unlocks variant party index 1).
    FlagSet(FLAG_GOT_VS_SEEKER);
    SetTrainerFlag(base);
}

static void CheckCycles(enum RematchID rid, enum TrainerID base, enum TrainerID variant)
{
    ArmNewTrainer(base);
    gSaveBlock1Ptr->rematchWinCounts[rid] = 0;   // clean, deterministic start

    // confirm setup took, so a lookup miss is distinguishable from a state miss
    EXPECT(FlagGet(FLAG_GOT_VS_SEEKER));
    EXPECT(HasTrainerBeenFought(base));
    EXPECT_EQ(GetRematchWinCount(base), 0);

    EXPECT_EQ(GetRematchTrainerId(base), base);      // count 0 -> base team
    IncrementRematchWinCount(base);
    EXPECT_EQ(GetRematchWinCount(base), 1);
    EXPECT_EQ(GetRematchTrainerId(base), variant);   // count 1 -> variant team
    IncrementRematchWinCount(base);
    EXPECT_EQ(GetRematchTrainerId(base), base);      // count 2 -> cycles back
}

TEST("Kaizo CONTROL: an existing vanilla rematch trainer cycles")
{
    // Same methodology against a vanilla trainer; if this fails too, the test
    // harness (not the new data) is the problem.
    ArmNewTrainer(TRAINER_YOUNGSTER_BEN);
    gSaveBlock1Ptr->rematchWinCounts[REMATCH_YOUNGSTER_BEN] = 0;
    EXPECT_EQ(GetRematchTrainerId(TRAINER_YOUNGSTER_BEN), TRAINER_YOUNGSTER_BEN);
}

TEST("Kaizo new route trainers cycle their 2 rematch teams by win count")
{
    CheckCycles(REMATCH_HIKER_DWAYNE,       TRAINER_HIKER_DWAYNE,       TRAINER_HIKER_DWAYNE_2);
    CheckCycles(REMATCH_BIKER_RAZOR,        TRAINER_BIKER_RAZOR,        TRAINER_BIKER_RAZOR_2);
    CheckCycles(REMATCH_POKEMANIAC_WENDELL, TRAINER_POKEMANIAC_WENDELL, TRAINER_POKEMANIAC_WENDELL_2);
    CheckCycles(REMATCH_SWIMMER_F_CORAL,    TRAINER_SWIMMER_F_CORAL,    TRAINER_SWIMMER_F_CORAL_2);
}

TEST("Kaizo new route trainer levels climb +2 per rematch win and clamp")
{
    enum TrainerID base = TRAINER_BIKER_RAZOR;
    u32 baseLevel = 73; // Razor's in-band ace level

    ArmNewTrainer(base);
    while (GetRematchWinCount(base) != 0)
        IncrementRematchWinCount(base);

    SetTrainerPartyLevelScaling(base);
    EXPECT_EQ(GetScaledTrainerMonLevel(baseLevel), 73); // 0 wins

    IncrementRematchWinCount(base);
    SetTrainerPartyLevelScaling(base);
    EXPECT_EQ(GetScaledTrainerMonLevel(baseLevel), 75); // +2

    IncrementRematchWinCount(base);
    SetTrainerPartyLevelScaling(base);
    EXPECT_EQ(GetScaledTrainerMonLevel(baseLevel), 77); // +4 (route trainer = +2/win)

    // Push the counter high; the scaled level must clamp at MAX_LEVEL.
    while (GetRematchWinCount(base) < 200)
        IncrementRematchWinCount(base);
    SetTrainerPartyLevelScaling(base);
    EXPECT_EQ(GetScaledTrainerMonLevel(baseLevel), MAX_LEVEL);
}
