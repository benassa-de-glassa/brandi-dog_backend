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
        self.name = name # 
        self.color = color
        self.ready = False # is the player ready to get the game started
        self.hand = Hand()
        
        # 
        self.goal = [0] * 4
        self.marbles = {}

    def set_color(self, color):
        self.color = color
    
    def set_ready(self):
        self.ready = True
    
    def set_starting_position(self, field):
        """
        set the players starting position
        """
        self.starting_node = field.get_starting_node(self)
        self.marbles = {mid: Marble(self.color, self.uid, self.starting_node ) for mid in range(4)} # mid: marble id
    
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
        return {
            'uid': self.uid,
            'name': self.name,
            'ready': self.ready,
            'marbles': [marble.to_json(mid) for mid, marble in self.marbles.items()] 
        }