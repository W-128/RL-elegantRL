import pandas as pd
import os
import datetime


def get_arrive_time_request_dic(arrive_time_index):
    '''
    将数据集转换为arriveTime_request_dic
    arriveTime_request_dic:
    key=arriveTime
    value=arriveTime为key的request_in_dic列表
    request_in_dic的形式为[request_id, arrive_time, rtl]
    '''
    new_arrive_request_in_dic = []
    curPath = os.path.abspath(os.path.dirname(__file__))
    filename = curPath + '/concurrent_request_num.csv'
    data = pd.read_csv(filename, header=0)
    for i in range(0, len(data)):
        request_in_dic = [data.loc[i, 'request_id'], data.loc[i, 'arrive_time'], data.loc[i, 'rtl']]
        new_arrive_request_in_dic.append(request_in_dic)

    arriveTime_request_dic = {}
    for request_in_dic in new_arrive_request_in_dic:
        if request_in_dic[arrive_time_index] in arriveTime_request_dic:
            arriveTime_request_dic[request_in_dic[arrive_time_index]].append(request_in_dic)
        else:
            request_list = [request_in_dic]
            arriveTime_request_dic[request_in_dic[arrive_time_index]] = request_list
    return new_arrive_request_in_dic, arriveTime_request_dic


def get_arrive_time_request_dic_from_request_record(arrive_time_index):
    '''
    将数据集转换为arriveTime_request_dic
    arriveTime_request_dic:
    key=arriveTime
    value=arriveTime为key的request_in_dic列表
    request_in_dic的形式为[request_id, arrive_time, rtl]
    '''
    new_arrive_request_in_dic_temp = []
    curPath = os.path.abspath(os.path.dirname(__file__))
    rootPath = os.path.split(curPath)[0]
    filename = rootPath + '/server/request_record.csv'
    data = pd.read_csv(filename, header=0)

    for i in range(0, len(data)):
        request_in_dic = [
            data.loc[i, 'request_id'],
            datetime.datetime.strptime(data.loc[i, 'arrive_time'], '%Y-%m-%d %H:%M:%S.%f'), data.loc[i, 'rtl']
        ]
        new_arrive_request_in_dic_temp.append(request_in_dic)
    new_arrive_request_in_dic_temp = sorted(new_arrive_request_in_dic_temp, key=lambda i: i[1])

    base_time = new_arrive_request_in_dic_temp[0][1].replace(microsecond=0)
    new_arrive_request_in_dic = []
    for i in range(0, len(new_arrive_request_in_dic_temp)):
        delta_second = int(new_arrive_request_in_dic_temp[i][1].timestamp() - base_time.timestamp())
        request_in_dic_second = list(new_arrive_request_in_dic_temp[i])
        request_in_dic_second[1] = delta_second
        new_arrive_request_in_dic.append(request_in_dic_second)

    arriveTime_request_dic = {}
    for request_in_dic in new_arrive_request_in_dic:
        if request_in_dic[arrive_time_index] in arriveTime_request_dic:
            arriveTime_request_dic[request_in_dic[arrive_time_index]].append(request_in_dic)
        else:
            request_list = [request_in_dic]
            arriveTime_request_dic[request_in_dic[arrive_time_index]] = request_list
    return new_arrive_request_in_dic, arriveTime_request_dic
