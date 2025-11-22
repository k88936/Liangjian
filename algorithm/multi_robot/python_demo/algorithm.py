#! /usr/bin/env python
# -*- coding: utf-8 -*-

import functools
import time
from dataclasses import dataclass
from typing import List

import numpy as np

from d_star_lite import DStarLite
from grid import OccupancyGridMap
from type import Index, Request, AlgorithmResult, RobotAction, MapCell, Robot
from type import OBSTACLE, UNOCCUPIED

STRAIGHT_BONUS = 3
np.set_printoptions(precision=2, suppress=True, linewidth=1000)


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


@dataclass
class RobotState:
    inner: Robot
    targets: List[int]


class Dfs:
    mapWidth: int
    mapHeight: int

    isRobotLoaded: bool

    @timing
    def run(self, request: Request) -> AlgorithmResult:

        if request.isInit:
            self.isRobotLoaded = False
            self.init(request)
            return AlgorithmResult([])
        if not self.isRobotLoaded:
            self.isRobotLoaded = True
            self.init_robots(request)

        self.load_robot_overlay_cost(request)

        actions = []
        for rbt in request.robots:
            p = rbt.assignedPath[-1].index
            last_dir = 0
            if rbt.assignedPath.__len__() > 1:
                last_dir = diff2dir(rbt.assignedPath[-2].index, rbt.assignedPath[-1].index)

            direction = self.getNextDirection(p, rbt.destIndex, last_dir)
            if direction == 0:
                break
            diff = dir2diff(direction)
            apd = (p[0] + diff[0], p[1] + diff[1])
            path = [self.index2cell(p), self.index2cell(apd)]
            ttt = RobotAction(rbt.robotId, path)
            actions.append(ttt)

            break
        result = AlgorithmResult(actions)

        return result

    robotOverlayCostMatrix: np.ndarray
    @timing
    def load_robot_overlay_cost(self, request: Request):
        self.robotOverlayCostMatrix = np.zeros((request.width, request.height), dtype=int)
        for robot in request.robots:
            # current cell is already in assignedPath
            (cx, cy) = robot.locationIndex
            self.robotOverlayCostMatrix[cx, cy] = OBSTACLE
            for cell in robot.assignedPath[1:]:
                (ix, iy) = cell.index
                self.robotOverlayCostMatrix[ix, iy] = OBSTACLE

    robotStates: List[RobotState] = []
    @timing
    def init_robots(self, request: Request):
        for robot in request.robots:
            pathfinder=DStarLite(self.structureCostMatrix,robot.position,robot.destIndex)
            state = RobotState(robot, [] , )
            self.robotStates.append(state)

    @timing
    def init(self, request: Request):
        self.mapWidth = request.width
        self.mapHeight = request.height

        self.build_map(request)

    def index2cell(self, index: Index):
        return self.id2cell[self.index2id(index)]

    structureCostMatrix: OccupancyGridMap
    id2cell: List[MapCell] = None
    @timing
    def build_map(self, request: Request):
        self.structureCostMatrix = OccupancyGridMap(self.mapWidth, self.mapHeight)
        for cell in request.mapCells:
            (ix, iy) = cell.index
            cost = OBSTACLE if cell.cellType == 'BLOCKED_CELL' else UNOCCUPIED
            self.structureCostMatrix.set_obstacle(cost)

        self.id2cell = [None for _ in range(self.mapWidth * self.mapHeight)]  # type: ignore
        for cell in request.mapCells:
            self.id2cell[self.index2id(cell.index)] = cell

        self.build_APSP()

    APSP_costMatrix: np.ndarray = None  # cost of move from (x1,y1) to (x2,y2)

    # Convert 2D coordinates to 1D indices
    def index2id(self, index: Index):
        (x, y) = index
        return x * self.mapHeight + y

    def id2index(self, di: int) -> Index:
        return di // self.mapHeight, di % self.mapHeight

    @timing
    def build_APSP(self):
        if self.structureCostMatrix is None:
            raise Exception('structureCostMatrix is None')
        if self.id2cell is None:
            raise Exception('index2cell is None')

        # Flatten indices for easier matrix operations
        n = self.mapWidth * self.mapHeight

        # Initialize cost matrix (n x n) and direction matrix (n x n)
        self.APSP_costMatrix = np.full((n, n), np.inf, dtype=np.float32)

        # Create a flattened view of the structure cost matrix
        flat_structure = self.structureCostMatrix.flatten()

        # Run BFS from each node
        for sx in range(self.mapWidth):
            for sy in range(self.mapHeight):
                start_idx = self.index2id((sx, sy))

                # Skip blocked starting cells
                if flat_structure[start_idx] == OBSTACLE:
                    continue

                # Initialize BFS
                queue = [(sx, sy, 0)]  # (x, y, cost, first_direction)
                visited = np.zeros((self.mapWidth, self.mapHeight), dtype=bool)
                visited[sx, sy] = True

                # Set distance to self as 0
                self.APSP_costMatrix[start_idx, start_idx] = 0

                # BFS loop
                while queue:
                    x, y, cost = queue.pop(0)
                    current_idx = self.index2id((x, y))

                    # Check 4-directional neighbors
                    for direction in range(1, 5):
                        dx, dy = dir2diff(direction)
                        nx, ny = x + dx, y + dy

                        # Check bounds
                        if 0 <= nx < self.mapWidth and 0 <= ny < self.mapHeight:
                            # Check if already visited
                            if visited[nx, ny]:
                                continue

                            neighbor_idx = self.index2id((nx, ny))

                            # Check if neighbor is passable
                            if flat_structure[neighbor_idx] != OBSTACLE:
                                # Mark as visited
                                visited[nx, ny] = True

                                # Calculate new cost
                                new_cost = cost + flat_structure[neighbor_idx]

                                # Update if this is a better path
                                if new_cost < self.APSP_costMatrix[start_idx, neighbor_idx]:
                                    self.APSP_costMatrix[start_idx, neighbor_idx] = new_cost

                                    queue.append((nx, ny, new_cost))

    def getShortestPathDistance(self, start: Index, end: Index) -> float:
        """Get the shortest path distance between two points in O(1) time"""

        # Convert 2D indices to 1D
        start_idx = self.index2id(start)
        end_idx = self.index2id(end)

        return self.APSP_costMatrix[start_idx, end_idx]

    def getNextDirection(self, start: Index, end: Index, last_dir: int) -> int:
        """Get the first move direction from start to end in O(1) time"""

        # Convert 2D indices to 1D
        start_idx = self.index2id(start)
        end_idx = self.index2id(end)

        if start_idx == end_idx:
            return 0  # arrived

        # Get cost-to-dest for all 8 neighbors
        src_cost = self.APSP_costMatrix[start_idx, end_idx]  # current cost
        best_cost = src_cost

        best_dir = None
        # Check 4-directional neighbors
        x, y = start
        for direction in range(1, 5):
            dx, dy = dir2diff(direction)
            nx, ny = x + dx, y + dy
            # Check bounds
            if 0 <= nx < self.mapWidth and 0 <= ny < self.mapHeight:
                neighbor_idx = self.index2id((nx, ny))
                neighbor_cost = self.APSP_costMatrix[neighbor_idx, end_idx]
                if neighbor_cost < src_cost and direction == last_dir:
                    neighbor_cost -= STRAIGHT_BONUS
                if neighbor_cost < best_cost:  # strictly better
                    best_cost = neighbor_cost
                    best_dir = direction

        return best_dir  # None if no improvement (shouldn't happen in valid paths)
