import csv
import time
import rainflow
import pandas as pd
import sys
from collections import deque
import functools
from threading import Thread, Event

class ActorExit(Exception):
    pass

def timer(func):
    @functools.wraps(func)
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
            csv_file = csv.reader(f)
            yield csv_file

def gen_lines(csv_files=None, func=_time_bar):
    csv_file_processed = 0
    for csv_file in csv_files:
        _ = next(csv_file)
        csv_file_processed += 1
        for line in csv_file:
            yield line

class Worker():
    def __init__(self):
        self._csv_to_process = deque()
        self._result = []
    
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
        counts = rainflow.count_cycles(series=series, ndigits=0)
        self._result.append(counts)
    
    def run(self):
        while True:
            if self._csv_to_process:
                series = self._csv_to_process.popleft()
                self._process(series)
            time.sleep(0.1)


#csv_files = gen_csvfiles(paths=paths)
#lines = gen_lines(csv_files=csv_files)
@timer
def main():
    worker = Worker()
    worker.start()
    worker.send([1,2,3,5,7,1,12,3,2])
    time.sleep(3)
    print(worker._result)

if __name__ == "__main__":
    main()