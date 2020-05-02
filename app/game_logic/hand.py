class Hand():
    def __init__(self):
        self.cards = {}

    def play_card(self, uid):
        return self.cards.pop(uid)
        
    def set_card(self, card):
        assert card.uid not in self.cards
        self.cards[card.uid] = card