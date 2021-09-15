import grpc
import os
import json
import copy
from ...proto import hephaestus_pb2
from ...proto import hephaestus_pb2_grpc
# from robot_algorithm_context import RobotEnvironmentContext, MapCell, Robot


class Algorithm:
    def __init__(self, host='127.0.0.1', port='10022'):
        # 连接远程服务
        self.conn = grpc.insecure_channel(host + ':' + port)
        self.client = hephaestus_pb2_grpc.RobotAlgorithmServiceStub(
            channel=self.conn)
        self.cellmap = {}
        self.agv_start_cell = {}
        self.algorithm_result_record = {}
        self.replay = False
        self.record = False
        self.assignedPath = {}
        
    def record_one_step_algorithm_result(self, context, algo_result):
        # 记录一步算法的结果，暂存在self.algorithm_result_record中，当结束后以json的格式保存在本地
        time_stamp = getattr(context, "time")
        self.algorithm_result_record[time_stamp] = []
        for one in algo_result.robotAlgorithmUpdates:
            if len(one.cells) == 0:
                self.algorithm_result_record[time_stamp].append({
                    'robotId': int(getattr(one, "robotId")),
                    'targetDirection': int(getattr(one, "direction"))
                    })
                
            else:
                cell_list = [[int(cell.index[0]), int(cell.index[1])] for cell in one.cells]
                self.algorithm_result_record[time_stamp].append({
                    'robotId': int(getattr(one, "robotId")),
                    'cellList': cell_list
                    })
                
    def record_one_step_algorithm_result2(self, context, algo_result):
        # 记录一步算法的结果，暂存在self.algorithm_result_record中，当结束后以json的格式保存在本地
        time_stamp = getattr(context, "time")
        self.algorithm_result_record[time_stamp] = []
        for one in algo_result.robotAlgorithmUpdates:
            if len(one.cells) == 0:
                self.algorithm_result_record[time_stamp].append({
                    'robotId': int(getattr(one, "robotId")),
                    'targetDirection': int(getattr(one, "direction"))
                    })
                
        time_stamp = getattr(context, "time") - 1000
        for item in context.robots:
            #print(dir(item))
            cell_list = [[int(cell.index[0]), int(cell.index[1])] for cell in item.assignedPath]
            if len(cell_list) > 1:
                if time_stamp == 0 and self.agv_start_cell[int(getattr(item, "robotId"))] != cell_list[0]:
                    # 补全起点的占用
                    cell_list = [self.agv_start_cell[int(getattr(item, "robotId"))]] + cell_list
                self.algorithm_result_record[time_stamp].append({
                    'robotId': int(getattr(item, "robotId")),
                    'cellList': cell_list
                    })
                
    def save_algorithm_result_to_json(self, mapId):
        # 计算路径: 从 multi_robot 回到项目根目录
        project_root = os.path.abspath(os.path.join(__file__, "../../../../.."))
        save_path = os.path.join(project_root, f'result_{mapId}.json')
    
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(self.algorithm_result_record, f)
    
        print("Saved to:", save_path)
        
    def load_algorithm_result_from_json(self, mapId):
        # 计算路径: 从 multi_robot 回到项目根目录
        project_root = os.path.abspath(os.path.join(__file__, "../../../../.."))
        file_path = os.path.join(project_root, f'result_{mapId}.json')
    
        with open(file_path, "r", encoding="utf-8") as f:
            self.algorithm_result_record = json.load(f)

        self.algorithm_result_record = {
            int(k): v for k, v in self.algorithm_result_record.items()
        }
        print("Load algo_result")
        self.replay = True

    def execute(self, context, status = False):
        # context = hephaestus_pb2.RobotEnvironmentContext()
        # context.time = result.timestamp
        # context.width = result.height
        # context.height = result.width
        # context.robots.extend(result.allRobots)
        # context.mapCells.extend(result.mapCells)
        # context.tasks.extend(tasks)
        # context.isInit = isInit
        # print(context.time)
        if not self.cellmap:
            for cell in context.mapCells:
                cellIndex = (int(cell.index[0]), int(cell.index[1]))
                self.cellmap[cellIndex] = copy.deepcopy(cell)
                
        if not self.agv_start_cell:
            for agv in context.robots:
                self.agv_start_cell[int(getattr(agv, "robotId"))] = [int(agv.locationIndex[0]), int(agv.locationIndex[1])]
            
        send_result = hephaestus_pb2.EnvironmentUpdateContext()
        if self.replay:
            curr_time = getattr(context, "time")
            if curr_time in self.algorithm_result_record.keys():
                assignedPath = {}
                for robot in context.robots:
                    assignedPath[getattr(robot, "robotId")] = [[int(seg.index[0]), int(seg.index[1])] for seg in robot.assignedPath]
                for one in self.algorithm_result_record[curr_time]:
                    if 'cellList' in one.keys():
                        update = self.__count_multi_robot_add(
                            send_result.updateRobots, one['robotId'])
                        if update is None:
                            update = hephaestus_pb2.RobotPathUpdate()
                            update.robotId = one['robotId']

                        cell_list = []
                        overlap_len = 0
                        max_len = min(len(assignedPath[one['robotId']]), len(one["cellList"]))
                        for k in range(max_len, 0, -1):
                            if assignedPath[one['robotId']][-k:] == one["cellList"][:k]:
                                overlap_len = k
                                break
                        if overlap_len < len(one["cellList"]):
                            cell_list = one["cellList"][max(0, overlap_len-1):]
                        if len(assignedPath[one['robotId']]) > 0 and len(cell_list) > 0:
                            if assignedPath[one['robotId']][-1] != cell_list[0]:
                                cell_list = [assignedPath[one['robotId']][-1]] + cell_list

                        last_cell = None
                        if len(cell_list) > 1:
                            for cell_index in cell_list:
                                cell = self.cellmap[(cell_index[0], cell_index[1])]
                                update.updatePath.append(cell)
                                update.directions.append(
                                    self.__count_direction(last_cell, cell))
                                last_cell = cell
    
                            send_result.updateRobots.append(update)
                    else:
                        around = hephaestus_pb2.TurnAroundRobots()
                        around.robotId = one['robotId']
                        around.targetDirection = int(one['targetDirection'])
                        
                        send_result.turnAroundRobots.append(around)
                # for update in send_result.updateRobots:
                #     print(update.robotId)
                #     print(assignedPath[update.robotId])
                #     print([cell.index for cell in update.updatePath])
                #     print([dire for dire in update.directions])
            return send_result
        
        algo_result = self.client.execute(context)
        if self.record:
            self.record_one_step_algorithm_result2(context, algo_result)
        
        for one in algo_result.robotAlgorithmUpdates:
            if len(one.cells) == 0:
                around = hephaestus_pb2.TurnAroundRobots()
                around.robotId = one.robotId
                around.targetDirection = one.direction

                send_result.turnAroundRobots.append(around)
            else:
                update = self.__count_multi_robot_add(
                    send_result.updateRobots, one.robotId)
                if update is None:
                    update = hephaestus_pb2.RobotPathUpdate()
                    update.robotId = one.robotId
                last_cell = None
                for cell in one.cells:
                    update.updatePath.append(cell)
                    update.directions.append(
                        self.__count_direction(last_cell, cell))
                    last_cell = cell

                send_result.updateRobots.append(update)
        # for update in send_result.updateRobots:
        #     print(update.robotId)
        #     print(assignedPath[update.robotId])
        #     print([cell.index for cell in update.updatePath])
        #     print([dire for dire in update.directions])
        return send_result

    # 验证算法结果是否同时传入多个相同机器人
    def __count_multi_robot_add(self, list, robot_id):
        for one in list:
            if one.robotId == robot_id:
                return one

        return None

    def __count_direction(self, last_cell, cell):
        result = 0
        if last_cell is None:
            return result

        if(last_cell.index[0] == cell.index[0]):
            result = 3 if last_cell.index[1] < cell.index[1] else 1

        if(last_cell.index[1] == cell.index[1]):
            result = 0 if last_cell.index[0] < cell.index[0] else 2

        return result
