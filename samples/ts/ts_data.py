# _*_ coding:utf-8 _*_

"""
@File    :   ts_data.py    
@Contact :   chenkai<chenkai15@geely.com>

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/1/19 上午8:39   chenkai      1.0         None
"""

# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
import tushare as ts

TOKEN = '600cc23991e8c96cac0ea4ed662d46a5dff74243638ea6ffe6220601'
ts.set_token(TOKEN)
pro = ts.pro_api()
df = pro.daily(ts_code='000001.SZ', start_date='20180701', end_date='20180718')
print(df.head())