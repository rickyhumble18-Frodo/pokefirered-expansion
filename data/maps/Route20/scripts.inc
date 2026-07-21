Route20_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route20_OnTransition
	.byte 0

Route20_OnTransition::
	call_if_unset FLAG_STOPPED_SEAFOAM_B3F_CURRENT, Route20_EventScript_ResetSeafoamBouldersForB3F
	call_if_unset FLAG_STOPPED_SEAFOAM_B4F_CURRENT, Route20_EventScript_ResetSeafoamBouldersForB4F
	end

Route20_EventScript_ResetSeafoamBouldersForB3F::
	clearflag FLAG_HIDE_SEAFOAM_1F_BOULDER_1
	clearflag FLAG_HIDE_SEAFOAM_1F_BOULDER_2
	setflag FLAG_HIDE_SEAFOAM_B1F_BOULDER_1
	setflag FLAG_HIDE_SEAFOAM_B1F_BOULDER_2
	setflag FLAG_HIDE_SEAFOAM_B2F_BOULDER_1
	setflag FLAG_HIDE_SEAFOAM_B2F_BOULDER_2
	setflag FLAG_HIDE_SEAFOAM_B3F_BOULDER_1
	setflag FLAG_HIDE_SEAFOAM_B3F_BOULDER_2
	return

Route20_EventScript_ResetSeafoamBouldersForB4F::
	clearflag FLAG_HIDE_SEAFOAM_B3F_BOULDER_3
	clearflag FLAG_HIDE_SEAFOAM_B3F_BOULDER_4
	clearflag FLAG_HIDE_SEAFOAM_B3F_BOULDER_5
	clearflag FLAG_HIDE_SEAFOAM_B3F_BOULDER_6
	setflag FLAG_HIDE_SEAFOAM_B4F_BOULDER_1
	setflag FLAG_HIDE_SEAFOAM_B4F_BOULDER_2
	return

Route20_EventScript_SeafoamIslandsSign::
	msgbox Route20_Text_SeafoamIslands, MSGBOX_SIGN
	end

@ GEN_ROUTE_TRAINERS_BEGIN
Route20_EventScript_KaizoTide::
	trainerbattle_single TRAINER_SWIMMER_M_TIDE, Route20_Text_KaizoTideIntro, Route20_Text_KaizoTideDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route20_EventScript_KaizoTideRematch
	msgbox Route20_Text_KaizoTidePost, MSGBOX_AUTOCLOSE
	end

Route20_EventScript_KaizoTideRematch::
	trainerbattle_rematch TRAINER_SWIMMER_M_TIDE, Route20_Text_KaizoTideRematch, Route20_Text_KaizoTideDefeat
	msgbox Route20_Text_KaizoTidePost, MSGBOX_AUTOCLOSE
	end

Route20_Text_KaizoTideIntro:
	.string "Let's battle!$"
Route20_Text_KaizoTideDefeat:
	.string "I lost!$"
Route20_Text_KaizoTidePost:
	.string "Come back anytime.$"
Route20_Text_KaizoTideRematch:
	.string "Ready for a rematch?$"

Route20_EventScript_KaizoKenji::
	trainerbattle_single TRAINER_BLACK_BELT_KENJI, Route20_Text_KaizoKenjiIntro, Route20_Text_KaizoKenjiDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route20_EventScript_KaizoKenjiRematch
	msgbox Route20_Text_KaizoKenjiPost, MSGBOX_AUTOCLOSE
	end

Route20_EventScript_KaizoKenjiRematch::
	trainerbattle_rematch TRAINER_BLACK_BELT_KENJI, Route20_Text_KaizoKenjiRematch, Route20_Text_KaizoKenjiDefeat
	msgbox Route20_Text_KaizoKenjiPost, MSGBOX_AUTOCLOSE
	end

Route20_Text_KaizoKenjiIntro:
	.string "Let's battle!$"
Route20_Text_KaizoKenjiDefeat:
	.string "I lost!$"
Route20_Text_KaizoKenjiPost:
	.string "Come back anytime.$"
Route20_Text_KaizoKenjiRematch:
	.string "Ready for a rematch?$"

@ GEN_ROUTE_TRAINERS_END
