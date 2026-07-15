import asyncio

from briscola5.web.engine.card import Card, Rank, Suit
from briscola5.web.engine.state import Phase
from briscola5.domain.trick import PlayedCard
from briscola5.web.manager import GameManager, Seat


def completed_trick_manager() -> GameManager:
    manager = GameManager()
    manager.started = True
    manager.seats = [Seat(i, f"P{i + 1}", None, is_bot=True) for i in range(5)]

    state = manager.service.state
    state.phase = Phase.TRICK_PLAY
    state.call.trump_suit = Suit.DENARI
    state.call.caller_player = 1
    state.call.partner_player_internal = 2
    state.call.partner_revealed = True
    state.call.target_points = 70
    state.trick.played = [
        PlayedCard(0, Card(Suit.COPPE, Rank.DUE)),
        PlayedCard(1, Card(Suit.COPPE, Rank.TRE)),
        PlayedCard(2, Card(Suit.SPADE, Rank.ASSO)),
        PlayedCard(3, Card(Suit.COPPE, Rank.RE)),
    ]
    state.turn.current_player = 4
    state.hands[4] = [Card(Suit.BASTONI, Rank.QUATTRO)]
    return manager


def test_completed_trick_remains_visible_with_winner() -> None:
    manager = completed_trick_manager()

    manager._play_card_with_animation(4, 0)

    assert manager.resolving_trick is True
    assert len(manager.table_snapshot or []) == 5
    assert manager.trick_result == {
        "winner_id": 1,
        "winner_name": "P2",
        "points": 25,
    }
    public = manager.public_state(None)
    assert public["phase"] == "trick_play"
    assert public["current_player"] is None
    assert public["trick_result"]["winner_name"] == "P2"


def test_final_trick_is_collected_before_final_result() -> None:
    manager = completed_trick_manager()
    manager._play_card_with_animation(4, 0)
    manager.trick_collect_delay = 0

    asyncio.run(manager.run_bots())

    assert manager.resolving_trick is False
    assert manager.table_snapshot is None
    assert manager.trick_result is None
    assert manager.finished_scored is True
    assert manager.public_state(None)["phase"] == "game_over"
