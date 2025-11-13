#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time
import functools
import numpy as np

from type import *

BLOCKED = 1000000
PASSABLE = 1


def diff2dir(diff: Position) -> int:
    (dx, dy) = diff
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
    path: List[Index]
    pathProgress: int

    # def followPath(self) -> List[Index]:
    #     pass


class Dfs:
    mapWidth: int
    mapHeight: int

    robotCostMatrix: np.ndarray

    @timing
    def run(self, request: Request) -> AlgorithmResult:

        if request.isInit:
            self.init(request)
            return AlgorithmResult([])
        self.load_robot_matrix(request)

        actions = []
        for rbt in request.robots:
            p = rbt.assignedPath[-1].index
            direction = self.getNextDirection(p, rbt.destIndex)
            if direction == 0:
                break
            diff = dir2diff(direction)
            apd = (p[0] + diff[0], p[1] + diff[1])
            path = [self.index2cell(p), self.index2cell(apd)]
            p = apd
            ttt = RobotAction(rbt.robotId, path)
            actions.append(ttt)
            break
        result = AlgorithmResult(actions)

        return result

    def load_robot_matrix(self, request: Request):
        pass
        # self.creepCostMatrix = np.zeros((request.width, request.height), dtype=int)
        # for robot in request.robots:
        #     # current cell is already in assignedPath
        #     for cell in robot.assignedPath:
        #         (ix, iy) = cell.index
        #         self.creepCostMatrix[ix, iy] = 100

    @timing
    def init(self, request: Request):
        self.mapWidth = request.width
        self.mapHeight = request.height

        self.build_map(request)

    def index2cell(self, index: Index):
        return self.id2cell[self.index2id(index)]

    structureCostMatrix: np.ndarray = None
    id2cell: List[MapCell] = None

    @timing
    def build_map(self, request: Request):
        self.structureCostMatrix = np.zeros((self.mapWidth, self.mapHeight), dtype=np.float32)
        for cell in request.mapCells:
            (ix, iy) = cell.index
            cost = BLOCKED if cell.cellType == 'BLOCKED_CELL' else PASSABLE
            self.structureCostMatrix[ix, iy] = cost

        self.id2cell = [None for _ in range(self.mapWidth * self.mapHeight)]  # type: ignore
        for cell in request.mapCells:
            self.id2cell[self.index2id(cell.index)] = cell

        self.build_APSP()

    APSP_costMatrix: np.ndarray = None  # cost of move from (x1,y1) to (x2,y2)
    APSP_dirMatrix: np.ndarray = None  # move from(x1,y1) to (x2,y2) 's next move dir

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
        self.APSP_dirMatrix = np.zeros((n, n), dtype=np.uint8)

        # Create a flattened view of the structure cost matrix
        flat_structure = self.structureCostMatrix.flatten()

        # Run BFS from each node
        for sx in range(self.mapWidth):
            for sy in range(self.mapHeight):
                start_idx = self.index2id((sx, sy))
                
                # Skip blocked starting cells
                if flat_structure[start_idx] == BLOCKED:
                    continue
                
                # Initialize BFS
                queue = [(sx, sy, 0, 0)]  # (x, y, cost, first_direction)
                visited = np.zeros((self.mapWidth, self.mapHeight), dtype=bool)
                visited[sx, sy] = True
                
                # Set distance to self as 0
                self.APSP_costMatrix[start_idx, start_idx] = 0
                
                # BFS loop
                while queue:
                    x, y, cost, first_direction = queue.pop(0)
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
                            if flat_structure[neighbor_idx] != BLOCKED:
                                # Mark as visited
                                visited[nx, ny] = True
                                
                                # Calculate new cost
                                new_cost = cost + flat_structure[neighbor_idx]
                                
                                # Update if this is a better path
                                if new_cost < self.APSP_costMatrix[start_idx, neighbor_idx]:
                                    self.APSP_costMatrix[start_idx, neighbor_idx] = new_cost
                                    
                                    # Set direction (use first_direction if this is the first step, otherwise keep it)
                                    if first_direction == 0:
                                        self.APSP_dirMatrix[start_idx, neighbor_idx] = direction
                                    else:
                                        self.APSP_dirMatrix[start_idx, neighbor_idx] = first_direction
                                
                                # Add to queue for further exploration
                                if first_direction == 0:
                                    queue.append((nx, ny, new_cost, direction))
                                else:
                                    queue.append((nx, ny, new_cost, first_direction))


    def getShortestPathDistance(self, start: Index, end: Index) -> float:
        """Get the shortest path distance between two points in O(1) time"""

        # Convert 2D indices to 1D
        start_idx = self.index2id(start)
        end_idx = self.index2id(end)

        return self.APSP_costMatrix[start_idx, end_idx]

    def getNextDirection(self, start: Index, end: Index) -> int:
        """Get the first move direction from start to end in O(1) time"""

        # Convert 2D indices to 1D
        start_idx = self.index2id(start)
        end_idx = self.index2id(end)

        return self.APSP_dirMatrix[start_idx, end_idx]
