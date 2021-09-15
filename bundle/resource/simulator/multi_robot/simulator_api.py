#! /usr/bin/env python
# -*- coding: utf-8 -*-

from ...proto import hephaestus_pb2_grpc
from ...proto import hephaestus_pb2
import grpc


class Simulator:
    def __init__(self,
                 host='127.0.0.1',
                 port='10020',
                 time_step=1000,
                 jump_prob=0.5,
                 occupy_len=3,
                 jump_noise=0.3,
                 wait_before_turn=20,
                 speed_low=1,
                 speed_high=1,
                 wait_low=2000,
                 wait_high=2000):
        self.context = None
        self.env_id = None
        self.time_step = time_step
        self.occupy_len = occupy_len
        self.jump_noise = jump_noise
        self.wait_before_turn = wait_before_turn
        self.speed_high = speed_high
        self.speed_low = speed_low
        self.wait_low = wait_low
        self.wait_high = wait_high
        self.time = 0
        self.current_time = 0
        self.map_cells = []
        # 连接远程服务
        self.conn = grpc.insecure_channel(host + ':' + port)
        self.client = hephaestus_pb2_grpc.RobotSimulationServiceStub(
            channel=self.conn)
        # 所有事件
        self.all_events = []
        self.jump_prob = jump_prob
        self.registerd = False
        # 机器人的路径点
        self.robot_history_path = {}
        self.environment_info = {}

    def __update_remote_environment(self, context: hephaestus_pb2.EnvironmentUpdateContext):
        # pb_update = hephaestus_pb2.EnvironmentUpdateContext()
        context.envId = self.env_id
        context.nextStep = True
        # pb_update.updateRobots.extend(context.robotPathUpdates)
        # pb_update.turnAroundRobots.extend(context.turnAroundRobots)

        # 调用远程
        self.environment_info = self.client.nextStep(context)

        if self.environment_info.errorCode < 0:
            print("更新模拟器环境失败: " +
                  self.environment_info.errorMsg)
            return True

        return False

    def __end_remote_environment(self):
        if self.registerd:
            pb_end = hephaestus_pb2.EnvironmentQuery()
            pb_end.envId = self.env_id
            self.client.closeEnvironment(pb_end)

    def get_environment_info(self):
        return self.environment_info

    def register(self, map, robots):
        # 准备context
        # 调用远程的接口
        pb_context = hephaestus_pb2.EnvironmentCreateContext()
        pb_context.mapData = map
        pb_context.tickTime = self.time_step
        pb_context.jumpProb = self.jump_prob
        pb_context.occupyLen = self.occupy_len
        pb_context.jumpNoise = self.jump_noise
        pb_context.waitBeforeTurn = self.wait_before_turn
        pb_context.speedLow = self.speed_low
        pb_context.speedHigh = self.speed_high
        pb_context.waitLow = self.wait_low
        pb_context.waitHigh = self.wait_high
        pb_context.useDynamicSpeed = True
        # 构建机器人信息
        for id in robots:
            robot = robots[id]
            robot_pb = hephaestus_pb2.Robot()
            robot_pb.robotId = robot['robot_id']
            robot_pb.locationIndex.append(robot['x'])
            robot_pb.locationIndex.append(robot['y'])
            robot_pb.direction = robot['direction']
            pb_context.robots.append(robot_pb)
        # 调用远程创建环境的服务
        result = self.client.createEnvironment(pb_context)
        if result.errorCode >= 0:
            self.env_id = result.detail.envId
            # 构建context
            self.map_cells = result.detail.mapCells
            self.environment_info = result.detail

            self.registerd = True
            return True
        else:
            print("创建模拟器环境失败")
            return False

    def update_robot(self, context):
        # 更新远程的环境
        return self.__update_remote_environment(context)

    def close(self):
        self.__end_remote_environment()
        # self.conn.close()

    # def get_robot_playback(self):
    #     return self.robot_history_path

    def get_time(self):
        return self.time
