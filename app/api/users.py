import random
import string

from fastapi import APIRouter #, Path

# from pydantic import BaseModel

from app.models.player import Player, PlayerBase

router = APIRouter()

users = {}

@router.post('/player',  response_model=Player)
def create_new_player(player: PlayerBase):
    player_id = ''.join(random.choice(string.ascii_uppercase) for i in range(4))
    while player_id in users:
        player_id = ''.join(random.choice(string.ascii_uppercase) for i in range(4)) # generate new game ids until a new id is found

    users[player_id] = {'name': player.name, 'uid': player_id}
    
    return users[player_id]

@router.get('/player', response_model=Player)
def get_player(player: PlayerBase):
    return users[player.uid]