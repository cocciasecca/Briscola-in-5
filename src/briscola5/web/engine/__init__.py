"""LAN-specific game adapter.

The original domain, application, bot and CLI packages remain untouched.  The
web interface uses this isolated variant because it presents Neapolitan card
labels and starts normal trick play immediately after the call.
"""

from .card import Card, Rank, Suit
from .game_service import GameService
from .greedy_bot import GreedyBot
from .state import GameState, Phase

__all__ = ["Card", "GameService", "GameState", "GreedyBot", "Phase", "Rank", "Suit"]
