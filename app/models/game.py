from pydantic import BaseModel
from typing import Dict, List

from .player import PlayerBase


class Game(BaseModel):
    game_id: str
    players: List[PlayerBase]

class GameList(BaseModel):
    games: List[Game]