# _*_ coding:utf-8 _*_

"""
@File    :   tushare_data.py    
@Contact :   chenkai<chenkai15@geely.com>

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/3/4 下午4:58   chenkai      1.0         None
"""
import numpy as np
import pandas as pd
import tushare as ts
import backtrader as bt


class TushareDataFrame:
    def __init__(self, code, start, end):
        self.code = code
        self.start = start
        self.end = end

    def get_data(self):
        df = ts.pro_bar(ts_code=self.code,
                        adj='qfq',
                        start_date=self.start,
                        end_date=self.end)
        df['date'] = df['trade_date']
        df['volume'] = df['vol']
        df.index = pd.to_datetime(df['date'])
        df['openinterest'] = 0
        df = df[['open', 'high', 'low', 'close', 'volume', 'openinterest']]
        return bt.feeds.PandasData(dataname=df.sort_index(),
                                   fromdate=pd.to_datetime(self.start),
                                   todate=pd.to_datetime(self.end))


# 在 backtrader 主函数中调用
data = TushareDataFrame(code='600000.SH',
                        start='20100331',
                        end='20200331').get_data()
cerebro.adddata(data)
