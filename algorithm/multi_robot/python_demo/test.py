#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Import service and message types
from algoService import AlgoService, serve
from type import Request, AlgorithmResult, RobotAction, MapCell


class FakeAlgorithm:

    def run(self, request: Request) -> AlgorithmResult:
        # Dump the incoming message to stdout
        print("FakeAlgorithm.run called")
        x = 19
        y = 0
        i = y + 20 * x
        print(request.mapCells[i].location)

        print(
            f"time={request.time}, robots={len(request.robots)}, "
            f"mapCells={len(request.mapCells)}, "
            f"isInit={request.isInit}, size={request.width}x{request.height}"
        )
        return AlgorithmResult([RobotAction(1, [], 2)])


def test_echo():
    service = AlgoService()
    # Inject fake algorithm
    service.algorithm = FakeAlgorithm()
    serve(service)


if __name__ == '__main__':
    test_echo()
