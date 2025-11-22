import numpy as np

from utils import get_movements_4n, heuristic, Vertices, Vertex
from typing import Dict, List

from type import UNOCCUPIED, OBSTACLE
class OccupancyGridMap:
    def __init__(self, x_dim, y_dim):
        """
        set initial values for the map occupancy grid
        |----------> y, column
        |           (x=0,y=2)
        |
        V (x=2, y=0)
        x, row
        :param x_dim: dimension in the x direction
        :param y_dim: dimension in the y direction
        """
        self.x_dim = x_dim
        self.y_dim = y_dim

        # the map extents in units [m]
        self.map_extents = (x_dim, y_dim)

        # the obstacle map
        self.occupancy_grid_map = np.zeros(self.map_extents, dtype=np.uint8)

    def is_unoccupied(self, pos: (int, int)) -> bool:
        """
        :param pos: cell position we wish to check
        :return: True if cell is occupied with obstacle, False else
        """
        (x, y) = (round(pos[0]), round(pos[1]))  # make sure pos is int
        (row, col) = (x, y)

        # if not self.in_bounds(cell=(x, y)):
        #    raise IndexError("Map index out of bounds")

        return self.occupancy_grid_map[row][col] == UNOCCUPIED

    def in_bounds(self, cell: (int, int)) -> bool:
        """
        Checks if the provided coordinates are within
        the bounds of the grid map
        :param cell: cell position (x,y)
        :return: True if within bounds, False else
        """
        (x, y) = cell
        return 0 <= x < self.x_dim and 0 <= y < self.y_dim

    def filter(self, neighbors: List, avoid_obstacles: bool):
        """
        :param neighbors: list of potential neighbors before filtering
        :param avoid_obstacles: if True, filter out obstacle cells in the list
        :return:
        """
        if avoid_obstacles:
            return [node for node in neighbors if self.in_bounds(node) and self.is_unoccupied(node)]
        return [node for node in neighbors if self.in_bounds(node)]

    def succ(self, vertex: (int, int), avoid_obstacles: bool = False) -> list:
        """
        :param avoid_obstacles:
        :param vertex: vertex you want to find direct successors from
        :return:
        """
        (x, y) = vertex

        movements = get_movements_4n(x=x, y=y)

        # not needed. Just makes aesthetics to the path
        if (x + y) % 2 == 0: movements.reverse()

        filtered_movements = self.filter(neighbors=movements, avoid_obstacles=avoid_obstacles)
        return list(filtered_movements)

    def set_obstacle(self, pos: (int, int)):
        """
        :param pos: cell position we wish to set obstacle
        :return: None
        """
        (x, y) = (round(pos[0]), round(pos[1]))  # make sure pos is int
        (row, col) = (x, y)
        self.occupancy_grid_map[row, col] = OBSTACLE

    def remove_obstacle(self, pos: (int, int)):
        """
        :param pos: position of obstacle
        :return: None
        """
        (x, y) = (round(pos[0]), round(pos[1]))  # make sure pos is int
        (row, col) = (x, y)
        self.occupancy_grid_map[row, col] = UNOCCUPIED

    def local_observation(self, global_position: (int, int), view_range: int = 2) -> Dict:
        """
        :param global_position: position of robot in the global map frame
        :param view_range: how far ahead we should look
        :return: dictionary of new observations
        """
        (px, py) = global_position
        nodes = [(x, y) for x in range(px - view_range, px + view_range + 1)
                 for y in range(py - view_range, py + view_range + 1)
                 if self.in_bounds((x, y))]
        return {node: UNOCCUPIED if self.is_unoccupied(pos=node) else OBSTACLE for node in nodes}

    def copy(self):
        """
        Create a deep copy of the OccupancyGridMap instance
        :return: a deep copy of the OccupancyGridMap instance
        """
        new_map = OccupancyGridMap(self.x_dim, self.y_dim)
        new_map.occupancy_grid_map = np.copy(self.occupancy_grid_map)
        return new_map


class SLAM:
    def __init__(self, map: OccupancyGridMap, view_range: int):
        self.ground_truth_map = map
        self.slam_map = map.copy()
        self.view_range = view_range

    def set_ground_truth_map(self, gt_map: OccupancyGridMap):
        self.ground_truth_map = gt_map

    def c(self, u: (int, int), v: (int, int)) -> float:
        """
        calcuclate the cost between nodes
        :param u: from vertex
        :param v: to vertex
        :return: euclidean distance to traverse. inf if obstacle in path
        """
        if not self.slam_map.is_unoccupied(u) or not self.slam_map.is_unoccupied(v):
            return float('inf')
        else:
            return heuristic(u, v)

