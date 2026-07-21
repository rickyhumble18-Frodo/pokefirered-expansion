Route18_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route18_OnTransition
	map_script MAP_SCRIPT_ON_WARP_INTO_MAP_TABLE, Route18_OnWarp
	.byte 0

Route18_OnTransition::
	call_if_eq VAR_MAP_SCENE_ROUTE16, 1, Route18_OnTransitionCyclingRoad
	end

Route18_OnTransitionCyclingRoad::
	setflag FLAG_SYS_ON_CYCLING_ROAD
	return

Route18_OnWarp::
	map_script_2 VAR_MAP_SCENE_ROUTE16, 1, Route18_OnWarpCyclingRoad
	.2byte 0

Route18_OnWarpCyclingRoad::
	special ForcePlayerOntoBike
	end

Route18_EventScript_RouteSign::
	msgbox Route18_Text_RouteSign, MSGBOX_SIGN
	end

Route18_EventScript_CyclingRoadSign::
	msgbox Route18_Text_CyclingRoadSign, MSGBOX_SIGN
	end

@ GEN_ROUTE_TRAINERS_BEGIN
Route18_EventScript_KaizoSpark::
	trainerbattle_single TRAINER_BIKER_SPARK, Route18_Text_KaizoSparkIntro, Route18_Text_KaizoSparkDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route18_EventScript_KaizoSparkRematch
	msgbox Route18_Text_KaizoSparkPost, MSGBOX_AUTOCLOSE
	end

Route18_EventScript_KaizoSparkRematch::
	trainerbattle_rematch TRAINER_BIKER_SPARK, Route18_Text_KaizoSparkRematch, Route18_Text_KaizoSparkDefeat
	msgbox Route18_Text_KaizoSparkPost, MSGBOX_AUTOCLOSE
	end

Route18_Text_KaizoSparkIntro:
	.string "Let's battle!$"
Route18_Text_KaizoSparkDefeat:
	.string "I lost!$"
Route18_Text_KaizoSparkPost:
	.string "Come back anytime.$"
Route18_Text_KaizoSparkRematch:
	.string "Ready for a rematch?$"

Route18_EventScript_KaizoDiesel::
	trainerbattle_single TRAINER_BIKER_DIESEL, Route18_Text_KaizoDieselIntro, Route18_Text_KaizoDieselDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route18_EventScript_KaizoDieselRematch
	msgbox Route18_Text_KaizoDieselPost, MSGBOX_AUTOCLOSE
	end

Route18_EventScript_KaizoDieselRematch::
	trainerbattle_rematch TRAINER_BIKER_DIESEL, Route18_Text_KaizoDieselRematch, Route18_Text_KaizoDieselDefeat
	msgbox Route18_Text_KaizoDieselPost, MSGBOX_AUTOCLOSE
	end

Route18_Text_KaizoDieselIntro:
	.string "Let's battle!$"
Route18_Text_KaizoDieselDefeat:
	.string "I lost!$"
Route18_Text_KaizoDieselPost:
	.string "Come back anytime.$"
Route18_Text_KaizoDieselRematch:
	.string "Ready for a rematch?$"

Route18_EventScript_KaizoWendell::
	trainerbattle_single TRAINER_POKEMANIAC_WENDELL, Route18_Text_KaizoWendellIntro, Route18_Text_KaizoWendellDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route18_EventScript_KaizoWendellRematch
	msgbox Route18_Text_KaizoWendellPost, MSGBOX_AUTOCLOSE
	end

Route18_EventScript_KaizoWendellRematch::
	trainerbattle_rematch TRAINER_POKEMANIAC_WENDELL, Route18_Text_KaizoWendellRematch, Route18_Text_KaizoWendellDefeat
	msgbox Route18_Text_KaizoWendellPost, MSGBOX_AUTOCLOSE
	end

Route18_Text_KaizoWendellIntro:
	.string "Let's battle!$"
Route18_Text_KaizoWendellDefeat:
	.string "I lost!$"
Route18_Text_KaizoWendellPost:
	.string "Come back anytime.$"
Route18_Text_KaizoWendellRematch:
	.string "Ready for a rematch?$"

Route18_EventScript_KaizoBoulder::
	trainerbattle_single TRAINER_HIKER_BOULDER, Route18_Text_KaizoBoulderIntro, Route18_Text_KaizoBoulderDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route18_EventScript_KaizoBoulderRematch
	msgbox Route18_Text_KaizoBoulderPost, MSGBOX_AUTOCLOSE
	end

Route18_EventScript_KaizoBoulderRematch::
	trainerbattle_rematch TRAINER_HIKER_BOULDER, Route18_Text_KaizoBoulderRematch, Route18_Text_KaizoBoulderDefeat
	msgbox Route18_Text_KaizoBoulderPost, MSGBOX_AUTOCLOSE
	end

Route18_Text_KaizoBoulderIntro:
	.string "Let's battle!$"
Route18_Text_KaizoBoulderDefeat:
	.string "I lost!$"
Route18_Text_KaizoBoulderPost:
	.string "Come back anytime.$"
Route18_Text_KaizoBoulderRematch:
	.string "Ready for a rematch?$"

@ GEN_ROUTE_TRAINERS_END
