from briscola5.application.game_service import GameService
from briscola5.bots.random_bot import RandomBot
from briscola5.domain.state import Phase


def test_game_with_random_bots():
    valid_game_started = False
    
    while not valid_game_started:
        service = GameService()
        service.setup_game(dealer_id=0)

        bots = {i: RandomBot(player_id=i) for i in range(5)}
        
        consecutive_passes = 0
        while service.state.phase == Phase.AUCTION:
            curr_player = service.state.turn.current_player
            bot = bots[curr_player]
            bid = bot.make_bid(service.state)
            
            if bid is None:
                consecutive_passes += 1
            else:
                consecutive_passes = 0
                
            service.auction_phase(curr_player, bid)
            
            if consecutive_passes >= 5:
                break
                
        if service.state.phase == Phase.DEAD_TRICK_PLAY:
            valid_game_started = True

    while service.state.phase == Phase.DEAD_TRICK_PLAY:
        curr_player = service.state.turn.current_player
        bot = bots[curr_player]
        card_index = bot.choose_discard(service.state)
        
        success = service.play_card(curr_player, card_index)
        if not success:
            hand = service.state.hands[curr_player]
            for fallback_idx in range(len(hand)):
                if service.play_card(curr_player, fallback_idx):
                    break

    if service.state.phase == Phase.DEAD_TRICK_CALL:
        caller_id = service.state.call.caller_player
        bot = bots[caller_id]
        suit, rank = bot.declare_trump_and_card(service.state)
        service.make_call(suit, rank)

    max_turn = 40
    turn_played = 0

    while service.state.phase == Phase.TRICK_PLAY and turn_played < max_turn:
        curr_player = service.state.turn.current_player
        bot = bots[curr_player]
        card_index = bot.play_card(service.state)
        service.normal_trick_rounds(card_index, curr_player)
        turn_played += 1

    assert service.state.phase == Phase.GAME_OVER, "Partita non terminata correttamente"

    service.end_game()
    assert service.state.call.caller_team_won is not None
