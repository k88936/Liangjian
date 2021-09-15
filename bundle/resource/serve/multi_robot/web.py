import asyncio
import signal
import sys
from ...proto.hephaestus_pb2 import MapCell
import websockets
import json
from google.protobuf.json_format import MessageToJson
from ...simulator.multi_robot.run import Resource


class Sim():
    def __init__(self):
        self.resource = Resource()
        self.isInit = True
        self.taskId = 0

    def register(self):
        self.resource = Resource()
        self.resource.register(self.taskId)
        context = self.resource.get_environment_info(self.isInit)

        return self.transSimInfo(context)

    def run_simulator(self):
        try:
            result = self.resource.run_algo(self.isInit)
            # isInit = False
        except Exception as e:
            print(e)
            # 发送错误信息
            return {'error': '算法执行存在错误'}

        if type(result) is float or type(result) is int:
            # 发送结果
            return {'result': result}
        else:
            context = self.resource.get_environment_info(self.isInit)

            return self.transSimInfo(context, result)
            # 发送前端状态

    def transSimInfo(self, context, algoResult=None):
        result = {}
        if context.robots is not None:
            robots = []
            for robot in context.robots:
                robotResult = {
                    "robotId": robot.robotId,
                    "position": robot.position,
                    # "shelfCode": robot.shelfCode,
                    "leftWaitTime": robot.leftWaitTime,
                    # "shelfActionStatus": robot.shelfActionStatus,
                    "direction": robot.direction,
                    "assignedPath": self.transRobotPath(robot.assignedPath)
                }
                if len(robot.locationIndex) == 2:
                    robotResult['locationIndex'] = [
                        robot.locationIndex[0], robot.locationIndex[1]]
                if len(robot.nextIndex) == 2:
                    robotResult['nextIndex'] = [
                        robot.nextIndex[0], robot.nextIndex[1]]
                if algoResult is not None:
                    robotAlgo = self.getAlgoRobotById(
                        algoResult.updateRobots, robot.robotId)
                    if robotAlgo is not None:
                        robotResult['updatePath'] = self.transRobotPath(
                            robotAlgo.updatePath)

                robots.append(robotResult)

            result['robots'] = robots

        if context.mapCells is not None:
            cells = []
            for cell in context.mapCells:
                cells.append(json.loads(MessageToJson(cell)))
            result['mapCells'] = cells

        result['timestamp'] = context.time / 1000
        result['width'] = context.width
        result['height'] = context.height

        return result

    def getAlgoRobotById(self, robots, id):
        result = None
        for robot in robots:
            if robot.robotId == id:
                result = robot
                break

        return result

    def transRobotPath(self, paths):
        result = []
        for path in paths:
            result.append([path.index[0], path.index[1]])
        return result

    async def time(self, websocket, path):
        while True:
            data = await websocket.recv()
            data = json.loads(data)
            if data['step'] == "init":
                taskLength = self.resource.get_task_length()
                result = json.dumps(
                    {"code": 200,
                     "type": 'init',
                     "data": {
                         "taskLength": taskLength
                     }})
                await websocket.send(result)

            if data["step"] == "start":
                self.taskId = data['taskId']
                task = None
                if 'taskId' in data:
                    task = self.resource.get_task_by_id(data['taskId'])

                self.isInit = True
                sim_data = None
                try:
                    sim_data = self.register()
                    result = json.dumps(
                        {"code": 200,
                         "type": 'start',
                         "data": {
                             **sim_data,
                             'task': task
                         }
                         })
                except Exception as e:
                    print(e)
                    result = json.dumps({
                        "code": 1,
                        "type": 'start',
                    })
                # sim_data = self.register()
                await websocket.send(result)

            if data["step"] == "next":
                run_data = self.run_simulator()
                result = json.dumps({"code": 200,
                                     "type": 'next', "data": run_data})
                self.isInit = False
                await websocket.send(result)


def run():
    sim = Sim()
    start_server = websockets.serve(sim.time, "0.0.0.0", 5678)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    run()
