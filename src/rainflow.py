# coding: utf-8
"""
Implements rainflow cycle counting algorythm for fatigue analysis
according to section 5.4.4 in ASTM E1049-85 (2011).
"""
from __future__ import division
from collections import deque, defaultdict
import math
from functools import wraps

try:
    from importlib import metadata as _importlib_metadata
except ImportError:
    import importlib_metadata as _importlib_metadata

__version__ = _importlib_metadata.version("rainflow")



def cal_parameter(async_gens, method):

    def decorate(func):

        @wraps(func)
        def wapper(point1, point2, count):
            result = func(point1, point2, count)  #计算原函数所要实现的功能
            print(point1)
            print(point2)
            print(count)
            for async_gen in async_gens.values():
                data = async_gen.send((point1[0], point2[0]))
                result.append(method(data))  # 追加可选参数的区间平均值

            return result

        return wapper

    return decorate
    

class Rainflow(object):

    def __init__(self, series, parameters=None):
        """用于接收所需计算的各参数数据并完成初始化

        Args:
            series (iterable item): 用于计算雨流循环计数的可迭代对象，计算路谱时为扭矩元素生成器。
            parameters (list, optional): 可选的其他计算参数列表，列表元素为（‘header’, header对应的参数生成器）. Defaults to None.
        """
        self.series = iter(series)
        
        if parameters:  # 当有其他参数输入，参与运算
            self.parameters = parameters
            self.gen_parameter = dict()
            for header, parameter_series in self.parameters:
                self.gen_parameter[header] = self._async_parameter(parameter_series)
                next(self.gen_parameter[header])  # 预激角度等参数计算协程
    
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
                    checkbook[index] = temp
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
        
        @cal_parameter(self.gen_parameter, lambda x: sum(x)//len(x))  # 附加计算区间角度平均值
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

        if sum(value is not None for value in (ndigits, nbins, binsize)) > 1:
            raise ValueError(
                "Arguments ndigits, nbins and binsize are mutually exclusive"
            )
        counts = defaultdict(dict)
        cycles = (
            (rng, count, angal)
            for rng, mean, count, i_start, i_end, angal in self.extract_cycles(self.series)
        )
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
            for rng, count, angal in cycles:
                if angal in counts[round_(rng)]:
                    counts[round_(rng)][angal] += count
                else:
                    counts[round_(rng)][angal] = count
               
        else:
            for rng, count in cycles:
                counts[rng] += count

        return sorted(counts.items())