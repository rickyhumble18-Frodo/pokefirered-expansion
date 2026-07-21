Route6_MapScripts::
	.byte 0

Route6_EventScript_UndergroundPathSign::
	msgbox Route6_Text_UndergroundPathSign, MSGBOX_SIGN
	end

@ GEN_ROUTE_TRAINERS_BEGIN
Route6_EventScript_KaizoDougal::
	trainerbattle_single TRAINER_FISHERMAN_DOUGAL, Route6_Text_KaizoDougalIntro, Route6_Text_KaizoDougalDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route6_EventScript_KaizoDougalRematch
	msgbox Route6_Text_KaizoDougalPost, MSGBOX_AUTOCLOSE
	end

Route6_EventScript_KaizoDougalRematch::
	trainerbattle_rematch TRAINER_FISHERMAN_DOUGAL, Route6_Text_KaizoDougalRematch, Route6_Text_KaizoDougalDefeat
	msgbox Route6_Text_KaizoDougalPost, MSGBOX_AUTOCLOSE
	end

Route6_Text_KaizoDougalIntro:
	.string "Let's battle!$"
Route6_Text_KaizoDougalDefeat:
	.string "I lost!$"
Route6_Text_KaizoDougalPost:
	.string "Come back anytime.$"
Route6_Text_KaizoDougalRematch:
	.string "Ready for a rematch?$"

Route6_EventScript_KaizoPercy::
	trainerbattle_single TRAINER_BUG_CATCHER_PERCY, Route6_Text_KaizoPercyIntro, Route6_Text_KaizoPercyDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route6_EventScript_KaizoPercyRematch
	msgbox Route6_Text_KaizoPercyPost, MSGBOX_AUTOCLOSE
	end

Route6_EventScript_KaizoPercyRematch::
	trainerbattle_rematch TRAINER_BUG_CATCHER_PERCY, Route6_Text_KaizoPercyRematch, Route6_Text_KaizoPercyDefeat
	msgbox Route6_Text_KaizoPercyPost, MSGBOX_AUTOCLOSE
	end

Route6_Text_KaizoPercyIntro:
	.string "Let's battle!$"
Route6_Text_KaizoPercyDefeat:
	.string "I lost!$"
Route6_Text_KaizoPercyPost:
	.string "Come back anytime.$"
Route6_Text_KaizoPercyRematch:
	.string "Ready for a rematch?$"

Route6_EventScript_KaizoRoland::
	trainerbattle_single TRAINER_YOUNGSTER_ROLAND, Route6_Text_KaizoRolandIntro, Route6_Text_KaizoRolandDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route6_EventScript_KaizoRolandRematch
	msgbox Route6_Text_KaizoRolandPost, MSGBOX_AUTOCLOSE
	end

Route6_EventScript_KaizoRolandRematch::
	trainerbattle_rematch TRAINER_YOUNGSTER_ROLAND, Route6_Text_KaizoRolandRematch, Route6_Text_KaizoRolandDefeat
	msgbox Route6_Text_KaizoRolandPost, MSGBOX_AUTOCLOSE
	end

Route6_Text_KaizoRolandIntro:
	.string "Let's battle!$"
Route6_Text_KaizoRolandDefeat:
	.string "I lost!$"
Route6_Text_KaizoRolandPost:
	.string "Come back anytime.$"
Route6_Text_KaizoRolandRematch:
	.string "Ready for a rematch?$"

@ GEN_ROUTE_TRAINERS_END
