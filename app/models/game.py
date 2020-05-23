from pydantic import BaseModel
from typing import Dict, List, Optional

from app.models.player import PlayerBase, Player, PlayerPublic
from app.models.card import Card

class GameBase(BaseModel):
    game_id: str
    players: List[Player]


class GamePublic(GameBase):
    game_state: int
    round_state: int
    round_turn: int
    order: List
    active_player_index: int
    players: Dict[str, Player]
    # thilo branch
    host: Player
    game_name: str
    top_card: Optional[Card]
