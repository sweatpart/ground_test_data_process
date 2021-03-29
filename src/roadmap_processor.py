import time
import sys
from queue import Queue
from collections import deque
from functools import partial
from threading import Thread, Event
import json


from src.tools import timer
from src.solvers import *


class Error(Exception):
    pass


class ProcessorExit(Error):
    pass


class Processor(object):

    def __init__(self):
        self._commands = deque()
    
    def start(self, result_q):
        self._terminated = Event()
        t = Thread(target=self._bootstrap, args=(result_q,))  # 定义一个后台服务线程
        t.daemon = True
        t.start()
    
    def _bootstrap(self, result_q):
        try:
            self.run(result_q)
        except ProcessorExit:
            pass
        finally:
            self._terminated.set()
    
    #关闭worker
    def close(self):
        self.send(ProcessorExit)
    
    def send(self, paths):
        self._commands.append(paths)

    def _process(self, command=None):

        try:
            config, solver = command
            result = solver().solver_method(config=config)
            return result
        except ProcessorExit:
            self._terminated.set()

    def run(self, result_q):
        while True:
            if self._commands:
                command = self._commands.popleft()
                result = self._process(command)
                result_q.put(result)

            time.sleep(0.1)


@timer
def main():
   
    result_q = Queue()
    worker = Processor()
    
    worker.start(result_q)

    test_file = '/root/ground_test_data_process/tests/testinput.csv'

    config = {
        'paths' : [test_file],
        'main_parm' : 'a',
        'optional_parms' : ['b', 'c']
    }

    worker.send((config, RainflowSolver))
    #time.sleep(4)
    result= result_q.get()
    print(result)

if __name__ == "__main__":
    main()