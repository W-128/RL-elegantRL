import numpy as np
import pandas as pd
import datetime
import csv

csv_path = "../server/request_record.csv"
data = pd.read_csv(csv_path, header=0)

time_data = []
base_time = None
for i in range(0, len(data)):
    arrive_time = datetime.datetime.strptime(data.loc[i, 'arrive_time'], '%Y-%m-%d %H:%M:%S.%f')
    if base_time == None:
        base_time = arrive_time.replace(microsecond=0)
    delta = arrive_time - base_time
    delta_second = delta.days * 24 * 60 * 60 + delta.seconds
    while len(time_data) < delta_second + 1:
        time_data.append(0)
    time_data[delta_second] += 1

dayIndex = pd.date_range(base_time, periods=len(time_data), freq='S')
df = pd.DataFrame({"datetime": dayIndex, "view": time_data})
df.datetime = df.datetime.dt.strftime("%Y-%m-%d %H:%M:%S")
df.to_csv("NASAJul95_gatling.csv", index=None)
# delta_second=delta.days*24+delta.
# time_list = []
# sla_more_provision = 0
# pattern = r'(\d+)ms'

# response_time_more_than_150s = 0

# for i in range(len(log)):
#     time = int(re.search(pattern, log[i]).group().replace('ms',
#                                                           ''))  # print(time)
#     # print(len(log[i]))
#     # print(log[i][len_index:])
#     time_list.append(time)
#     # 违约
#     if time > request_response_time:
#         sla_violate = sla_violate + 1
#         if time > 150000:
#             response_time_more_than_150s = response_time_more_than_150s + 1
#     # 未违约，计算超供量
#     else:
#         sla_more_provision = sla_more_provision + request_response_time - time

# std = np.std(time_list)
# print("请求个数: " + str(len(time_list)))
# print("average response time:" + str(mean(time_list)))
# print("sla violate rate:" + str(sla_violate / len(log)))
# print("sla超供量: " + str(sla_more_provision / len(time_list)))
# print("标准差: " + str(std))
# print("最长响应时间: " + str(max(time_list)))
# print("response_time_more_than_150s: " + str(response_time_more_than_150s))
# df = pd.DataFrame(time_list, columns=['response_time'])
# df.to_excel("response_time.xlsx", index=False)
