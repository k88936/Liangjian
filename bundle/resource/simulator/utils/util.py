from ...proto import hephaestus_pb2


class Utils():

    def __init__(self):
        self.shelves_target_area = {}
        self.robot_task_info = {}
        self.shelves_with_robot = {}

    def check_context(self, context, shelves, robots, isInit):
        algoContext = hephaestus_pb2.RobotEnvironmentContext()
        algoContext.time = context.timestamp
        algoContext.width = context.height
        algoContext.height = context.width
        algoContext.isInit = isInit

        if isInit:
            if shelves is not None:
                self.__count_shelf_target_area(shelves, context.mapCells)
            self.__count_robot_info(robots)

        extend_robot = self.__extend_robots(context.allRobots, isInit)
        algoContext.robots.extend(extend_robot)

        if shelves is not None:
            extend_shelf = self.__extend_shelves(context.shelves)
            algoContext.shelves.extend(extend_shelf)

        algoContext.mapCells.extend(context.mapCells)
        # algoContext.tasks.extend(tasks)

        return algoContext

    def __extend_shelves(self, shelves):
        result = []
        for shelf in shelves:
            # print(shelf)
            shelfExtend = hephaestus_pb2.ShelfExtend()
            shelfExtend.code = shelf.code
            if shelf.code in self.shelves_with_robot:
                val = self.shelves_with_robot[shelf.code]
                # shelfExtend.placement.extend(val['placement'])
                shelfExtend.robotId = val['robotId']
            else:
                shelfExtend.placement.extend(shelf.placement)
                shelfExtend.robotId = shelf.robotId
            shelfExtend.targetArea.extend(self.shelves_target_area[shelf.code])
            result.append(shelfExtend)
        return result

    def __extend_robots(self, robots, isInit):
        result = []
        for robot in robots:
            # print(shelf)
            taskinfo = self.robot_task_info[
                robot.robotId]
            robotWithTask = hephaestus_pb2.RobotWithTask()
            robotWithTask.robotId = robot.robotId
            robotWithTask.locationIndex.extend(robot.locationIndex)
            robotWithTask.nextIndex.extend(robot.nextIndex)
            robotWithTask.assignedPath.extend(robot.assignedPath)
            robotWithTask.speed = robot.speed
            robotWithTask.isBlock = robot.isBlock
            robotWithTask.position = robot.position
            if isInit:
                robotWithTask.direction = taskinfo['direction']
            else:
                robotWithTask.direction = robot.direction
            robotWithTask.leftWaitTime = robot.leftWaitTime
            if "endDirection" in taskinfo:
                robotWithTask.endDirection = taskinfo['endDirection']
                robotWithTask.destIndex.extend(taskinfo['destIndex'])

            result.append(robotWithTask)

            if "shelfCode" in taskinfo:
                robotWithTask.shelfCode = taskinfo['shelfCode']

                if taskinfo['shelfCode'] != '':
                    self.shelves_with_robot[taskinfo['shelfCode']] = {
                        "placement": robot.locationIndex,
                        "robotId": robot.robotId
                    }

        return result

    def __count_shelf_target_area(self, shelves, mapCells):
        for code in shelves:
            shelf = shelves[code]
            self.shelves_target_area[code] = []
            for cell in shelf['targetArea']:
                self.shelves_target_area[code].append(
                    self.__get_map_cell(cell, mapCells))

    def __count_robot_info(self, robots):
        # robot_task_info
        for id in robots:
            robot = robots[id]
            self.robot_task_info[id] = {
                "direction": robot['direction']
            }
            if "destX" in robot:
                self.robot_task_info[id]["destIndex"] = [
                    robot['destX'], robot['destY']]

            if "endDirection" in robot:
                self.robot_task_info[id]["endDirection"] = robot['endDirection']

            if "shelfCode" in robot:
                self.robot_task_info[id]["shelfCode"] = robot['shelfCode']

    def __get_map_cell(self, index, mapCells):
        for cell in mapCells:
            if cell.index[0] == index['x'] and cell.index[1] == index['y']:
                return cell
        return None
