Route19_MapScripts::
	.byte 0

Route19_EventScript_RouteSign::
	msgbox Route19_Text_RouteSign, MSGBOX_SIGN
	end

@ GEN_ROUTE_TRAINERS_BEGIN
Route19_EventScript_KaizoMarina::
	trainerbattle_single TRAINER_SWIMMER_F_MARINA, Route19_Text_KaizoMarinaIntro, Route19_Text_KaizoMarinaDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route19_EventScript_KaizoMarinaRematch
	msgbox Route19_Text_KaizoMarinaPost, MSGBOX_AUTOCLOSE
	end

Route19_EventScript_KaizoMarinaRematch::
	trainerbattle_rematch TRAINER_SWIMMER_F_MARINA, Route19_Text_KaizoMarinaRematch, Route19_Text_KaizoMarinaDefeat
	msgbox Route19_Text_KaizoMarinaPost, MSGBOX_AUTOCLOSE
	end

Route19_Text_KaizoMarinaIntro:
	.string "Let's battle!$"
Route19_Text_KaizoMarinaDefeat:
	.string "I lost!$"
Route19_Text_KaizoMarinaPost:
	.string "Come back anytime.$"
Route19_Text_KaizoMarinaRematch:
	.string "Ready for a rematch?$"

Route19_EventScript_KaizoReef::
	trainerbattle_single TRAINER_SWIMMER_M_REEF, Route19_Text_KaizoReefIntro, Route19_Text_KaizoReefDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route19_EventScript_KaizoReefRematch
	msgbox Route19_Text_KaizoReefPost, MSGBOX_AUTOCLOSE
	end

Route19_EventScript_KaizoReefRematch::
	trainerbattle_rematch TRAINER_SWIMMER_M_REEF, Route19_Text_KaizoReefRematch, Route19_Text_KaizoReefDefeat
	msgbox Route19_Text_KaizoReefPost, MSGBOX_AUTOCLOSE
	end

Route19_Text_KaizoReefIntro:
	.string "Let's battle!$"
Route19_Text_KaizoReefDefeat:
	.string "I lost!$"
Route19_Text_KaizoReefPost:
	.string "Come back anytime.$"
Route19_Text_KaizoReefRematch:
	.string "Ready for a rematch?$"

@ GEN_ROUTE_TRAINERS_END
