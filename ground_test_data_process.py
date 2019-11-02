# -*- coding: utf-8 -*-
import os
import sys
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np
from sqlalchemy import create_engine
import pymysql
import rainflow

ENGINE_URL = 'mysql+pymysql://root:Haojiyou11235@localhost:3306/sys'
VEL_SPEED = 'WhlGndVelLNonDrvnHSC1[km/h]'
TORQUE_RL = 'Torque_RL[Nm]'

class ExcelProcess(object):
    """A class which can process the excel test data.

    Longer class information:NA

    Attributes:
        path: A string indicating EXCEL file path.
        common_name: A string indicating the pocessing file name.
        data: A dataFrame containing test data imported from EXCEL file.
    """
    def __init__(self, path=None):
        self.path = path
        self.common_name = '--> EXCEL FILE: {}  |  '.format(path.split('/')[-1])   # 从路径里取出文件名
        self.data = None
        print(self.common_name + 'Initial done!')
    def __repr__(self):
        pass

    def info(self):
        try:
            result = self.data.info()
            return result
        except:
            print(self.common_name + 'Data not established.') 

    def __getitem__(self, columne_name):
        try:
            result = self.data[columne_name]
            print(self.common_name + 'Fetch data of column {}.'.format(columne_name)) 
            return result
        except:
            print(self.common_name + 'Data has no column name {}.'.format(columne_name)) 

    def excel_import_data(self):
        print(self.common_name + 'Opening file, please wait...')
        with pd.io.excel.ExcelFile(self.path) as excel_file:
            print(self.common_name + 'File opened successfully!')
            print(self.common_name + 'Importing sheets.')
            sheet_names = excel_file.sheet_names
            sheet_count = 0
            for sheet_name in sheet_names:
                data_temp = pd.read_excel(excel_file, sheet_name)
                if self.data is None:
                    self.data = data_temp
                else:
                    self.data = pd.concat([self.data, data_temp], ignore_index = True)
                sheet_count += 1
                self.time_bar(num = float(sheet_count) / len(sheet_names) * 40)
                print(self.common_name + 'Sheets imported successfully.')
        print(self.common_name + 'Excel file closed')
        return self

    def wash_data(self, drop_columns=None):
        """Dropping data columns.

        Some columns in the data may not be useful. You can choose to
        drop them before the data imported to SQL where you can save 
        storage,

        Args:
            drop_columns: A list indicating which list to be dropped.

        Returns:
            Self for chain calling.

        Raises:
            NA
        """
        self.data.drop(columns = self.data.columns[drop_columns], inplace = True)
        self.data[VEL_SPEED] = self.data[VEL_SPEED].fillna(method = 'ffill')
        self.data[VEL_SPEED] = self.data[VEL_SPEED].fillna(method = 'bfill')
        self.data.dropna(subset = [TORQUE_RL], inplace = True)  # clear null line in torque_Rl
        print(self.common_name + 'Data washed successfully!')
        return self

    def merge_data(self, another_excel_data=None):
        self.data = pd.concat([self.data, another_excel_data.data], ignore_index = True)
        print(self.common_name + 'Data merged successfully!')
        return self

    def data_to_sql(self, sql_file_name='data_of_test'):
        engine = create_engine(ENGINE_URL)
        self.data.to_sql(sql_file_name, engine)
        print(self.common_name + 'Data [{}] has established in mySQL.'.format(sql_file_name))
        return self

    def time_bar(self, num = None, max_num = 40, shape = '█'):
        rate = float(num) / float(max_num)
        rate_percent = rate * 100   
        rate_num = int(rate * max_num)    
        print('\r{}%| '.format(rate_percent) + shape*rate_num + ' '*(max_num - rate_num) + ' |', flush=True)
        # sys.stdout.write('\r%d%%| ' % rate_percent + shape*rate_num + ' '*(max_num - rate_num) + ' |')   
        # sys.stdout.flush() 
        return True


class DataAnalysis(object):
    def __init__(self, analysis_object=None, path=None):
        self.common_name = '--> ANALYSIS OBJECT: {}  |  '.format(analysis_object)
        print(self.common_name + 'Pocess start.')
        engine = create_engine(ENGINE_URL)
        self.data = pd.read_sql_table(analysis_object, engine)
        self.path = path
        print(self.common_name + 'Import data finished.')

    def info(self):
        try:
            result = self.data.info()
            return result
        except:
            print(self.common_name + 'Data not existed.') 

    def __getitem__(self, columne_name):
        try:
            result = self.data[columne_name]
            print(self.common_name + 'Fetch data of column {}.'.format(columne_name)) 
            return result
        except:
            print(self.common_name + 'Data has no column named {}.'.format(columne_name)) 

    def hist_distribution(self, distribution_object=None, plot_flag=False, norm_fit_flag=False, kde_fit_flag=False):
        """
        """
        bins_gap = 100 if max(self.data[distribution_object]) > 200 else 10   # 针对不同数量级，直方图间隔不同
        limit = {'lower_limit': (int(min(self.data[distribution_object]/bins_gap)) - 1) * bins_gap, 'upper_limit': (int(max(self.data[distribution_object]/bins_gap)) + 2) * bins_gap}
        num_bins_hist = np.arange(limit['lower_limit'], limit['upper_limit'], bins_gap)   # array([limit['lower_limit'] ... limit['upper_limit'] - bins_gap]), 因此上一行要 + 2
        n, bins, patches = plt.hist(self.data[distribution_object], bins = num_bins_hist, density = 0, facecolor = 'blue', edgecolor = 'k', alpha = 0.7, rwidth = 0.9)
        header = (distribution_object + '_value_average', distribution_object + '_value_num')   # 命名导出数据的标题
        result = pd.DataFrame(dict(zip(header, (map(lambda x : x + bins_gap/2, bins[0 : len(bins) - 1]), n))))   # 取每一个数据区间的中值代表其扭矩特征
        if os.path.exists(self.path) is False:   # 导出数据到CSV文件，如无所需目录则创建一个
            os.mkdir(self.path)
            print(self.common_name + 'Forlder not found. Establishing one.')
        result.to_csv(path_or_buf = self.path + '/{}.csv'.format(distribution_object.split('[')[0]))   # 去除列表名的单位（如km/h重的的/），防止影响文件生成
        print(self.common_name + 'Data distribution report finished.')
        print(self.common_name + 'Report saved in {}'.format(self.path))
        if plot_flag is True:   # 按需要绘制直方图和拟合
            num_bins_line = np.linspace(limit['lower_limit'], limit['upper_limit'], bins_gap)
            if norm_fit_flag is True:   # NORM FIT
                mu = self.data[distribution_object].mean()
                sigma = self.data[distribution_object].std()
                median = self.data[distribution_object].median()
                plt.text(0, 1000, r'test_driver %s test data : $\mu$ = %d, $\sigma$ = %d, median = %d' % (driver, mu, sigma, median))
            if kde_fit_flag is True:   # KDE FIT
                kde = mlab.GaussianKDE(torque)
                plt.plot(num_bins_line, kde(num_bins_line), color[0] + '-')
            plt.grid(True)   # 显示纵坐标分割线
            plt.legend()   # 显示图例
            plt.show()   # 展示图像
        return result

    def rainflow_distribution(self, distribution_object=None, ndigits_user=-2):
        result = rainflow.count_cycles(self.data[distribution_object], ndigits=ndigits_user)   # ndigit参数控制雨流计数的精度，正代表小数点后几位。-2代表以100为分界计算。
        return result

if __name__ == "__main__":
    print('This module is only for importing.')