import csv

from src.rainflow import Rainflow

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
        csv_files_torque = self.gen_csvfiles(paths=paths)
        csv_files_angal = self.gen_csvfiles(paths=paths)
        csv_files_c = self.gen_csvfiles(paths=paths)
        lines_torque = self.gen_lines(csv_files=csv_files_torque, header='a')
        lines_angal = self.gen_lines(csv_files=csv_files_angal, header='b')
        lines_c = self.gen_lines(csv_files=csv_files_c, header='c')
        digits_torque = self.gen_digits(lines_torque)
        digits_angal = self.gen_digits(lines_angal)
        digits_c = self.gen_digits(lines_c)
        rf = Rainflow(series=digits_torque, parameters=[('b', digits_angal),('c', digits_c)])
        #rf = Rainflow(series=digits_torque)
        result = rf.count_cycles(ndigits=0)  # ndigit参数控制雨流计数的精度，正代表小数点后几位。-2代表以100为分界计算。
        return result

    def gen_csvfiles(self, paths):
        self.total_files = len(paths)
        for path in paths:
            with open(file=path, newline='', encoding='gb18030') as f:  # 根据文件编码调整encoding 
                csv_file = csv.DictReader(f) # 读取每行作为一个字典，字典的键来自每个csv的第一行
                yield csv_file

    def gen_lines(self, csv_files, header):
        temp = None
        csv_file_processed = 0
        for csv_file in csv_files:
            for line in csv_file:
                if line[header]:
                    temp = line[header]
                yield temp
            csv_file_processed += 1
            print('{} / {} files processed.'.format(csv_file_processed, self.total_files))

    def gen_digits(self, lines):
        for line in lines:
            yield float(line)


class TestSolver(BaseSolver):

    def solver_method(self):
        pass
class VisualSolver(BaseSolver):

    def solver_method(self):
        pass


class ToCsv(BaseSolver):

    def solver_method(self):
        pass


SOLVERS = {
    '1': ('RainflowSolver', RainflowSolver),
    '2': ('VisualSolver', VisualSolver),
    '3': ('TestSolver', TestSolver)
}

def main():
    pass

if __name__ == '__main__':
    main()