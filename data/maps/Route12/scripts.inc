Route12_MapScripts::
	map_script MAP_SCRIPT_ON_RESUME, Route12_OnResume
	.byte 0

Route12_OnResume::
	call_if_set FLAG_SYS_SPECIAL_WILD_BATTLE, Route12_EventScript_TryRemoveSnorlax
	end

Route12_EventScript_TryRemoveSnorlax::
	removeobject VAR_LAST_TALKED
	return

Route12_EventScript_Snorlax::
	lock
	faceplayer
	goto_if_unset FLAG_GOT_POKE_FLUTE, Route12_EventScript_SnorlaxNoPokeFlute
	goto_if_questlog EventScript_ReleaseEnd
	special QuestLog_CutRecording
	msgbox Text_WantToUsePokeFlute, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, Route12_EventScript_DontUsePokeFlute
	call EventScript_AwakenSnorlax
	setwildbattle SPECIES_SNORLAX, 30
	waitse
	playmoncry SPECIES_SNORLAX, CRY_MODE_ENCOUNTER
	delay 40
	waitmoncry
	setflag FLAG_HIDE_ROUTE_12_SNORLAX
	setflag FLAG_SYS_SPECIAL_WILD_BATTLE
	setflag FLAG_WOKE_UP_ROUTE_12_SNORLAX
	dowildbattle
	clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route12_EventScript_FoughtSnorlax
	goto_if_eq VAR_RESULT, B_OUTCOME_RAN, Route12_EventScript_FoughtSnorlax
	goto_if_eq VAR_RESULT, B_OUTCOME_PLAYER_TELEPORTED, Route12_EventScript_FoughtSnorlax
	release
	end

Route12_EventScript_DontUsePokeFlute::
	release
	end

Route12_EventScript_FoughtSnorlax::
	msgbox Text_SnorlaxReturnedToMountains
	release
	end

Route12_EventScript_SnorlaxNoPokeFlute::
	msgbox Route12_Text_MonSprawledOutInSlumber
	release
	end

Route12_EventScript_RouteSign::
	msgbox Route12_Text_RouteSign, MSGBOX_SIGN
	end

Route12_EventScript_FishingSign::
	msgbox Route12_Text_SportfishingArea, MSGBOX_SIGN
	end

@ GEN_ROUTE_TRAINERS_BEGIN
Route12_EventScript_KaizoMarlon::
	trainerbattle_single TRAINER_FISHERMAN_MARLON, Route12_Text_KaizoMarlonIntro, Route12_Text_KaizoMarlonDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route12_EventScript_KaizoMarlonRematch
	msgbox Route12_Text_KaizoMarlonPost, MSGBOX_AUTOCLOSE
	end

Route12_EventScript_KaizoMarlonRematch::
	trainerbattle_rematch TRAINER_FISHERMAN_MARLON, Route12_Text_KaizoMarlonRematch, Route12_Text_KaizoMarlonDefeat
	msgbox Route12_Text_KaizoMarlonPost, MSGBOX_AUTOCLOSE
	end

Route12_Text_KaizoMarlonIntro:
	.string "Let's battle!$"
Route12_Text_KaizoMarlonDefeat:
	.string "I lost!$"
Route12_Text_KaizoMarlonPost:
	.string "Come back anytime.$"
Route12_Text_KaizoMarlonRematch:
	.string "Ready for a rematch?$"

Route12_EventScript_KaizoSerena::
	trainerbattle_single TRAINER_BEAUTY_SERENA, Route12_Text_KaizoSerenaIntro, Route12_Text_KaizoSerenaDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route12_EventScript_KaizoSerenaRematch
	msgbox Route12_Text_KaizoSerenaPost, MSGBOX_AUTOCLOSE
	end

Route12_EventScript_KaizoSerenaRematch::
	trainerbattle_rematch TRAINER_BEAUTY_SERENA, Route12_Text_KaizoSerenaRematch, Route12_Text_KaizoSerenaDefeat
	msgbox Route12_Text_KaizoSerenaPost, MSGBOX_AUTOCLOSE
	end

Route12_Text_KaizoSerenaIntro:
	.string "Let's battle!$"
Route12_Text_KaizoSerenaDefeat:
	.string "I lost!$"
Route12_Text_KaizoSerenaPost:
	.string "Come back anytime.$"
Route12_Text_KaizoSerenaRematch:
	.string "Ready for a rematch?$"

Route12_EventScript_KaizoJax::
	trainerbattle_single TRAINER_ROCKER_JAX, Route12_Text_KaizoJaxIntro, Route12_Text_KaizoJaxDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route12_EventScript_KaizoJaxRematch
	msgbox Route12_Text_KaizoJaxPost, MSGBOX_AUTOCLOSE
	end

Route12_EventScript_KaizoJaxRematch::
	trainerbattle_rematch TRAINER_ROCKER_JAX, Route12_Text_KaizoJaxRematch, Route12_Text_KaizoJaxDefeat
	msgbox Route12_Text_KaizoJaxPost, MSGBOX_AUTOCLOSE
	end

Route12_Text_KaizoJaxIntro:
	.string "Let's battle!$"
Route12_Text_KaizoJaxDefeat:
	.string "I lost!$"
Route12_Text_KaizoJaxPost:
	.string "Come back anytime.$"
Route12_Text_KaizoJaxRematch:
	.string "Ready for a rematch?$"

@ GEN_ROUTE_TRAINERS_END
