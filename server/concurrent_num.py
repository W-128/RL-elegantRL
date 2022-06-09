import datetime
import math
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

method_name = 'ppo_1chu2'
log_file_path = 'log/retest/request_' + method_name + '.log'
log = open(log_file_path, mode='r').readlines()

baseTime = None
timeData = []

for i in range(len(log)):
    dt = datetime.datetime.strptime(log[i][:19], "%Y-%m-%d %H:%M:%S")
    if baseTime == None:
        baseTime = dt
    totalTimeDelta = dt - baseTime
    deltaSecond = math.floor(totalTimeDelta.days * 24 * 60 * 60 + totalTimeDelta.seconds)  # number of seconds
    while len(timeData) < deltaSecond + 1:
        timeData.append(0)
    timeData[deltaSecond] += 1

dayIndex = pd.date_range(baseTime, periods=len(timeData), freq='S')
df = pd.DataFrame(timeData, index=dayIndex)
df=df.resample('5S').mean()

# for i in range(len(df)):
#     if df.loc[i]['view'] > 60:
#         print(df.loc[i]['datetime'])

sns.set()
fig = plt.figure()
df.plot()
plt.savefig("log/retest/submit_every_second" + method_name, dpi=400, bbox_inches='tight')
