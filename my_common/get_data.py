import pandas as pd
import os


def get_arrive_time_request_dic():
    '''
    将数据集转换为arriveTime_request_dic
    arriveTime_request_dic:
    key=arriveTime
    value=arriveTime为key的request_in_dic列表
    request_in_dic的形式为{'request_id', 'arrive_time', 'rtl', 'task_id'}
    '''
    new_arrive_request_in_dic = []
    curPath = os.path.abspath(os.path.dirname(__file__))
    filename = curPath + '/concurrent_request_num.csv'
    data = pd.read_csv(filename, header=0)
    for i in range(0, len(data)):
        request_in_dic = {
            'request_id': data.loc[i, 'request_id'],
            'arrive_time': data.loc[i, 'arrive_time'],
            'rtl': data.loc[i, 'rtl'],
            'task_id': 'task1'
        }
        new_arrive_request_in_dic.append(request_in_dic)

    arriveTime_request_dic = {}
    for request_in_dic in new_arrive_request_in_dic:
        if request_in_dic['arrive_time'] in arriveTime_request_dic:
            arriveTime_request_dic[request_in_dic['arrive_time']].append(request_in_dic)
        else:
            arriveTime_request_dic[request_in_dic['arrive_time']] = [request_in_dic]
    return new_arrive_request_in_dic, arriveTime_request_dic
