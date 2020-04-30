from .hand import Hand
from .marble import Marble

class Player():
    """
    Player object instance handling the Player
    
    Player.name stores the Player name
    Player.ready stores whether the player is ready
    Player.hand is an instance of the Players Hand
    """

    def __init__(self, name, color=None):
        self.name = name # 
        self.color = color
        self.ready = False # is the player ready to get the game started
        self.hand = Hand()
        
        # 
        self.start = [Marble(self.color ) for _ in range(4)]
        self.goal = [0] * 4

    def set_color(self, color):
        self.color = color
    
    def set_starting_position(self, pos):
        """
        set the players starting position
        """
        self.starting_position = pos * 16
    
    def set_card(self, card):
        """
        add a card to the players hand
        """
        self.hand.set_card(card)

    
    def choose_action(self, card_id):
        """
        return a list of available options given a card
        """
        return self.hand.cards[card_id].action_options

    """
    Player State


    """
    def to_json(self):
        pass