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
            - 4: purged # should never be seen
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

    # Initialization - Stage 0
    def __init__(self, game_id, host, seed=None, game_name=None, debug=False):
        self.game_id = game_id
        self.game_name = game_name
        self.host = Player(host.uid, host.name)
        self.game_state = 0  # start in the initialized state
        self.round_state = 0

        self.deck = Deck(seed)  # initialize a deck instance
        self.players = {}  # initialize a new player list
        self.order = []  # list of player uids to keep track of the order
        self.active_player_index = 0  # keep track of whos players turn it is to make a move

        self.round_cards = [6, 5, 4, 3, 2]  # number of cards dealt at the
        # beginning of each round
        self.round_turn = 0  # count which turn is reached

        # keep track of how many cards have been swapped so that cards are revealed to the players correctly
        self.card_swap_count = 0
        if debug:
            test_players = [
                {'name': 'Test Player 1', 'uid': 'AAAA'},
                {'name': 'Test Player 2', 'uid': 'BBBB'},
                {'name': 'Test Player 3', 'uid': 'CCCC'},
            ]
            for player in test_players:
                self.player_join(Player(player['uid'], player['name']))

        # not actually necessary for the game, but nice to look at on the frontend
        self.top_card = None

    def set_name(self, name):
        self.game_name = name

    def set_host(self, player):
        self.host = Player(player.uid, player.name)

    def player_join(self, player: Player):
        # have a player join the game
        if player.uid in self.players:
            return {
                'requestValid': False,
                'note': 'Player has already joined the game.'
            }
        self.players[player.uid] = Player(player.uid, player.name)
        # place new player at the beginning of the list to make testing easier when debugging
        self.order.insert(0, player.uid)

    def change_teams(self, playerlist):
        """
        allow for the teams to be chosen by the players before the game has 
        started

        Parameters:

        player_ids (list): List of player_ids, players with index 0 and 2 play 
            together
        """
        if not (self.game_state < 2):  # assert the game is not yet running
            return {
                'requestValid': False,
                'note': 'game has already started, you can no longer switch teams'
            }
        for player in playerlist:  # assert the user ids in user are in the game
            if player.uid not in self.players:
                return {
                    'requestValid': False,
                    'note': f'Player {player.name} is not part of this game'
                }
        self.order = [player.uid for player in playerlist]
        return {
            'requestValid': True,
            'note': f'Teams modified successfully'
        }

    def start_game(self):
        """
        start the game:
            - check that all players are present
            - players are assigned their starting position based on self.order
            - first round is started
        """
        if not all([e is not None for e in self.order]):  # check that all players are present
            return {
                'requestValid': False,
                'note': 'Not all players are present.'
            }
        if not self.game_state == 0:
            return {
                'requestValid': False,
                'note': 'Game has already started.'
            }

        if not len(self.order) == PLAYER_COUNT:
            return {
                'requestValid': False,
                'note': 'Not all players are present.'
            }
        # create a new field instance for the game
        self.field = Field(self.order)  # field of players

        self.assign_starting_positions()

        self.start_round()
        return {
            'requestValid': True,
            'note': 'Game is started.'
        }

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
        if not self.round_state in [0, 5]:
            return {
                'requestValid': False,
                'note': 'The round has already started.'
            }
        self.game_state = 2
        self.round_state = 1
        self.deal_cards()
        self.round_turn += 1

        # reset the has folded attribute
        for uid in self.order:
            self.players[uid].has_folded = False

        return {
            'requestValid': True,
            'note': 'Round is started.'
        }

    def deal_cards(self):
        """
        deal the correct number of cards to all players depending on the current
        round turn
        """
        if not (self.game_state == 2 and self.round_state == 1):  # check that the game is in the correct state
            return {
                'requestValid': False,
                'note': f'The game is not in the correct state to deal cards.'
            }
        for uid in self.order:
            for _ in range(self.round_cards[self.round_turn % 5]):
                self.players[uid].set_card(self.deck.give_card())

        self.round_state = 2

    def swap_card(self, player, card):
        if not self.round_state == 2:
            return {
                'requestValid': False,
                'note': f'The round is not in the game swapping state.'
            }
        if not self.players[player.uid].may_swap_cards:
            return {
                'requestValid': False,
                'note': f'You have already swapped a card.'
            }
        team_member = self.order[(self.order.index(
            player.uid) + PLAYER_COUNT // 2) % PLAYER_COUNT]  # find the teammember

        swapped_card = self.players[player.uid].hand.play_card(card)
        self.players[team_member].hand.set_card(swapped_card)

        self.card_swap_count += 1

        # make sure the players only swap one card
        self.players[player.uid].may_swap_cards = False
        if self.card_swap_count % PLAYER_COUNT == 0:  # when all players have sent their card to swap

            self.round_state += 1

            # reset swapping ability for next round
            for uid in self.order:
                self.players[uid].may_swap_cards = True
            self.round_state += 1
            return {
                'requestValid': True,
                'taskFinished': True,
                'note': 'Cards have been swapped.'
            }
        return {
            'requestValid': True,
            'taskFinished': False,
            'note': 'Card has been swapped.'
        }

    def increment_active_player_index(self):
        """
        increment the active player index until a player is found who has not yet folded
        """
        skipped_player_count = 0
        # check for victory
        team_1_has_won = True
        team_2_has_won = True
        for i, player_uid in enumerate(self.order):
            if i % 2 == 0:
                team_1_has_won *= self.players[player_uid].has_finished_marbles()
            else:
                team_2_has_won *= self.players[player_uid].has_finished_marbles()

        if team_1_has_won:
            self.game_state = 3
            return {
                'requestValid': True,
                'note': f'Team 1 of players {self.players[self.order[0]].name} and {self.players[self.order[2]].name} have won.',
                'gameOver': True
            }
        if team_2_has_won:
            self.game_state = 3
            return {
                'requestValid': True,
                'note': f'Team 2 of players {self.players[self.order[1]].name} and {self.players[self.order[3]].name} have won.',
                'gameOver': True
            }

        self.active_player_index = (
            self.active_player_index + 1) % PLAYER_COUNT

        while self.players[self.order[self.active_player_index]].has_finished_cards():
            self.active_player_index = (
                self.active_player_index + 1) % PLAYER_COUNT
            # if all players have been skipped then the round has finished and a new round starts
            if skipped_player_count == PLAYER_COUNT:
                self.round_state = 5
                self.start_round()
                return {
                    'requestValid': True,
                    'note': f'Round #{self.round_turn} has started due to all players having no cards left.',
                    'new_round': True
                }

            skipped_player_count += 1

    """
    Game play events: 

    """

    def event_player_fold(self, player):
        """

        """

        # for self.check_card_marble_action
        # check whether the player can at this point play one of his cards and perform an action of those on one of his marbles
        '''
        can_play = True
        for card in self.players[player.uid].hand.cards.values():
            for possible_action in card.action_options:
                for marble in self.players[player.uid].marbles:
                    pass
        '''

        self.players[player.uid].fold()
        res = self.increment_active_player_index()
        if res is not None:
            return res
        return {
            'requestValid': True,
            'note': f'Player {player.name} has folded for this round.'
        }

    def event_move_marble(self, player, action):
        if self.round_state != 4:
            return {
                'requestValid': False,
                'note': f'You have to finish swapping cards first.'
            }
        if player.uid != self.order[self.active_player_index]:
            return {
                'requestValid': False,
                'note': f'It is not player {player.name}s turn.'
            }
        if action.card.uid not in self.players[player.uid].hand.cards:
            return {
                'requestValid': False,
                'note': 'You do not have this card.'
            }

        if action.action not in self.players[player.uid].hand.cards[action.card.uid].action_options:
            return {
                'requestValid': False,
                'note': 'Desired action does not match the card.'
            }

        if self.players[self.order[self.active_player_index]].steps_of_seven_remaining != -1:
            return {
                'requestValid': False,
                'note': f'Player {player.name} has to finish using his seven moves.'
            }

        marble = self.players[player.uid].marbles[action.mid]
        if self.players[player.uid].has_finished_marbles():
            team_member = self.order[(self.order.index(
                player.uid) + PLAYER_COUNT // 2) % PLAYER_COUNT]
            marble = self.players[team_member].marbles[action.mid]
        pnt = marble.curr

        #  get out of the start
        if action.action == 0:
            if pnt is not None:
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
                marble.blocking = True  # make the marble blocking other marbles

                self.increment_active_player_index()
                self.top_card = self.players[player.uid].hand.play_card(
                    action.card)
                return {
                    'requestValid': True,
                    'note': f'Marble {action.mid} moved to {marble.curr.position}.'
                }
        # normal actions
        elif action.action in [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13]:
            # try to move action.action nodes ahead

            # use pnt variable to check the path along the action of the marble i.e. whether it
            # is blocked or it may enter its goal
            if pnt is None:
                return {
                    'requestValid': False,
                    'note': 'In the starting position.'
                }

            flag_has_entered_home = False
            for i in range(action.action):

                # check whether pnt is looking at the own exit node and if it can enter
                if marble.can_enter_goal and pnt.get_entry_node() == player.uid:
                    flag_home_is_blocking = False
                    # make a copy of the pointer to check whether or not the home fields are blocking
                    pnt_copy = pnt.curr
                    pnt_copy.next = pnt_copy.exit
                    # check the remaining steps in goal for blockage
                    for _ in range(i, action.action):
                        pnt_copy = pnt_copy.next
                        flag_home_is_blocking = pnt_copy.is_blocking()

                    if flag_home_is_blocking is False:
                        pnt = pnt_copy
                        flag_has_entered_home = True
                    else:
                        pnt = pnt.next
                else:
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

            # performing any motion with a marble on the field removes the blocking capability
            # however entering the goals makes the marble blocking again
            marble.blocking = False + flag_has_entered_home
            marble.can_enter_goal = True
            marble.set_new_position(pnt)
            self.increment_active_player_index()
            self.top_card = self.players[player.uid].hand.play_card(
                action.card)

            return {
                'requestValid': True,
                'note': f'Marble {action.mid} moved to {marble.curr.position}.'
            }

        elif action.action == -4:  # go backwards 4
            # try to move action.action nodes ahead

            # use pnt variable to check the path along the action of the marble i.e. whether it
            # is blocked or it may enter its goal
            pnt = marble.curr
            for i in range(abs(action.action)):
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

            # performing any motion with a marble on the field removes the blocking capability
            # it also allows the marble to enter the goal
            marble.blocking = False
            marble.can_enter_goal = True

            # move the marble to the entry node
            marble.set_new_position(pnt)

            self.increment_active_player_index()
            self.top_card = self.players[player.uid].hand.play_card(
                action.card)

            return {
                'requestValid': True,
                'note': f'Marble {action.mid} moved to {marble.curr.position}.'
            }

        elif action.action == 'switch':
            if player.uid == action.pid_2:
                return {
                    'requestValid': False,
                    'note': f'You can not swap two of your own marbles.'
                }
            if action.mid_2 is None:
                return {
                    'requestValid': False,
                    'note': f'No marble to switch was selected.'
                }
            if action.pid_2 is None:  # make sure a playerid was submitted
                return {
                    'requestValid': False,
                    'note': f'No player to switch was selected.'
                }

            marble_1_node = self.players[player.uid].marbles[action.mid].curr
            marble_2_node = self.players[action.pid_2].marbles[action.mid_2].curr

            if marble_1_node.curr.is_blocking():
                return {
                    'requestValid': False,
                    'note': f'Marble {marble_1_node.mid} is blocking.'
                }
            if marble_2_node.curr.is_blocking():
                return {
                    'requestValid': False,
                    'note': f'Marble {marble_2_node.mid} is blocking.'
                }
            self.players[player.uid].marbles[action.mid].set_new_position(
                marble_2_node)
            self.players[action.pid_2].marbles[action.mid_2].set_new_position(
                marble_2_node)
            self.increment_active_player_index()
            self.top_card = self.players[player.uid].hand.play_card(
                action.card)

        elif action.action == 7:
            if pnt is None:
                return {
                    'requestValid': False,
                    'note': 'In the starting position.'
                }

            if self.players[player.uid].steps_of_seven_remaining == -1:
                """
                this is the first step of the seven the player is attempting to take. 
                we need to take a snapshot of the game, so that we can come back to it later
                if the player was to not be able to finish his moves
                """
                is_seven_playable = self.check_card_marble_action(
                    self.players[player.uid], 7, self.players[player.uid].marbles)
                if not is_seven_playable:
                    return {
                        'requestValid': False,
                        'note': 'The seven steps can not be fully executed.'
                    }

                self.players[player.uid].steps_of_seven_remaining = 7

            # check whether pnt is looking at the own exit node and if it can enter
            if marble.can_enter_goal and pnt.get_entry_node() == player.uid:
                flag_home_is_blocking = False
                # make a copy of the pointer to check whether or not the home fields are blocking
                pnt_copy = pnt.curr
                pnt_copy.next = pnt_copy.exit
                for _ in range(1):  # check the remaining steps in goal for blockage
                    pnt_copy = pnt_copy.next
                    flag_home_is_blocking = pnt_copy.is_blocking()

                if flag_home_is_blocking is False:
                    pnt = pnt_copy
                    flag_has_entered_home = True
                else:
                    pnt = pnt.next
            else:
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

            # performing any motion with a marble on the field removes the blocking capability
            # however entering the goals makes the marble blocking again
            marble.blocking = False + flag_has_entered_home
            marble.can_enter_goal = True
            marble.set_new_position(pnt)

            self.players[player.uid].steps_of_seven_remaining -= 1

            if self.players[player.uid].steps_of_seven_remaining == 1:
                self.increment_active_player_index()

                self.top_card = self.players[player.uid].hand.play_card(
                    action.card)
                self.players[player.uid].steps_of_seven_remaining = -1

            return {
                'requestValid': True,
                'note': f'Marble {action.mid} moved to {marble.curr.position}.'
            }

    """
    Event Assertions
    """
    '''
    TODO: 
    def check_player_can_move(self, player):
        cards = self.players[player.uid].hand.cards
        marbles = self.players[player.uid].marbles
    '''

    def check_card_marble_action(self, player, action, marble):
        """
        function to test if a marble can perform a certain action
        should be executed on a copy of marbles such that the marble positions are not
        overridden
        """
        if action == 0:
            pnt = marble.curr
            if pnt is not None:
                return False
            if pnt.next.is_blocking():
                return False
            return True
        elif action in [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13]:
            # check you are not in the starting position
            pnt = marble.curr
            if pnt is None:
                return False

            for _ in range(action.action):

                # check whether pnt is looking at the own exit node and if it can enter
                if marble.can_enter_goal and pnt.get_entry_node() == player.uid:
                    pnt = pnt.exit
                else:
                    pnt = pnt.next
                # check whether a marble is blocking along the way
                if pnt.is_blocking():
                    return False
            return True
        elif action == "switch":
            pnt = marble.curr
            if pnt is None:
                return False
            if pnt.is_blocking():
                return False
            if self.players[action.pid_2].marbles[action.mid_2].curr.is_blocking():
                return False
            if self.players[action.pid_2].marbles[action.mid_2].curr is None:
                return False
            return True
        elif action == 7:
            assert isinstance(marble, list)
            total_distance_to_blockade = 0
            for m in marble:  # for all the players marbles check how far they can be moved to the next blocking marble
                pnt = m.curr
                while not pnt.next.is_blocking():  # move until the current marble m is blocked
                    pnt = pnt.next
                    # count the steps the marble m can take without being blocked
                    total_distance_to_blockade += 1
            if total_distance_to_blockade < 7:
                return False
            return True

    """
    GAMESTATE:

    write and read the full game state as JSON
    """

    def get_cards(self, player):
        return self.players[player.uid].private_state()

    def public_state(self):
        return {
            'game_id': self.game_id,
            'game_name': self.game_name,
            'host': self.host.to_json(),
            'game_state': self.game_state,
            'round_state': self.round_state,
            'round_turn': self.round_turn,
            'order': self.order,
            'active_player_index': self.active_player_index,
            'players': {uid: self.players[uid].to_json() for uid in self.order},
            'top_card': self.top_card.to_json() if self.top_card is not None else None
        }

    def to_json(self):
        """
        Return game state as a JSON object

        """
        return {
            'game_id': self.game_id,
            'game_name': self.game_name,
            'host': self.host.to_json(),
            'game_state': self.game_state,
            'round_state': self.round_state,
            'round_turn': self.round_turn,
            'deck': self.deck.to_json(),
            'players': [player.to_json() for player in self.players],
            'order': self.order,
            'active_player_index': self.active_player_index,
            'top_card': self.top_card.to_json() if self.top_card is not None else None
        }

    def from_json(self, file):
        """
        Set game state from a JSON object

        """
        # state = json.load(file)
        pass
