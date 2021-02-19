import csv
import time
import rainflow
import pandas as pd
import sys
from collections import deque
from functools import partial
from threading import Thread, Event
from tools import timer

class ActorExit(Exception):
    pass

def gen_csvfiles(paths=None):
    for path in paths:
        with open(file=path, newline='', encoding='utf-8') as f:
            csv_file = csv.DictReader(f) # 每行作为一个字典，字典的键来自每个csv的第一行
            yield csv_file

def gen_lines(csv_files=None):
    csv_file_processed = 0
    key = 0
    for csv_file in csv_files:
        csv_file_processed += 1
        for line in csv_file:
            yield int(line[key])

class Worker():
    def __init__(self):
        self._csv_to_process = deque()
        self._results = []
    
    #定义一个后台服务线程
    def start(self):
        self._terminated = Event()
        t = Thread(target=self._bootstrap)
        t.daemon = True
        t.start()
    
    def _bootstrap(self):
        try:
            self.run()
        except ActorExit:
            pass
        finally:
            self._terminated.set()
    
    #关闭worker
    def close(self):
        self.send(ActorExit)
    
    def send(self, paths):
        self._csv_to_process.append(paths)

    def _process(self, series):
        # ndigit参数控制雨流计数的精度，正代表小数点后几位。-2代表以100为分界计算。
        result = rainflow.count_cycles(series=series, ndigits=1)
        self._results.append(result)
    
    def run(self):
        while True:
            if self._csv_to_process:
                series = self._csv_to_process.popleft()
                self._process(series)
            time.sleep(0.1)

@timer
def main():
    worker = Worker()
    worker.start()
    paths = ['/Users/sunlei/Documents/Github/ground_test_data_process/tests/testinput.csv']
    csv_files = gen_csvfiles(paths=paths)
    lines = gen_lines(csv_files=csv_files)
    worker.send(lines)
    time.sleep(5)

if __name__ == "__main__":
    main()