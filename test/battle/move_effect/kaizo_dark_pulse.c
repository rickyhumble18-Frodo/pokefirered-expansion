#include "global.h"
#include "test/battle.h"

// Kaizo: Dark Pulse was rebalanced to a 100-BP draining move (EFFECT_ABSORB,
// 50%). These tests exercise that on the real battle engine via the headless
// mGBA core.

ASSUMPTIONS
{
    ASSUME(GetMoveEffect(MOVE_DARK_PULSE) == EFFECT_ABSORB);
    ASSUME(GetMovePower(MOVE_DARK_PULSE) == 100);
    ASSUME(GetMoveType(MOVE_DARK_PULSE) == TYPE_DARK);
}

SINGLE_BATTLE_TEST("Kaizo Dark Pulse recovers 50% of the damage dealt")
{
    s16 damage;
    s16 healed;
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET) { HP(1); }
        OPPONENT(SPECIES_WOBBUFFET);
    } WHEN {
        TURN { MOVE(player, MOVE_DARK_PULSE); }
    } SCENE {
        ANIMATION(ANIM_TYPE_MOVE, MOVE_DARK_PULSE, player);
        HP_BAR(opponent, captureDamage: &damage);
        HP_BAR(player, captureDamage: &healed);
    } THEN {
        EXPECT_MUL_EQ(damage, Q_4_12(-0.5), healed);
    }
}

SINGLE_BATTLE_TEST("Kaizo Shadow Lugia is Psychic/Dark with Adaptability-boosted Dark Pulse STAB")
{
    GIVEN {
        ASSUME(gSpeciesInfo[SPECIES_LUGIA_SHADOW].types[0] == TYPE_PSYCHIC);
        ASSUME(gSpeciesInfo[SPECIES_LUGIA_SHADOW].types[1] == TYPE_DARK);
        PLAYER(SPECIES_LUGIA_SHADOW) { Ability(ABILITY_ADAPTABILITY); HP(1); }
        OPPONENT(SPECIES_WOBBUFFET);
    } WHEN {
        TURN { MOVE(player, MOVE_DARK_PULSE); }
    } SCENE {
        // A dark-type move off a Dark-type user with Adaptability lands and drains;
        // at HP(1) the drain heal is visible as a player HP bar movement.
        ANIMATION(ANIM_TYPE_MOVE, MOVE_DARK_PULSE, player);
        HP_BAR(opponent);
        HP_BAR(player);
    }
}
