from app.game_logic.hand import Hand
from app.game_logic.marble import Marble


class Player():
    """
    Player object instance handling the Player

    Player.name stores the Player name
    Player.ready stores whether the player is ready
    Player.hand is an instance of the Players Hand
    """

    def __init__(self, uid,  name, color=None):
        self.uid = uid
        self.name = name
        self.color = color
        self.hand = Hand()

        #
        self.goal = [0] * 4
        self.marbles = {}

        # keep track of actions
        self.may_swap_cards = True
        self.has_folded = False
        self.steps_of_seven_remaining = -1

    def set_color(self, color):
        self.color = color

    def set_starting_position(self, field, ind):
        """
        set the players starting position
        """
        self.starting_node = field.get_starting_node(self)
        self.marbles = {mid: Marble(self.color, mid, self.starting_node) for mid in range(
            ind * 4, 4 * ind + 4)}  # mid: marble id

    def set_card(self, card):
        """
        add a card to the players hand
        """
        self.hand.set_card(card)

    def fold(self):
        self.hand.fold()
        self.has_folded = True

    def has_finished_cards(self):
        return self.has_folded or self.hand.cards == {}

    def has_finished_marbles(self):
        if any(marble.curr == None for marble in self.marbles.values()): return False
        return sum([marble.curr.position for marble in self.marbles.values()]) > 4000

    """
    Player State


    """

    def private_state(self):
        return {
            'uid': self.uid,
            'name': self.name,
            'hand': self.hand.to_json(),
            'marbles': [marble.to_json() for marble in self.marbles.values()],
            'steps_of_seven': self.steps_of_seven_remaining
        }

    def to_json(self):
        return {
            'uid': self.uid,
            'name': self.name,
            'marbles': [marble.to_json() for marble in self.marbles.values()]
        }
