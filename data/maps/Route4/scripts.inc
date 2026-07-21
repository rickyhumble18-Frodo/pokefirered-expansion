Route4_MapScripts::
	.byte 0

Route4_EventScript_Unused::
	end

Route4_EventScript_Woman::
	msgbox Route4_Text_TrippedOverGeodude, MSGBOX_NPC
	end

Route4_EventScript_MtMoonSign::
	msgbox Route4_Text_MtMoonEntrance, MSGBOX_SIGN
	end

Route4_EventScript_RouteSign::
	msgbox Route4_Text_RouteSign, MSGBOX_SIGN
	end

@ GEN_ROUTE_TRAINERS_BEGIN
Route4_EventScript_KaizoDwayne::
	trainerbattle_single TRAINER_HIKER_DWAYNE, Route4_Text_KaizoDwayneIntro, Route4_Text_KaizoDwayneDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route4_EventScript_KaizoDwayneRematch
	msgbox Route4_Text_KaizoDwaynePost, MSGBOX_AUTOCLOSE
	end

Route4_EventScript_KaizoDwayneRematch::
	trainerbattle_rematch TRAINER_HIKER_DWAYNE, Route4_Text_KaizoDwayneRematch, Route4_Text_KaizoDwayneDefeat
	msgbox Route4_Text_KaizoDwaynePost, MSGBOX_AUTOCLOSE
	end

Route4_Text_KaizoDwayneIntro:
	.string "Let's battle!$"
Route4_Text_KaizoDwayneDefeat:
	.string "I lost!$"
Route4_Text_KaizoDwaynePost:
	.string "Come back anytime.$"
Route4_Text_KaizoDwayneRematch:
	.string "Ready for a rematch?$"

Route4_EventScript_KaizoTobias::
	trainerbattle_single TRAINER_CAMPER_TOBIAS, Route4_Text_KaizoTobiasIntro, Route4_Text_KaizoTobiasDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route4_EventScript_KaizoTobiasRematch
	msgbox Route4_Text_KaizoTobiasPost, MSGBOX_AUTOCLOSE
	end

Route4_EventScript_KaizoTobiasRematch::
	trainerbattle_rematch TRAINER_CAMPER_TOBIAS, Route4_Text_KaizoTobiasRematch, Route4_Text_KaizoTobiasDefeat
	msgbox Route4_Text_KaizoTobiasPost, MSGBOX_AUTOCLOSE
	end

Route4_Text_KaizoTobiasIntro:
	.string "Let's battle!$"
Route4_Text_KaizoTobiasDefeat:
	.string "I lost!$"
Route4_Text_KaizoTobiasPost:
	.string "Come back anytime.$"
Route4_Text_KaizoTobiasRematch:
	.string "Ready for a rematch?$"

Route4_EventScript_KaizoPriscilla::
	trainerbattle_single TRAINER_LASS_PRISCILLA, Route4_Text_KaizoPriscillaIntro, Route4_Text_KaizoPriscillaDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route4_EventScript_KaizoPriscillaRematch
	msgbox Route4_Text_KaizoPriscillaPost, MSGBOX_AUTOCLOSE
	end

Route4_EventScript_KaizoPriscillaRematch::
	trainerbattle_rematch TRAINER_LASS_PRISCILLA, Route4_Text_KaizoPriscillaRematch, Route4_Text_KaizoPriscillaDefeat
	msgbox Route4_Text_KaizoPriscillaPost, MSGBOX_AUTOCLOSE
	end

Route4_Text_KaizoPriscillaIntro:
	.string "Let's battle!$"
Route4_Text_KaizoPriscillaDefeat:
	.string "I lost!$"
Route4_Text_KaizoPriscillaPost:
	.string "Come back anytime.$"
Route4_Text_KaizoPriscillaRematch:
	.string "Ready for a rematch?$"

@ GEN_ROUTE_TRAINERS_END
