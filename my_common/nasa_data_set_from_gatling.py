# Load the Dataset and grab a subset
# In this python code we grab the dataset and scale a subset of dataset to use as
# sample workload in our application.
import sys
import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(os.path.split(rootPath)[0])
sys.path.append(rootPath)

from my_common.utils import concurrent_request_num_per_second_list_to_concurrent_request_num

csv_file = 'NASAJul95_gatling.csv'  # or use the url for the file in this repo to fetch remotely
df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
df = df.groupby('datetime').sum()
# similar to paper: Stochastic Resource Provisioning for
#                   Containerized Multi-Tier Web Services in Clouds

sns.set()


print(np.mean(df['view']))
print(np.sum(df['view']))
df.plot()
plt.savefig('nasa_from_gatling_sample.png')
plt.show()

concurrent_request_num_per_second_list = []
for i in range(len(df.index)):
    concurrent_request_num_per_second_list.append(df['view'][i])

concurrent_request_num_per_second_list_to_concurrent_request_num(concurrent_request_num_per_second_list)
