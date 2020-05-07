import random
import string

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from typing import List

# Brandi game object
from app.game_logic.brandi import Brandi

# models
from app.models.player import Player
from app.models.action import Action
from app.models.card import Card
from app.models.game import GameList

router = APIRouter()

games = {}


@router.get('/games', response_model=GameList)
def get_list_of_games():
    """
    return a list of game keys
    """
    return [
        {
            'game_id' : game_key,
            'players' : [player.to_json() for player in game_instance.players.values()]
        } 
        for game_key, game_instance in games.items()]

@router.post('/games', response_model=GameList)
def initialize_new_game(player: Player):
    """
    start a new game
    """

    game_id = ''.join(random.choice(string.ascii_uppercase) for i in range(4))
    while game_id in games:
        game_id = ''.join(random.choice(string.ascii_uppercase) for i in range(4)) # generate new game ids until a new id is found

    games[game_id] = Brandi()
    games[game_id].player_join(player)
    return {
        'games': [
            {
                'game_id' : game_key,
                'players' : [player.to_json() for player in game_instance.players.values()]
            } 
            for game_key, game_instance in games.items()
        ]
    }

@router.get('/games/{game_id}')
def get_game_state(game_id: str, player: Player):
    """
    get the state of a game
    """
    if player.uid not in games[game_id].players:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Player not in Game."
        )
    return games[game_id].public_state()

@router.post('/games/{game_id}/join')
def join_game(game_id: str, player: Player):
    """
    join an existing game
    """
    if player.uid in games[game_id].players: # ensure no player joins twice
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Player {player.name} has already joined.")
        
    games[game_id].player_join(player)
    return games[game_id].public_state()

@router.post('/games/{game_id}/teams')
def set_teams(game_id: str, player: Player, teams: List[Player]):
    if player.uid not in games[game_id].players :
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Player {player.uid} not in Game.")
    if not all([_p.uid in games[game_id].players for _p in teams]): # check validity of teams
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Players not in Game.")
        
    if not len(set(teams)) == len(teams): # assert no doule players
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Not all players selected in request.")

    games[game_id].change_teams([player.uid for player in teams])
    return games[game_id].public_state()

@router.post('/games/{game_id}/ready', response_model=Player)
def toggle_player_ready(game_id: str, player: Player):
    if player.uid not in games[game_id].players :
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Player {player.uid} not in Game.")
    return games[game_id].public_state()

@router.post('/games/{game_id}/start')
def start_game(game_id: str, player: Player):
    """
    start an existing game
    """
    if player.uid not in games[game_id].players:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Player {player.uid} not in Game.")


    games[game_id].start_game()
    return games[game_id].public_state()

@router.post('/games/{game_id}/action')
def perform_action(game_id: str, player: Player, action: Action):
    """
    
    """
    games[game_id].event_play_card(player, action)
    return games[game_id].public_state()