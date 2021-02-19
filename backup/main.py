import ground_test_data_process as gtdp
import pandas as pd
import threading
import time
import os
from functools import wraps

dic_path = '/Users/sunlei/Documents/python/ground_test_data_process/SAICMARVEL/road/'
file_common_name = 'SDS EV Torque_SAIC MarvelX_2019_'
report_root_path = '/Users/sunlei/Documents/python/ground_test_data_process/report/'

data_road_tester = {'1': ('05_05_090', '05_05_091', '05_05_092', '05_05_093',\
                          '05_17_163', '05_17_164', '05_17_165', '05_17_166',\
                          '05_23_202', '05_23_203', '05_23_204', '05_23_205',\
                          '05_27_220', '05_27_221', '05_27_222', '05_27_223',\
                          '05_28_228', '05_28_229', '05_28_230', '05_28_231',\
                          '05_28_232', '05_28_233', '05_28_234', '05_28_235'),
                    '2': ('04_30_081', '04_30_082', '04_30_083', '04_30_084',\
                          '05_05_085', '05_05_086', '05_05_087', '05_05_088',\
                          '05_06_095', '05_06_096', '05_06_097', '05_06_098',\
                          '05_07_105', '05_07_106', '05_07_107', '05_07_108',\
                          '05_13_129', '05_13_130', '05_13_131', '05_13_132',\
                          '05_16_155', '05_16_156', '05_16_157', '05_16_158'),
                    '3': ('05_08_112', '05_08_113', '05_08_114', '05_08_115',\
                          '05_17_168', '05_17_169', '05_17_170', '05_17_171',\
                          '05_22_190', '05_22_191', '05_22_192', '05_22_193',\
                          '05_29_240', '05_29_241', '05_29_242', '05_29_243',\
                          '05_30_244', '05_30_245', '05_30_246', '05_30_247',\
                          '05_30_248', '05_30_249', '05_30_250', '05_30_251'),
                    '4': ('05_10_124', '05_10_125', '05_10_126', '05_10_127',\
                          '05_15_145', '05_15_146', '05_15_147', '05_15_148',\
                          '05_16_159', '05_16_160', '05_16_161', '05_16_162',\
                          '05_24_208', '05_24_209', '05_24_210', '05_24_211',\
                          '05_27_224', '05_27_225', '05_27_226', '05_27_227',\
                          '05_29_236', '05_29_237', '05_29_238', '05_29_239'),
                    '5': ('05_06_100', '05_06_101', '05_06_102', '05_06_103',\
                          '05_08_116', '05_08_117', '05_08_118', '05_08_119',\
                          '05_14_141', '05_14_142', '05_14_143', '05_14_144',\
                          '05_20_176', '05_20_177', '05_20_178', '05_20_179',\
                          '05_24_212', '05_24_213', '05_24_214', '05_24_215',\
                          '05_25_216', '05_25_217', '05_25_218', '05_25_219'),
                    '6': ('05_10_120', '05_10_121', '05_10_122', '05_10_123',\
                          '05_13_133', '05_13_134', '05_13_135', '05_13_136',\
                          '05_14_137', '05_14_138', '05_14_139', '05_14_140',\
                          '05_20_172', '05_20_173', '05_20_174', '05_20_175',\
                          '05_21_181', '05_21_182', '05_21_183', '05_21_184',\
                          '05_22_195', '05_22_196', '05_22_197', '05_22_198')} 
                        
OBJECT_LIST = ['t(hist)', 'JointTemp_RL(hist)', 'JointTemp_RR(hist)', 'Torque_RL(hist)',\
               'Torque_RR(hist)', 'JounceAngle_RL(hist)', 'JounceAngle_RR(hist)', 'ABSAHSC1(hist)',\
               'TCSAHSC1(hist)', 'VehDynYawRateHSC1(hist)', 'VSESysAHSC1(hist)',\
               'EPTAccelActuPosHSC1(hist)', 'BrkPdlPos_h1HSC1(hist)',\
               'StrgWhlAngHSC1(hist)', 'VSELatAccHSC1(hist)', 'VSELongtAccHSC1(hist)',\
               'WhlGndVelLDrvnHSC1(hist)', 'WhlGndVelRDrvnHSC1(hist)', 'WhlGndVelLNonDrvnHSC1(hist)',\
               'WhlGndVelRNonDrvnHSC1(hist)', 'ISGActuToqHSC6(hist)', 'TMActuToqHSC6(hist)']


def dur_time_wrapper(func):
    @wraps(func) # 是很重要的， 它能保留原始函数的元数据
    def inner(*args,**kwargs):
        start_time = time.time()
        time.sleep(1)
        result = func(*args,**kwargs)
        dur_time = time.time() - start_time
        print('Process running time: {}s'.format(dur_time) + '*' * 60)
        return result
    return inner

@dur_time_wrapper
def process_one_file(file_code=None):
    file_path = dic_path + file_common_name + file_code + '.xls'
    report_path = report_root_path + file_code
    data = gtdp.DataProcess()
    data.data_from_excel(path=file_path)
    for analysis_object in list(data.data.columns):
        data.hist_distribution(analysis_object)
    data.data_to_file(path=report_path)
    return True

def do_many(func, *args):
    trd = dict()
    for file_code in data_road_tester['1']:
        trd[file_code] = threading.Thread(target=func,args=(*args,))
        trd[file_code].start()
        time.sleep(1)  
    map(lambda x: x.join(), trd.keys())

@dur_time_wrapper
def merge_csv(driver_no, analysis_object):
    csv_list = []
    for file_code in data_road_tester[driver_no]:
        file_path = report_root_path + 'driver_{}/{}/{}.csv'.format(driver_no, file_code, analysis_object)
        print('open' + file_path)
        csv_file = pd.read_csv(filepath_or_buffer=file_path, index_col=[1])
        csv_file.drop(columns=csv_file.columns[0], inplace=True)
        csv_list.append(csv_file)
    result = csv_list[0]
    for csv_file in csv_list[1:]:
        result = result.add(csv_file, fill_value=0)
    if os.path.exists(report_root_path + '/driver_{}/summary'.format(driver_no)) is not True:
        os.mkdir(report_root_path + '/driver_{}/summary'.format(driver_no))
    result.to_csv(path_or_buf=report_root_path + '/driver_{}/summary/{}_summary.csv'.format(driver_no, analysis_object)) 
    return result

if __name__ == '__main__':
    for i in ['1', '2', '3', '4', '5', '6']:    
        for j in OBJECT_LIST:
            merge_csv(i, j)
    #map(process_one_file, data_road_tester['3'])
    #for i in ['4', '5', '6']:
    #    for file_code in data_road_tester[i]:
    #        process_one_file(file_code)