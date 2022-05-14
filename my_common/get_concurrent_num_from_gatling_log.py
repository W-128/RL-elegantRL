import numpy as np
import pandas as pd
import datetime
import csv
import seaborn as sns
import matplotlib.pyplot as plt

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

df = df.groupby('datetime').sum()

sns.set()

print(np.mean(df['view']))
print(np.sum(df['view']))

df.plot()
plt.savefig('nasa_from_gatling_sample.png')
plt.show()

concurrent_request_num_per_second_list = []
for i in range(len(df.index)):
    concurrent_request_num_per_second_list.append(df['view'][i])

print(concurrent_request_num_per_second_list)