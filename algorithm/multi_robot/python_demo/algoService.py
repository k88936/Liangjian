#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
from concurrent import futures

import grpc

import hephaestus_pb2
import hephaestus_pb2_grpc
# 在这里引入自己设计的算法文件
from algorithm import Dfs
from type import AlgorithmResult, Request

_HOST = '127.0.0.1'
_PORT = '10022'

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class AlgoService(hephaestus_pb2_grpc.RobotAlgorithmServiceServicer):
    def __init__(self):
        self.dfs = None
        self.algorithm = Dfs()

    # 每一个timestamp都会调用此方法
    def execute(self, request: Request, context):
        print(request.time)
        # request说明
        #   request.time        模拟器当前timestamp,类型为int64
        #   request.robots      当前timestamp下的所有机器人的集合，类型为List,每一个元素为Robot的实例
        #   request.mapCells    地图所有点集合，类型为List,每一个元素为MapCell的实例
        #   request.tasks       任务信息，类型为List,每一个元素为Task的实例
        #   request.isInit      是否场景初次调用
        #   request.width       地图场景宽度
        #   request.height      地图场景高度

        # 任务信息 Task 说明
        #     int64 robotId = 1;
        #     repeated int32 index = 2;             例：[1,1]
        #     repeated int32 dest = 3;              例：[1,1]

        # 地图点 MapCell 说明
        #     int32 floorId = 1;
        #     string cellCode = 2;
        #     repeated int32 index = 4;             单元格在二维表中的索引，例：[1,1]
        #     repeated double location = 5;         单元格在仓库中的实际位置，例：[1.5,1.5]
        #     repeated int32 directionCost = 6;     单元格方向，例：[1,1,0,1]
        #     string cellType = 7;                  单元格类型，例：“BLOCKED_CELL”为障碍点

        # 机器人 Robot 主要字段说明
        #     int64 robotId = 1;
        #     repeated int32 locationIndex = 2;     当前所有位置，例：[1,1]
        #     repeated int32 nextIndex = 12;        下一步位置：例：[1,1]
        #     double position = 13;                 机器人在两个单元格的中间状态
        #     repeated MapCell path = 3;            由MapCell组成的List
        #     repeated MapCell assignedPath = 11;   由MapCell组成的List
        #     bool isBlock = 8;                     机器人是否被阻挡

        # 将信息传给算法
        algorithm_result: AlgorithmResult = self.algorithm.run(request)

        # 初始化返回结果对象
        result = hephaestus_pb2.RobotAlgorithmResult()

        for action in algorithm_result.paths:
            if len(action.cells) == 1:
                continue
            # 为需要规划路径的机器人创建结果容器
            update = hephaestus_pb2.RobotAlgorithmUpdates()
            # 传入机器人ID
            update.robotId = action.robotId
            # 添加机器人路径，每个路径点的类型为MapCell
            for cell in action.cells:
                update.cells.append(cell)
                update.direction = 0
            # apply rotation
            if action.direction != 0:
                update.direction = action.direction
            # 将机器人结果容器添加到返回结果对象上
            result.robotAlgorithmUpdates.append(update)

        print(result)
        return result


def serve(service=AlgoService()):
    grpcServer = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    hephaestus_pb2_grpc.add_RobotAlgorithmServiceServicer_to_server(
        service, grpcServer)
    grpcServer.add_insecure_port(_HOST + ':' + _PORT)
    grpcServer.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        grpcServer.stop(0)

if __name__ == '__main__':
    serve()
