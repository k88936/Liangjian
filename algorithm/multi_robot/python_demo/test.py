#! /usr/bin/env python
# -*- coding: utf-8 -*-

import io
import sys
import time
import unittest


# Import service and message types
from algoService import AlgoService ,serve
from type import Request, AlgorithmResult


class FakeAlgorithmResult:
    def __init__(self):
        self.paths = []
        self.turnAround = []


class FakeAlgorithm:
    def run(self, request: Request)-> AlgorithmResult:
        try:
            # Dump the incoming message to stdout
            print("FakeAlgorithm.run called")
            print(
                f"time={request.time}, robots={len(request.robots)}, "
                f"mapCells={len(request.mapCells)}, "
                f"isInit={request.isInit}, size={request.width}x{request.height}"
            )
            return FakeAlgorithmResult()

        except Exception as e:
            print(e)
            return AlgorithmResult()


def test_echo():
    service = AlgoService()
    # Inject fake algorithm
    service.algorithm = FakeAlgorithm()
    serve(service)

if __name__ == '__main__':
    test_echo()
