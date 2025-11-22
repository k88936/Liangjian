import functools
import math
import time
from typing import List

from type import Index


class Vertex:
    def __init__(self, pos: (int, int)):
        self.pos = pos
        self.edges_and_costs = {}

    def add_edge_with_cost(self, succ: (int, int), cost: float):
        if succ != self.pos:
            self.edges_and_costs[succ] = cost

    @property
    def edges_and_c_old(self):
        return self.edges_and_costs


class Vertices:
    def __init__(self):
        self.list = []

    def add_vertex(self, v: Vertex):
        self.list.append(v)

    @property
    def vertices(self):
        return self.list
    def isEmpty(self):
        return len(self.list) == 0


def heuristic(p: (int, int), q: (int, int)) -> float:
    """
    Helper function to compute distance between two points.
    :param p: (x,y)
    :param q: (x,y)
    :return: manhattan distance
    """
    # return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)
    return  math.fabs(p[0] - q[0]) + math.fabs(p[1] - q[1])


def get_movements(x: int, y: int) -> List:
    """
    get all possible 4-connectivity movements.
    :return: list of movements with cost [(dx, dy, movement_cost)]
    """
    return [(x + 1, y + 0),
            (x + 0, y + 1),
            (x - 1, y + 0),
            (x + 0, y - 1)]


def diff2dir(src: Index, dist: Index) -> int:
    (dx, dy) = (dist[0] - src[0], dist[1] - src[1])
    if dx > 0 and dy == 0: return 4
    if dx < 0 and dy == 0: return 2
    if dy > 0 and dx == 0: return 3
    if dy < 0 and dx == 0: return 1
    return 0


def dir2diff(direction: int) -> Index:
    if direction == 1: return 0, -1
    if direction == 2: return -1, 0
    if direction == 3: return 0, 1
    if direction == 4: return 1, 0
    return 0, 0


def timing(func):
    """
    A decorator that measures the execution time of a function and prints it.

    Usage:
    @timing_decorator
    def my_function():
        # some code
        pass
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"{func.__name__} executed in {execution_time:.6f}s")
        return result

    return wrapper
