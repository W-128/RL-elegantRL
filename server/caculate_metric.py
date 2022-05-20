import re
import pandas as pd
from requests import request
import numpy as np

log_file_path = 'log/request.log'
log = open(log_file_path, mode='r').readlines()

#接收到的总请求数量
request_record_csv_file = 'edf_threshold_request_record.csv'
request_record_csv = pd.read_csv(request_record_csv_file, header=0)

success_rate = len(log) * 100.0 / len(request_record_csv)
print('成功率：{:.1f}%'.format(success_rate))

more_provision_request_num = 0
more_provision_request_sum = 0
more_provision_list = []
response_time_bigger_than_rtl_sum = 0

response_time_pattern = r'(\d+)ms'
rtl_pattern = r'rtllevel:(\d+)'

for i in range(len(log)):
    response_time = int(re.search(response_time_pattern, log[i]).group().replace('ms', ''))
    rtl = int(re.search(rtl_pattern, log[i]).group().replace('rtllevel:', ''))
    if response_time < rtl * 1000:
        more_provision_request_num += 1
        more_provision_request_sum += (rtl * 1000 - response_time)
        more_provision_list.append((rtl - response_time / 1000.0) / rtl)
    else:
        response_time_bigger_than_rtl_sum += 1

# print('more_provision_request_sum' + str(more_provision_request_num))
# print('response_time_bigger_than_rtl_sum' + str(response_time_bigger_than_rtl_sum))
# print('超供总量：' + str(more_provision_request_sum))
print('超供率：{:.1f}%'.format(more_provision_request_num / len(request_record_csv) * 100))
print('超供程度：{:.1f}%'.format(np.mean(more_provision_list) * 100))
