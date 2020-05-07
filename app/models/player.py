from pydantic import BaseModel
from typing import List


class Marble(BaseModel):
    position: int
    color: str

class PlayerBase(BaseModel):
    name:str

class Player(PlayerBase):
    uid: str

class PlayerPublic(PlayerBase):
    ready: bool
    marbles: List[Marble]

class PlayerPrivate(Player, PlayerPublic):
    pass