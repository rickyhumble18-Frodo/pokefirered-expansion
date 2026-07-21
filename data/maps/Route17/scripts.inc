Route17_MapScripts::
	.byte 0

Route17_EventScript_ItemsNotice::
	msgbox Route17_Text_WatchOutForDiscardedItems, MSGBOX_SIGN
	end

Route17_EventScript_TrainerTips1::
	msgbox Route17_Text_SameSpeciesGrowDifferentRates, MSGBOX_SIGN
	end

Route17_EventScript_TrainerTips2::
	msgbox Route17_Text_PressBToStayInPlace, MSGBOX_SIGN
	end

Route17_EventScript_RouteSign::
	msgbox Route17_Text_RouteSign, MSGBOX_SIGN
	end

Route17_EventScript_BallsNotice::
	msgbox Route17_Text_DontThrowGameThrowBalls, MSGBOX_SIGN
	end

Route17_EventScript_CyclingRoadSign::
	msgbox Route17_Text_CyclingRoadSign, MSGBOX_SIGN
	end

@ GEN_ROUTE_TRAINERS_BEGIN
Route17_EventScript_KaizoTorque::
	trainerbattle_single TRAINER_BIKER_TORQUE, Route17_Text_KaizoTorqueIntro, Route17_Text_KaizoTorqueDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route17_EventScript_KaizoTorqueRematch
	msgbox Route17_Text_KaizoTorquePost, MSGBOX_AUTOCLOSE
	end

Route17_EventScript_KaizoTorqueRematch::
	trainerbattle_rematch TRAINER_BIKER_TORQUE, Route17_Text_KaizoTorqueRematch, Route17_Text_KaizoTorqueDefeat
	msgbox Route17_Text_KaizoTorquePost, MSGBOX_AUTOCLOSE
	end

Route17_Text_KaizoTorqueIntro:
	.string "Let's battle!$"
Route17_Text_KaizoTorqueDefeat:
	.string "I lost!$"
Route17_Text_KaizoTorquePost:
	.string "Come back anytime.$"
Route17_Text_KaizoTorqueRematch:
	.string "Ready for a rematch?$"

Route17_EventScript_KaizoNitro::
	trainerbattle_single TRAINER_BIKER_NITRO, Route17_Text_KaizoNitroIntro, Route17_Text_KaizoNitroDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route17_EventScript_KaizoNitroRematch
	msgbox Route17_Text_KaizoNitroPost, MSGBOX_AUTOCLOSE
	end

Route17_EventScript_KaizoNitroRematch::
	trainerbattle_rematch TRAINER_BIKER_NITRO, Route17_Text_KaizoNitroRematch, Route17_Text_KaizoNitroDefeat
	msgbox Route17_Text_KaizoNitroPost, MSGBOX_AUTOCLOSE
	end

Route17_Text_KaizoNitroIntro:
	.string "Let's battle!$"
Route17_Text_KaizoNitroDefeat:
	.string "I lost!$"
Route17_Text_KaizoNitroPost:
	.string "Come back anytime.$"
Route17_Text_KaizoNitroRematch:
	.string "Ready for a rematch?$"

Route17_EventScript_KaizoCarmen::
	trainerbattle_single TRAINER_BEAUTY_CARMEN, Route17_Text_KaizoCarmenIntro, Route17_Text_KaizoCarmenDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route17_EventScript_KaizoCarmenRematch
	msgbox Route17_Text_KaizoCarmenPost, MSGBOX_AUTOCLOSE
	end

Route17_EventScript_KaizoCarmenRematch::
	trainerbattle_rematch TRAINER_BEAUTY_CARMEN, Route17_Text_KaizoCarmenRematch, Route17_Text_KaizoCarmenDefeat
	msgbox Route17_Text_KaizoCarmenPost, MSGBOX_AUTOCLOSE
	end

Route17_Text_KaizoCarmenIntro:
	.string "Let's battle!$"
Route17_Text_KaizoCarmenDefeat:
	.string "I lost!$"
Route17_Text_KaizoCarmenPost:
	.string "Come back anytime.$"
Route17_Text_KaizoCarmenRematch:
	.string "Ready for a rematch?$"

@ GEN_ROUTE_TRAINERS_END
