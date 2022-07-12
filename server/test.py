import pandas as pd
import datetime
import numpy as np

dic={}
dic[datetime.datetime.strptime('2016/1/1', "%Y/%m/%d")]=np.nan
dic[datetime.datetime.strptime('2016/1/2', "%Y/%m/%d")]=np.nan
dic[datetime.datetime.strptime('2016/1/3', "%Y/%m/%d")]=3
dic[datetime.datetime.strptime('2016/1/4', "%Y/%m/%d")]=4
dic[datetime.datetime.strptime('2016/1/5', "%Y/%m/%d")]=np.nan
dic[datetime.datetime.strptime('2016/1/6', "%Y/%m/%d")]=6

df=pd.Series(dic)


