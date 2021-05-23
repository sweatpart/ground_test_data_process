from functools import wraps
import time
import sys

def timer(func):
    @wraps(func)
    def wapper(*args, **kargs):
        t0 = time.time()
        func(*args, **kargs)
        t1 = time.time()
        print('Running time of function {} is {}s'.format(func.__name__, (t1-t0)))
    return wapper

def time_bar(rate, max_num=40, shape='█'):
    """A timebar show the progress. Mostly used for excel importing by far."""
    rate_percent = int(rate * 100)   
    rate_num = int(rate * max_num)    
    sys.stdout.write('\r%d%%| ' % rate_percent + shape*rate_num + ' '*(max_num - rate_num) + ' |')   
    sys.stdout.flush() 
    return True