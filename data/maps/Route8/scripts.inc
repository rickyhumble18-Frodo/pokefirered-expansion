Route8_MapScripts::
	.byte 0

Route8_EventScript_UndergroundPathSign::
	msgbox Route8_Text_UndergroundPathSign, MSGBOX_SIGN
	end

@ GEN_ROUTE_TRAINERS_BEGIN
Route8_EventScript_KaizoEwald::
	trainerbattle_single TRAINER_SUPER_NERD_EWALD, Route8_Text_KaizoEwaldIntro, Route8_Text_KaizoEwaldDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route8_EventScript_KaizoEwaldRematch
	msgbox Route8_Text_KaizoEwaldPost, MSGBOX_AUTOCLOSE
	end

Route8_EventScript_KaizoEwaldRematch::
	trainerbattle_rematch TRAINER_SUPER_NERD_EWALD, Route8_Text_KaizoEwaldRematch, Route8_Text_KaizoEwaldDefeat
	msgbox Route8_Text_KaizoEwaldPost, MSGBOX_AUTOCLOSE
	end

Route8_Text_KaizoEwaldIntro:
	.string "Let's battle!$"
Route8_Text_KaizoEwaldDefeat:
	.string "I lost!$"
Route8_Text_KaizoEwaldPost:
	.string "Come back anytime.$"
Route8_Text_KaizoEwaldRematch:
	.string "Ready for a rematch?$"

Route8_EventScript_KaizoAxel::
	trainerbattle_single TRAINER_BIKER_AXEL, Route8_Text_KaizoAxelIntro, Route8_Text_KaizoAxelDefeat
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, Route8_EventScript_KaizoAxelRematch
	msgbox Route8_Text_KaizoAxelPost, MSGBOX_AUTOCLOSE
	end

Route8_EventScript_KaizoAxelRematch::
	trainerbattle_rematch TRAINER_BIKER_AXEL, Route8_Text_KaizoAxelRematch, Route8_Text_KaizoAxelDefeat
	msgbox Route8_Text_KaizoAxelPost, MSGBOX_AUTOCLOSE
	end

Route8_Text_KaizoAxelIntro:
	.string "Let's battle!$"
Route8_Text_KaizoAxelDefeat:
	.string "I lost!$"
Route8_Text_KaizoAxelPost:
	.string "Come back anytime.$"
Route8_Text_KaizoAxelRematch:
	.string "Ready for a rematch?$"

@ GEN_ROUTE_TRAINERS_END
