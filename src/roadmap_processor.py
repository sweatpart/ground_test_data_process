import csv
import time
import sys
from queue import Queue
from collections import deque
from functools import partial
from threading import Thread, Event

import rainflow

from .tools import timer

class ActorExit(Exception):
    pass

def gen_csvfiles(paths=None):
    for path in paths:
        with open(file=path, newline='', encoding='utf-8') as f:
            csv_file = csv.DictReader(f) # 每行作为一个字典，字典的键来自每个csv的第一行
            yield csv_file

def gen_lines(csv_files=None):
    csv_file_processed = 0
    key = 'a'
    for csv_file in csv_files:
        csv_file_processed += 1
        for line in csv_file:
            yield int(line[key])

class Processor():
    def __init__(self):
        self._csv_to_process = deque()
    
    #定义一个后台服务线程
    def start(self, result_q):
        self._terminated = Event()
        t = Thread(target=self._bootstrap, args=(result_q,))
        t.daemon = True
        t.start()
    
    def _bootstrap(self, result_q):
        try:
            self.run(result_q)
        except ActorExit:
            pass
        finally:
            self._terminated.set()
    
    #关闭worker
    def close(self):
        self.send(ActorExit)
    
    def send(self, paths):
        self._csv_to_process.append(paths)

    def _process(self, series, result_q):
        # ndigit参数控制雨流计数的精度，正代表小数点后几位。-2代表以100为分界计算。
        result = rainflow.count_cycles(series=series, ndigits=1)
        result_q.put(result)
    
    def run(self, result_q):
        while True:
            if self._csv_to_process:
                paths = self._csv_to_process.popleft()
                csv_files = gen_csvfiles(paths=paths)
                lines = gen_lines(csv_files=csv_files)
                self._process(lines, result_q)

            time.sleep(0.1)

@timer
def main():
    result_q = Queue()
    worker = Processor()
    worker.start(result_q)
    paths = ['/Users/sunlei/Documents/Github/ground_test_data_process/tests/testinput.csv']
    worker.send(paths)
    time.sleep(5)
    result= result_q.get()
    print(result)

if __name__ == "__main__":
    main()