from pydantic import BaseModel

class PlayerBase(BaseModel):
    name:str

class Player(PlayerBase):
    uid: str
