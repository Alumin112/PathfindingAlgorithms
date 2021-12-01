from time import sleep, time
import threading
import json
from numpy import asarray
import pygame
from PIL import Image
from node import Node


class Grid:
    """The Grid Window

    Args:
        source (tuple[int, int]|str): width and height of the window (number of cells) or a map
        scale_down (int, optional): Scale down of the map. Defaults to 1.
        cell (tuple[int, int, int], optional): dimensions of a cell. Defaults to (10, 10, 0).

    Raises:
        ValueError: when wrong format for a source map is passed
    """

    BLACK : tuple     = (0, 0, 0)
    WHITE : tuple     = (255, 255, 255)
    GREEN : tuple     = (0, 255, 0)
    RED : tuple       = (255, 0, 0)
    BLUE : tuple      = (0, 0, 255)
    PINK : tuple      = (255, 0, 255)
    YELLOW : tuple    = (255, 255, 0)
    ORANGE : tuple    = (255,165,0)
    TURQUOISE : tuple  = (48,213,200)

    MARGIN_COLOR : tuple|str          = BLACK
    PATH_COLOR : tuple|str            = WHITE
    CURRENT_NODE_COLOR : tuple|str    = YELLOW
    OBSTACLE_COLOR : tuple|str        = BLACK
    START_NODE_COLOR : tuple|str      = ORANGE
    END_NODE_COLOR : tuple|str        = TURQUOISE
    SOLVED_PATH_COLOR : tuple|str     = BLUE
    DISCOVERED_NODE_COLOR : tuple|str = GREEN
    EXPLORED_NODE_COLOR : tuple|str   = RED

    DIJKSTRA : str    = "Dijkstra's Pathfinding Algorithm"
    GREEDY_BFS : str  = "Greedy Best-First Search Algorithm"
    A_STAR : str      = "A* Pathfinding Algorithm"
    EUCLIDEAN : str   = "Euclidean Distance"
    MANHATTAN : str   = "Manhattan Distance"
    TCHEBYCHEV : str  = "Tchebychev distance"


    def __init__(self, source:tuple[int, int]|str, scale_down:int=1,
                cell:tuple[int, int, int]=(10, 10, 0)) -> None:
        if isinstance(source, (tuple, list)):
            self.width = source[0]
            self.height = source[1]
            self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        elif source.endswith(".json"):
            self.__dict__ = self.load(source)
        elif source.endswith(".jpeg") or source[-4:] in (".png", ".jpg"):
            with Image.open(source) as im:
                pix_val = asarray(im).tolist()
                self.width, self.height = im.size
            self.make_grid(pix_val, scale_down)
            self.width //= scale_down
            self.height //= scale_down
        else:
            raise ValueError("Wrong format")

        self.cell = self.cell if hasattr(self, 'cell') else cell
        self.start = self.start if hasattr(self, 'start') else tuple()
        self.end = self.end if hasattr(self, 'end') else tuple()
        if not hasattr(self, 'window_size'):
            self.window_size = [(self.cell[0]+self.cell[2]) * self.height,
                                (self.cell[0]+self.cell[2]) * self.width]

    def make_grid(self, pix_val:list[list[list[int]]], scale_down:int) -> None:
        """Makes the grid

        Args:
            pix_val (list[list[list[int]]]): pixel values of the image
            scale_down (int): scale-down of the image
        """
        self.grid = []
        for row, i in zip(range(self.width), range(0, self.width, scale_down)):
            self.grid.append([])
            for col in range(0, self.height, scale_down):
                px = tuple(pix_val[col][i][:3])
                if px == Grid.PATH_COLOR:
                    self.grid[row].append(0)
                elif px == Grid.OBSTACLE_COLOR:
                    self.grid[row].append(2)
                elif px in (Grid.START_NODE_COLOR, 1):
                    self.start = (row, col)
                    self.grid[row].append(1)
                elif px in (Grid.END_NODE_COLOR, 3):
                    self.end = (row, col)
                    self.grid[row].append(3)
                else:
                    self.grid[row].append(px)

    def run(self, mode:str|None=None, distance:str|None=None, **kwargs) -> None:
        self.running = False
        self.update = None
        self.kwargs = self.kwargs if "kwargs" in self.__dict__ else kwargs
        self.draw_ = self.kwargs.get("draw") if self.kwargs.get("draw") is not None else self.draw_ if hasattr(self, 'draw_') else True
        self.delay = self.kwargs.get("delay") if self.kwargs.get("draw") is not None else self.delay if hasattr(self, 'delay') else 0
        self.after_delay = self.kwargs.get("after_delay") if self.kwargs.get("after_delay") is not None else self.after_delay if hasattr(self, 'after_delay') else 3
        Node.mode = mode if mode is not None else Grid.A_STAR
        Node.distance = distance if distance is not None else Grid.MANHATTAN
        self.current = self.kwargs.get("current") if self.kwargs.get("current") is not None else self.current if hasattr(self, 'current') else False
        self.max = self.kwargs.get("max") if self.kwargs.get("max") is not None else self.max if hasattr(self, 'max') else False
        if self.kwargs.get("start") is not None:
            if self.start: self.grid[self.start[0]][self.start[1]] = 0
            self.start = self.kwargs.get("start")
            self.grid[self.start[0]][self.start[1]] = 1
            del self.kwargs["start"]
        if self.kwargs.get("end") is not None:
            if self.end: self.grid[self.end[0]][self.end[1]] = 0
            self.end = self.kwargs.get("end")
            self.grid[self.end[0]][self.end[1]] = 3
            del self.kwargs["end"]

        pygame.init()
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption(f"{Node.mode} - {Node.distance}")
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.running:
                        thread = threading.Thread(target=self.pathfind)
                        thread.start()
                        self.running = True
                    elif event.key == pygame.K_k:
                        self.save()
                    elif event.key == pygame.K_s:
                        pos = pygame.mouse.get_pos()
                        column = pos[0] // (self.cell[0] + self.cell[2])
                        row = pos[1] // (self.cell[1] + self.cell[2])
                        if self.start:
                            self.grid[self.start[0]][self.start[1]] = 0
                            if self.grid[self.start[0]][self.start[1]] == 3:
                                self.end = tuple()
                        self.start = (row, column)
                        self.grid[self.start[0]][self.start[1]] = 1
                    elif event.key == pygame.K_e:
                        pos = pygame.mouse.get_pos()
                        column = pos[0] // (self.cell[0] + self.cell[2])
                        row = pos[1] // (self.cell[1] + self.cell[2])
                        if self.end:
                            self.grid[self.end[0]][self.end[1]] = 0
                            if self.grid[self.start[0]][self.start[1]] == 1:
                                self.start = tuple()
                        self.end = (row, column)
                        self.grid[self.end[0]][self.end[1]] = 3

                buttons =  pygame.mouse.get_pressed()
                if any(buttons):
                    pos = pygame.mouse.get_pos()
                    column = pos[0] // (self.cell[0] + self.cell[2])
                    row = pos[1] // (self.cell[1] + self.cell[2])
                    if buttons[2]:
                        if self.grid[row][column] == 2:
                            self.grid[row][column] = 0
                            self.update=(row, column)
                    elif buttons[0]:
                        if self.grid[row][column] == 1: self.start = tuple()
                        elif self.grid[row][column] == 3: self.end = tuple()
                        self.grid[row][column] = 2
                    elif buttons[1]:
                        self.grid = [[0 for _ in range(self.height)] for _ in range(self.width)]
                        self.grid[self.start[0]][self.start[1]] = 1
                        self.grid[self.end[0]][self.end[1]] = 3
                        self.update = (row, column)

            if not self.running: self.draw()
            clock.tick(z if (z:=self.kwargs.get("fps")) else 60)

    def draw(self, blue:list[Node]|None=None, green:list[Node]|None=None,
            red:list[Node]|Node=None, current:Node|None=None) -> None:
        """Draws the stuff on the screen

        Args:
            blue (list[Node], optional): nodes in blue color. Defaults to None.
            green (list[Node], optional): nodes in green color. Defaults to None.
            red (list[Node], optional): nodes in red color. Defaults to None.
            current (Node, optional): current node. Defaults to None.
        """
        self.screen.fill(Grid.MARGIN_COLOR)

        for row in range(self.width):
            for column in range(self.height):
                color = Grid.PATH_COLOR

                if self.draw_:
                    if red:
                        for i in red:
                            if row == i.x_pos and column == i.y_pos:
                                color = Grid.EXPLORED_NODE_COLOR
                                break
                    if green:
                        for i in green:
                            if row == i.x_pos and column == i.y_pos:
                                color = Grid.DISCOVERED_NODE_COLOR
                                break
                if blue:
                    for i in blue:
                        if row == i.x_pos and column == i.y_pos:
                            color = Grid.SOLVED_PATH_COLOR
                            break

                if self.grid[row][column] == 1:
                    color = Grid.START_NODE_COLOR
                elif self.grid[row][column] == 2:
                    color = Grid.OBSTACLE_COLOR
                elif self.grid[row][column] == 3:
                    color = Grid.END_NODE_COLOR
                elif isinstance(self.grid[row][column], tuple):
                    color = self.grid[row][column]
                elif current and row == current.x_pos and column == current.y_pos:
                    color = Grid.CURRENT_NODE_COLOR
                pygame.draw.rect(self.screen, color, 
                                [(self.cell[2] + self.cell[0]) * column + self.cell[2],
                                (self.cell[2] + self.cell[1]) * row + self.cell[2],
                                self.cell[0], self.cell[1]])
        pygame.display.update()

    def pathfind(self) -> None:
        if not (self.start and self.end):
            pygame.display.set_caption("Not enough points")
            sleep(z if (z:=self.kwargs.get("after_delay")) else 3)
            pygame.display.set_caption(f"{Node.mode} - {Node.distance}")
            self.running = False
            return

        start_time = time()
        pygame.display.set_caption("Finding a path...")
        Node.end = self.end
        discovered = [Node(self.start)]
        explored = []
        current = None

        while True:
            if self.kwargs.get("draw"):
                if self.kwargs.get("current"):
                    pygame.display.set_caption(f"Current Node: {current.cost if current else None}")
                    self.draw(green=discovered, red=explored, current=current)
                else:
                    self.draw(green=discovered, red=explored)
            if self.kwargs.get("delay") and self.kwargs.get("delay") > 0:
                sleep(self.kwargs.get("delay"))

            if not discovered or not self.end or current == self.end: break
            current = Node.get_min(discovered, self.max)
            discovered.remove(current)
            explored.append(current)

            if self.update is not None:
                n = Node(self.update)
                for neighbour in n.neighbors():
                    if neighbour not in explored: continue
                    if n.f_cost(neighbour) > n.cost:
                        n.set_parent(neighbour)
                if n.parent: discovered.append(n)
                else: del n
                self.update = None

            for neighbour in current.neighbors():
                if neighbour in explored: continue
                if not (0 <= neighbour.x_pos < self.width and 0 <= neighbour.y_pos < self.height):
                    continue
                if self.grid[neighbour.x_pos][neighbour.y_pos] == 2: continue
                if isinstance(self.grid[neighbour.x_pos][neighbour.y_pos], tuple): continue

                if neighbour.f_cost(current) < neighbour.cost or neighbour not in discovered:
                    neighbour.set_parent(current)
                    if neighbour not in discovered: discovered.append(neighbour)

        solved = []
        if current == self.end:
            while current:
                solved.append(current)
                current = current.parent
            pygame.display.set_caption(f"Path found! - {Node.path_cost(solved):.2f} blocks in {time()-start_time :.2f} seconds")
        else: pygame.display.set_caption("No Path Found")
        if not self.draw_:
            explored, discovered = 0, 0
        self.draw(solved, discovered, explored)
        sleep(z if (z:=self.kwargs.get("after_delay")) else 3)
        pygame.display.set_caption(f"{Node.mode} - {Node.distance}")
        self.running=False

    def save(self) -> None:
        """Saves the map
        """
        # Image.fromarray(array(pxls, uint8)).save("save.png")
        x = self.__dict__.copy()
        del x["screen"]
        file = self.kwargs.get("save") or "map.json"
        with open(file, "w") as f:
            json.dump(x, f, indent=4)

    def load(self, map_:str) -> None:
        """[summary]

        Args:
            map_ (str): name of the file in which the map is stored

        Raises:
            FileNotFoundError: If the file to load from is not found
        """
        try:
            with open(map_) as f:
                return json.load(f)
        except (FileNotFoundError) as e:
            with open(map, "w"): pass
            raise e
