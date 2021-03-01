import csv

import rainflow

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


class RainflowSolver(BaseSolver):

    def solver_method(self, paths):
        csv_files = self.gen_csvfiles(paths=paths)
        lines = self.gen_lines(csv_files=csv_files)
        result = rainflow.count_cycles(series=lines, ndigits=1)  # ndigit参数控制雨流计数的精度，正代表小数点后几位。-2代表以100为分界计算。
        return result

    def gen_csvfiles(self, paths=None):
        for path in paths:
            with open(file=path, newline='', encoding='utf-8') as f:
                csv_file = csv.DictReader(f) # 每行作为一个字典，字典的键来自每个csv的第一行
                yield csv_file

    def gen_lines(self, csv_files=None):
        csv_file_processed = 0
        key = 'a'
        for csv_file in csv_files:
            csv_file_processed += 1
            for line in csv_file:
                yield int(line[key])


class TestSolver(BaseSolver):

    def solver_method(self):
        pass

class VisualSolver(BaseSolver):

    def solver_method(self):
        pass

SOLVERS = {
    '1': ('RainflowSolver', RainflowSolver),
    '2': ('VisualSolver', VisualSolver),
    '3': ('TestSolver', TestSolver)
}