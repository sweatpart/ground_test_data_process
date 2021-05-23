from re import S
import time
import sys
from queue import Queue
from functools import partial
from threading import Thread, Event

from src.db import insert_db
from src.tools import time_bar

class Error(Exception):
    pass


class ProcessorExit(Error):
    pass


class Processor(object):

    def __init__(self):
        self._commands = Queue()
        self.progress_rate = Queue()
    
    def start(self, result_q=None):
        self._terminated = Event()
        if result_q is not None:
            t = Thread(target=self._bootstrap, args=(result_q,))  # 定义一个后台服务线程
        else:
            t = Thread(target=self._bootstrap)
        t.daemon = True
        t.start()
    
    def _bootstrap(self, result_q=None):
        try:
            if result_q is not None:
                self.run(result_q)
            else:
                self.run()
        except ProcessorExit:
            pass
        finally:
            self._terminated.set()
    
    #关闭worker
    def close(self):
        self.send(ProcessorExit)
    
    def send(self, command):
        self._commands.put(command)

    def join(self):
        self._terminated.wait()

    def _process(self, command):

        try:
            paths, config, solver = command
            s = solver(progress_rate=self.progress_rate)
            result = s.solver_method(paths=paths, config=config)
            # 将计算结果存入mogodb
            #insert_db(username=config['username'], project=config['project'], solver=solver.__name__, result=result)
            return result
        except ProcessorExit:
            raise ProcessorExit()

    def run(self, result_q=None):
        while True:
            if self._commands:
                command = self._commands.get()
                if command is ProcessorExit:
                    raise ProcessorExit()
                result = self._process(command)
                if result_q is not None:
                    result_q.put(result)

            time.sleep(0.1)

def main():
    print('This module can only be imported.')

if __name__ == "__main__":
    main()