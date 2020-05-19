
class Marble():
    """
    Marble Object


    """

    def __init__(self, color, mid, starting_node):
        self.prev = None
        self.curr = None  # start in the starting area
        self.next = starting_node

        # store the starting position separately for a reset
        self.starting_position = starting_node
        colors = ['red', 'yellow', 'green', 'blue']
        self.color = colors[mid//4]
        self.mid = mid  # marble
        self.blocking = False
        self.can_enter_goal = False

    def reset_to_starting_position(self):
        self.curr.unset_marble()

        self.prev = None
        self.curr = None
        self.next = self.starting_position

        self.blocking = False
        self.can_enter_goal = False

    def set_new_position(self, node):
        # remove the marble from the previous position
        if self.curr is not None:
            self.curr.unset_marble()

        self.curr = node.curr
        self.prev = node.prev
        self.next = node.next

        node.marble = self

    def to_json(self):
        if self.curr is None:  # at start
            position = -self.mid - 1
        else:
            position = self.curr.position

        return {
            'mid': self.mid,
            'position': position,
            'color': self.color
        }
