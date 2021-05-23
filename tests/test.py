import csv
import json
import time
from queue import Queue

from src.processor import Processor
from src.solvers import DutyCycleSolver, RainflowSolver
from src.tools import time_bar

def rainflow():

    test_file = '/Users/sunlei/Downloads.csv'
    paths = [test_file]
    config = {
        'username': 'admin',
        'project': 'test',
        'main_parm': 'Torque_RL[Nm]',
        'optional_parms': ['JounceAngle_RL[deg]'],
        'ndigits': 0
    }
    my_processor = Processor()
    my_processor.start()
    my_processor.send((paths, config, RainflowSolver))

def dutycycle():
    paths = ['/Users/sunlei/Downloads/2/csv/{}.csv'.format(i) for i in range(1, 10)]
    config = {
        'username': 'admin',
        'project': 'test',
        'main_parm' : 'Torque_RL[Nm]',
        'optional_parms' : ['WhlGndVelLDrvnHSC1[km/h]', 'JounceAngle_RL[deg]'],
        'tire_radius' : 0.3,
        'time_interval' : 0.05
    }
    # 启动计算子进程
    my_processor = Processor()
    my_processor.start()
    my_processor.send((paths, config, DutyCycleSolver))
    # 计算时，主线程来到这里
    # TODO 未考虑多个slave传递进度的情况
    while True:
        if my_processor.progress_rate:
            rate = my_processor.progress_rate.get()
            time_bar(rate=rate[0]/rate[1])
            if rate[0] == rate[1]:
                break

    my_processor.close()
    my_processor.join()

if __name__ == '__main__':
    #rainflow()
    dutycycle()
    time.sleep(5)
