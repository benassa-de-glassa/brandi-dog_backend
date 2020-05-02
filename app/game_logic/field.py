NODES_BETWEEN_PLAYERS = 16

class Node(object):
    def __init__(self):
        self.next = None
        self.prev = None
    
class GameNode(Node):
    def __init__(self, position):
        self.position = None
        self.marble = None

    def set_marble(self, marble):
        self.marble = marble

    def unset_marble(self):
        self.marble = None

    def is_blocking(self):
        """
        
        A game node cannot be blocking 
        This is a convinience function
        """
        return False 
    def has_marble(self):
        return self.marble is not None

class EntryExitNode(GameNode):
    def __init__(self, uid, position):
        super().__init__(self, position)

        self.entry_exit_for_player = uid
        self.exit = [None, None, None ,None]
        

    def is_blocking(self):
        """
        returns true if a marble is placed in this node and the marble is blocking
        returns false else

        """
        if self.marble is not None:
            return self.marble.blocking
        
        return False



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
            new_entry_node.entry_exit_for_player = players[i]
            self.entry_nodes[players[i]] = new_entry_node
            nodes.append(new_entry_node)
            

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
