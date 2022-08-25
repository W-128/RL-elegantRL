# Load the Dataset and grab a subset
# In this python code we grab the dataset and scale a subset of dataset to use as
# sample workload in our application.
import re
import sys
import os
from urllib.request import Request
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from torch import xlogy

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(os.path.split(rootPath)[0])
sys.path.append(rootPath)

from my_common.utils import concurrent_request_num_per_second_list_to_concurrent_request_num

csv_file = 'NASAJul95.csv'  # or use the url for the file in this repo to fetch remotely
df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
df = df.groupby('datetime').sum()
# similar to paper: Stochastic Resource Provisioning for
#                   Containerized Multi-Tier Web Services in Clouds
# sub_df = df['1998-06-02 12:00:01':'1998-06-04 00:00:00']
# sub_df = df['1998-06-30 08:00:01':'1998-06-30 18:00:00']
sub_df = df['1995-07-01 00:01:00':'1995-07-03 00:00:00']

sns.set()

# Scaling the number of requests to another maximum
# 放缩到最大流量为scaled_max
scaled_max_low = 70
scaled_sub_df_low = (sub_df / sub_df['view'].max() * scaled_max_low).apply(lambda x: round(x))
scaled_sub_df_low['view'] = scaled_sub_df_low['view'].apply(lambda x: int(x))
resample_df_low = scaled_sub_df_low.resample('20min').mean()

scaled_max_normal = 100
scaled_sub_df_normal = (sub_df / sub_df['view'].max() * scaled_max_normal).apply(lambda x: round(x))
scaled_sub_df_normal['view'] = scaled_sub_df_normal['view'].apply(lambda x: int(x))
resample_df_normal = scaled_sub_df_normal.resample('20min').mean()

scaled_max_high = 120
scaled_sub_df_high = (sub_df / sub_df['view'].max() * scaled_max_high).apply(lambda x: round(x))
scaled_sub_df_high['view'] = scaled_sub_df_high['view'].apply(lambda x: int(x))
resample_df_high = scaled_sub_df_high.resample('20min').mean()

used_scaled_sub_df = scaled_sub_df_high

# print(np.mean(scaled_sub_df_normal['view']))
# print(np.sum(scaled_sub_df_normal['view']))
# used_scaled_sub_df.plot()
# plt.savefig('nasa_sample.png')

plt.xlabel('Time(Sampling every 20s)')
# plt.plot(list(range(len(resample_df_low.index))), resample_df_low['view'], label='low Request(request/s)')
plt.plot(list(range(len(resample_df_normal.index))), resample_df_normal['view'], label='normal Request(request/s)')
# plt.plot(list(range(len(resample_df_high.index))), resample_df_high['view'], label='high Request(request/s)')


plt.legend(loc='upper right', fontsize=8)  # 标签位置
plt.grid(color='gray')
ax = plt.gca()  # 获取当前的axes
ax.spines['right'].set_color('gray')
ax.spines['left'].set_color('gray')
ax.spines['top'].set_color('gray')
ax.spines['bottom'].set_color('gray')
# plt.xlim(-10, len(resample_df_low.index) + 10)
plt.ylim(0, 80)
# plt.savefig('nasa_diff_threshold.png', dpi=400, bbox_inches='tight')

plt.savefig('nasa_resample.png', dpi=400, bbox_inches='tight',transparent=True)

# plt.savefig('nasa_sample_minitues.png')
concurrent_request_num_per_second_list = []
for i in range(len(used_scaled_sub_df.index)):
    concurrent_request_num_per_second_list.append(used_scaled_sub_df['view'][i])

print(concurrent_request_num_per_second_list)

concurrent_request_num_per_second_list_to_concurrent_request_num(concurrent_request_num_per_second_list)
