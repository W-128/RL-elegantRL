import re
from turtle import rt
import pandas as pd
from requests import request
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import datetime
#接收到的总请求数量
method_name = 'fifo'
request_record_csv_file = 'log/' + method_name + '_request_record.csv'
request_record_csv = pd.read_csv(request_record_csv_file, header=0)

log_file_path = 'log/request_' + method_name + '.log'
log = open(log_file_path, mode='r').readlines()

success_rate = len(log) * 100.0 / len(request_record_csv)
if method_name != 'fifo':
    print('成功率：{:.1f}%'.format(success_rate))

more_provision_request_num = 0
more_provision_request_sum = 0
more_provision_degree_list = []
more_provision_list = []
response_time_bigger_than_rtl_sum = 0

response_time_pattern = r'(\d+)ms'
rtl_pattern = r'rtllevel:(\d+)'
success_request_dic_key_is_end_time = {}
rtl_respond_time_dic = {}
for i in range(len(log)):
    dt = datetime.datetime.strptime(log[i][:19], "%Y-%m-%d %H:%M:%S")
    response_time = int(re.search(response_time_pattern, log[i]).group().replace('ms', ''))
    rtl = int(re.search(rtl_pattern, log[i]).group().replace('rtllevel:', ''))
    # 维持key=end_time value=[request{rtl:response_time}]的success_request_dic_key_is_end_time
    if dt in success_request_dic_key_is_end_time:
        success_request_dic_key_is_end_time[dt].append({'rtl': rtl, 'response_time': response_time / 1000.0})
    else:
        success_request_dic_key_is_end_time[dt] = [{'rtl': rtl, 'response_time': response_time / 1000.0}]

    #维持一个rtl_list
    if rtl not in rtl_respond_time_dic:
        rtl_respond_time_dic[rtl] = [response_time]
    else:
        rtl_respond_time_dic[rtl].append(response_time)

    if response_time < rtl * 1000:
        more_provision_request_num += 1
        more_provision_request_sum += (rtl - response_time / 1000.0)
        more_provision_degree_list.append((rtl - response_time / 1000.0) / rtl)
        more_provision_list.append(rtl - response_time / 1000.0)
    else:
        response_time_bigger_than_rtl_sum += 1

# print('more_provision_request_sum' + str(more_provision_request_num))
if method_name!='fifo':
    print('response_time_bigger_than_rtl_sum' + str(response_time_bigger_than_rtl_sum))
else:
    print('成功率：{:.1f}%'.format(100.0*(len(log)-response_time_bigger_than_rtl_sum)/len(log)))
# print('超供总量：' + str(more_provision_request_sum))
print('超供率：{:.1f}%'.format(more_provision_request_num / len(request_record_csv) * 100))
print('超供程度：{:.1f}%'.format(np.mean(more_provision_degree_list) * 100))
print('超供均值：{:.1f}'.format(np.mean(more_provision_list)))
for rtl in rtl_respond_time_dic:
    print('rtl:' + str(rtl) + '等待时间平均值:{:.1f}ms'.format(np.mean(rtl_respond_time_dic[rtl])))

# success_request_dic_key_is_end_time = {}
# print(log[0][:19])
# dt = datetime.datetime.strptime(log[0][:19], "%Y-%m-%d %H:%M:%S")
# print(dt)
# for i in range(len(log)):
#     dt = datetime.datetime.strptime(log[0][:19], "%Y-%m-%d %H:%M:%S")

#     if dt in success_request_dic_key_is_end_time:
#         success_request_dic_key_is_end_time[dt].append()

sns.set()
fig = plt.figure()
plt.title("{} response_time".format(method_name))
plt.xlabel('time(second)')
x = list(success_request_dic_key_is_end_time.keys())
rtl_avg_wait_time_dic = {}
# {rtl1:[],rtl2:[]}
for rtl in rtl_respond_time_dic.keys():
    rtl_avg_wait_time_dic[rtl] = []
for end_time in success_request_dic_key_is_end_time.keys():
    rtl_wait_time_dic = {}
    # {rtl1:[],rtl2:[]}
    for rtl in rtl_respond_time_dic.keys():
        rtl_wait_time_dic[rtl] = []
    for request in success_request_dic_key_is_end_time[end_time]:
        rtl_wait_time_dic[request['rtl']].append(request['response_time'])
    for rtl in rtl_wait_time_dic:
        if rtl_wait_time_dic[rtl] == []:
            rtl_avg_wait_time_dic[rtl].append(np.nan)
        else:
            rtl_avg_wait_time_dic[rtl].append(np.mean(rtl_wait_time_dic[rtl]))

for rtl in rtl_respond_time_dic.keys():
    mask = np.isfinite(rtl_avg_wait_time_dic[rtl])
    line, = plt.plot(np.array(x)[mask], np.array(rtl_avg_wait_time_dic[rtl])[mask], ls="--", lw=1)
    plt.plot(x, rtl_avg_wait_time_dic[rtl], color=line.get_color(), lw=1.5, label=rtl)
    # 辅助线
    sup_line = [rtl for i in range(len(x))]
    plt.plot(x, sup_line, color='black', linestyle='--', linewidth='1')

    plt.legend()
    plt.savefig("more_provision_" + method_name)
    # plt.show()