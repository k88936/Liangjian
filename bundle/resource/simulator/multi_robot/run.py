import copy
from .task import tasks
from .validation import Validation


class Resource():
    # 初始化模拟器
    def __init__(self):
        self.validation = Validation()

    def register(self, taskId=0):
        task = tasks[taskId]
        self._register(
            copy.deepcopy(task['map']),
            copy.deepcopy(task['robots'])
        )

        return self.context

    def _register(self, map, robots):
        self._register_sim(map, robots)
        self._register_algo()

    def _register_sim(self, map, robots):
        self.context = self.validation.register_simulator(map, robots)

    def _register_algo(self):
        self.validation.register_algorithm()

    # 调用算法，执行模拟器next
    def run_algo(self, isInit):
        result = self.validation.run_algorithm(isInit)
        return result

    def get_environment_info(self, isInit):
        context = self.validation.get_environment_info(isInit)
        return context

    def get_task_length(self):
        return len(tasks)

    def get_task_by_id(self, id):
        task = tasks[id]
        return task['robots']
