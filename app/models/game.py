from pydantic import BaseModel
from typing import Dict, List

from app.models.player import Player, PlayerPublic


class GameBase(BaseModel):
    game_id: str
    players: List[Player]

class GamePublic(GameBase):
    game_state: int
    round_state: int
    round_turn: int
    order: List
    active_player_index: int
    players: List[Player]