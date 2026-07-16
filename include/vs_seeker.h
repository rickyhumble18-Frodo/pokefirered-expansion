#ifndef GUARD_VS_SEEKER_H
#define GUARD_VS_SEEKER_H

#include "global.h"
#include "script.h"

#define REMATCH_TRAINER_COUNT 221
#define MAX_REMATCH_PARTIES 6
#define VSSEEKER_RECHARGE_STEPS 100

// Placeholder in a rematch chain for a story-progression stage where the
// trainer's party doesn't change (see sRematches).
#define REMATCH_SKIP_ID 0xFFFF

struct RematchData
{
    enum TrainerID trainerIDs[MAX_REMATCH_PARTIES];
    u16 mapGroup; // unused
    u16 mapNum; // unused
};

void Task_VsSeeker_0(u8 taskId);
void ClearRematchStateByTrainerId(void);
void ClearRematchStateOfLastTalked(void);
enum TrainerID GetRematchTrainerId(enum TrainerID trainerId);
bool8 UpdateVsSeekerStepCounter(void);
void MapResetTrainerRematches(u16 mapGroup, u16 mapNum);
void NativeVsSeekerRematchId(struct ScriptContext *ctx);
bool32 GetActiveTrainerRematches(u32 matchCallId);
void SetActiveTrainerRematches(u32 matchCallId, u32 value);
u32 GetTrainerRematchStepCounter(void);
void SetTrainerRematchStepCounter(u32 value);

extern const struct RematchData sRematches[];

#endif //GUARD_VS_SEEKER_H
