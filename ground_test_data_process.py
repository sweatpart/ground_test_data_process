# -*- coding: utf-8 -*-
import os
import sys
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sqlalchemy import create_engine
import pymysql
import rainflow

ENGINE_URL = 'mysql+pymysql://root:Haojiyou11235@localhost:3306/sys'
VEL_SPEED = 'WhlGndVelLNonDrvnHSC1[km/h]'
TORQUE_RL = 'Torque_RL[Nm]'

def wrapper(func):
    def inner(*args,**kwargs):
        """函数执行之前的操作"""
        start_time=time.time()
        time.sleep(4)
        res=func(*args,**kwargs)
        dur=time.time()-start_time
        print("该函数的执行时间：%s" %dur)
        """函数执行后执行的操作"""
        return res
    return inner

class DataProcess(object):
    """A class which can process the excel test data.

    Longer class information:NA

    Attributes:
        path: A string indicating EXCEL file path.
        common_name: A string indicating the pocessing file name.
        data: A dataFrame containing test data imported from EXCEL file.
    """
    def __init__(self):
        self.file_name = None
        self.common_name = None
        self.data = None
        self.distribution_results = dict()

    def __repr__(self):
        class_name = type(self).__name__
        return '{}({!r})'.format(class_name, self.file_name) 

    def __getitem__(self, columne_name=None):
        try:
            result = self.data[columne_name]
            print(self.common_name + 'Fetch data of column {}.'.format(columne_name)) 
            return result
        except:
            print(self.common_name + 'Data has no column name {}.'.format(columne_name))
            raise AttributeError 

    def info(self):
        try:
            result = self.data.info()
            return result
        except:
            print(self.common_name + 'Data not established.') 

    def data_from_excel(self, path=None):
        if os.path.exists(path):   # 检查文件路径是否存在，如不存在报出异常
            self.file_name = path.split('/')[-1]
            self.common_name = '--> DATA FILE: {}  |  '.format(self.file_name)   # 从路径里取出文件名
        else:
            print('File does not exist. Please check.')
            raise FileNotFoundError 
        print(self.common_name + 'Opening file, please wait...')
        with pd.io.excel.ExcelFile(path) as excel_file:
            print(self.common_name + 'File opened successfully!')
            print(self.common_name + 'Importing sheets.')
            sheet_names = excel_file.sheet_names
            sheet_count = 0
            for sheet_name in sheet_names:
                data_temp = pd.read_excel(excel_file, sheet_name)   # 读取一个sheet到缓存
                self.data = data_temp if self.data is None else pd.concat([self.data, data_temp], ignore_index = True)   # 拼接所有sheet
                sheet_count += 1
                self._time_bar(num = float(sheet_count) / len(sheet_names) * 40)
                print('\n')
            print(self.common_name + 'Sheets imported successfully.')
        print(self.common_name + 'Excel file closed')
        return self

    def data_from_sql(self, analysis_object=None):
        engine = create_engine(ENGINE_URL)
        self.file_name = analysis_object
        self.common_name = '--> DATA FILE: {}  |  '.format(self.file_name)
        try:
            print(self.common_name + 'Importing data from mySQL...')  
            self.data = pd.read_sql_table(analysis_object, engine)  
        except:
            print(self.common_name + 'SQL data not exist.')
        else:
            self.data = pd.read_sql_table(analysis_object, engine)
            print(self.common_name + 'Importing data successfully.')
        return self

    def data_to_sql(self, sql_file_name=None):
        if sql_file_name is None:
            sql_file_name = input(self.common_name + 'Please define the name of data: ')
        engine = create_engine(ENGINE_URL)
        try:
            self.data.to_sql(sql_file_name, engine)   # 将数据存入数据库
        except:
            print(self.common_name + 'Error occur during transferring data to mySQL!')
            raise
        else:
            print(self.common_name + 'Data [{}] has established in mySQL.'.format(sql_file_name))
        return self

    def data_to_file(self, path=None):
        if os.path.exists(path) is False:   # 导出数据到CSV文件，如无所需目录则创建一个
            os.mkdir(path)
            print(self.common_name + 'Forlder not found. Establishing folder {}.'.format(path))
        for key, item in self.distribution_results:
            item.to_csv(path_or_buf = path + '/{}.csv'.format(key))
            print(self.common_name + 'Data distribution report of {} saved in {}.',format(key, path))
        
    def data_wash(self, drop_columns=None):
        """Dropping data columns.

        Some columns in the data may not be useful. You can choose to drop them before 
        the data imported to SQL where you can save storage,

        Args:
            drop_columns: A list indicating which list to be dropped.

        Returns:
            Self for chain calling.

        Raises:
            NA
        """
        if drop_columns is not None:
            try:
                self.data.drop(columns = self.data.columns[drop_columns], inplace=True)
                print(self.common_name + 'Columns {} dropped successfully!'.format(drop_columns))
            except:
                pass
        for column in self.data.columns:
            if column is not TORQUE_RL:
                self.data[column] = self.data[column].fillna(method = 'ffill')   # 填补采样率不同造成的不同数据列中空行
                self.data[column] = self.data[column].fillna(method = 'bfill')   # 同上
        print(self.common_name + 'Filling NA data successfully! (except line {})'.format(TORQUE_RL))
        self.data.dropna(subset = [TORQUE_RL], inplace = True)  # 根据扭矩列采样周期去掉其他列中的行
        print(self.common_name + 'Dropping NA data based on line {} successfully!'.format(TORQUE_RL))
        return self

    def data_merge(self, another_data=None):
        try:   # 尝试根据要求合并文件，失败则报错
            self.data = pd.concat([self.data, another_data.data], ignore_index=True)   # 合并所选择excel文件或SQL导入的数据
        except:
            print(self.common_name + 'Error occur during merging data!')
            raise
        else:
            print(self.common_name + 'Data merged successfully!')
            return self

    def hist_distribution(self, distribution_object=None, path=None):
        """
        """
        range_of_data = max(self.data[distribution_object]) - min(self.data[distribution_object])
        if 100 < range_of_data < 1000:   # 不同数据数量级不同，直方图间隔不同
            bins_gap = 10
        elif range_of_data > 1000:
            bins_gap = 100
        else:
            bins_gap = 1
        limit = {'lower_limit': (int(min(self.data[distribution_object]/bins_gap)) - 1) * bins_gap,\
                 'upper_limit': (int(max(self.data[distribution_object]/bins_gap)) + 2) * bins_gap}
        num_of_bins = np.arange(limit['lower_limit'], limit['upper_limit'], bins_gap)   # array([limit['lower_limit'] ... limit['upper_limit'] - bins_gap]), 因此上一行要 + 2
        n, bins, patches = plt.hist(self.data[distribution_object], bins = num_of_bins, density = 0)
        header = (distribution_object.split('[')[0] + '_value_average', distribution_object.split('[')[0] + '_value_num')   # 命名导出数据的标题
        content = (map(lambda x : x + bins_gap/2, bins[0 : len(bins) - 1]), n)   # 取每一个数据区间的中值代表其扭矩特征
        result = pd.DataFrame(dict(zip(header, content)))   
        self.distribution_results[distribution_object.split('[')[0] + '(hist)'] = result
        return result

    def rainflow_distribution(self, distribution_object=None, ndigits_user=-2):
        result = rainflow.count_cycles(self.data[distribution_object], ndigits=ndigits_user)   # ndigit参数控制雨流计数的精度，正代表小数点后几位。-2代表以100为分界计算。
        self.distribution_results[distribution_object.split('[')[0] + '(rainflow)'] = result
        return result

    def _time_bar(self, num=None, max_num=40, shape='█'):
        rate = float(num) / float(max_num)
        rate_percent = int(rate * 100)   
        rate_num = int(rate * max_num)    
        sys.stdout.write('\r%d%%| ' % rate_percent + shape*rate_num + ' '*(max_num - rate_num) + ' |')   
        sys.stdout.flush() 
        return True

if __name__ == "__main__":
    print('This module is only for importing.')