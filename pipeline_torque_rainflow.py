import csv
import time
import rainflow
import pandas as pd
import sys
from collections import deque, defaultdict

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
        with open(file=path, newline='', encoding='gbk') as f:
            csv_file = csv.reader(f)
            yield csv_file

def gen_lines(csv_files=None, func=_time_bar):
    csv_file_processed = 0
    for csv_file in csv_files:
        _ = next(csv_file)
        csv_file_processed += 1
        for line in csv_file:
            yield line
        func(num=csv_file_processed, max_num=len(csv_files))

def gen_rainflow(lines):
    pass

class Worker():
    def __init__(self):
        self._csv_to_process = deque()
        self._result = []
    
    def load(self, paths):
        self._csv_to_process.append(paths)

    def _process(self, paths):
        csv_files = gen_csvfiles(paths=paths)
        lines = gen_lines(csv_files=csv_files)
        self._result.append(gen_rainflow(lines))
    
    def run(self):
        while True:
            if self._csv_to_process:
                paths = self._csv_to_process.popleft()
                self._process(paths)
            time.sleep(0.1)

def main():
    pass

if __name__ == "__main__":
    t0 = time.time()
    main()
    t1 = time.time()
    print('Running time is {}s'.format((t1-t0)))