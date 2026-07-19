CeruleanCave_B1F_MapScripts::
	map_script MAP_SCRIPT_ON_RESUME, CeruleanCave_B1F_OnResume
	map_script MAP_SCRIPT_ON_TRANSITION, CeruleanCave_B1F_OnTransition
	.byte 0

CeruleanCave_B1F_OnResume::
	call_if_set FLAG_SYS_SPECIAL_WILD_BATTLE, CeruleanCave_B1F_EventScript_TryRemoveMewtwo
	end

CeruleanCave_B1F_EventScript_TryRemoveMewtwo::
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_ne VAR_RESULT, B_OUTCOME_CAUGHT, EventScript_Return
	removeobject VAR_LAST_TALKED
	return

CeruleanCave_B1F_OnTransition::
	call_if_unset FLAG_FOUGHT_MEWTWO, CeruleanCave_B1F_EventScript_ShowMewtwo
	call_if_ge VAR_REMATCH_FRODO, 1, CeruleanCave_B1F_EventScript_SuperbossAside
	end

CeruleanCave_B1F_EventScript_ShowMewtwo::
	clearflag FLAG_HIDE_MEWTWO
	return

CeruleanCave_B1F_EventScript_Mewtwo::
	goto_if_questlog EventScript_ReleaseEnd
	special QuestLog_CutRecording
	lock
	faceplayer
	waitse
	playmoncry SPECIES_MEWTWO, CRY_MODE_ENCOUNTER
	message CeruleanCave_B1F_Text_Mew
	waitmessage
	waitmoncry
	delay 20
	playbgm MUS_ENCOUNTER_GYM_LEADER, 0
	waitbuttonpress
	setwildbattle SPECIES_MEWTWO, 70
	setflag FLAG_SYS_SPECIAL_WILD_BATTLE
	special BattleSetup_StartLegendaryBattle
	waitstate
	clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, CeruleanCave_B1F_EventScript_DefeatedMewtwo
	goto_if_eq VAR_RESULT, B_OUTCOME_RAN, CeruleanCave_B1F_EventScript_RanFromMewtwo
	goto_if_eq VAR_RESULT, B_OUTCOME_PLAYER_TELEPORTED, CeruleanCave_B1F_EventScript_RanFromMewtwo
	setflag FLAG_FOUGHT_MEWTWO
	release
	end

CeruleanCave_B1F_EventScript_DefeatedMewtwo::
	setflag FLAG_FOUGHT_MEWTWO
	goto EventScript_RemoveStaticMon
	end

CeruleanCave_B1F_EventScript_RanFromMewtwo::
	setvar VAR_0x8004, SPECIES_MEWTWO
	goto EventScript_MonFlewAway
	end

CeruleanCave_B1F_EventScript_SuperbossAside::
	setobjectxyperm LOCALID_CERULEAN_CAVE_SUPERBOSS, 8, 16
	setobjectmovementtype LOCALID_CERULEAN_CAVE_SUPERBOSS, MOVEMENT_TYPE_FACE_DOWN
	return

CeruleanCave_B1F_EventScript_Superboss::
	lock
	faceplayer
	goto_if_ge VAR_REMATCH_FRODO, 1, CeruleanCave_B1F_EventScript_SuperbossRematch
	msgbox CeruleanCave_B1F_Text_SuperbossIntro, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, CeruleanCave_B1F_EventScript_SuperbossDecline
	trainerbattle_no_intro TRAINER_SUPERBOSS_FRODO, CeruleanCave_B1F_Text_SuperbossDefeat
	msgbox CeruleanCave_B1F_Text_SuperbossFirstLoss
	closemessage
	applymovement LOCALID_CERULEAN_CAVE_SUPERBOSS, CeruleanCave_B1F_Movement_SuperbossStepAside
	waitmovement 0
	call CeruleanCave_B1F_EventScript_SuperbossAside
	release
	end

CeruleanCave_B1F_EventScript_SuperbossRematch::
	msgbox CeruleanCave_B1F_Text_SuperbossRematchAsk, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, CeruleanCave_B1F_EventScript_SuperbossDecline
	trainerbattle_no_intro TRAINER_SUPERBOSS_FRODO, CeruleanCave_B1F_Text_SuperbossDefeat
	msgbox CeruleanCave_B1F_Text_SuperbossPostBattle
	release
	end

CeruleanCave_B1F_EventScript_SuperbossDecline::
	msgbox CeruleanCave_B1F_Text_SuperbossDecline
	release
	end

CeruleanCave_B1F_Movement_SuperbossStepAside::
	walk_right
	face_down
	step_end

CeruleanCave_B1F_Text_SuperbossIntro::
	.string "…You feel it too, don't you?\n"
	.string "The thing sleeping past me.\p"
	.string "I've guarded this door long enough\n"
	.string "to know most trainers aren't ready.\p"
	.string "Prove you are. Shall we?$"

CeruleanCave_B1F_Text_SuperbossDefeat::
	.string "…So the wall breaks.$"

CeruleanCave_B1F_Text_SuperbossFirstLoss::
	.string "…Fine. The door is yours.\p"
	.string "But don't get comfortable…\n"
	.string "next time it's a different team,\l"
	.string "and I don't stop growing.$"

CeruleanCave_B1F_Text_SuperbossRematchAsk::
	.string "Back again?\n"
	.string "I've been training. Shall we?$"

CeruleanCave_B1F_Text_SuperbossPostBattle::
	.string "Hmph. Stronger every time…\n"
	.string "Both of us.$"

CeruleanCave_B1F_Text_SuperbossDecline::
	.string "…Come back when the silence\n"
	.string "gets too loud.$"
