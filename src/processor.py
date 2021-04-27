import time
import sys
from queue import Queue
from collections import deque
from functools import partial
from threading import Thread, Event
import json


from src.tools import timer
from src.solvers import RainflowSolver, DutyCycleSolver 
from src.db import insert_db


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

    def join(self):
        self._terminated.wait()

    def _process(self, command=None):

        try:
            paths, config, solver = command
            result = solver().solver_method(paths=paths, config=config)
            insert_db(username='sl', project='test', solver=solver.__class__.__name__, result=result)
            return result
        except ProcessorExit:
            raise ProcessorExit()

    def run(self, result_q):
        while True:
            if self._commands:
                command = self._commands.popleft()
                result = self._process(command)
                result_q.put(result)

            time.sleep(0.1)

def main():
    print('This module can only be imported.')

if __name__ == "__main__":
    main()