# _*_ coding:utf-8 _*_

"""
@File    :   stock_select.py.py    
@Contact :   chenkai<chenkai15@geely.com>

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/2/26 下午2:28   chenkai      1.0         None
"""

# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime  # 用于datetime对象操作
import os.path  # 用于管理路径
import sys  # 用于在argvTo[0]中找到脚本名称
import pandas as pd


# 判断金叉
def golden_crossover(df, fast, slow):
    # K线数目不足，次新股
    if df.shape[0] < slow:
        return False
    # 技术指标名称
    fast_indicator = 'ma_%d' % fast
    slow_indicator = 'ma_%d' % slow
    # 最后一日短期均线在长期均线上方，且倒数第二日短期均线在长期均线下方
    return df[fast_indicator][df.index[0]] > df[slow_indicator][df.index[0]] \
           and df[fast_indicator][df.index[1]] < df[slow_indicator][df.index[1]]


# 读入股票代码
stk_code_file = '../TQDat/TQDown2020v1/data/stock_code_update.csv'
stk_pools = pd.read_csv(stk_code_file, encoding='gbk')
out_df = pd.DataFrame(columns=['code'], dtype=str)
# 对每个股票进行判断
for stk_code in stk_pools['code']:
    stk_code = '%06d' % stk_code
    # 读入数据
    input_file = './tmp/' + stk_code + '.csv'
    df = pd.read_csv(input_file, index_col=0)
    df = df.sort_index(ascending=False)
    if golden_crossover(df, 5, 60):
        out_df = out_df.append({'code': stk_code}, ignore_index=True)
        print(stk_code)

out_df.to_csv('./output/stock_picking.csv')
