#! /usr/bin/env python
# -*- coding: utf-8 -*-
from abc import ABC
from dataclasses import dataclass
from typing import Protocol, Sequence, Tuple, List
from collections import namedtuple


# Type alias
# class Index(Tuple[int,int]):
#     def x(self) -> int:
#         return self[0]
#
#     def y(self) -> int:
#         return self[1]
#
#
# class Position(Tuple[float, float]):
#     def x(self) -> float:
#         return self[0]
#
#     def y(self) -> float:
#         return self[1]
#
#     pass


Index = Tuple[int, int]
Position = Tuple[float, float]


# direction:
#       3
#   2       4
#       1


@dataclass(frozen=True)
class MapCell:
    cellCode: str
    index: Index
    location: Position
    cellType: str  # BLOCKED_CELL or not


@dataclass(frozen=True)
class Robot:
    robotId: int
    locationIndex: Index
    nextIndex: Index
    destIndex: Index
    position: float  # 机器人在两个格子中间的状态取值在  0-1  之间
    assignedPath: Sequence[MapCell]


@dataclass(frozen=True)
class Request:
    time: int
    robots: Sequence[Robot]
    mapCells: Sequence[MapCell]
    isInit: bool
    width: int
    height: int


@dataclass
class RobotAction:
    robotId: int
    cells: List[MapCell]
    direction: int = 0


@dataclass
class AlgorithmResult:
    actions: List[RobotAction]
