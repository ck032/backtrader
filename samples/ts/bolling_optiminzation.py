# _*_ coding:utf-8 _*_

"""
@File    :   bolling_optiminzation.py    
@Contact :   chenkai<chenkai15@geely.com>

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/3/1 上午10:39   chenkai      1.0         None
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import datetime
import time

from backtrader.utils.py3 import range

import backtrader as bt
import backtrader.indicators as btind
import backtrader.feeds as btfeeds


class OptimizeStrategy(bt.Strategy):
    params = (('smaperiod', 15),
              ('macdperiod1', 12),
              ('macdperiod2', 26),
              ('macdperiod3', 9),
              )

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
            self.inds[d] = dict()
            # 布林线中轨
            boll_mid = bt.ind.BBands(d.close).mid
            # 买入条件
            self.inds[d]['buy_cond'] = bt.And( \
                # 突破中轨
                d.open < boll_mid, d.close > boll_mid, \
                # 放量
                d.volume == bt.ind.Highest(d.volume, period=self.p.p_period_volume, plot=False))
            # 卖出条件
            self.inds[d]['sell_cond'] = d.close < bt.ind.SMA(d.close, period=self.p.p_sell_ma)
            # 跳过第一只股票data，第一只股票data作为主图数据
            if i > 0:
                if self.p.p_oneplot:
                    d.plotinfo.plotmaster = self.datas[0]

    def next(self):
        for i, d in enumerate(self.datas):
            dt, dn = self.datetime.date(), d._name  # 获取时间及股票代码
            pos = self.getposition(d).size
            if not pos:  # 不在场内，则可以买入
                if self.inds[d]['buy_cond']:  # 如果金叉
                    self.buy(data=d, size=self.p.pstake)  # 买买买
            elif self.inds[d]['sell_cond']:  # 在场内，且死叉
                self.close(data=d)  # 卖卖卖

    def notify_trade(self, trade):
        dt = self.data.datetime.date()
        if trade.isclosed:
            print('{} {} Closed: PnL Gross {}, Net {}'.format(
                dt, trade.data._name, round(trade.pnl, 2), round(trade.pnlcomm, 2)
            ))


# 指标
# 期初余额
# 期末余额
# 盈利率
# 年化单利收益率
# 胜率
# 盈亏比
# 权益最大回撤

def runstrat():
    args = parse_args()

    # Create a cerebro entity
    cerebro = bt.Cerebro(maxcpus=args.maxcpus,
                         runonce=not args.no_runonce,
                         exactbars=args.exactbars,
                         optdatas=not args.no_optdatas,
                         optreturn=not args.no_optreturn)

    # Add a strategy
    # 核心：optstategy
    # 用range传入范围，然后进行优化
    cerebro.optstrategy(
        OptimizeStrategy,
        smaperiod=range(args.ma_low, args.ma_high),
        macdperiod1=range(args.m1_low, args.m1_high),
        macdperiod2=range(args.m2_low, args.m2_high),
        macdperiod3=range(args.m3_low, args.m3_high),
    )

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

    print('==================================================')
    for stratrun in stratruns:
        print('**************************************************')
        for strat in stratrun:
            print('--------------------------------------------------')
            print(strat.p._getkwargs())
            rets = strat.analyzers.returns.get_analysis()
            print('Strat Name {}:\n  - analyzer: {}\n'.format(
                strat.__class__.__name__, rets))
    print('==================================================')

    # print out the result
    print('Time used:', str(tend - tstart))


def parse_args():
    parser = argparse.ArgumentParser(
        description='Optimization',
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        '--data', '-d',
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

    parser.add_argument(
        '--maxcpus', '-m',
        type=int, required=False, default=0,
        help=('Number of CPUs to use in the optimization'
              '\n'
              '  - 0 (default): use all available CPUs\n'
              '  - 1 -> n: use as many as specified\n'))

    parser.add_argument(
        '--no-runonce', action='store_true', required=False,
        help='Run in next mode')

    parser.add_argument(
        '--exactbars', required=False, type=int, default=0,
        help=('Use the specified exactbars still compatible with preload\n'
              '  0 No memory savings\n'
              '  -1 Moderate memory savings\n'
              '  -2 Less moderate memory savings\n'))

    parser.add_argument(
        '--no-optdatas', action='store_true', required=False,
        help='Do not optimize data preloading in optimization')

    parser.add_argument(
        '--no-optreturn', action='store_true', required=False,
        help='Do not optimize the returned values to save time')

    parser.add_argument(
        '--ma_low', type=int,
        default=10, required=False,
        help='SMA range low to optimize')

    parser.add_argument(
        '--ma_high', type=int,
        default=30, required=False,
        help='SMA range high to optimize')

    parser.add_argument(
        '--m1_low', type=int,
        default=12, required=False,
        help='MACD Fast MA range low to optimize')

    parser.add_argument(
        '--m1_high', type=int,
        default=20, required=False,
        help='MACD Fast MA range high to optimize')

    parser.add_argument(
        '--m2_low', type=int,
        default=26, required=False,
        help='MACD Slow MA range low to optimize')

    parser.add_argument(
        '--m2_high', type=int,
        default=30, required=False,
        help='MACD Slow MA range high to optimize')

    parser.add_argument(
        '--m3_low', type=int,
        default=9, required=False,
        help='MACD Signal range low to optimize')

    parser.add_argument(
        '--m3_high', type=int,
        default=15, required=False,
        help='MACD Signal range high to optimize')

    return parser.parse_args()


if __name__ == '__main__':
    runstrat()
