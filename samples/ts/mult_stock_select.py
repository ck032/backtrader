# _*_ coding:utf-8 _*_

"""
@File    :   放量突破布林中线.py
@Contact :   chenkai<chenkai15@geely.com>

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/2/26 下午2:44   chenkai      1.0     https://blog.csdn.net/m0_46603114/article/list/2
"""

from __future__ import (absolute_import, division, print_function, unicode_literals)

import argparse
import datetime
import time

import backtrader as bt
import backtrader.feeds as btfeeds


# 创建策略
class BollStrategy(bt.Strategy):
    # 可配置策略参数
    params = dict(
        p_period_volume=10,  # 前n日最大交易量
        p_sell_ma=5,  # 跌破该均线卖出
        p_oneplot=False,  # 是否打印到同一张图
        pstake=1000,  # 单笔交易股票数
    )

    def __init__(self):
        self.inds = dict()
        for i, d in enumerate(self.datas):
            print(i, d)
            self.inds[d] = dict()
            # 布林线中轨
            boll_mid = bt.ind.BBands(d.close).mid
            # 买入条件
            self.inds[d]['buy_con'] = bt.And( \
                # 突破中轨
                d.open < boll_mid, d.close > boll_mid, \
                # 放量
                d.volume == bt.ind.Highest(d.volume, period=self.p.p_period_volume, plot=False))
            self.inds[d]['sell_con'] = d.close < bt.ind.SMA(d.close, period=self.p.p_sell_ma)

    def next(self):
        choices = []
        for i, d in enumerate(self.datas):
            dt, dn = self.datetime.date(), d._name  # 获取时间及股票代码
            pos = self.getposition(d).size
            if not pos:  # 不在场内，则可以买入
                if self.inds[d]['buy_con']:  # 如果金叉
                    self.buy(data=d, size=self.p.pstake)  # 买买买
            elif self.inds[d]['sell_con']:  # 在场内，且死叉
                self.close(data=d)  # 卖卖卖


def runstrat():
    args = parse_args()

    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    # 核心：optstategy
    # 用range传入范围，然后进行优化
    cerebro.addstrategy(BollStrategy)

    # Get the dates from the args
    fromdate = datetime.datetime.strptime(args.fromdate, '%Y-%m-%d')
    todate = datetime.datetime.strptime(args.todate, '%Y-%m-%d')

    # Create the 1st data
    data = btfeeds.BacktraderCSVData(
        dataname=args.data,
        fromdate=fromdate,
        todate=todate)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # clock the start of the process
    tstart = time.clock()

    # Run over everything
    stratruns = cerebro.run()

    # clock the end of the process
    tend = time.clock()

    # print out the result
    print('Time used:', str(tend - tstart))


def parse_args():
    parser = argparse.ArgumentParser(
        description='Optimization',
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        '--data0', '-d0',
        default='../../datas/2006-day-001.txt',
        help='data to add to the system')

    parser.add_argument(
        '--data1', '-d1',
        default='../../datas/2006-day-001.txt',
        help='data to add to the system')

    parser.add_argument(
        '--fromdate', '-f',
        default='2006-01-01',
        help='Starting date in YYYY-MM-DD format')

    parser.add_argument(
        '--todate', '-t',
        default='2006-03-30',
        help='Starting date in YYYY-MM-DD format')

    return parser.parse_args()


if __name__ == '__main__':
    runstrat()
