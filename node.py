"""Pathfinding algorithm Node"""

class Node:
    """A Node"""

    DIJKSTRA : str    = "Dijkstra's Pathfinding Algorithm"
    GREEDY_BFS : str  = "Greedy Best-First Search Algorithm"
    A_STAR : str      = "A* Pathfinding Algorithm"

    EUCLIDEAN : str   = "Euclidean Distance"
    MANHATTAN : str   = "Manhattan Distance"
    TCHEBYCHEV : str  = "Tchebychev distance"

    distance : str    = MANHATTAN
    end : tuple       = tuple()
    mode : str        = A_STAR

    def __init__(self, positon:tuple[int, int], parent=None) -> None:
        if not Node.end:
            raise ValueError("No end point")
        self.x_pos, self.y_pos = positon
        self.h_cost =  0 if Node.mode == Node.DIJKSTRA else self.calc_h_cost()
        self.set_parent(parent)

    def set_parent(self, parent) -> None:
        """Set a parent for the node"""
        self.parent = parent
        if parent is not None and Node.mode != Node.GREEDY_BFS:
            if bool(self.parent.x_pos - self.x_pos) != bool(self.parent.y_pos - self.y_pos):
                self.g_cost = 1 + self.parent.g_cost
            elif Node.distance == Node.EUCLIDEAN:
                self.g_cost = 1.4 + self.parent.g_cost
            elif Node.distance == Node.TCHEBYCHEV:
                self.g_cost = 1 + self.parent.g_cost
        else: self.g_cost = 0
        self.cost = self.h_cost + self.g_cost

    def calc_h_cost(self) -> float:
        """Calculate the h cost of the node"""
        xdiff, ydiff = abs(self.x_pos - Node.end[0]), abs(self.y_pos - Node.end[1])
        if Node.distance == Node.EUCLIDEAN:
            xydiff = abs(xdiff - ydiff)
            max_ = xdiff if xdiff > ydiff else ydiff
            diagonal = max_ - xydiff
            return xydiff + diagonal*1.4
        if Node.distance == Node.TCHEBYCHEV:
            return xdiff if xdiff > ydiff else ydiff
        return xdiff + ydiff

    def neighbors(self):
        """A generator function that yields all the neighbouring nodes"""
        for x_pos in [-1, 0, 1]:
            for y_pos in [-1, 0, 1]:
                if Node.distance == Node.EUCLIDEAN or Node.distance == Node.TCHEBYCHEV:
                    if (x_pos, y_pos) == (0, 0):
                        continue
                    yield Node((self.x_pos + x_pos, self.y_pos + y_pos), self)
                elif bool(x_pos) != bool(y_pos):
                    yield Node((self.x_pos + x_pos, self.y_pos + y_pos), self)

    def f_cost(self, parent) -> int:
        """Return the f_cost if the parent of the node would be the passed node"""
        if bool(parent.x_pos - self.x_pos) != bool(parent.y_pos - self.y_pos):
            return 1 + parent.g_cost + self.h_cost
        if Node.distance == Node.EUCLIDEAN:
            return 1.4 + parent.g_cost + self.h_cost
        if Node.distance == Node.TCHEBYCHEV:
            return 1 + parent.g_cost + self.h_cost
        return 0

    def __eq__(self, other) -> bool:
        if isinstance(other, Node):
            return self.x_pos == other.x_pos and self.y_pos == other.y_pos
        if isinstance(other, (tuple, list)):
            return self.x_pos == other[0] and self.y_pos == other[1]
        return None

    @staticmethod
    def get_min(seq:list, max_=False):
        """Returns the node with the minimum/maximum cost"""
        var = -1 if max_ else 1
        smallest = seq[0]
        for node in seq[1:]:
            if var*node.cost < var*smallest.cost:
                smallest = node
            elif node.cost == smallest.cost:
                if var*node.h_cost < var*smallest.h_cost:
                    smallest = node
        return smallest

    def __repr__(self) -> str:
        return f"{self.cost:.2f}-({self.x_pos},{self.y_pos})"

    @staticmethod
    def path_cost(path) -> float:
        """Returns the total cost of the path"""
        if Node.mode != Node.GREEDY_BFS:
            return path[0].cost
        cost = 0
        for num, node in enumerate(path[1:]):
            if bool(path[num-1].x_pos - node.x_pos) != bool(path[num-1].y_pos - node.y_pos):
                cost += 1
            else: cost += 1.4
        return cost
