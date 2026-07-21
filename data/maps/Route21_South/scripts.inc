Route21_South_MapScripts::
	.byte 0

@ GEN_ROUTE_TRAINERS_BEGIN
Route21_South_EventScript_KaizoCrest::
	trainerbattle_single TRAINER_SWIMMER_M_CREST, Route21_South_Text_KaizoCrestIntro, Route21_South_Text_KaizoCrestDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route21_South_EventScript_KaizoCrestRematch
	msgbox Route21_South_Text_KaizoCrestPost, MSGBOX_AUTOCLOSE
	end

Route21_South_EventScript_KaizoCrestRematch::
	trainerbattle_rematch TRAINER_SWIMMER_M_CREST, Route21_South_Text_KaizoCrestRematch, Route21_South_Text_KaizoCrestDefeat
	msgbox Route21_South_Text_KaizoCrestPost, MSGBOX_AUTOCLOSE
	end

Route21_South_Text_KaizoCrestIntro:
	.string "Let's battle!$"
Route21_South_Text_KaizoCrestDefeat:
	.string "I lost!$"
Route21_South_Text_KaizoCrestPost:
	.string "Come back anytime.$"
Route21_South_Text_KaizoCrestRematch:
	.string "Ready for a rematch?$"

Route21_South_EventScript_KaizoCoral::
	trainerbattle_single TRAINER_SWIMMER_F_CORAL, Route21_South_Text_KaizoCoralIntro, Route21_South_Text_KaizoCoralDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route21_South_EventScript_KaizoCoralRematch
	msgbox Route21_South_Text_KaizoCoralPost, MSGBOX_AUTOCLOSE
	end

Route21_South_EventScript_KaizoCoralRematch::
	trainerbattle_rematch TRAINER_SWIMMER_F_CORAL, Route21_South_Text_KaizoCoralRematch, Route21_South_Text_KaizoCoralDefeat
	msgbox Route21_South_Text_KaizoCoralPost, MSGBOX_AUTOCLOSE
	end

Route21_South_Text_KaizoCoralIntro:
	.string "Let's battle!$"
Route21_South_Text_KaizoCoralDefeat:
	.string "I lost!$"
Route21_South_Text_KaizoCoralPost:
	.string "Come back anytime.$"
Route21_South_Text_KaizoCoralRematch:
	.string "Ready for a rematch?$"

@ GEN_ROUTE_TRAINERS_END
