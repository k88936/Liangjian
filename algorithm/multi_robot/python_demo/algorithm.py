#! /usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import List, Union

import numpy as np
from numpy.f2py.auxfuncs import throw_error
from pkg_resources import require

from type import *

BLOCKED = 65535
PASSABLE =1


@dataclass
class RobotState:
    inner: Robot
    path: List[Index]
    pathProgress: int

    def followPath(self) -> List[Index]:
        pass


def diff2dir(diff: Position) -> int:
    (dx, dy) = diff
    if dx > 0 and dy == 0: return 4
    if dx < 0 and dy == 0: return 2
    if dy > 0 and dx == 0: return 3
    if dy < 0 and dx == 0: return 1
    return 0


def dir2diff(direction: int) -> Position:
    if direction == 1: return 0, -1
    if direction == 2: return -1, 0
    if direction == 3: return 0, 1
    if direction == 4: return 1, 0
    return 0,0


class Dfs:
    mapWidth: int
    mapHeight: int

    creepCostMatrix: np.ndarray

    def run(self, request: Request) -> AlgorithmResult:
        if request.isInit:
            self.init(request)
            return AlgorithmResult([])
        self.load_creep_matrix(request)

        result = AlgorithmResult([])
        return result

    def load_creep_matrix(self, request: Request):
        pass
        # self.creepCostMatrix = np.zeros((request.width, request.height), dtype=int)
        # for robot in request.robots:
        #     # current cell is already in assignedPath
        #     for cell in robot.assignedPath:
        #         (ix, iy) = cell.index
        #         self.creepCostMatrix[ix, iy] = 100

    structureCostMatrix: np.ndarray = None
    index2cell: List[List[MapCell]] = None

    def init(self, request: Request):
        self.mapWidth = request.width
        self.mapHeight = request.height

        self.structureCostMatrix = np.zeros((request.width, request.height), dtype=np.uint16)
        for cell in request.mapCells:
            (ix, iy) = cell.index
            cost = BLOCKED if cell.cellType == 'BLOCKED_CELL' else PASSABLE
            self.structureCostMatrix[ix, iy] = cost

        self.index2cell = [[None for _ in range(request.height)] for _ in range(request.width)]  # type: ignore
        for cell in request.mapCells:
            (ix, iy) = cell.index
            self.index2cell[ix][iy] = cell

    APSP_costMatrix: np.ndarray = None  #
    APSP_moveMatrix: np.ndarray = None

    def buildAPSP(self, request: Request):
        if self.structureCostMatrix is None:
            raise Exception('structureCostMatrix is None')
        if self.index2cell is None:
            raise Exception('index2cell is None')
        self.APSP_costMatrix = np.zeros((self.mapWidth, self.mapHeight, self.mapWidth, self.mapHeight), dtype=np.uint16)
        self.APSP_moveMatrix = np.zeros((self.mapWidth, self.mapHeight, self.mapWidth, self.mapHeight), dtype=np.uint8)
