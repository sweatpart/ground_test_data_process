import csv
import json

#导入具体算法模型
from src.rainflow import Rainflow
from src.dutycycle import DutyCycle
from src.db import get_db

class BaseSolver(object):

    def __init__(self):
        """
            抽象类方法，子类具体实现
        """
        pass

    def __repr__(self):
        return type(self).__name__

    def solver_method(self):
        """
            抽象类方法，子类具体实现
        """
        pass

    def gen_csvfiles(self, paths):
        self.total_files = len(paths)
        for path in paths:
            with open(file=path, newline='', encoding='gb18030') as f:  # 根据文件编码调整encoding 
                csv_file = csv.DictReader(f) # 读取每行作为一个字典，字典的键来自每个csv的第一行
                yield csv_file

    def gen_lines(self, csv_files):
        for csv_file in csv_files:
            for line in csv_file:
                yield line

    def gen_processed_lines(self):
        """
            抽象类方法，子类具体实现
        """
        pass

    def insert_db(self, result):
        db = get_db()
        record = {
            'user_id': 'sl',
            'project': 'test',
            'solver': self.__class__.__name__,
            'result': json.dumps(result) 
        }
        db['test'].insert_one(record)


class RainflowSolver(BaseSolver):

    def solver_method(self, paths, config):
        csv_files_main = self.gen_csvfiles(paths=paths)
        lines_main = self.gen_lines(csv_files=csv_files_main)
        digits_main = self.gen_processed_lines(lines=lines_main, header=config['main_parm'])

        parameters = []
        if config['optional_parms']:
            csv_files_optional = dict()
            lines_optionsal = dict()
            digits_optional = dict()

            for parm in config['optional_parms']:
                csv_files_optional[parm] = self.gen_csvfiles(paths=paths)
                lines_optionsal[parm] = self.gen_lines(csv_files=csv_files_optional[parm])
                digits_optional[parm] = self.gen_processed_lines(lines=lines_optionsal[parm], header=parm)
                parameters.append((parm, digits_optional[parm]))
        
        rf = Rainflow(series=digits_main, parameters=parameters)

        result = rf.count_cycles(ndigits=config['ndigits'])  # ndigit参数控制雨流计数的精度，正代表小数点后几位。-2代表以100为分界计算。
        self.insert_db(result)
        return result
    
    def gen_processed_lines(self, lines, header):
        data = None
        for line in lines:
            if line[header]:
                data = float(line[header])
            yield data


class DutyCycleSolver(BaseSolver):
    
    def solver_method(self, paths, config):
        csv_files = self.gen_csvfiles(paths=paths)
        lines = self.gen_lines(csv_files=csv_files)
        processed_line = self.gen_processed_lines(lines=lines, main_parm=config['main_parm'], optional_parms=config['optional_parms'])
        dc = DutyCycle(series=processed_line, config=config)
        result = dc.count_cycles()
        #print(result)
        self.insert_db(result)
        return result

    def gen_processed_lines(self, lines, main_parm, optional_parms):  
        last_parms = dict()
        for line in lines:
            for parm in optional_parms: # 填补次要参数的空值
                if line[parm]:
                    last_parms[parm] = line[parm]
                else:
                    line[parm] = last_parms[parm]
            if line[main_parm]:  # 如果主参数值非空则产出数据行
                yield line
                

class VisualSolver(BaseSolver):

    def solver_method(self):
        pass


class ToCsv(BaseSolver):

    def solver_method(self):
        pass


SOLVERS = {
    '1': ('RainflowSolver', RainflowSolver),
    '2': ('DutyCycleSolver', DutyCycleSolver)
}

def main():
    print('This module can only be imported.')

if __name__ == '__main__':
    main()