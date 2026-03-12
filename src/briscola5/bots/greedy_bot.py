from collections import Counter
import random 
from briscola5.bots.base import BaseBot
from briscola5.domain.card import Card, Rank, Suit
from briscola5.domain.state import GameState


def evaluate_trump_suit(hand: list[Card], suit: Suit) -> float:
    cards = [c for c in hand if c.suit == suit]
    count = len(cards)

    points = sum(c.points for c in cards)
    strength_score = sum(c.strength for c in cards)
    length_bonus = count * 1.2

    has_ace = any(c.rank == Rank.ASSO for c in cards)
    has_three = any(c.rank == Rank.TRE for c in cards)
    combo_bonus = 5 if has_ace and has_three else 0

    return points + length_bonus + combo_bonus + strength_score * 0.2


def estimate_hand_strength(hand: list[Card]) -> float:
    base_points = sum(c.points for c in hand)
    best_trump_value = max(evaluate_trump_suit(hand, s) for s in Suit)
    return base_points + best_trump_value


def max_bid(strength: float) -> int:
    s_min = 15.0
    s_max = 80.0
    normalized = (strength - s_min) / (s_max - s_min)
    normalized = max(0.0, min(1.0, normalized))
    bid = 71 + normalized * (120 - 71)
    return int(round(bid))


class GreedyBot(BaseBot):

    def make_bid(self, state: GameState) -> int | None:
        hand = state.hands[self.player_id]
        current_bid = state.auction.last_bid if state.auction.last_bid is not None else 70

        strength = estimate_hand_strength(hand)

        active_players = state.auction.active_players_count()
        factor = 1.05 if active_players <= 3 else 1.0

        calculated_max_bid = int(max_bid(strength) * factor)

        if current_bid >= calculated_max_bid:
            return None
    
        distance = calculated_max_bid - current_bid
        
        pass_probability = 1 / (distance + 1)

        if random.random() < pass_probability:
            return None

        return max(current_bid + 1, 71)
    
    def choose_discard(self, state: GameState) -> int:
        hand = state.hands[self.player_id]
        suit_counts = Counter(card.suit for card in hand)
        dangerous_ranks = [Rank.ASSO, Rank.TRE, Rank.RE]

        naked_high_cards = [
            i
            for i, card in enumerate(hand)
            if suit_counts[card.suit] == 1 and card.rank in dangerous_ranks
        ]

        trick_points = sum(pc.card.points for pc in state.trick.played)
        if naked_high_cards and trick_points < 10:
            return max(naked_high_cards, key=lambda i: hand[i].strength)

        trump = state.call.trump_suit
        non_trumps = [i for i, card in enumerate(hand) if trump is None or card.suit != trump]

        if non_trumps:
            return min(non_trumps, key=lambda i: (hand[i].points, hand[i].strength))

        return min(range(len(hand)), key=lambda i: (hand[i].points, hand[i].strength))

    def declare_trump_and_card(self, state: GameState) -> tuple[Suit, Rank]:
        hand = state.hands[self.player_id]
        best_suit = max(list(Suit), key=lambda s: evaluate_trump_suit(hand, s))

        ranks_in_hand = [card.rank for card in hand if card.suit == best_suit]

        played_cards = [pc.card for pc in state.trick.played]
        played_ranks_of_trump = [c.rank for c in played_cards if c.suit == best_suit]

        call_priority = [
            Rank.ASSO,
            Rank.TRE,
            Rank.RE,
            Rank.CAVALLO,
            Rank.DONNA,
            Rank.SETTE,
            Rank.SEI,
            Rank.CINQUE,
            Rank.QUATTRO,
            Rank.DUE,
        ]

        target_rank = Rank.ASSO
        for rank in call_priority:
            if rank not in ranks_in_hand and rank not in played_ranks_of_trump:
                target_rank = rank
                break

        return best_suit, target_rank

    # pylint: disable=too-many-locals, too-many-branches
    def play_card(self, state: GameState) -> int:
        hand = state.hands[self.player_id]
        played = state.trick.played
        trump_suit = state.call.trump_suit
        caller = state.call.caller_player
        called_card = state.call.called_card

        am_i_partner = called_card in hand

        if not played:
            if self.player_id == caller:
                t_idx = [i for i, c in enumerate(hand) if c.suit == trump_suit]
                if t_idx:
                    t_sorted = sorted(t_idx, key=lambda i: hand[i].strength)
                    return t_sorted[len(t_sorted) // 2]
            return min(range(len(hand)), key=lambda i: (hand[i].points, hand[i].strength))

        lead_suit = played[0].card.suit
        winning_pc = played[0]

        for pc in played[1:]:
            c = pc.card
            w = winning_pc.card
            if c.suit == trump_suit and w.suit != trump_suit:
                winning_pc = pc
            elif c.suit == w.suit and c.strength > w.strength:
                winning_pc = pc

        winning_player = winning_pc.player_id
        trick_points = sum(pc.card.points for pc in played)
        is_last = len(played) == len(state.hands) - 1

        friend_winning = False
        if (
            self.player_id == caller
            and state.call.partner_revealed
            and winning_player == state.call.partner_player_internal
        ):
            friend_winning = True
        elif am_i_partner and winning_player == caller:
            friend_winning = True
        elif (
            self.player_id != caller
            and not am_i_partner
            and winning_player != caller
            and winning_player != state.call.partner_player_internal
        ):
            friend_winning = True

        if friend_winning and is_last:
            non_trumps = [i for i, c in enumerate(hand) if c.suit != trump_suit]
            if non_trumps:
                return max(non_trumps, key=lambda i: hand[i].points)

        beating_indices = []
        for i, card in enumerate(hand):
            w = winning_pc.card
            if card.suit == trump_suit and w.suit != trump_suit:
                beating_indices.append(i)
            elif card.suit == w.suit and card.strength > w.strength:
                if w.suit in (lead_suit, trump_suit):
                    beating_indices.append(i)

        if beating_indices and not friend_winning:
            if is_last or trick_points >= 10:
                return min(beating_indices, key=lambda i: hand[i].strength)

        non_trumps = [i for i, c in enumerate(hand) if trump_suit is None or c.suit != trump_suit]
        if non_trumps:
            return min(non_trumps, key=lambda i: (hand[i].points, hand[i].strength))

        return min(range(len(hand)), key=lambda i: (hand[i].points, hand[i].strength))
