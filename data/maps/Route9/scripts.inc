Route9_MapScripts::
	.byte 0

Route9_EventScript_RouteSign::
	msgbox Route9_Text_RouteSign, MSGBOX_SIGN
	end

@ GEN_ROUTE_TRAINERS_BEGIN
Route9_EventScript_KaizoBruno::
	trainerbattle_single TRAINER_HIKER_BRUNO, Route9_Text_KaizoBrunoIntro, Route9_Text_KaizoBrunoDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route9_EventScript_KaizoBrunoRematch
	msgbox Route9_Text_KaizoBrunoPost, MSGBOX_AUTOCLOSE
	end

Route9_EventScript_KaizoBrunoRematch::
	trainerbattle_rematch TRAINER_HIKER_BRUNO, Route9_Text_KaizoBrunoRematch, Route9_Text_KaizoBrunoDefeat
	msgbox Route9_Text_KaizoBrunoPost, MSGBOX_AUTOCLOSE
	end

Route9_Text_KaizoBrunoIntro:
	.string "Let's battle!$"
Route9_Text_KaizoBrunoDefeat:
	.string "I lost!$"
Route9_Text_KaizoBrunoPost:
	.string "Come back anytime.$"
Route9_Text_KaizoBrunoRematch:
	.string "Ready for a rematch?$"

Route9_EventScript_KaizoDexter::
	trainerbattle_single TRAINER_POKEMANIAC_DEXTER, Route9_Text_KaizoDexterIntro, Route9_Text_KaizoDexterDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route9_EventScript_KaizoDexterRematch
	msgbox Route9_Text_KaizoDexterPost, MSGBOX_AUTOCLOSE
	end

Route9_EventScript_KaizoDexterRematch::
	trainerbattle_rematch TRAINER_POKEMANIAC_DEXTER, Route9_Text_KaizoDexterRematch, Route9_Text_KaizoDexterDefeat
	msgbox Route9_Text_KaizoDexterPost, MSGBOX_AUTOCLOSE
	end

Route9_Text_KaizoDexterIntro:
	.string "Let's battle!$"
Route9_Text_KaizoDexterDefeat:
	.string "I lost!$"
Route9_Text_KaizoDexterPost:
	.string "Come back anytime.$"
Route9_Text_KaizoDexterRematch:
	.string "Ready for a rematch?$"

@ GEN_ROUTE_TRAINERS_END
