import random

import logging
import json

from app.game_logic.deck import Deck
from app.game_logic.player import Player
from app.game_logic.field import Field, EntryExitNode
from app.game_logic.marble import Marble


NODES_BETWEEN_PLAYERS = 16
PLAYER_COUNT = 4
FIELD_SIZE = PLAYER_COUNT * 16
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


        Brandi.deck is an instance of a Deck object containing shuffled cards.

        Brandi.players is a list of Player instances

        Brandi.order:
            - is a list of player uids to keep track of the order and the teams
                player at position 0 and at position 2 always play together
        Brandi.active_player_index: keeps track of who's turn it is to play a card and 
            move a marble
        
        Brandi.round_turn: keeps track of which turn is reached
        Brandi.round_cards: list of how many cards are to be dealt at the 
            beginning of each round
        
        Brandi.field: field instance to keep track of the marbles
    """

    ### Initialization - Stage 0
    def __init__(self, game_id, seed = None):
        self.game_id = game_id
        self.game_state = 0 # start in the initialized state
        self.round_state = 0

        self.deck = Deck(seed) # initialize a deck instance
        self.players = {} # initialize a new player list
        self.order = [] # list of player uids to keep track of the order

        self.active_player_index = 0 # keep track of whos players turn it is to make a move
        
        self.round_cards = [6, 5, 4, 3, 2] # number of cards dealt at the 
        # beginning of each round
        self.round_turn = 0 # count which turn is reached

        self.blocking_positions = list(range(0, FIELD_SIZE, NODES_BETWEEN_PLAYERS))


        self.card_swap_count = 0 # keep track of how many cards have been swapped so that cards are revealed to the players correctly



    def player_join(self, player: Player):
        # have a player join the game
        assert player.uid not in self.players
        self.players[player.uid] = Player(player.uid, player.name)
        self.order.append(player.uid)

    def change_teams(self, playerlist):
        """
        allow for the teams to be chosen by the players before the game has 
        started

        Parameters:

        player_ids (list): List of player_ids, players with index 0 and 2 play 
            together
        """
        assert self.game_state < 2 # assert the game is not yet running
        for player in playerlist: # assert the user ids in user are in the game
            assert player.uid in self.players
        self.order = [player.uid for player in playerlist]

    def start_game(self):
        """
        start the game:
            - check that all players are present
            - players are assigned their starting position based on self.order
            - first round is started
        """
        assert all([e is not None for e in self.order]) # check that all players are present
        assert self.game_state == 0
        assert len(self.order) == 4
        # create a new field instance for the game
        self.field = Field(self.order) # field of players

        self.assign_starting_positions()

        self.start_round()

    def assign_starting_positions(self):
        """
        assign starting positions for the game based on self.order

        """
        for ind, player_uid in enumerate(self.order):
            self.players[player_uid].set_starting_position(self.field, ind)
        

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

        # reset the has folded attribute
        for uid in self.order:
            self.players[uid].has_folded = False            
        

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

    def swap_card(self, player, card):
        assert self.round_state == 2
        assert self.players[player.uid].may_swap_cards
        team_member = self.order[(self.order.index(player.uid) + PLAYER_COUNT // 2) % PLAYER_COUNT] # find the teammember

        swapped_card = self.players[player.uid].hand.play_card(card)
        self.players[team_member].hand.set_card(swapped_card)

        self.card_swap_count += 1

        # make sure the players only swap one card
        self.players[player.uid].may_swap_cards = False
        if self.card_swap_count % PLAYER_COUNT == 0: # when all players have sent their card to swap
            """
            TODO: send websocket with game state
            """
            self.round_state +=1

            # reset swapping ability for next round
            for uid in self.order:
                self.players[uid].may_swap_cards = True
        return None
    
    def increment_active_player_index(self):
        """
        increment the active player index until a player is found who has not yet folded
        """
        self.active_player_index = (self.active_player_index + 1) % PLAYER_COUNT

        while self.players[self.order[self.active_player_index]].has_finished():
            self.active_player_index = (self.active_player_index + 1) % PLAYER_COUNT


    """
    Game play events: 

    """
    def event_player_fold(self, player):
        """
        
        """
        self.players[player.uid].fold()
        self.increment_active_player_index()
        return {
            'requestValid': True,
            'note': f'Player {player.name} has folded for this round.' 
        }

    def event_move_marble(self, player, action):

        if player.uid != self.order[self.active_player_index]:
            return {
                'requestValid': False,
                'note': f'It is not player {player.name}s turn.'
            }
        marble = self.players[player.uid].marbles[action.mid]
        position = marble.curr
        if action.action not in self.players[player.uid].hand.cards[action.card.uid].action_options:
            return { 
                    'requestValid': False,
                    'note': 'Desired action does not match the card.'
                }
        #  get out of the start
        if action.action == 0: 
            if position is not None:
                return { 
                    'requestValid': False,
                    'note': 'Not in the starting position.'
                }
            # check that the marble goes to an entry node 
            # and
            # check whether the entrynode is blocked
            elif marble.next.is_blocking(): 
                return { 
                    'requestValid': False,
                    'note': 'Blocked by a marble.'
                }
            # marble is allowed to move
            else:
                # check whether there already is a marble
                if marble.next.has_marble():
                    # kick the exiting marble
                    marble.next.marble.reset_to_starting_position()
                

                # move the marble to the entry node
                marble.set_new_position(marble.next)
                marble.blocking = True # make the marble blocking other marbles
                
                self.increment_active_player_index()

                return {
                    'requestValid': True,
                    'note': f'Marble {action.mid} moved to {marble.curr.position}.' 
                }
        # normal actions
        elif action.action in [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13]:
            # try to move action.action nodes ahead

            # use pnt variable to check the path along the action of the marble i.e. whether it 
            # is blocked or it may enter its goal
            pnt = marble.curr
            for _ in range(action.action):
                pnt = pnt.next
                # check whether a marble is blocking along the way
                if pnt.is_blocking():
                    return { 
                        'requestValid': False,
                        'note': f'Blocked by a marble at position {pnt.position}.'
                    }

            if pnt.has_marble():
                # kick the marble
                pnt.marble.reset_to_starting_position()
            
            # move the marble to the entry node
            marble.set_new_position(pnt)
            # performing any motion with a marble on the field removes the blocking capability
            marble.blocking = False 

            self.increment_active_player_index()

            return {
                'requestValid': True,
                'note': f'Marble {action.mid} moved to {marble.curr.position}.' 
            }

        elif action.action == -4: # go backwards 4
            # try to move action.action nodes ahead

            # use pnt variable to check the path along the action of the marble i.e. whether it 
            # is blocked or it may enter its goal
            pnt = marble.curr
            for _ in range(abs(action.action)):
                pnt = pnt.prev
                # check whether a marble is blocking along the way
                if pnt.is_blocking():
                    return { 
                        'requestValid': False,
                        'note': f'Blocked by a marble at position {pnt.position}.'
                    }

            if pnt.has_marble():
                # kick the marble
                pnt.marble.reset_to_starting_position()
            
            # move the marble to the entry node
            marble.set_new_position(pnt)
            # performing any motion with a marble on the field removes the blocking capability
            marble.blocking = False 

            self.increment_active_player_index()

            return {
                'requestValid': True,
                'note': f'Marble {action.mid} moved to {marble.curr.position}.' 
            }

        elif action.action == 'switch':
            assert action.mid_2 is not None # make sure a second marble was submitted
            assert action.pid_2 is not None # make sure a playerid was submitted

                


    """
    Event Assertions
    """

    def potential_target_position(self, player, action):
        # find the target position i.e. wheter in ones own goal or on the field
        start = action.marble_position
        preliminary_target = (action.marble_position + action.action) % FIELD_SIZE
        
        # check if player can enter own goal
        field_range_representation = set(range(0, FIELD_SIZE)[start : preliminary_target])
        
        if player.starting_position in field_range_representation:
            pass

        

    """
    GAMESTATE:

    write and read the full game state as JSON
    """
    def get_cards(self, player):
        return self.players[player.uid].private_state()
        

    def public_state(self):
        return {
            'game_id': self.game_id,
            'game_state': self.game_state,
            'round_state': self.round_state,
            'round_turn': self.round_turn,
            'order': self.order,
            'active_player_index': self.active_player_index,
            'players': [self.players[uid].to_json() for uid in self.order]
        }

    def to_json(self):
        """
        Return game state as a JSON object

        """
        return {
            'game_id': self.game_id,
            'game_state': self.game_state,
            'round_state': self.round_state,
            'round_turn': self.round_turn,
            'deck': self.deck.to_json(),
            'players': [player.to_json() for player in self.players], 
            'order': self.order,
            'active_player_index': self.active_player_index,
        }
    
    def from_json(self):
        """
        Set game state from a JSON object

        """
        pass