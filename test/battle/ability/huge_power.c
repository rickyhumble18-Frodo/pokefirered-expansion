#include "global.h"
#include "test/battle.h"

// Regigigas's second ability slot is Huge Power in this hack (a kaizo boss
// ability; see docs). These verify the physical-attack doubling is applied
// correctly - including at the high levels bosses and rematch scaling reach,
// where the base-damage formula must not overflow.

SINGLE_BATTLE_TEST("Huge Power doubles Regigigas's physical damage", s16 damage)
{
    u32 ability;
    PARAMETRIZE { ability = ABILITY_STAMINA; }     // inert while attacking
    PARAMETRIZE { ability = ABILITY_HUGE_POWER; }
    GIVEN {
        ASSUME(GetMoveCategory(MOVE_TACKLE) == DAMAGE_CATEGORY_PHYSICAL);
        PLAYER(SPECIES_REGIGIGAS) { Ability(ability); Level(50); }
        OPPONENT(SPECIES_SHUCKLE) { Level(50); MaxHP(600); HP(600); }
    } WHEN {
        TURN { MOVE(player, MOVE_TACKLE); MOVE(opponent, MOVE_CELEBRATE); }
    } SCENE {
        HP_BAR(opponent, captureDamage: &results[i].damage);
    } FINALLY {
        EXPECT_MUL_EQ(results[0].damage, Q_4_12(2.0), results[1].damage);
    }
}

SINGLE_BATTLE_TEST("Huge Power does not boost Regigigas's special moves", s16 damage)
{
    u32 ability;
    PARAMETRIZE { ability = ABILITY_STAMINA; }
    PARAMETRIZE { ability = ABILITY_HUGE_POWER; }
    GIVEN {
        ASSUME(GetMoveCategory(MOVE_HYPER_VOICE) == DAMAGE_CATEGORY_SPECIAL);
        PLAYER(SPECIES_REGIGIGAS) { Ability(ability); Level(50); }
        OPPONENT(SPECIES_SHUCKLE) { Level(50); MaxHP(600); HP(600); }
    } WHEN {
        TURN { MOVE(player, MOVE_HYPER_VOICE); MOVE(opponent, MOVE_CELEBRATE); }
    } SCENE {
        HP_BAR(opponent, captureDamage: &results[i].damage);
    } FINALLY {
        EXPECT_EQ(results[0].damage, results[1].damage);
    }
}

SINGLE_BATTLE_TEST("Huge Power still doubles cleanly at high level (no overflow)", s16 damage)
{
    u32 ability;
    PARAMETRIZE { ability = ABILITY_STAMINA; }
    PARAMETRIZE { ability = ABILITY_HUGE_POWER; }
    GIVEN {
        ASSUME(GetMoveCategory(MOVE_TACKLE) == DAMAGE_CATEGORY_PHYSICAL);
        PLAYER(SPECIES_REGIGIGAS) { Ability(ability); Level(250); }
        OPPONENT(SPECIES_SHUCKLE) { Level(250); MaxHP(30000); HP(30000); }
    } WHEN {
        TURN { MOVE(player, MOVE_TACKLE); MOVE(opponent, MOVE_CELEBRATE); }
    } SCENE {
        HP_BAR(opponent, captureDamage: &results[i].damage);
    } FINALLY {
        EXPECT_MUL_EQ(results[0].damage, Q_4_12(2.0), results[1].damage);
    }
}
