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

import baostock as bs
import pandas as pd
import numpy as np
import talib as ta
import datetime

stockcodelist = ['sh.600000', 'sz.300009', 'sz.300128']

login_result = bs.login(user_id='anonymous', password='123456')
print('login respond error_msg:' + login_result.error_msg)

startdate = '2018-01-01'
today = datetime.datetime.now()
delta = datetime.timedelta(days=1)
# 获取截至上一个交易日的历史行情
predate = today - delta
strpredate = datetime.datetime.strftime(predate, '%Y-%m-%d')

for stockcode in stockcodelist:
    # 获取沪深A股行情和估值指标(日频)数据并返回收盘价20日均线
    rs = bs.query_history_k_data("%s" % stockcode,
                                 "date,code,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM",
                                 start_date=startdate,
                                 end_date=strpredate,
                                 frequency="d",
                                 adjustflag="2")

result_list = []
while (rs.error_code == '0') & rs.next():
    # 获取一条记录，将记录合并在一起
    result_list.append(rs.get_row_data())
    result = pd.DataFrame(result_list, columns=rs.fields)

    closelist = [float(price) for price in list(result['close'])]
    highlist = [float(price) for price in list(result[high])]
    lowlist = [float(price) for price in list(result[low])]
