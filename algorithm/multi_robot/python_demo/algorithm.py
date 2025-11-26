#! /usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import List

import numpy as np

from utils import diff2dir, dir2diff, timing
from grid import DynamicOccupancyGridMap
from d_star_lite import DStarLite
from type import Index, Request, AlgorithmResult, RobotAction, MapCell, Robot

STRAIGHT_BONUS = 0.5
np.set_printoptions(precision=2, suppress=True, linewidth=1000)


@dataclass
class RobotState:
    inner: Robot
    # targets: List[int]
    pathfinder: DStarLite


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
            # if rbt.robotId>4:
            #     break
            # if len(actions) > 16:
            #     break
            p = rbt.assignedPath[-1].index
            status = self.robotStates[rbt.robotId]
            pppp = (p[0], p[1])
            self.obstacleMatrix.set_dynamic_mask(rbt.robotId)
            dist = status.pathfinder.replan(pppp)

            # print("-->> ",rbt.robotId)
            # print(status.pathfinder.slam_map.get_map().T)
            # print(status.pathfinder.g.T)
            if not dist:
                if rbt.direction != rbt.endDirection:
                    actions.append(RobotAction(rbt.robotId, [], rbt.endDirection))
                continue
            path = [self.index2cell(p), self.index2cell(dist)]
            ttt = RobotAction(rbt.robotId, path)
            actions.append(ttt)

        result = AlgorithmResult(actions)
        print("--------------------------------")
        return result

    @timing
    def load_robot_overlay_cost(self, request: Request):
        self.obstacleMatrix.clear_dynamic()
        for robot in request.robots:
            self.obstacleMatrix.set_dynamic_obstacle(robot.locationIndex, robot.robotId)

            # for cell in robot.assignedPath[:4]:
            #     self.obstacleMatrix.set_dynamic_obstacle(cell.index, robot.robotId)

    robotStates: List[RobotState] = None

    @timing
    def init_robots(self, request: Request):
        self.robotStates = [None for _ in range(self.mapWidth * self.mapHeight)]  # type: ignore
        for robot in request.robots:
            end_idx = self.index2id(robot.destIndex)
            pathfinder = DStarLite(self.obstacleMatrix, robot.locationIndex, robot.destIndex,
                                   self.APSP_costMatrix[end_idx])
            state = RobotState(robot, pathfinder)
            self.robotStates[robot.robotId] = state

    @timing
    def init(self, request: Request):
        self.mapWidth = request.width
        self.mapHeight = request.height

        self.build_map(request)

    def index2cell(self, index: Index):
        return self.id2cell[self.index2id(index)]

    obstacleMatrix: DynamicOccupancyGridMap
    id2cell: List[MapCell] = None

    @timing
    def build_map(self, request: Request):
        self.obstacleMatrix = DynamicOccupancyGridMap(self.mapWidth, self.mapHeight)
        for cell in request.mapCells:
            if cell.cellType == 'BLOCKED_CELL':
                self.obstacleMatrix.set_obstacle(cell.index)

        self.id2cell = [None for _ in range(self.mapWidth * self.mapHeight)]  # type: ignore
        for cell in request.mapCells:
            self.id2cell[self.index2id(cell.index)] = cell

        self.build_APSP()

    APSP_costMatrix: List[np.ndarray] = None

    # Convert 2D coordinates to 1D indices
    def index2id(self, index: Index):
        (x, y) = index
        return x * self.mapHeight + y

    def id2index(self, di: int) -> Index:
        return di // self.mapHeight, di % self.mapHeight

    @timing
    def build_APSP(self):
        if self.obstacleMatrix is None:
            raise Exception('structureCostMatrix is None')
        if self.id2cell is None:
            raise Exception('index2cell is None')

        # Flatten indices for easier matrix operations
        n = self.mapWidth * self.mapHeight
        self.APSP_costMatrix = [np.ones((self.mapWidth, self.mapHeight), dtype=np.float32) * np.inf for _ in range(n)]

        # Run BFS from each node
        for ex in range(self.mapWidth):
            for ey in range(self.mapHeight):
                end_idx = self.index2id((ex, ey))

                # Initialize BFS
                queue = [(ex, ey, 0)]  # (x, y, cost)
                visited = np.zeros((self.mapWidth, self.mapHeight), dtype=bool)
                visited[ex, ey] = True

                # Set distance to self as 0
                self.APSP_costMatrix[end_idx][ex, ey] = 0

                # Skip blocked starting cells
                if not self.obstacleMatrix.is_unoccupied((ex, ey)):
                    continue

                # BFS loop
                while queue:
                    x, y, cost = queue.pop(0)
                    # Check 4-directional neighbors
                    for suc in self.obstacleMatrix.succ((x, y), avoid_obstacles=True):
                        nx, ny = suc

                        # Check if already visited
                        if visited[nx, ny]:
                            continue
                        # Mark as visited
                        visited[nx, ny] = True
                        # Calculate new cost
                        new_cost = cost + 1
                        # Update if this is a better path
                        if new_cost < self.APSP_costMatrix[end_idx][nx, ny]:
                            self.APSP_costMatrix[end_idx][nx, ny] = new_cost
                            queue.append((nx, ny, new_cost))
