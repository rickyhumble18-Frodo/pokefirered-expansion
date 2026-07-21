Route10_MapScripts::
	.byte 0

Route10_EventScript_Unused::
	end

Route10_EventScript_NorthRockTunnelSign::
	msgbox Route10_Text_RockTunnelDetourToLavender, MSGBOX_SIGN
	end

Route10_EventScript_SouthRockTunnelSign::
	msgbox Route10_Text_RockTunnel, MSGBOX_SIGN
	end

Route10_EventScript_PowerPlantSign::
	msgbox Route10_Text_PowerPlant, MSGBOX_SIGN
	end

@ GEN_ROUTE_TRAINERS_BEGIN
Route10_EventScript_KaizoOhmer::
	trainerbattle_single TRAINER_SUPER_NERD_OHMER, Route10_Text_KaizoOhmerIntro, Route10_Text_KaizoOhmerDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route10_EventScript_KaizoOhmerRematch
	msgbox Route10_Text_KaizoOhmerPost, MSGBOX_AUTOCLOSE
	end

Route10_EventScript_KaizoOhmerRematch::
	trainerbattle_rematch TRAINER_SUPER_NERD_OHMER, Route10_Text_KaizoOhmerRematch, Route10_Text_KaizoOhmerDefeat
	msgbox Route10_Text_KaizoOhmerPost, MSGBOX_AUTOCLOSE
	end

Route10_Text_KaizoOhmerIntro:
	.string "Let's battle!$"
Route10_Text_KaizoOhmerDefeat:
	.string "I lost!$"
Route10_Text_KaizoOhmerPost:
	.string "Come back anytime.$"
Route10_Text_KaizoOhmerRematch:
	.string "Ready for a rematch?$"

Route10_EventScript_KaizoGrant::
	trainerbattle_single TRAINER_HIKER_GRANT, Route10_Text_KaizoGrantIntro, Route10_Text_KaizoGrantDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route10_EventScript_KaizoGrantRematch
	msgbox Route10_Text_KaizoGrantPost, MSGBOX_AUTOCLOSE
	end

Route10_EventScript_KaizoGrantRematch::
	trainerbattle_rematch TRAINER_HIKER_GRANT, Route10_Text_KaizoGrantRematch, Route10_Text_KaizoGrantDefeat
	msgbox Route10_Text_KaizoGrantPost, MSGBOX_AUTOCLOSE
	end

Route10_Text_KaizoGrantIntro:
	.string "Let's battle!$"
Route10_Text_KaizoGrantDefeat:
	.string "I lost!$"
Route10_Text_KaizoGrantPost:
	.string "Come back anytime.$"
Route10_Text_KaizoGrantRematch:
	.string "Ready for a rematch?$"

Route10_EventScript_KaizoSilas::
	trainerbattle_single TRAINER_POKEMANIAC_SILAS, Route10_Text_KaizoSilasIntro, Route10_Text_KaizoSilasDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route10_EventScript_KaizoSilasRematch
	msgbox Route10_Text_KaizoSilasPost, MSGBOX_AUTOCLOSE
	end

Route10_EventScript_KaizoSilasRematch::
	trainerbattle_rematch TRAINER_POKEMANIAC_SILAS, Route10_Text_KaizoSilasRematch, Route10_Text_KaizoSilasDefeat
	msgbox Route10_Text_KaizoSilasPost, MSGBOX_AUTOCLOSE
	end

Route10_Text_KaizoSilasIntro:
	.string "Let's battle!$"
Route10_Text_KaizoSilasDefeat:
	.string "I lost!$"
Route10_Text_KaizoSilasPost:
	.string "Come back anytime.$"
Route10_Text_KaizoSilasRematch:
	.string "Ready for a rematch?$"

Route10_EventScript_KaizoZiggy::
	trainerbattle_single TRAINER_ROCKER_ZIGGY, Route10_Text_KaizoZiggyIntro, Route10_Text_KaizoZiggyDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route10_EventScript_KaizoZiggyRematch
	msgbox Route10_Text_KaizoZiggyPost, MSGBOX_AUTOCLOSE
	end

Route10_EventScript_KaizoZiggyRematch::
	trainerbattle_rematch TRAINER_ROCKER_ZIGGY, Route10_Text_KaizoZiggyRematch, Route10_Text_KaizoZiggyDefeat
	msgbox Route10_Text_KaizoZiggyPost, MSGBOX_AUTOCLOSE
	end

Route10_Text_KaizoZiggyIntro:
	.string "Let's battle!$"
Route10_Text_KaizoZiggyDefeat:
	.string "I lost!$"
Route10_Text_KaizoZiggyPost:
	.string "Come back anytime.$"
Route10_Text_KaizoZiggyRematch:
	.string "Ready for a rematch?$"

@ GEN_ROUTE_TRAINERS_END
