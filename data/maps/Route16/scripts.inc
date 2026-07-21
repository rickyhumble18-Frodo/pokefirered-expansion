Route16_MapScripts::
	map_script MAP_SCRIPT_ON_RESUME, Route16_OnResume
	map_script MAP_SCRIPT_ON_TRANSITION, Route16_OnTransition
	map_script MAP_SCRIPT_ON_WARP_INTO_MAP_TABLE, Route16_OnWarp
	.byte 0

Route16_OnResume::
	call_if_set FLAG_SYS_SPECIAL_WILD_BATTLE, Route16_EventScript_RemoveSnorlax
	end

Route16_EventScript_RemoveSnorlax::
	removeobject VAR_LAST_TALKED
	return

Route16_OnTransition::
	call_if_eq VAR_MAP_SCENE_ROUTE16, 1, Route16_OnTransitionCyclingRoad
	end

Route16_OnTransitionCyclingRoad::
	setflag FLAG_SYS_ON_CYCLING_ROAD
	return

Route16_OnWarp::
	map_script_2 VAR_MAP_SCENE_ROUTE16, 1, Route16_OnWarpCyclingRoad
	.2byte 0

Route16_OnWarpCyclingRoad::
	special ForcePlayerOntoBike
	end

Route16_EventScript_Snorlax::
	lock
	faceplayer
	goto_if_unset FLAG_GOT_POKE_FLUTE, Route16_EventScript_SnorlaxNoPokeFlute
	goto_if_questlog EventScript_ReleaseEnd
	special QuestLog_CutRecording
	msgbox Text_WantToUsePokeFlute, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, Route16_EventScript_DontUsePokeFlute
	call EventScript_AwakenSnorlax
	setwildbattle SPECIES_SNORLAX, 30
	waitse
	playmoncry SPECIES_SNORLAX, CRY_MODE_ENCOUNTER
	delay 40
	waitmoncry
	setflag FLAG_HIDE_ROUTE_16_SNORLAX
	setflag FLAG_SYS_SPECIAL_WILD_BATTLE
	dowildbattle
	clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route16_EventScript_FoughtSnorlax
	goto_if_eq VAR_RESULT, B_OUTCOME_RAN, Route16_EventScript_FoughtSnorlax
	goto_if_eq VAR_RESULT, B_OUTCOME_PLAYER_TELEPORTED, Route16_EventScript_FoughtSnorlax
	release
	end

Route16_EventScript_DontUsePokeFlute::
	release
	end

Route16_EventScript_FoughtSnorlax::
	msgbox Text_SnorlaxReturnedToMountains
	release
	end

Route16_EventScript_SnorlaxNoPokeFlute::
	msgbox Route16_Text_MonSprawledOutInSlumber
	release
	end

Route16_EventScript_CyclingRoadSign::
	msgbox Route16_Text_CyclingRoadSign, MSGBOX_SIGN
	end

Route16_EventScript_RouteSign::
	msgbox Route16_Text_RouteSign, MSGBOX_SIGN
	end

@ GEN_ROUTE_TRAINERS_BEGIN
Route16_EventScript_KaizoRazor::
	trainerbattle_single TRAINER_BIKER_RAZOR, Route16_Text_KaizoRazorIntro, Route16_Text_KaizoRazorDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route16_EventScript_KaizoRazorRematch
	msgbox Route16_Text_KaizoRazorPost, MSGBOX_AUTOCLOSE
	end

Route16_EventScript_KaizoRazorRematch::
	trainerbattle_rematch TRAINER_BIKER_RAZOR, Route16_Text_KaizoRazorRematch, Route16_Text_KaizoRazorDefeat
	msgbox Route16_Text_KaizoRazorPost, MSGBOX_AUTOCLOSE
	end

Route16_Text_KaizoRazorIntro:
	.string "Let's battle!$"
Route16_Text_KaizoRazorDefeat:
	.string "I lost!$"
Route16_Text_KaizoRazorPost:
	.string "Come back anytime.$"
Route16_Text_KaizoRazorRematch:
	.string "Ready for a rematch?$"

Route16_EventScript_KaizoVivian::
	trainerbattle_single TRAINER_BEAUTY_VIVIAN, Route16_Text_KaizoVivianIntro, Route16_Text_KaizoVivianDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route16_EventScript_KaizoVivianRematch
	msgbox Route16_Text_KaizoVivianPost, MSGBOX_AUTOCLOSE
	end

Route16_EventScript_KaizoVivianRematch::
	trainerbattle_rematch TRAINER_BEAUTY_VIVIAN, Route16_Text_KaizoVivianRematch, Route16_Text_KaizoVivianDefeat
	msgbox Route16_Text_KaizoVivianPost, MSGBOX_AUTOCLOSE
	end

Route16_Text_KaizoVivianIntro:
	.string "Let's battle!$"
Route16_Text_KaizoVivianDefeat:
	.string "I lost!$"
Route16_Text_KaizoVivianPost:
	.string "Come back anytime.$"
Route16_Text_KaizoVivianRematch:
	.string "Ready for a rematch?$"

Route16_EventScript_KaizoClutch::
	trainerbattle_single TRAINER_BIKER_CLUTCH, Route16_Text_KaizoClutchIntro, Route16_Text_KaizoClutchDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route16_EventScript_KaizoClutchRematch
	msgbox Route16_Text_KaizoClutchPost, MSGBOX_AUTOCLOSE
	end

Route16_EventScript_KaizoClutchRematch::
	trainerbattle_rematch TRAINER_BIKER_CLUTCH, Route16_Text_KaizoClutchRematch, Route16_Text_KaizoClutchDefeat
	msgbox Route16_Text_KaizoClutchPost, MSGBOX_AUTOCLOSE
	end

Route16_Text_KaizoClutchIntro:
	.string "Let's battle!$"
Route16_Text_KaizoClutchDefeat:
	.string "I lost!$"
Route16_Text_KaizoClutchPost:
	.string "Come back anytime.$"
Route16_Text_KaizoClutchRematch:
	.string "Ready for a rematch?$"

@ GEN_ROUTE_TRAINERS_END
