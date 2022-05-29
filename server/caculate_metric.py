import re
from turtle import rt
import pandas as pd
from requests import request
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import datetime
import math
from matplotlib.pyplot import MultipleLocator


method_name = 'ppo'
#接收到的总请求数量
request_record_csv_file = 'log/unserved_violate/' + method_name + '_request_record.csv'
# request_record_csv = pd.read_csv( method_name + '_request_record.csv', header=0)
request_record_csv = pd.read_csv(request_record_csv_file, header=0)

log_file_path = 'log/unserved_violate/request_' + method_name + '.log'
# log = open('log/request.log', mode='r').readlines()
log = open(log_file_path, mode='r').readlines()


success_rate = 100.0*len(log)  / len(request_record_csv)
print('失败率：{:.1f}%'.format(100-success_rate))

more_provision_request_num = 0
more_provision_request_sum = 0
more_provision_degree_list = []
more_provision_list = []
sla_violate_num = 0

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
        sla_violate_num += 1

print('违约率：{:.1f}%'.format(100.0 * sla_violate_num / len(request_record_csv)))
print('超供率：{:.1f}%'.format(more_provision_request_num / len(request_record_csv) * 100))
print('超供程度：{:.1f}%'.format(np.mean(more_provision_degree_list) * 100))
print('超供均值：{:.1f}'.format(np.mean(more_provision_list)))
for rtl in rtl_respond_time_dic:
    print('rtl:' + str(rtl) + '等待时间平均值:{:.1f}ms'.format(np.mean(rtl_respond_time_dic[rtl])))

# 计算平均响应时间/每分钟
baseTime = None
timeData = []

# {rtl1:[],rtl2:[]}
for end_time in success_request_dic_key_is_end_time.keys():
    if baseTime == None:
        baseTime = end_time.replace(second=0)
    totalTimeDelta = end_time - baseTime
    deltaMinute = math.floor(totalTimeDelta.days * 24 * 60 + totalTimeDelta.seconds / 60)  # number of minutes
    while len(timeData) < deltaMinute + 1:
        timeData.append(0)

dayIndex = pd.date_range(baseTime, periods=len(timeData), freq='min')

rtl_response_time_list_dic = {}
for rtl in rtl_respond_time_dic.keys():
    rtl_response_time_list_dic[rtl]=[]
    for i in range(len(timeData)):
        rtl_response_time_list_dic[rtl].append([np.nan])
for end_time in success_request_dic_key_is_end_time.keys():
    for request in success_request_dic_key_is_end_time[end_time]:
        totalTimeDelta = end_time - baseTime
        deltaMinute = math.floor(totalTimeDelta.days * 24 * 60 + totalTimeDelta.seconds / 60)  # number of minutes
        if rtl_response_time_list_dic[request['rtl']][deltaMinute] == [np.nan]:
            rtl_response_time_list_dic[request['rtl']][deltaMinute] = [request['response_time']]
        else:
            rtl_response_time_list_dic[request['rtl']][deltaMinute].append(request['response_time'])

rtl_avg_response_time_dic={}
for rtl in rtl_respond_time_dic.keys():
    rtl_avg_response_time_dic[rtl]=[]

for rtl in rtl_response_time_list_dic:
    for response_time_list in rtl_response_time_list_dic[rtl]:
        if response_time_list==[np.nan]:
            rtl_avg_response_time_dic[rtl].append(np.nan)
        else:
            if np.mean(response_time_list) <= 60:
                rtl_avg_response_time_dic[rtl].append(np.mean(response_time_list))
            else:
                rtl_avg_response_time_dic[rtl].append(np.nan)

# 画图
rtl_tanent_dit={2:'tenantA',7:'tenantB'}

sns.set()
fig = plt.figure()
# plt.title("{} response_time".format(method_name))
plt.xlabel('time(minutes)')

for rtl in rtl_respond_time_dic.keys():
    y_major_locator=MultipleLocator(2)
    mask = np.isfinite(rtl_avg_response_time_dic[rtl])
    line, = plt.plot(np.array(list(range(len(timeData))))[mask][:-1], np.array(rtl_avg_response_time_dic[rtl])[mask][:-1], ls="--", lw=1)
    plt.plot(list(range(len(timeData)))[:-1], rtl_avg_response_time_dic[rtl][:-1], color=line.get_color(), lw=1.5, label=rtl_tanent_dit[rtl]+' Response Time')
    # 辅助线
    sup_line = [rtl for i in range(len(dayIndex))]
    plt.plot(list(range(len(timeData)))[:-1], sup_line[:-1], color=line.get_color(), linestyle='--', linewidth='1', label=rtl_tanent_dit[rtl]+' Response Time SLA')

ax=plt.gca()
#ax为两条坐标轴的实例
ax.yaxis.set_major_locator(y_major_locator)
plt.legend(loc='upper right', fontsize=8) # 标签位置
plt.xlim(-0.5)
plt.ylim(-0.5,20)
plt.savefig("more_provision_" + method_name,dpi=400)
