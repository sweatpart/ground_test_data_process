# coding: utf-8
"""
Implements rainflow cycle counting algorythm for fatigue analysis
according to section 5.4.4 in ASTM E1049-85 (2011).
"""
from __future__ import division
from collections import deque, defaultdict
import math
from functools import wraps

""" try:
    from importlib import metadata as _importlib_metadata
except ImportError:
    import importlib_metadata as _importlib_metadata

__version__ = _importlib_metadata.version("rainflow") """


class Rainflow(object):

    def __init__(self, series, parameters=None):
        """用于接收所需计算的各参数数据并完成初始化

        Args:
            series (iterable item): 用于计算雨流循环计数的可迭代对象，计算路谱时为扭矩元素生成器。
            parameters (list, optional): 可选的其他计算参数列表，列表元素为（‘header’, header对应的数据行生成器）. Defaults to None.
        """
        self.series = iter(series)
        self.parameters = None
        
        if parameters:  # 当有其他参数输入，参与运算
            self.parameters = parameters
            self.gen_parameters = dict()
            for header, parameter_series in self.parameters:
                self.gen_parameters[header] = self._async_parameter(parameter_series)
                next(self.gen_parameters[header])  # 预激角度等参数计算协程
    
    def _async_parameter(self, series):
        """用于提取可选参数数据区间内值的协程

        Args:
            series (iterable item): 含可选参数对应数据的可迭代对象.

        Yields:
            int: 根据主线程发进来的起始index提取区间内数据
        """
        series = iter(series)
        index = 0
        checkbook = dict()
        result = None
        while True:
            start, stop = yield result  # 计算平均值并取整
            result = []
            while index <= stop:
                temp = next(series)
                if temp is not None:  # 数据行非空值
                    checkbook[index] = abs(temp)
                index += 1
            for i in range(start, stop+1):
                if i in checkbook.keys():
                    result.append(checkbook.pop(i))
                         

    def reversals(self, series):
        """Iterate reversal points in the series.

        A reversal point is a point in the series at which the first derivative
        changes sign. Reversal is undefined at the first (last) point because the
        derivative before (after) this point is undefined. The first and the last
        points are treated as reversals.

        Parameters
        ----------
        series : iterable sequence of numbers

        Yields
        ------
        Reversal points as tuples (index, value).
        """
        series = iter(series)

        x_last, x = next(series), next(series)
        d_last = (x - x_last)
        yield 0, x_last

        for index, x_next in enumerate(series, start=1):    
            if x_next == x:
                continue
            d_next = x_next - x
            if d_last * d_next < 0:
                yield index, x
            x_last, x = x, x_next
            d_last = d_next
        
        yield index + 1, x_next


    def extract_cycles(self, series):
        """Iterate cycles in the series.

        Parameters
        ----------
        series : iterable sequence of numbers

        Yields
        ------
        cycle : tuple
            Each tuple contains (range, mean, count, start index, end index).
            Count equals to 1.0 for full cycles and 0.5 for half cycles.
        """
        points = deque()
        
        def format_output(point1, point2, count):
            i1, x1 = point1
            i2, x2 = point2
            rng = abs(x1 - x2)
            mean = 0.5 * (x1 + x2) 
            return [rng, mean, count, i1, i2]

        for point in self.reversals(series):
            points.append(point)

            while len(points) >= 3:
                # Form ranges X and Y from the three most recent points
                x1, x2, x3 = points[-3][1], points[-2][1], points[-1][1]
                X = abs(x3 - x2)
                Y = abs(x2 - x1)

                if X < Y:
                    # Read the next point
                    break
                elif len(points) == 3:
                    # Y contains the starting point
                    # Count Y as one-half cycle and discard the first point
                    yield format_output(points[0], points[1], 0.5)
                    points.popleft()
                else:
                    # Count Y as one cycle and discard the peak and the valley of Y
                    yield format_output(points[-3], points[-2], 1.0)
                    last = points.pop()
                    points.pop()
                    points.pop()
                    points.append(last)
        else:
            # Count the remaining ranges as one-half cycles
            while len(points) > 1:
                yield format_output(points[0], points[1], 0.5)
                points.popleft()


    def count_cycles(self, ndigits=None, nbins=None, binsize=None):
        """Count cycles in the series.

        Parameters
        ----------
        series : iterable sequence of numbers
        ndigits : int, optional
            Round cycle magnitudes to the given number of digits before counting.
            Use a negative value to round to tens, hundreds, etc.
        nbins : int, optional
            Specifies the number of cycle-counting bins.
        binsize : int, optional
            Specifies the width of each cycle-counting bin

        Arguments ndigits, nbins and binsize are mutually exclusive.

        Returns
        -------
        A sorted list containing pairs of range and cycle count.
        The counts may not be whole numbers because the rainflow counting
        algorithm may produce half-cycles. If binning is used then ranges
        correspond to the right (high) edge of a bin.
        """

        def _get_round_function(ndigits=None):
            if ndigits is None:
                return lambda x: x
            else:
                return lambda x: round(x, ndigits)

        def _cal_parameter(gen_parameters, process_method, start, stop):
            result = []
            for gen_parameter in gen_parameters.values():
                data = gen_parameter.send((start, stop))  # 获得区间内参数值列表
                result.append(process_method(data))
            return result

        def rec_dd():
            return defaultdict(rec_dd)  # 用于循环建立defaultdict

        counts = rec_dd()
        #counts = defaultdict(dict) if self.parameters else defaultdict(float)  # 根据需计算参数个数定义
            
        if sum(value is not None for value in (ndigits, nbins, binsize)) > 1:
            raise ValueError(
                "Arguments ndigits, nbins and binsize are mutually exclusive"
            )
        
        parameter_process_method = lambda x: sum(x)//len(x)

        cycles = (
            [rng, count] + [_cal_parameter(self.gen_parameters, parameter_process_method, i_start, i_end)] if self.parameters else [rng, count]
            for rng, mean, count, i_start, i_end in self.extract_cycles(self.series)
        )  # 如果parameters有可选参数需要计算，则进行追加

        if nbins is not None:
            binsize = (max(self.series) - min(self.series)) / nbins

        if binsize is not None:
            nmax = 0
            for rng, count in cycles:
                n = int(math.ceil(rng / binsize))  # using int for Python 2 compatibility
                counts[n * binsize] += count
                nmax = max(n, nmax)

            for i in range(1, nmax):
                counts.setdefault(i * binsize, 0.0)

        elif ndigits is not None:
            round_ = _get_round_function(ndigits)
            if self.parameters:
                for rng, count, parameters in cycles:
                    rounded_rng = int(round_(rng))
                    print(rng)
                    sub_dict = counts[rounded_rng]
                    while parameters:
                        if len(parameters) == 1:
                            temp = int(parameters.pop())
                            if sub_dict[temp]:
                                sub_dict[temp] += count
                            else:
                                sub_dict[temp] = count
                        else:
                            sub_dict = sub_dict[int(parameters.pop())]
                    print(counts)
            else:
                for rng, count in cycles:
                    if counts[round_(rng)]:
                        counts[round_(rng)] += count
                    else:
                        counts[round_(rng)] = count
       
        else:
            for rng, count in cycles:
                counts[rng] += count
        print(counts)
        return counts
        #return sorted(counts.items())