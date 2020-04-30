
class Card():
    """
    Card object. Each card has a value, a color and a list of possible actions

    action_options values can be the following:
        0: get started
        2: move up 2
        3: move up 3
        4: move up 4
        -4: move 4 back
        5: move up 5
        6: move up 6
        7: move up 7 times 1
        8: move up 8
        9: move up 9
        10: move up 10
        switch: switch marble position with opponents marble

    """
    def __init__(self, value, color, uid):
        self.value = value
        self.color = color
        self.uid = uid
        
        if self.value == 'A':
            self.action_options = [0, 1, 11]
        if self.value == 'K':
            self.action_options = [0, 13]
        if self.value == 'Q':
            self.action_options = [12]
        if self.value == 'Ja':
            self.action_options = ['switch']
        if self.value == '10':
            self.action_options = [10]
        if self.value == '9':
            self.action_options = [9]
        if self.value == '8':
            self.action_options = [8]
        if self.value == '7':
            self.action_options = [7]
        if self.value == '6':
            self.action_options = [6]
        if self.value == '5':
            self.action_options = [5]
        if self.value == '4':
            self.action_options = [-4, 4]
        if self.value == '3':
            self.action_options = [3]
        if self.value == '2':
            self.action_options = [2]

        

            