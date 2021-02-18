import csv
import time
import rainflow
import pandas as pd
import sys
from collections import deque
from functools import wraps, partial
from threading import Thread, Event

class ActorExit(Exception):
    pass

def timer(func):
    @wraps(func)
    def wapper(*args, **kargs):
        t0 = time.time()
        func(*args, **kargs)
        t1 = time.time()
        print('Running time of function {} is {}s'.format(func.__name__, (t1-t0)))
    return wapper


def _time_bar(num, max_num,len_of_bar=40, shape='#'):
    """A timebar show the progress. Mostly used for excel importing by far."""
    rate = float(num) / float(max_num)
    rate_percent = int(rate * 100)   
    rate_num = int(rate * len_of_bar)    
    sys.stdout.write('\r{}/{} complete - {}%| '.format(num, max_num, rate_percent) + shape*rate_num + ' '*(len_of_bar - rate_num) + ' |' + '.'*int(num%10) + ' '*10)   
    sys.stdout.flush() 
    return True

def gen_csvfiles(paths=None):
    for path in paths:
        with open(file=path, newline='', encoding='utf-8') as f:
            csv_file = csv.DictReader(f) # 每行作为一个字典，字典的键来自每个csv的第一行
            yield csv_file

def gen_lines(csv_files=None, func=_time_bar):
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