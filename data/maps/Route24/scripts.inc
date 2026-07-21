Route24_MapScripts::
	.byte 0

Route24_EventScript_Rocket::
	lock
	faceplayer
	goto_if_eq VAR_MAP_SCENE_ROUTE24, 1, Route24_EventScript_RocketPostBattle
	msgbox Route24_Text_JustEarnedFabulousPrize
	checkitemspace ITEM_NUGGET
	goto_if_eq VAR_RESULT, FALSE, Route24_EventScript_NoRoomForNugget
	call Route24_EventScript_BattleRocket
	release
	end

Route24_EventScript_NoRoomForNugget::
	msgbox Route24_Text_YouDontHaveAnyRoom
	release
	end

Route24_EventScript_RocketPostBattle::
	msgbox Route24_Text_YoudBecomeTopRocketLeader
	release
	end

Route24_EventScript_RocketTriggerLeft::
	lockall
	setvar VAR_TEMP_1, 0
	goto Route24_EventScript_RocketTrigger
	end

Route24_EventScript_RocketTriggerRight::
	lockall
	setvar VAR_TEMP_1, 1
	goto Route24_EventScript_RocketTrigger
	end

Route24_EventScript_RocketTrigger::
	textcolor NPC_TEXT_COLOR_MALE
	call_if_eq VAR_TEMP_1, 0, Route24_EventScript_RocketApproachPlayer
	call_if_eq VAR_TEMP_1, 1, Route24_EventScript_RocketMotionToPlayer
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterRight
	waitmovement 0
	msgbox Route24_Text_JustEarnedFabulousPrize
	checkitemspace ITEM_NUGGET
	goto_if_eq VAR_RESULT, FALSE, Route24_EventScript_NoRoomForNuggetTrigger
	call Route24_EventScript_BattleRocket
	releaseall
	end

Route24_EventScript_BattleRocket::
	giveitem_msg Route24_Text_ReceivedNuggetFromMysteryTrainer, ITEM_NUGGET
	message Route24_Text_JoinTeamRocket
	waitmessage
	playbgm MUS_ENCOUNTER_ROCKET, 0
	waitbuttonpress
	setvar VAR_LAST_TALKED, LOCALID_ROUTE24_ROCKET
	trainerbattle_no_intro TRAINER_TEAM_ROCKET_GRUNT_6, Route24_Text_RocketDefeat
	msgbox Route24_Text_YoudBecomeTopRocketLeader
	setvar VAR_MAP_SCENE_ROUTE24, 1
	return

Route24_EventScript_RocketApproachPlayer::
	applymovement LOCALID_ROUTE24_ROCKET, Route24_Movement_RocketApproachPlayer
	waitmovement 0
	return

Route24_EventScript_RocketMotionToPlayer::
	applymovement LOCALID_ROUTE24_ROCKET, Common_Movement_WalkInPlaceFasterLeft
	waitmovement 0
	return

Route24_EventScript_NoRoomForNuggetTrigger::
	msgbox Route24_Text_YouDontHaveAnyRoom
	closemessage
	applymovement LOCALID_PLAYER, Route24_Movement_WalkDown
	waitmovement 0
	call_if_eq VAR_TEMP_1, 0, Route24_EventScript_RocketWalkBackToPos
	release
	end

Route24_EventScript_RocketWalkBackToPos::
	applymovement LOCALID_ROUTE24_ROCKET, Route24_Movement_RocketWalkBackToPos
	waitmovement 0
	return

Route24_Movement_RocketApproachPlayer::
	walk_left
	step_end

Route24_Movement_RocketWalkBackToPos::
	walk_right
	walk_in_place_faster_left
	step_end

Route24_Movement_WalkDown::
	walk_down
	step_end

@ GEN_ROUTE_TRAINERS_BEGIN
Route24_EventScript_KaizoMarv::
	trainerbattle_single TRAINER_BUG_CATCHER_MARV, Route24_Text_KaizoMarvIntro, Route24_Text_KaizoMarvDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route24_EventScript_KaizoMarvRematch
	msgbox Route24_Text_KaizoMarvPost, MSGBOX_AUTOCLOSE
	end

Route24_EventScript_KaizoMarvRematch::
	trainerbattle_rematch TRAINER_BUG_CATCHER_MARV, Route24_Text_KaizoMarvRematch, Route24_Text_KaizoMarvDefeat
	msgbox Route24_Text_KaizoMarvPost, MSGBOX_AUTOCLOSE
	end

Route24_Text_KaizoMarvIntro:
	.string "Let's battle!$"
Route24_Text_KaizoMarvDefeat:
	.string "I lost!$"
Route24_Text_KaizoMarvPost:
	.string "Come back anytime.$"
Route24_Text_KaizoMarvRematch:
	.string "Ready for a rematch?$"

Route24_EventScript_KaizoOdette::
	trainerbattle_single TRAINER_LASS_ODETTE, Route24_Text_KaizoOdetteIntro, Route24_Text_KaizoOdetteDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route24_EventScript_KaizoOdetteRematch
	msgbox Route24_Text_KaizoOdettePost, MSGBOX_AUTOCLOSE
	end

Route24_EventScript_KaizoOdetteRematch::
	trainerbattle_rematch TRAINER_LASS_ODETTE, Route24_Text_KaizoOdetteRematch, Route24_Text_KaizoOdetteDefeat
	msgbox Route24_Text_KaizoOdettePost, MSGBOX_AUTOCLOSE
	end

Route24_Text_KaizoOdetteIntro:
	.string "Let's battle!$"
Route24_Text_KaizoOdetteDefeat:
	.string "I lost!$"
Route24_Text_KaizoOdettePost:
	.string "Come back anytime.$"
Route24_Text_KaizoOdetteRematch:
	.string "Ready for a rematch?$"

@ GEN_ROUTE_TRAINERS_END
