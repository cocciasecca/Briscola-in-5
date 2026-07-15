from __future__ import annotations

import asyncio
import secrets
from dataclasses import dataclass
from typing import Any

from briscola5.web.engine import Card, GameService, GreedyBot, Phase, Rank, Suit


@dataclass
class Seat:
    """A lobby seat. Human tokens never leave the server or owning browser."""
    player_id: int
    name: str
    token: str | None
    is_bot: bool = False
    connected: bool = True


class GameManager:
    """Owns the single LAN lobby, match state, clients and bot automation."""

    def __init__(self) -> None:
        self.service = GameService()
        self.seats: list[Seat | None] = [None] * 5
        self.started = False
        self.paused = False
        self.pause_reason = ""
        self.host_token: str | None = None
        self.websockets: dict[str, Any] = {}
        self.lock = asyncio.Lock()
        self.bot_lock = asyncio.Lock()
        self.last_event = "In attesa dei giocatori"
        self.finished_scored = False
        # Delay between automatic moves so players can follow the table.
        self.bot_delay = 1.0
        # Keep a completed trick visible before collecting its cards.
        self.trick_collect_delay = 1.5
        self.table_snapshot: list[dict[str, Any]] | None = None
        self.trick_result: dict[str, Any] | None = None
        self.resolving_trick = False

    def reset(self) -> None:
        """Return the single-room server to an empty pre-game state."""
        self.service = GameService()
        self.seats = [None] * 5
        self.started = False
        self.paused = False
        self.pause_reason = ""
        self.host_token = None
        self.websockets = {}
        self.last_event = "In attesa dei giocatori"
        self.finished_scored = False
        self.table_snapshot = None
        self.trick_result = None
        self.resolving_trick = False

    def join(self, name: str, reconnect_token: str | None = None) -> tuple[int, str, bool]:
        """Create a human seat or reclaim it using the browser reconnect token."""
        clean_name = (name or "Giocatore").strip()[:24] or "Giocatore"
        if reconnect_token:
            for seat in self.seats:
                if seat and seat.token == reconnect_token and not seat.is_bot:
                    seat.connected = True
                    seat.name = clean_name
                    self._refresh_pause()
                    return seat.player_id, reconnect_token, seat.player_id == 0

        if self.started:
            raise ValueError("La partita è già iniziata. Usa il token di riconnessione.")

        try:
            player_id = self.seats.index(None)
        except ValueError as exc:
            raise ValueError("Il tavolo è pieno.") from exc

        token = secrets.token_urlsafe(24)
        seat = Seat(player_id=player_id, name=clean_name, token=token)
        self.seats[player_id] = seat
        if self.host_token is None:
            self.host_token = token
        self.last_event = f"{clean_name} si è unito al tavolo"
        return player_id, token, token == self.host_token

    def disconnect(self, token: str) -> None:
        seat = self.seat_for_token(token)
        if seat is None or seat.is_bot:
            return
        seat.connected = False
        if self.started:
            self.paused = True
            self.pause_reason = f"{seat.name} si è disconnesso"
            self.last_event = self.pause_reason
        else:
            self.seats[seat.player_id] = None
            if token == self.host_token:
                self._assign_new_host()

    def _assign_new_host(self) -> None:
        humans = [s for s in self.seats if s and not s.is_bot and s.connected]
        self.host_token = humans[0].token if humans else None

    def _refresh_pause(self) -> None:
        disconnected = [s for s in self.seats if s and not s.is_bot and not s.connected]
        if not disconnected:
            self.paused = False
            self.pause_reason = ""

    def seat_for_token(self, token: str | None) -> Seat | None:
        if not token:
            return None
        return next((s for s in self.seats if s and s.token == token), None)

    def require_host(self, token: str) -> None:
        if token != self.host_token:
            raise ValueError("Solo l'host può eseguire questa operazione.")

    def start_game(self, token: str) -> None:
        """Fill empty seats with bots and start the only match hosted by this process."""
        self.require_host(token)
        if self.started:
            raise ValueError("La partita è già iniziata.")
        if self.seats[0] is None:
            raise ValueError("Non ci sono giocatori.")
        for i, seat in enumerate(self.seats):
            if seat is None:
                self.seats[i] = Seat(i, f"Bot {i + 1}", None, is_bot=True)
        self.service.setup_game(dealer_id=4)
        self.started = True
        self.last_event = "Partita iniziata"

    def replace_with_bot(self, token: str, player_id: int) -> None:
        self.require_host(token)
        if not 0 <= player_id < 5:
            raise ValueError("Posto non valido.")
        seat = self.seats[player_id]
        if seat is None or seat.is_bot:
            raise ValueError("Questo posto non appartiene a un giocatore disconnesso.")
        if seat.connected:
            raise ValueError("Il giocatore è ancora connesso.")
        old_token = seat.token
        self.seats[player_id] = Seat(player_id, f"Bot {player_id + 1}", None, is_bot=True)
        if old_token == self.host_token:
            self._assign_new_host()
        self._refresh_pause()
        self.last_event = f"Il giocatore {player_id + 1} è stato sostituito da un bot"

    def bid(self, token: str, offer: int | None) -> None:
        seat = self._human_turn(token, Phase.AUCTION)
        before = self.service.state.turn.current_player
        self.service.auction_phase(seat.player_id, offer)
        if before == seat.player_id:
            self.last_event = f"{seat.name} passa" if offer is None else f"{seat.name} offre {offer}"

    def play(self, token: str, card_index: int) -> None:
        phase = self.service.state.phase
        if phase not in (Phase.DEAD_TRICK_PLAY, Phase.TRICK_PLAY):
            raise ValueError("In questa fase non puoi giocare una carta.")
        seat = self._human_turn(token, phase)
        hand = self.service.state.hands[seat.player_id]
        if not 0 <= card_index < len(hand):
            raise ValueError("Carta non valida.")
        card = self._play_card_with_animation(seat.player_id, card_index)
        if not self.resolving_trick:
            self.last_event = f"{seat.name} gioca {self.card_label(card)}"

    def call(self, token: str, suit: str, rank: str) -> None:
        seat = self._human_turn(token, Phase.DEAD_TRICK_CALL, caller_only=True)
        try:
            suit_value = Suit(suit)
            rank_value = Rank(rank)
        except ValueError as exc:
            raise ValueError("Carta chiamata non valida.") from exc
        if not self.service.make_call(suit_value, rank_value):
            raise ValueError("La carta chiamata non è valida.")
        self.last_event = f"{seat.name} chiama {rank_value.value} di {suit_value.value}"

    def _human_turn(self, token: str, phase: Phase, caller_only: bool = False) -> Seat:
        if not self.started:
            raise ValueError("La partita non è iniziata.")
        if self.paused:
            raise ValueError("La partita è in pausa.")
        if self.resolving_trick:
            raise ValueError("Attendi che la presa venga raccolta.")
        if self.service.state.phase != phase:
            raise ValueError("Azione non valida in questa fase.")
        seat = self.seat_for_token(token)
        if seat is None or seat.is_bot:
            raise ValueError("Giocatore non riconosciuto.")
        expected = (
            self.service.state.call.caller_player
            if caller_only
            else self.service.state.turn.current_player
        )
        if seat.player_id != expected:
            raise ValueError("Non è il tuo turno.")
        return seat

    async def run_bots(self) -> None:
        """Advance automatic seats until a human decision or pause is reached."""
        if self.bot_lock.locked():
            return
        async with self.bot_lock:
            while self.started and not self.paused:
                # The engine has already resolved the trick, but the web layer
                # keeps all five cards visible long enough for humans to see it.
                if self.resolving_trick:
                    await asyncio.sleep(self.trick_collect_delay)
                    self.table_snapshot = None
                    self.trick_result = None
                    self.resolving_trick = False
                    await self.broadcast()

                if self.service.state.phase == Phase.GAME_OVER:
                    break

                state = self.service.state
                if state.phase == Phase.DEAD_TRICK_CALL:
                    player_id = state.call.caller_player
                else:
                    player_id = state.turn.current_player
                if player_id is None:
                    return
                seat = self.seats[player_id]
                if seat is None or not seat.is_bot:
                    return

                # One full second before every bot decision/card, so consecutive
                # automatic moves do not appear all at once.
                await asyncio.sleep(self.bot_delay)
                if self.paused:
                    return

                bot = GreedyBot(player_id)
                if state.phase == Phase.AUCTION:
                    offer = bot.make_bid(state)
                    self.service.auction_phase(player_id, offer)
                    self.last_event = f"{seat.name} passa" if offer is None else f"{seat.name} offre {offer}"
                elif state.phase == Phase.DEAD_TRICK_PLAY:
                    idx = bot.choose_discard(state)
                    valid = self._valid_dead_trick_indices(player_id)
                    if idx not in valid:
                        idx = min(valid, key=lambda i: state.hands[player_id][i].points)
                    card = state.hands[player_id][idx]
                    if not self.service.play_card(player_id, idx):
                        raise RuntimeError("Il motore ha rifiutato uno scarto verificato come valido")
                    self.last_event = f"{seat.name} scarta {self.card_label(card)}"
                elif state.phase == Phase.DEAD_TRICK_CALL:
                    suit, rank = bot.declare_trump_and_card(state)
                    if not self.service.make_call(suit, rank):
                        suit, rank = self._first_valid_call(player_id)
                        self.service.make_call(suit, rank)
                    self.last_event = f"{seat.name} chiama {rank.value} di {suit.value}"
                elif state.phase == Phase.TRICK_PLAY:
                    idx = bot.play_card(state)
                    card = self._play_card_with_animation(player_id, idx)
                    if not self.resolving_trick:
                        self.last_event = f"{seat.name} gioca {self.card_label(card)}"
                await self.broadcast()

            # The final trick must remain visible before the final result replaces it.
            if self.resolving_trick:
                await asyncio.sleep(self.trick_collect_delay)
                self.table_snapshot = None
                self.trick_result = None
                self.resolving_trick = False
                await self.broadcast()

            if self.started and self.service.state.phase == Phase.GAME_OVER and not self.finished_scored:
                self.service.end_game()
                self.finished_scored = True
                self.last_event = "Partita terminata"
                await self.broadcast()

    def _play_card_with_animation(self, player_id: int, card_index: int) -> Card:
        """Play a card and preserve a completed trick for the browser animation."""
        state = self.service.state
        card = state.hands[player_id][card_index]
        completing_normal_trick = state.phase == Phase.TRICK_PLAY and len(state.trick.played) == 4
        table_before = [
            {"player_id": pc.player_id, **self.card_dict(pc.card)}
            for pc in state.trick.played
        ]

        if not self.service.play_card(player_id, card_index):
            raise ValueError("Questa carta non può essere giocata.")

        if completing_normal_trick:
            full_table = [*table_before, {"player_id": player_id, **self.card_dict(card)}]
            winner_id = self.service.state.turn.current_player
            winner_seat = self.seats[winner_id]
            winner_name = winner_seat.name if winner_seat else f"Giocatore {winner_id + 1}"
            points = sum(int(item["points"]) for item in full_table)
            self.table_snapshot = full_table
            self.trick_result = {
                "winner_id": winner_id,
                "winner_name": winner_name,
                "points": points,
            }
            self.resolving_trick = True
            self.last_event = f"Prende {winner_name} (+{points} punti)"
        return card

    def _valid_dead_trick_indices(self, player_id: int) -> list[int]:
        state = self.service.state
        target = state.call.target_points or 0
        on_table = sum(pc.card.points for pc in state.trick.played)
        valid = [
            i for i, card in enumerate(state.hands[player_id])
            if target + on_table + card.points <= 120
        ]
        if not valid:
            raise RuntimeError("Nessuno scarto valido: stato della prima mano incoerente")
        return valid

    def _first_valid_call(self, player_id: int) -> tuple[Suit, Rank]:
        hand = self.service.state.hands[player_id]
        played = [pc.card for pc in self.service.state.trick.played]
        for suit in Suit:
            for rank in Rank:
                candidate = Card(suit, rank)
                if candidate not in hand and candidate not in played:
                    return suit, rank
        raise RuntimeError("Nessuna carta chiamabile")

    def public_state(self, token: str | None) -> dict[str, Any]:
        """Build a viewer-specific snapshot without leaking opponents' hands."""
        viewer = self.seat_for_token(token)
        state = self.service.state
        players = []
        for seat in self.seats:
            if seat is None:
                players.append(None)
            else:
                players.append(
                    {
                        "id": seat.player_id,
                        "name": seat.name,
                        "is_bot": seat.is_bot,
                        "connected": seat.connected,
                        "cards": len(state.hands[seat.player_id]) if self.started else 0,
                        "points": state.score.player_points[seat.player_id] if self.started else 0,
                    }
                )

        # The viewer receives only their own hand. Opponent card counts are public,
        # but the actual cards remain exclusively in the server-side GameState.
        hand = []
        if viewer and self.started:
            hand = [self.card_dict(c, i) for i, c in enumerate(state.hands[viewer.player_id])]

        caller = state.call.caller_player if self.started else None
        partner = state.call.partner_player_internal if state.call.partner_revealed else None
        result = None
        if state.phase == Phase.GAME_OVER and self.finished_scored and caller is not None:
            result = {
                "caller": caller,
                "partner": state.call.partner_player_internal,
                "target": state.call.target_points,
                "team_points": state.team_points_if_known()[0]
                if state.team_points_if_known()
                else None,
                "won": state.call.caller_team_won,
            }

        return {
            "started": self.started,
            "paused": self.paused,
            "pause_reason": self.pause_reason,
            "phase": (
                Phase.TRICK_PLAY.value
                if self.resolving_trick and state.phase == Phase.GAME_OVER
                else state.phase.value
            ) if self.started else "lobby",
            "players": players,
            "viewer_id": viewer.player_id if viewer else None,
            "is_host": bool(viewer and viewer.token == self.host_token),
            "current_player": (
                None if self.resolving_trick else state.turn.current_player
            ) if self.started else None,
            "caller": caller,
            "partner": partner,
            "target": state.call.target_points if self.started else None,
            "last_bid": state.auction.last_bid if self.started else None,
            "last_bidder": state.auction.last_bidder if self.started else None,
            "passed": state.auction.passed if self.started else [False] * 5,
            "trump": state.call.trump_suit.value if state.call.trump_suit else None,
            "called_card": self.card_dict(state.call.called_card)
            if state.call.called_card
            else None,
            "trick_index": (
                max(0, state.trick.index - 1) if self.resolving_trick else state.trick.index
            ) if self.started else 0,
            "table": self.table_snapshot if self.table_snapshot is not None else [
                {"player_id": pc.player_id, **self.card_dict(pc.card)}
                for pc in state.trick.played
            ],
            "trick_result": self.trick_result,
            "resolving_trick": self.resolving_trick,
            "hand": hand,
            "last_event": self.last_event,
            "result": result,
        }

    async def broadcast(self) -> None:
        """Push a separately filtered state snapshot to every connected browser."""
        stale = []
        for token, websocket in list(self.websockets.items()):
            try:
                await websocket.send_json(self.public_state(token))
            except Exception:  # pragma: no cover - network cleanup
                stale.append(token)
        for token in stale:
            self.websockets.pop(token, None)

    @staticmethod
    def card_label(card: Card) -> str:
        return f"{card.rank.value} di {card.suit.value}"

    @staticmethod
    def card_dict(card: Card | None, index: int | None = None) -> dict[str, Any] | None:
        if card is None:
            return None
        data: dict[str, Any] = {
            "suit": card.suit.value,
            "rank": card.rank.value,
            "points": card.points,
            "strength": card.strength,
        }
        if index is not None:
            data["index"] = index
        return data
