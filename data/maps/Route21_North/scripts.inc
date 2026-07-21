Route21_North_MapScripts::
	.byte 0

@ GEN_ROUTE_TRAINERS_BEGIN
Route21_North_EventScript_KaizoPearl::
	trainerbattle_single TRAINER_SWIMMER_F_PEARL, Route21_North_Text_KaizoPearlIntro, Route21_North_Text_KaizoPearlDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route21_North_EventScript_KaizoPearlRematch
	msgbox Route21_North_Text_KaizoPearlPost, MSGBOX_AUTOCLOSE
	end

Route21_North_EventScript_KaizoPearlRematch::
	trainerbattle_rematch TRAINER_SWIMMER_F_PEARL, Route21_North_Text_KaizoPearlRematch, Route21_North_Text_KaizoPearlDefeat
	msgbox Route21_North_Text_KaizoPearlPost, MSGBOX_AUTOCLOSE
	end

Route21_North_Text_KaizoPearlIntro:
	.string "Let's battle!$"
Route21_North_Text_KaizoPearlDefeat:
	.string "I lost!$"
Route21_North_Text_KaizoPearlPost:
	.string "Come back anytime.$"
Route21_North_Text_KaizoPearlRematch:
	.string "Ready for a rematch?$"

Route21_North_EventScript_KaizoSalton::
	trainerbattle_single TRAINER_FISHERMAN_SALTON, Route21_North_Text_KaizoSaltonIntro, Route21_North_Text_KaizoSaltonDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route21_North_EventScript_KaizoSaltonRematch
	msgbox Route21_North_Text_KaizoSaltonPost, MSGBOX_AUTOCLOSE
	end

Route21_North_EventScript_KaizoSaltonRematch::
	trainerbattle_rematch TRAINER_FISHERMAN_SALTON, Route21_North_Text_KaizoSaltonRematch, Route21_North_Text_KaizoSaltonDefeat
	msgbox Route21_North_Text_KaizoSaltonPost, MSGBOX_AUTOCLOSE
	end

Route21_North_Text_KaizoSaltonIntro:
	.string "Let's battle!$"
Route21_North_Text_KaizoSaltonDefeat:
	.string "I lost!$"
Route21_North_Text_KaizoSaltonPost:
	.string "Come back anytime.$"
Route21_North_Text_KaizoSaltonRematch:
	.string "Ready for a rematch?$"

@ GEN_ROUTE_TRAINERS_END
