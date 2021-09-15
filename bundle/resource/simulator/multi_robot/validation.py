
# from ...hephaestus_pb2 import Task
import time
from ...proto.hephaestus_pb2 import Task
from .simulator_api import Simulator
from .algorithm_api import Algorithm
from ..utils.util import Utils
from collections import Counter


class Validation():
    def __init__(self):
        self.algoTopRunTime = 0
        self.utils = Utils()

    def register_simulator(self, map, robots):
        self.env_id = None
        self.sim = Simulator(host='127.0.0.1',
                             port='10020',
                             occupy_len=4,
                             wait_before_turn=2,
                             speed_low=1,
                             speed_high=1,
                             wait_low=2000,
                             wait_high=2000)

        # 2. 添加机器人：机器人编号，起点，终点
        # self.sim.add_robot(robots)

        self.robots = robots

        # 3. 在远程服务器注册
        self.registerd = self.sim.register(map, robots)
        context = None
        if self.registerd:
            context = self.sim.get_environment_info()

        return context

    def close_simulator(self):
        self.sim.close()

    def register_algorithm(self):

        self.algo = Algorithm(host='127.0.0.1', port='10022')
        return self.algo

    def get_environment_info(self, isInit=False):
        context = self.sim.get_environment_info()
        algoContext = self.utils.check_context(
            context, None, self.robots, isInit)

        return algoContext

    def run_algorithm(self, isInit=False):
        context = self.sim.get_environment_info()
        algoContext = self.utils.check_context(
            context, None, self.robots, isInit)

        status = self._check_result(algoContext)

        if status:
        # 结束运行
            self.algo.execute(algoContext, status=True)
            self.sim.close()
            return context.timestamp / 1000

        # 调用算法execute方法
        try:
            start_time = time.time()
            algo_result = self.algo.execute(algoContext)
            end_time = time.time()
            c_time = end_time - start_time
            if c_time > self.algoTopRunTime:
                self.algoTopRunTime = c_time
        except Exception as e:
            print(e)
            print('算法执行存在错误')
            self.sim.close()
            return 0.0

        # 更新远程的环境
        try:
            result = self.sim.update_robot(algo_result)
        except Exception as e:
            print(e)
            print('更新模拟器环境报错')
            self.sim.close()
            return 0.0

        if result:
            print(result)
            # 算法的输出存在错误，结束运行
            print('算法输出格式存在错误')
            self.sim.close()
            return 0.0

        return algo_result

    def _check_result(self, context):
        # 判断所有机器人是否到达终点
        stop_flag = True

        for robot in context.robots:
            if robot.destIndex != robot.locationIndex:
                stop_flag = False
                break
            else:
                if robot.direction != robot.endDirection and robot.endDirection != 5:
                    stop_flag = False
                    break

        if stop_flag:
            print('top algo run time : %s \n' % (self.algoTopRunTime))
            self.sim.close()

        return stop_flag
