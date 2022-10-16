import os
import sys
import matplotlib.pyplot as plt

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
sys.path.append(curPath + '/my_common')
sys.path.append(os.path.split(rootPath)[0])
from my_common.utils import concurrent_request_num_per_second_list_to_concurrent_request_num
import random
# t=1000ms
TIME_UNIT = 1
TIME_UNIT_IN_ON_SECOND = int(1 / TIME_UNIT)
# 生成一个先升后降的流量 时长320s 0to80to0 阈值40
header = ['concurrent_request_num_per_second']


# def request_number(second):
#     if int(0.5 * second) == 0:
#         return 1
#     else:
#         return int(0.5 * second)

first_peak = 50
first_bottom = 10
second_peak = 100
first_peak_point = 720
first_bottom_point = 1440
second_peak_point = 2160
end_point = 2880
first_k = (first_peak + 0.0) / first_peak_point
second_k = (first_bottom - first_peak + 0.0) / (first_bottom_point - first_peak_point)
third_k = (second_peak - first_bottom + 0.0) / (second_peak_point - first_bottom_point)
forth_k = (0.0 - second_peak) / (end_point - second_peak_point)
concurrent_request_num_per_second = []
for second in range(first_peak_point):
    concurrent_request_num_per_second.append(int(first_k * second + 1))

for second in range(first_peak_point, first_bottom_point):
    concurrent_request_num_per_second.append(int(first_peak + second_k * (second - first_peak_point) + 1))

for second in range(first_bottom_point, second_peak_point):
    concurrent_request_num_per_second.append(int(first_bottom + third_k * (second - first_bottom_point) + 1))

for second in range(second_peak_point, end_point):
    concurrent_request_num_per_second.append(int(second_peak + forth_k * (second - second_peak_point) + 1))

# concurrent_request_num_per_second index是到达时间 element是请求个数
print(concurrent_request_num_per_second)
plt.plot(list(range(len(concurrent_request_num_per_second))), concurrent_request_num_per_second)
plt.savefig('test_data.png', dpi=400, bbox_inches='tight')

concurrent_request_num_per_second_list_to_concurrent_request_num(concurrent_request_num_per_second)

# # 先造只有rtl1 和rtl3
# rtl_list = [1, 3]
# for i in range(len(rtl_list)):
#     rtl_list[i] = rtl_list[i] * TIME_UNIT_IN_ON_SECOND
#
# request_list = []
# for i in range(len(concurrent_request_num_per_second)):
#     request_sum_the_second = concurrent_request_num_per_second[i]
#     request_num_in_the_second = [int(request_sum_the_second * TIME_UNIT)] * (TIME_UNIT_IN_ON_SECOND)
#     remain_request_num = request_sum_the_second - int(request_sum_the_second * TIME_UNIT) * (TIME_UNIT_IN_ON_SECOND)
#     for j in range(remain_request_num):
#         request_num_in_the_second[j] = request_num_in_the_second[j] + 1
#     np.random.shuffle(request_num_in_the_second)
#     print(request_num_in_the_second)
#     for k in range(TIME_UNIT_IN_ON_SECOND):
#         for h in range(request_num_in_the_second[k]):
#             # [request_id, arrive_time, rtl]
#             request = []
#             request.append(str(uuid.uuid1()))
#             request.append(i * TIME_UNIT_IN_ON_SECOND + k)
#             request.append(np.random.choice(rtl_list))
#             request_list.append(request)
#
# headers = ['request_id', 'arrive_time', 'rtl']
# with open('concurrent_request_num.csv', 'w', newline='')as f:
#     f_csv = csv.writer(f)
#     f_csv.writerow(headers)
#     f_csv.writerows(request_list)
