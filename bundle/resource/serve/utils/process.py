from multiprocessing import Process, Value, Manager
import psutil
import time


class ProcessInfo():
    def __init__(self):
        manager = Manager()
        self.childProcess = None
        self.is_start = Value('b', False)
        self.info = manager.list()
        self.pidList = manager.list()
        for proc in psutil.process_iter(['pid', 'name', 'cwd']):
            if proc.info['cwd'] is not None and proc.info['cwd'].find('algorithm') != -1:
                if proc.info['name'].find('python') != -1 or proc.info['name'].find('java') != -1:
                    self.pidList.append(proc.info)

    def __get_info(self, start, info, pidList):
        cpuinfo = None
        memory = None
        arr = []

        for i in pidList:
            pid = i['pid']
            arr.append(psutil.Process(pid))

        while start.value:
            for p in arr:
                cpu_percent = p.cpu_percent()
                mem_percent = p.memory_percent()
                print('cpu:%s,memory:%s' % (cpu_percent, mem_percent))

            time.sleep(1)

        # print('Child process end.')

    def count_time(self, description):
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                print('%s:%s \n' % (description, end_time-start_time))
                return result
            return wrapper
        return decorator

    def start(self):
        self.is_start.value = True

        self.childProcess = Process(
            target=self.__get_info, args=(self.is_start, self.info, self.pidList))
        self.childProcess.start()

    def stop(self):
        self.is_start.value = False
        self.childProcess = None


if __name__ == '__main__':
    process = ProcessInfo()
    process.start()
    time.sleep(5)
    process.stop()
