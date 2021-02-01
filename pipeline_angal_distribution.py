import csv
import time
import rainflow
import pandas as pd
import sys
#目标是发现各个角度区间的扭矩循环数
#角度区间[0,1], [1, 2], [2, 3], [3, 4]
DRIVER_NO = 2
FILES_NO = 950

def _time_bar(num, max_num,len_of_bar=40, shape='#'):
    """A timebar show the progress. Mostly used for excel importing by far."""
    rate = float(num) / float(max_num)
    rate_percent = int(rate * 100)   
    rate_num = int(rate * len_of_bar)    
    sys.stdout.write('\r{}/{} complete - {}%| '.format(num, max_num, rate_percent) + shape*rate_num + ' '*(len_of_bar - rate_num) + ' |' + '.'*int(num%10) + ' '*10)   
    sys.stdout.flush() 
    return True
#pipline of data process
def gen_csvfiles(path=None, files_num=None):
    for i in range(1,files_num+1):
        with open(file='{}/{}.csv'.format(path, i), newline='', encoding='gbk') as f:
            yield f

def gen_from_csvs(files=None, func=_time_bar):
    csv_file_processed = 0
    for f in files:
        csvfile = csv.reader(f)
        header = next(csvfile)
        csv_file_processed += 1
        func(num=csv_file_processed, max_num=FILES_NO)
        #sys.stdout.write('\r{} csvs have been processed'.format(csv_file_processed) + '.'*int(csv_file_processed%10) + ' '*10)
        #sys.stdout.flush()
        for line in csvfile:
            yield line

def gen_from_csv(path=None):
    with open(path, newline='', encoding='gbk') as f:
        csvfile = csv.reader(f)
        header = next(csvfile)
        for line in csvfile:
            yield line

def gen_rainflow(lines):
    data_chunk = []
    angal = None
    user_asc = angal_scope_checker()
    for line in lines:
        if line[5]:
            angal = int(float(line[5]))
            is_angal_scope_change, last_angal_scope = user_asc(angal=angal)
        if line[3]:
            torque = int(float(line[3]))
            if angal is not None and is_angal_scope_change and len(data_chunk) >= 2:
                yield (last_angal_scope, rainflow.count_cycles(pd.DataFrame({'TORQUE':data_chunk})['TORQUE'], ndigits=-2))
                # rainflow返回的数据格式为元组组成的元组
                data_chunk = []            
            data_chunk.append(torque)
    if data_chunk:
        yield (last_angal_scope, rainflow.count_cycles(pd.DataFrame({'TORQUE':data_chunk})['TORQUE'], ndigits=-2))

def angal_scope_checker():
    last_angal_scope = None
    def angal_scope(angal):
        if angal in range(-5, 6):
            return '<5'
        else:
            return '>5'
    def inner(angal):
        nonlocal last_angal_scope
        now_angal_scope = angal_scope(angal)
        if last_angal_scope is None:
            last_angal_scope = now_angal_scope
            return (False, last_angal_scope)
        if now_angal_scope is not last_angal_scope:
            last_angal_scope = now_angal_scope
            return (True, last_angal_scope)
        else:
            return (False, last_angal_scope)
    return inner

if __name__ == "__main__":
    t0 = time.time()
    report = {i : dict() for i in ['<5', '>5']}
    report_angal = {i : 0 for i in range(-15, 16)}
    files = gen_csvfiles(path='/Users/sunlei/Desktop/csvfiles/{}/csv'.format(DRIVER_NO), files_num=FILES_NO)
    lines = gen_from_csvs(files=files) 
    for line in lines:
        if line[5]:
            angal = int(float(line[5]))
            report_angal[angal] += 1
            
    data_chunks = gen_rainflow(lines=lines)
    for data_chunk in data_chunks:
        angal_scope, data_cells = data_chunk
        #print(angal_scope, data_cells)
        for data_cell in data_cells:
            torque_amplitude, count = data_cell
            if report[angal_scope].get(torque_amplitude):
                report[angal_scope][torque_amplitude] += count
            else:
                report[angal_scope][torque_amplitude] = count
    print('\n')
    print('-' * 42)
    t1 = time.time()
    print('Running time is {}s'.format((t1-t0)))
    print('THE REPORT IS AS BELOW:')
    print(report_angal)