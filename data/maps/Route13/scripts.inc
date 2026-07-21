Route13_MapScripts::
	.byte 0

Route13_EventScript_TrainerTips1::
	msgbox Route13_Text_LookToLeftOfThatPost, MSGBOX_SIGN
	end

Route13_EventScript_TrainerTips2::
	msgbox Route13_Text_SelectToSwitchItems, MSGBOX_SIGN
	end

Route13_EventScript_RouteSign::
	msgbox Route13_Text_RouteSign, MSGBOX_SIGN
	end

@ GEN_ROUTE_TRAINERS_BEGIN
Route13_EventScript_KaizoCletus::
	trainerbattle_single TRAINER_FISHERMAN_CLETUS, Route13_Text_KaizoCletusIntro, Route13_Text_KaizoCletusDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route13_EventScript_KaizoCletusRematch
	msgbox Route13_Text_KaizoCletusPost, MSGBOX_AUTOCLOSE
	end

Route13_EventScript_KaizoCletusRematch::
	trainerbattle_rematch TRAINER_FISHERMAN_CLETUS, Route13_Text_KaizoCletusRematch, Route13_Text_KaizoCletusDefeat
	msgbox Route13_Text_KaizoCletusPost, MSGBOX_AUTOCLOSE
	end

Route13_Text_KaizoCletusIntro:
	.string "Let's battle!$"
Route13_Text_KaizoCletusDefeat:
	.string "I lost!$"
Route13_Text_KaizoCletusPost:
	.string "Come back anytime.$"
Route13_Text_KaizoCletusRematch:
	.string "Ready for a rematch?$"

Route13_EventScript_KaizoLacey::
	trainerbattle_single TRAINER_BEAUTY_LACEY, Route13_Text_KaizoLaceyIntro, Route13_Text_KaizoLaceyDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route13_EventScript_KaizoLaceyRematch
	msgbox Route13_Text_KaizoLaceyPost, MSGBOX_AUTOCLOSE
	end

Route13_EventScript_KaizoLaceyRematch::
	trainerbattle_rematch TRAINER_BEAUTY_LACEY, Route13_Text_KaizoLaceyRematch, Route13_Text_KaizoLaceyDefeat
	msgbox Route13_Text_KaizoLaceyPost, MSGBOX_AUTOCLOSE
	end

Route13_Text_KaizoLaceyIntro:
	.string "Let's battle!$"
Route13_Text_KaizoLaceyDefeat:
	.string "I lost!$"
Route13_Text_KaizoLaceyPost:
	.string "Come back anytime.$"
Route13_Text_KaizoLaceyRematch:
	.string "Ready for a rematch?$"

Route13_EventScript_KaizoMordecai::
	trainerbattle_single TRAINER_PSYCHIC_MORDECAI, Route13_Text_KaizoMordecaiIntro, Route13_Text_KaizoMordecaiDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route13_EventScript_KaizoMordecaiRematch
	msgbox Route13_Text_KaizoMordecaiPost, MSGBOX_AUTOCLOSE
	end

Route13_EventScript_KaizoMordecaiRematch::
	trainerbattle_rematch TRAINER_PSYCHIC_MORDECAI, Route13_Text_KaizoMordecaiRematch, Route13_Text_KaizoMordecaiDefeat
	msgbox Route13_Text_KaizoMordecaiPost, MSGBOX_AUTOCLOSE
	end

Route13_Text_KaizoMordecaiIntro:
	.string "Let's battle!$"
Route13_Text_KaizoMordecaiDefeat:
	.string "I lost!$"
Route13_Text_KaizoMordecaiPost:
	.string "Come back anytime.$"
Route13_Text_KaizoMordecaiRematch:
	.string "Ready for a rematch?$"

@ GEN_ROUTE_TRAINERS_END
