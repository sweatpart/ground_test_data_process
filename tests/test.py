import csv
import json
import time
from queue import Queue

from src.processor import Processor
from src.solvers import DutyCycleSolver, RainflowSolver
from src.tools import time_bar
from src.db import result2csv

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
    result_q = Queue()
    home_path = '/mnt/e/Documents/WORK/SAICMARVEL/csvfiles/'
    paths = [home_path + '2/{}.csv'.format(i) for i in range(1, 881)]
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
    my_processor.start(result_q=result_q)
    my_processor.send((paths, config, DutyCycleSolver))
    # 计算时，主线程来到这里
    # TODO 未考虑多个slave传递进度的情况
    while True:
        if my_processor.progress_rate:
            rate = my_processor.progress_rate.get()
            time_bar(rate=rate[0]/rate[1])
            if rate[0] == rate[1]:
                break
    if result_q:
        result = result_q.get()
    print(result)
    result2csv(result=result, save_path='/mnt/e/Documents/WORK/SAICMARVEL/csvfiles/6.csv')
    my_processor.close()
    my_processor.join()

if __name__ == '__main__':
    #rainflow()
    dutycycle()
    time.sleep(5)
