#include "global.h"
#include "data.h"
#include "event_data.h"
#include "rematch_scaling.h"
#include "vs_seeker.h"
#include "constants/trainers.h"
#include "constants/vars.h"

// Persistent rematch win counters and level scaling.
//
// Every defeat of a trainer raises the levels of their next party:
// +2 per win for regular trainers, +5 per win for bosses (gym leaders,
// Elite Four, Champion). Route trainer counters are stored in
// gSaveBlock1Ptr->rematchWinCounts (indexed by enum RematchID); boss
// counters use the VAR_REMATCH_* vars so map scripts can read them too.

STATIC_ASSERT(REMATCH_TRAINER_COUNT == REMATCH_COUNT, RematchTableSizeMatchesRematchIDs);

#define MAX_BOSS_VARIANTS 3

struct BossRematch
{
    u16 counterVar;
    u8 numVariants;
    enum TrainerID variants[MAX_BOSS_VARIANTS];
};

// Every trainer ID a boss can appear as, grouped under one counter.
// variants[0] is the base ID the counter is keyed to; the battle cycles
// through the list as the win count climbs. The Champion is one logical
// boss with three starter-dependent variant chains sharing a counter.
static const struct BossRematch sBossRematches[] =
{
    { VAR_REMATCH_BROCK,    2, { TRAINER_LEADER_BROCK,    TRAINER_LEADER_BROCK_2    } },
    { VAR_REMATCH_MISTY,    2, { TRAINER_LEADER_MISTY,    TRAINER_LEADER_MISTY_2    } },
    { VAR_REMATCH_LT_SURGE, 2, { TRAINER_LEADER_LT_SURGE, TRAINER_LEADER_LT_SURGE_2 } },
    { VAR_REMATCH_ERIKA,    2, { TRAINER_LEADER_ERIKA,    TRAINER_LEADER_ERIKA_2    } },
    { VAR_REMATCH_KOGA,     2, { TRAINER_LEADER_KOGA,     TRAINER_LEADER_KOGA_2     } },
    { VAR_REMATCH_SABRINA,  2, { TRAINER_LEADER_SABRINA,  TRAINER_LEADER_SABRINA_2  } },
    { VAR_REMATCH_BLAINE,   2, { TRAINER_LEADER_BLAINE,   TRAINER_LEADER_BLAINE_2   } },
    { VAR_REMATCH_GIOVANNI, 2, { TRAINER_LEADER_GIOVANNI, TRAINER_LEADER_GIOVANNI_2 } },
    { VAR_REMATCH_LORELEI,  2, { TRAINER_ELITE_FOUR_LORELEI, TRAINER_ELITE_FOUR_LORELEI_2 } },
    { VAR_REMATCH_BRUNO,    2, { TRAINER_ELITE_FOUR_BRUNO,   TRAINER_ELITE_FOUR_BRUNO_2   } },
    { VAR_REMATCH_AGATHA,   2, { TRAINER_ELITE_FOUR_AGATHA,  TRAINER_ELITE_FOUR_AGATHA_2  } },
    { VAR_REMATCH_LANCE,    2, { TRAINER_ELITE_FOUR_LANCE,   TRAINER_ELITE_FOUR_LANCE_2   } },
    { VAR_REMATCH_CHAMPION, 2, { TRAINER_CHAMPION_FIRST_SQUIRTLE,   TRAINER_CHAMPION_REMATCH_SQUIRTLE   } },
    { VAR_REMATCH_CHAMPION, 2, { TRAINER_CHAMPION_FIRST_BULBASAUR,  TRAINER_CHAMPION_REMATCH_BULBASAUR  } },
    { VAR_REMATCH_CHAMPION, 2, { TRAINER_CHAMPION_FIRST_CHARMANDER, TRAINER_CHAMPION_REMATCH_CHARMANDER } },
    { VAR_REMATCH_FRODO,    3, { TRAINER_SUPERBOSS_FRODO, TRAINER_SUPERBOSS_FRODO_2, TRAINER_SUPERBOSS_FRODO_3 } },
};

static EWRAM_DATA u32 sPartyLevelBoost = 0;

static const struct BossRematch *FindBossRematch(enum TrainerID trainerId)
{
    u32 i, j;

    for (i = 0; i < ARRAY_COUNT(sBossRematches); i++)
    {
        for (j = 0; j < sBossRematches[i].numVariants; j++)
        {
            if (sBossRematches[i].variants[j] == trainerId)
                return &sBossRematches[i];
        }
    }
    return NULL;
}

// Returns the index into sRematches whose chain contains trainerId, or -1.
static s32 FindRematchTableIdx(enum TrainerID trainerId)
{
    u32 i, j;

    for (i = 0; i < REMATCH_TRAINER_COUNT; i++)
    {
        for (j = 0; j < MAX_REMATCH_PARTIES; j++)
        {
            enum TrainerID id = sRematches[i].trainerIDs[j];
            if (id == TRAINER_NONE)
                break;
            if (id == REMATCH_SKIP_ID)
                continue;
            if (id == trainerId)
                return i;
        }
    }
    return -1;
}

bool8 IsBossTrainer(enum TrainerID trainerId)
{
    switch (GetTrainerClassFromId(trainerId))
    {
    case TRAINER_CLASS_LEADER:
    case TRAINER_CLASS_ELITE_FOUR:
    case TRAINER_CLASS_CHAMPION:
        return TRUE;
    default:
        return FALSE;
    }
}

// Maps any variant trainer ID back to the ID its win counter is keyed to.
enum TrainerID GetBaseTrainerId(enum TrainerID trainerId)
{
    const struct BossRematch *boss = FindBossRematch(trainerId);
    s32 rematchIdx;

    if (boss != NULL)
        return boss->variants[0];

    rematchIdx = FindRematchTableIdx(trainerId);
    if (rematchIdx != -1)
        return sRematches[rematchIdx].trainerIDs[0];

    return trainerId;
}

u16 GetRematchWinCount(enum TrainerID trainerId)
{
    const struct BossRematch *boss = FindBossRematch(trainerId);
    s32 rematchIdx;

    if (boss != NULL)
        return VarGet(boss->counterVar);

    rematchIdx = FindRematchTableIdx(trainerId);
    if (rematchIdx != -1)
        return gSaveBlock1Ptr->rematchWinCounts[rematchIdx];

    return 0;
}

void IncrementRematchWinCount(enum TrainerID trainerId)
{
    const struct BossRematch *boss = FindBossRematch(trainerId);
    s32 rematchIdx;

    if (boss != NULL)
    {
        u16 count = VarGet(boss->counterVar);
        if (count < 0xFFFF)
            VarSet(boss->counterVar, count + 1);
        return;
    }

    rematchIdx = FindRematchTableIdx(trainerId);
    if (rematchIdx != -1 && gSaveBlock1Ptr->rematchWinCounts[rematchIdx] < 0xFF)
        gSaveBlock1Ptr->rematchWinCounts[rematchIdx]++;
}

// For bosses, picks which team variant to fight based on the win count.
// Non-boss IDs are returned unchanged (route trainer variants are picked
// by the VS Seeker in GetRematchTrainerId).
enum TrainerID GetBossVariantTrainerId(enum TrainerID trainerId)
{
    const struct BossRematch *boss = FindBossRematch(trainerId);

    if (boss == NULL)
        return trainerId;

    return boss->variants[VarGet(boss->counterVar) % boss->numVariants];
}

// Called before enemy party generation so GetScaledTrainerMonLevel can
// boost levels. Cleared by CreateNPCTrainerPartyFromTrainer when done, so
// parties built outside the standard opponent path are never scaled.
void SetTrainerPartyLevelScaling(enum TrainerID trainerId)
{
    enum TrainerID baseId = GetBaseTrainerId(trainerId);
    u32 perWin = IsBossTrainer(baseId) ? REMATCH_LEVEL_BOOST_BOSS : REMATCH_LEVEL_BOOST_TRAINER;

    sPartyLevelBoost = perWin * GetRematchWinCount(baseId);
}

void ClearTrainerPartyLevelScaling(void)
{
    sPartyLevelBoost = 0;
}

u32 GetScaledTrainerMonLevel(u32 baseLevel)
{
    u32 level = baseLevel + sPartyLevelBoost;

    if (level > MAX_LEVEL)
        level = MAX_LEVEL;
    if (level < 1)
        level = 1;
    return level;
}

// Script interface for testing: gSpecialVar_0x8004 holds a trainer ID.
void Special_GetRematchWinCount(void)
{
    gSpecialVar_Result = GetRematchWinCount(gSpecialVar_0x8004);
}

// gSpecialVar_0x8004 = trainer ID, gSpecialVar_0x8005 = new win count.
// Boss counters can also be edited directly through the debug menu's
// variable editor (VAR_REMATCH_*).
void Special_SetRematchWinCount(void)
{
    enum TrainerID trainerId = gSpecialVar_0x8004;
    const struct BossRematch *boss = FindBossRematch(trainerId);
    s32 rematchIdx;

    if (boss != NULL)
    {
        VarSet(boss->counterVar, gSpecialVar_0x8005);
        return;
    }

    rematchIdx = FindRematchTableIdx(trainerId);
    if (rematchIdx != -1)
        gSaveBlock1Ptr->rematchWinCounts[rematchIdx] = min(gSpecialVar_0x8005, 0xFF);
}
