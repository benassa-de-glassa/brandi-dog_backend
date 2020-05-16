NODES_BETWEEN_PLAYERS = 16

class Node(object):
    def __init__(self):
        self.next = None
        self.prev = None
        self.curr = self
    
class GameNode(Node):
    def __init__(self, position, marble=None):
        super().__init__()
        self.position = position
        self.marble = marble
    # def __copy__(self):
    #     return type(self)(position, Marble)

    def set_marble(self, marble):
        self.marble = marble

    def unset_marble(self):
        self.marble = None

    def is_blocking(self):
        """
        A game node cannot be blocking 
        This is a convinience function
        """
        if self.marble is not None:
            return self.marble.blocking
        return False

    def has_marble(self):
        return self.marble is not None

    def get_entry_node(self):
        """
        A game node cannot be an entry node
        This is placed here for convience, such that
        both the GameNode Class and the EntryExitNode 
        class inherit the same
        """
        return False

class EntryExitNode(GameNode):
    def __init__(self, uid, position, marble=None, exit = None):
        super().__init__(position)

        self.entry_exit_for_player = uid
        self.exit = None
    
    def get_entry_node(self):
        return self.entry_exit_for_player



class Field():
    """
    Field is a doubly linked list with additional entry nodes at the players starting postions
    """
    def __init__(self, players: list):
        """
        
        players: list of player uids
        """    
        self.entry_nodes = {} # store the entry nodes for each of the players
        
        nodes = []


        for i in range(len(players)): # range(4)
            new_entry_node = EntryExitNode(players[i], len(nodes))

            self.entry_nodes[players[i]] = new_entry_node
            nodes.append(new_entry_node)

            exit_nodes = []
            for j in range(4):
                new_node = GameNode(1000 + 10 * i + j) # goal nodes are designated by a position larger then 1000
                exit_nodes.append(new_node)

            new_entry_node.exit = exit_nodes[0]
            for j in range(3):
                exit_nodes[j].next = exit_nodes[j+1]
                exit_nodes[j].prev = exit_nodes[j+1] # both directions point to the next, so that one can easily enter with a -4 but not exit

            for _ in range(NODES_BETWEEN_PLAYERS - 1):
                new_node = GameNode(len(nodes))
                nodes.append(new_node)
            
        # connect the nodes
        for index in range(len(nodes)):
            nodes[index].next = nodes[(index + 1 ) % len(nodes)]
            nodes[index].prev = nodes[(index - 1 ) % len(nodes)]

        self.game_start_node = nodes[0]
        
    def get_starting_node(self, player):
        return self.entry_nodes[player.uid]
