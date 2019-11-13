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

ENGINE_URL = 'mysql+pymysql://root:Haojiyou11235@localhost:3306/sys'   # 定义SQL数据库路径

class DataProcess(object):
    """Process test data in EXCEL file

    Test data in excel file may too hard to be analysed with excel itself.
    The class is a handful tool to convert the excel file to DataFrame where 
    the pandas module can help us a lot.

    Attributes:
        file_name: A string indicating the name of excel file.
        common_name: A string indicating the common part of output.
        data: A dataFrame containing test data imported from excel file or MySQL.
        distribution_results: A dict to save distrition results of the data columns.
    """
    def __init__(self):
        """Initial the attributes of the class."""
        self.file_name = None
        self.common_name = None
        self.data = None
        self.distribution_results = dict()

    def __repr__(self):
        """Representing the information of class instance."""
        class_name = type(self).__name__
        return '{}({!r})'.format(class_name, self.file_name) 

    def __getitem__(self, column_name=None):
        """Getting the column of data

        Args:
            columne: A string indicating which list to be dropped.

        Returns:
            Sepecific column indicated by column_name.

        Raises:
            AttributeError: An error occurred when the specific column is
            not existed in the data.
        """
        try:
            result = self.data[column_name]
            print(self.common_name + 'Fetch data of column {}'.format(column_name)) 
            return result
        except:
            print(self.common_name + 'Data has no column name {}'.format(column_name))
            raise AttributeError 

    def info(self):
        """Return the info of the data. Basically just use the DataFrame.info() method."""
        try:
            result = self.data.info()
            return result
        except:
            print(self.common_name + 'Data not established') 

    def data_from_excel(self, path=None):
        """Importing excel file to DataFrame.

        Args:
            path: A string indicating the excel file path.

        Returns:
            Self for chain calling.

        Raises:
            FileNotFoundError: An error ocurred accessing excel file not existed.
        """
        if os.path.exists(path):   # 检查文件路径是否存在，如不存在报出异常
            self.file_name = path.split('/')[-1]   # 从路径里取出文件名
            self.common_name = '--> DATA FILE: {}  |  '.format(self.file_name)
        else:
            raise FileNotFoundError('File does not exist. Please check.') 
        print(self.common_name + 'Opening file, please wait...')
        with pd.io.excel.ExcelFile(path) as excel_file:
            print(self.common_name + 'File opened successfully')
            print(self.common_name + 'Importing sheets...')
            sheet_names = excel_file.sheet_names
            sheet_count = 0
            for sheet_name in sheet_names:
                data_temp = pd.read_excel(excel_file, sheet_name)   # 读取一个sheet到缓存
                self.data = data_temp if self.data is None else pd.concat([self.data, data_temp], ignore_index = True)   # 拼接所有sheet
                sheet_count += 1
                self._time_bar(num = float(sheet_count) / len(sheet_names) * 40)
            self.data = self.data.iloc[0:-8]
            print('\n')   # 从进度条换行
            print(self.common_name + 'Sheets imported successfully')
        print(self.common_name + 'Excel file closed')
        return self

    def data_from_sql(self, analysis_object=None):
        """Importing MySQL table to DataFrame.

        Args:
            analysis_object: A string indicating the MySQL table name.

        Returns:
            Self for chain calling.

        Raises:
            NA
        """
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
            print(self.common_name + 'Importing data successfully')
        return self

    def data_to_sql(self, sql_file_name=None):
        """Transferring DataFrame type data to MySQL

        Some columns in the data may not be useful. You can choose to drop them before 
        the data imported to SQL where you can save storage,

        Args:
            sql_file_name: A string indicating which list to be dropped.

        Returns:
            Self for chain calling.

        Raises:
            NA
        """
        if sql_file_name is None:
            sql_file_name = input(self.common_name + 'Please define the name of data: ')
        engine = create_engine(ENGINE_URL)
        try:
            self.data.to_sql(sql_file_name, engine)   # 将数据存入数据库
        except:
            print(self.common_name + 'Error occur during transferring data to mySQL')
            raise
        else:
            print(self.common_name + 'Data [{}] has established in mySQL'.format(sql_file_name))
        return self

    def data_to_file(self, path=None):
        """Saving distrition_results to csv files seperatelly.

        Args:
            path: A string indicating dictionary path to save csv files.

        Returns:
            True for indicating of method successful.

        Raises:
            NA
        """
        if os.path.exists(path) is False:   # 导出数据到CSV文件，如无所需目录则创建一个
            try:
                os.mkdir(path)
            except:
                #print(self.common_name + 'Wrong path {}.'.format(path))
                raise
            print(self.common_name + 'Forlder not found. Establishing folder {}'.format(path))
        for key, item in self.distribution_results.items():
            item.to_csv(path_or_buf = path + '/{}.csv'.format(key))
            print(self.common_name + 'Report <{}> restored in {}'.format(key, path))
        return True
        
    def data_merge(self, another_data=None):
        """Merging the data attribute of second instance into the first one.

        Args:
            another_data: A DataPocess instance ofr merging.

        Returns:
            Self for chain calling.

        Raises:
            NA
        """
        try:   # 尝试根据要求合并文件，失败则报错
            self.data = pd.concat([self.data, another_data.data], ignore_index=True)   # 合并所选择excel文件或SQL导入的数据
        except:
            print(self.common_name + 'Error occur during merging data')
            raise
        else:
            print(self.common_name + 'Data merged successfully')
            return self

    def hist_distribution(self, distribution_object=None):
        """Analysing the hist distribution of specific object.

        Args:
            distrition_object: A string indicating the column for distribution analysis.

        Returns:
            A DataFrame instance show the hist distribution result of the object.

        Raises:
            NA
        """
        distribution_object_dropna = self.data[distribution_object].dropna()
        range_of_data = max(distribution_object_dropna) - min(distribution_object_dropna)
        if 100 < range_of_data < 1000:   # 不同数据数量级不同，直方图间隔不同
            bins_gap = 10
        elif range_of_data > 1000:
            bins_gap = 100
        else:
            bins_gap = 1
        limit = {'lower_limit': (int(min(distribution_object_dropna/bins_gap)) - 1) * bins_gap,\
                 'upper_limit': (int(max(distribution_object_dropna/bins_gap)) + 2) * bins_gap}
        num_of_bins = np.arange(limit['lower_limit'], limit['upper_limit'], bins_gap)   # array([limit['lower_limit'] ... limit['upper_limit'] - bins_gap]), 因此上一行要 + 2
        n, bins, __ = plt.hist(distribution_object_dropna, bins = num_of_bins, density = 0)
        header = (distribution_object.split('[')[0] + '_value_average',\
                  distribution_object.split('[')[0] + '_value_num')   # 命名导出数据的标题
        content = (map(lambda x : x + bins_gap/2, bins[0 : len(bins) - 1]), n)   # 取每一个数据区间的中值代表其扭矩特征
        result = pd.DataFrame(dict(zip(header, content)))   
        self.distribution_results[distribution_object.split('[')[0] + '(hist)'] = result
        print(self.common_name + 'Hist distribution analysis of <{}> done'.format(distribution_object))
        return result

    def rainflow_distribution(self, distribution_object=None, ndigits_user=-2):
        """Analysing the rainflow distribution of specific object.

        Args:
            distrition_object: A string indicating the column for distribution analysis.
            ndigits_user: A interger indicating the wide for rainflow count.

        Returns:
            A DataFrame instance show the rainflow distribution result of the object.

        Raises:
            NA
        """
        distribution_object_dropna = self.data[distribution_object].dropna()
        result = rainflow.count_cycles(distribution_object_dropna, ndigits=ndigits_user)   # ndigit参数控制雨流计数的精度，正代表小数点后几位。-2代表以100为分界计算。
        self.distribution_results[distribution_object.split('[')[0] + '(rainflow)'] = result
        return result

    def _time_bar(self, num=None, max_num=40, shape='█'):
        """A timebar show the progress. Mostly used for excel importing by far."""
        rate = float(num) / float(max_num)
        rate_percent = int(rate * 100)   
        rate_num = int(rate * max_num)    
        sys.stdout.write('\r%d%%| ' % rate_percent + shape*rate_num + ' '*(max_num - rate_num) + ' |')   
        sys.stdout.flush() 
        return True

if __name__ == "__main__":
    print('This module is only for importing.')