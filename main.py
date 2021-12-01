from grid import Grid

# Only 1 possible path(maze) or fastest solution -> Greedy BFS
# Optimal Solution but slow -> Dijkstra
# Mostly optimal and fast -> A*

g = Grid("goal.json")
# g = Grid("maze.png", scale_down=3)
# g = Grid("map.json")
# x = g.__dict__.copy()
# del x["grid"]
# print(x)
g.run(distance=Grid.EUCLIDEAN, mode=Grid.A_STAR)
