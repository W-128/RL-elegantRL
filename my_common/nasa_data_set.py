# Load the Dataset and grab a subset
# In this python code we grab the dataset and scale a subset of dataset to use as
# sample workload in our application.
import sys
import os
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
scaled_max = 100
scaled_sub_df = (sub_df / sub_df['view'].max() * scaled_max).apply(lambda x: round(x))
scaled_sub_df['view'] = scaled_sub_df['view'].apply(lambda x: int(x))

print(np.mean(scaled_sub_df['view']))
print(np.sum(scaled_sub_df['view']))
# scaled_sub_df.plot()
# plt.savefig('nasa_sample.png')

plt.xlabel('time(minutes)')
# scaled_sub_df共包含2880分钟，2880个数据点
# resample_df 30min采一次样，共2880分钟，96个数据点
resample_min = 10
resample_df = scaled_sub_df.resample(str(resample_min) + 'min').sum()
# 横轴为[0,48h]
x = []
for i in range(len(resample_df['view'])):
    x.append(i * resample_min / 60.0)
plt.plot(x, resample_df['view'], label='traffic')
plt.legend(loc='upper right', fontsize=8)  # 标签位置
plt.grid(color='gray')
ax = plt.gca() # 获取当前的axes
ax.spines['right'].set_color('gray')
ax.spines['left'].set_color('gray')
ax.spines['top'].set_color('gray')
ax.spines['bottom'].set_color('gray')
plt.xlim(0,50)
plt.ylim(0,700)

plt.savefig('nasa_sample_minitues.png', dpi=400,bbox_inches='tight', transparent=True)

concurrent_request_num_per_second_list = []
for i in range(len(scaled_sub_df.index)):
    concurrent_request_num_per_second_list.append(scaled_sub_df['view'][i])

print(concurrent_request_num_per_second_list)

concurrent_request_num_per_second_list_to_concurrent_request_num(concurrent_request_num_per_second_list)
