#! /usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Protocol, Sequence, Tuple

# Type aliases
Index = Tuple[int, int]
Position = Tuple[float, float]
DirectionMask = Tuple[int, int, int, int]


# direction:
#       3
#   2       4
#       1

class MapCell(Protocol):
    floorId: int
    cellCode: str
    index: Index
    location: Position
    directionCost: DirectionMask
    cellType: str  # BLOCKED_CELL or not


class Robot(Protocol):
    robotId: int
    locationIndex: Index
    nextIndex: Index
    destIndex: Index
    position: float  # 机器人在两个格子中间的状态取值在  0-1  之间
    assignedPath: Sequence[MapCell]


class Request(Protocol):
    time: int
    robots: Sequence[Robot]
    mapCells: Sequence[MapCell]
    isInit: bool
    width: int
    height: int


@dataclass
class RobotAction:
    def __init__(self, robot_id: int, cells: Sequence[MapCell], direction: int = 0):
        self.robotId = robot_id
        self.cells = cells
        self.direction = direction


@dataclass
class AlgorithmResult:
    def __init__(
            self,
            actions: Sequence[RobotAction],
    ):
        self.paths = actions
