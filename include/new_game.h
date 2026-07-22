#ifndef GUARD_NEW_GAME_H
#define GUARD_NEW_GAME_H

#include "global.h"

extern bool8 gDifferentSaveFile;

// Difficulty tier chosen on the new-game menu (see src/oak_speech.c). Held in a
// global rather than the difficulty var because NewGameInitData clears every
// saveblock1 var; it is applied once that reset has finished.
extern u8 gNewGameStartDifficulty;

void SetTrainerId(u32 trainerId, u8 *dst);
u32 GetTrainerId(u8 *trainerId);
void CopyTrainerId(u8 *dst, u8 *src);
void NewGameInitData(void);
void ResetMenuAndMonGlobals(void);
void Sav2_ClearSetDefault(void);

#endif // GUARD_NEW_GAME_H
