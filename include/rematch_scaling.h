#ifndef GUARD_REMATCH_SCALING_H
#define GUARD_REMATCH_SCALING_H

#include "global.h"

// Levels added to a trainer's party per previous win against them.
#define REMATCH_LEVEL_BOOST_TRAINER 2
#define REMATCH_LEVEL_BOOST_BOSS    5

u16 GetRematchWinCount(enum TrainerID trainerId);
void IncrementRematchWinCount(enum TrainerID trainerId);
bool8 IsBossTrainer(enum TrainerID trainerId);
enum TrainerID GetBaseTrainerId(enum TrainerID trainerId);
enum TrainerID GetBossVariantTrainerId(enum TrainerID trainerId);
void SetTrainerPartyLevelScaling(enum TrainerID trainerId);
void ClearTrainerPartyLevelScaling(void);
u32 GetScaledTrainerMonLevel(u32 baseLevel);

void Special_GetRematchWinCount(void);
void Special_SetRematchWinCount(void);

#endif // GUARD_REMATCH_SCALING_H
