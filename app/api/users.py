import random
import string

from fastapi import APIRouter, Path

from pydantic import BaseModel

from ..models.player import Player, PlayerBase

router = APIRouter()

players = {}

@router.post('/player',  response_model=Player)
def create_new_player(player: PlayerBase):
    player_id = ''.join(random.choice(string.ascii_uppercase) for i in range(4))
    while player_id in players:
        player_id = ''.join(random.choice(string.ascii_uppercase) for i in range(4)) # generate new game ids until a new id is found

    players[player_id] = {'name': player.name, 'uid': player_id}
    
    return players[player_id]

@router.get('/player', response_model=Player)
def get_player(player: PlayerBase):
    return players[player.uid]