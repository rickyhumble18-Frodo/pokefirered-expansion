IndigoPlateau_PokemonCenter_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, IndigoPlateau_PokemonCenter_1F_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
	.byte 0

IndigoPlateau_PokemonCenter_1F_OnTransition::
	setrespawn HEAL_LOCATION_INDIGO_PLATEAU
	specialvar VAR_RESULT, IsNationalPokedexEnabled
	call_if_eq VAR_RESULT, TRUE, IndigoPlateau_PokemonCenter_1F_EventScript_CheckBlockDoor
	end

IndigoPlateau_PokemonCenter_1F_EventScript_CheckBlockDoor::
	goto_if_set FLAG_SYS_CAN_LINK_WITH_RS, EventScript_Return
	setobjectxyperm LOCALID_LEAGUE_DOOR_GUARD, 4, 2
	return

IndigoPlateau_PokemonCenter_1F_EventScript_DoorGuard::
	lock
	faceplayer
	specialvar VAR_RESULT, IsNationalPokedexEnabled
	goto_if_eq VAR_RESULT, TRUE, IndigoPlateau_PokemonCenter_1F_EventScript_CheckSeviiIslandComplete
	msgbox IndigoPlateau_PokemonCenter_1F_Text_FaceEliteFourGoodLuck
	release
	end

IndigoPlateau_PokemonCenter_1F_EventScript_CheckSeviiIslandComplete::
	goto_if_set FLAG_SYS_CAN_LINK_WITH_RS, IndigoPlateau_PokemonCenter_1F_EventScript_SeviiIslandComplete
	msgbox IndigoPlateau_PokemonCenter_1F_Text_LoreleiIsAbsentClosedForTimeBeing
	release
	end

IndigoPlateau_PokemonCenter_1F_EventScript_SeviiIslandComplete::
	msgbox IndigoPlateau_PokemonCenter_1F_Text_FaceEliteFourGoodLuck
	release
	end

IndigoPlateau_PokemonCenter_1F_EventScript_GymGuy::
	msgbox IndigoPlateau_PokemonCenter_1F_Text_GymGuyAdvice, MSGBOX_NPC
	end

IndigoPlateau_PokemonCenter_1F_EventScript_Clerk::
	goto_if_questlog EventScript_ReleaseEnd
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart SHOP_ID_INDIGO_PLATEAU_POKEMON_CENTER_1F
	msgbox Text_PleaseComeAgain
	release
	end

IndigoPlateau_PokemonCenter_1F_EventScript_Nurse::
	lock
	faceplayer
	call EventScript_PkmnCenterNurse
	release
	end

	.set ABILITY_COACH_PRICE, 100000

IndigoPlateau_PokemonCenter_1F_EventScript_AbilityCoach::
	lock
	faceplayer
	goto_if_unset FLAG_SYS_GAME_CLEAR, IndigoPlateau_PokemonCenter_1F_EventScript_AbilityCoachNotChampion
	msgbox IndigoPlateau_PokemonCenter_1F_Text_AbilityCoachIntro, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, IndigoPlateau_PokemonCenter_1F_EventScript_AbilityCoachBye
	special ChoosePartyMon
	waitstate
	lock
	faceplayer
	goto_if_ge VAR_0x8004, PARTY_SIZE, IndigoPlateau_PokemonCenter_1F_EventScript_AbilityCoachBye
	specialvar VAR_RESULT, ScriptGetPartyMonSpecies
	goto_if_eq VAR_RESULT, SPECIES_EGG, IndigoPlateau_PokemonCenter_1F_EventScript_AbilityCoachEgg
	special ScrSpecial_BufferMonAbility
	msgbox IndigoPlateau_PokemonCenter_1F_Text_AbilityCoachCurrent
	multichoice 0, 0, MULTI_ABILITY_COACH, FALSE
	switch VAR_RESULT
	case 3, IndigoPlateau_PokemonCenter_1F_EventScript_AbilityCoachBye
	case MULTI_B_PRESSED, IndigoPlateau_PokemonCenter_1F_EventScript_AbilityCoachBye
	copyvar VAR_0x8005, VAR_RESULT
	setvar VAR_0x8006, 0
	special ScrSpecial_SetMonAbilitySlot
	goto_if_eq VAR_RESULT, 0, IndigoPlateau_PokemonCenter_1F_EventScript_AbilityCoachInvalid
	showmoneybox 0, 0
	msgbox IndigoPlateau_PokemonCenter_1F_Text_AbilityCoachConfirm, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, IndigoPlateau_PokemonCenter_1F_EventScript_AbilityCoachDeclined
	checkmoney ABILITY_COACH_PRICE
	goto_if_eq VAR_RESULT, FALSE, IndigoPlateau_PokemonCenter_1F_EventScript_AbilityCoachNoMoney
	removemoney ABILITY_COACH_PRICE
	updatemoneybox
	setvar VAR_0x8006, 1
	special ScrSpecial_SetMonAbilitySlot
	goto_if_eq VAR_RESULT, 0, IndigoPlateau_PokemonCenter_1F_EventScript_AbilityCoachInvalid
	playfanfare MUS_LEVEL_UP
	waitfanfare
	msgbox IndigoPlateau_PokemonCenter_1F_Text_AbilityCoachDone
	hidemoneybox
	release
	end

IndigoPlateau_PokemonCenter_1F_EventScript_AbilityCoachNotChampion::
	msgbox IndigoPlateau_PokemonCenter_1F_Text_AbilityCoachNotChampion
	release
	end

IndigoPlateau_PokemonCenter_1F_EventScript_AbilityCoachInvalid::
	hidemoneybox
	msgbox IndigoPlateau_PokemonCenter_1F_Text_AbilityCoachInvalid
	release
	end

IndigoPlateau_PokemonCenter_1F_EventScript_AbilityCoachDeclined::
	hidemoneybox
	msgbox IndigoPlateau_PokemonCenter_1F_Text_AbilityCoachBye2
	release
	end

IndigoPlateau_PokemonCenter_1F_EventScript_AbilityCoachNoMoney::
	hidemoneybox
	msgbox IndigoPlateau_PokemonCenter_1F_Text_AbilityCoachNoMoney
	release
	end

IndigoPlateau_PokemonCenter_1F_EventScript_AbilityCoachEgg::
	msgbox IndigoPlateau_PokemonCenter_1F_Text_AbilityCoachEgg
	release
	end

IndigoPlateau_PokemonCenter_1F_EventScript_AbilityCoachBye::
	msgbox IndigoPlateau_PokemonCenter_1F_Text_AbilityCoachBye2
	release
	end

IndigoPlateau_PokemonCenter_1F_Text_AbilityCoachIntro::
	.string "I study POKéMON potential.\p"
	.string "For ¥100,000 I can awaken a\n"
	.string "different ability in a POKéMON…\l"
	.string "even a HIDDEN one.\p"
	.string "Interested?$"

IndigoPlateau_PokemonCenter_1F_Text_AbilityCoachCurrent::
	.string "Its ability right now is\n"
	.string "{STR_VAR_2}.\p"
	.string "Which slot shall I awaken?$"

IndigoPlateau_PokemonCenter_1F_Text_AbilityCoachConfirm::
	.string "That slot holds {STR_VAR_3}.\p"
	.string "The price is ¥100,000.\n"
	.string "Shall I proceed?$"

IndigoPlateau_PokemonCenter_1F_Text_AbilityCoachDone::
	.string "It's done!\p"
	.string "Its ability is now\n"
	.string "{STR_VAR_3}!$"

IndigoPlateau_PokemonCenter_1F_Text_AbilityCoachInvalid::
	.string "Hmm… no. Either it has no ability\n"
	.string "in that slot, or that slot is\l"
	.string "already active.\p"
	.string "No charge, of course.$"

IndigoPlateau_PokemonCenter_1F_Text_AbilityCoachNoMoney::
	.string "You don't have ¥100,000.\n"
	.string "I don't work on credit.$"

IndigoPlateau_PokemonCenter_1F_Text_AbilityCoachEgg::
	.string "…That's an EGG.\n"
	.string "It hasn't even decided what it is.$"

IndigoPlateau_PokemonCenter_1F_Text_AbilityCoachNotChampion::
	.string "My services are for CHAMPIONS.\p"
	.string "Come back once your name is in\n"
	.string "the HALL OF FAME.$"

IndigoPlateau_PokemonCenter_1F_Text_AbilityCoachBye2::
	.string "Potential is patient.\n"
	.string "It'll wait.$"
