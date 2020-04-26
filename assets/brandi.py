import random

import logging
import json

from deck import Deck
from player import Player
from field import Field

class Brandi():
    """
        Brandi Dog game instance handling the game logic.

        Brandi.game_state can take values between 0 and 4, indicating one of the 
        following game states:
            - 0: initialized, waiting for players
            - 1: ready to be started
            - 2: running
            - 3: finished, ready to be purged
            - 4: purged
        Brandi.round_state can take values between 0 and 2 indicating one of the
        following round states:
            - 0: round has not yet started # should only be the case for the very first round of a game
            - 1: round has started and cards have not yet been dealt
            - 2: round has started and cards have been dealt but not yet 
                exchanged within the team
            - 3: round has started and cards to be exchanged have been dealt but
                not yet been shown to the teammate
            - 4: round has started and cards have been exchanged between 
                teammates
            - 5: round has finished 


        Brandi.Deck is an instance of a Deck object containing shuffled cards.

        Brandi.players is a list of Player instances

        Brandi.order:
            - is a list of player uids to keep track of the order and the teams
                player at position 0 and at position 2 always play together
        Brandi.turn_order: keeps track of who's turn it is to play a card and 
            move a marble
        
        Brandi.round_turn: keeps track of which turn is reached
        Brandi.round_cards: list of how many cards are to be dealt at the 
            beginning of each round
        
        Brandi.field: field instance to keep track of the marbles
    """

    ### Initialization - Stage 0
    def __init__(self, seed = None):
        self.game_state = 0 # start in the initialized state
        self.round_state = 0

        self.deck = Deck(seed) # initialize a deck instance
        self.players = {} # initialize a new player list
        self.order = [] # list of player uids to keep track of the order
        self.turn_order = 0 # keep track of whos players turn it is to make a move

        self.round_cards = [6, 5, 4, 3, 2] # number of cards dealt at the 
        # beginning of each round
        self.round_turn = 0 # count which turn is reached

        self.field = Field() # field of players


    def player_join(self, user):
        # have a player join the game
        assert user.uid not in self.players
        self.players[user.uid] = Player(user.name)
        self.order.append(user.uid)

    def change_teams(self, player_ids):
        """
        allow for the teams to be chosen by the players before the game has 
        started

        Parameters:

        player_ids (list): List of player_ids, players with index 0 and 2 play 
            together
        """
        assert self.game_state < 2 # assert the game is not yet running
        for user_id in player_ids: # assert the user ids in user are in the game
            assert user_id in self.players
        self.order = player_ids


    def assign_starting_positions(self):
        """
        assign starting positions for the game based on self.order

        """
        for ind, uid in enumerate(self.order):
            self.players[uid].set_starting_position(ind)

    def start_game(self):
        """
        start the game:
            - check that all players are present
            - players are assigned their starting position based on self.order
            - first round is started
        """
        assert all([e is not None for e in self.order]) # check that all players are present
        assert self.game_state == 0
        self.assign_starting_positions()
        

    def start_round(self):
        """
        start a round:
            - check and set the correct game state
            - deal cards
        """
        assert self.round_state in [0, 5]
        self.game_state = 2
        self.round_state = 1

        self.deal_cards()
        

    def deal_cards(self):
        """
        deal the correct number of cards to all players depending on the current
        round turn
        """
        assert self.game_state == 2 and self.round_state == 1 # check that the game is in the correct state

        for uid in self.order:
            for _ in range(self.round_cards[self.round_turn % 5]):
                self.players[uid].set_card(self.deck.give_card()) 

        self.round_state = 2


    """
    EVENTS: 

    do some action by:
        - choosing a card
        - choosing an action from that card 
        - choosing a marble to perform that action on
    """
    def event_play_card(self, player_id, card_id):
        assert player_id in self.players
        assert card_id in self.players[player_id].hand.cards


    def choose_action(self, player_id, card_id):
        assert self.order[self.turn_order] == player_id
        return self.players[player_id].choose_action(card_id)

    def move_marble(self, action):
        """
        move a selected marble
        """
        assert player_id == self.order[self.turn_order]

