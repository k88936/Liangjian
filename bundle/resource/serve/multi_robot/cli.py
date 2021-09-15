import time
import argparse
from ...simulator.multi_robot.run import Resource


def _loop(sim, mapId, replay=False, record=False):
    count = 1
    time_out = 300
    isInit = True
    # 循环调用算法
    if replay:
        sim.validation.algo.load_algorithm_result_from_json(mapId)
    if record:
        sim.validation.algo.record = True
    while count < time_out:
        count += 1
        result = sim.run_algo(isInit)
        isInit = False

        if type(result) is float or type(result) is int:
            if not replay and record:
                sim.validation.algo.save_algorithm_result_to_json(mapId)
            return result
    if not replay and record:
        sim.validation.algo.save_algorithm_result_to_json(mapId)
    print('当前环境信息：\n')
    print('任务完成总时间超时\n')
    return 0.0


def go():
    parser = argparse.ArgumentParser()

    parser.add_argument("--record", action="store_true", help="whether record algorithm results")
    parser.add_argument("--replay", action="store_true", help="whether replay recorded results")

    args = parser.parse_args()
    
    num = 1
    avgscore = 0
    start_time = time.time()
    sim = Resource()
    taskLength = sim.get_task_length()
    for j in range(taskLength):
        sim.register(j)
        print('第%s个地图开始\n' % str(j+1))
        result = _loop(sim, j+1, replay=args.replay, record=args.record)
        if result == 0:
            print('第%s个地图结束，成绩为：%s\n' % (str(j+1), result))
        else:
            print('第%s个地图结束，成绩为：%s\n' % (str(j+1), 300 - result))
            avgscore += (300 - result)

    end_time = time.time()
    avgscore = avgscore / taskLength

    print('整体耗时:%s \n' % (end_time-start_time))
    print('(score:', avgscore, ') \n')
    
    return avgscore


if __name__ == '__main__':
    go()
