#! /usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Protocol, Sequence, List, Optional, Tuple


# Type aliases
Index = Tuple[int, int]  # (x, y)


class MapCell(Protocol):
    floorId: int
    cellCode: str
    index: Sequence[int]
    location: Sequence[float]
    directionCost: Sequence[int]
    cellType: str


class Robot(Protocol):
    robotId: int
    locationIndex: Sequence[int]
    nextIndex: Sequence[int]
    destIndex: Sequence[int]
    position: float
    path: Sequence[MapCell]
    assignedPath: Sequence[MapCell]
    isBlock: bool


class Request(Protocol):
    time: int
    robots: Sequence[Robot]
    mapCells: Sequence[MapCell]
    isInit: bool
    width: int
    height: int


class TurnAroundUpdate(Protocol):
    robotId: int
    direction: int


class PathEntry(Protocol):
    robotId: int
    cells: Sequence[MapCell]


class AlgorithmResult(Protocol):
    paths: Sequence[PathEntry]
    turnAround: Sequence[TurnAroundUpdate]
