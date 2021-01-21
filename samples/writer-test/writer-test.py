#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2015-2020 Daniel Rodriguez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import datetime

# The above could be sent to an independent module
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
from backtrader.analyzers import SQN


class LongShortStrategy(bt.Strategy):
    '''This strategy buys/sells upong the close price crossing
    upwards/downwards a Simple Moving Average.

    It can be a long-only strategy by setting the param "onlylong" to True
    '''
    params = dict(
        period=15,
        stake=1,
        printout=True,
        onlylong=False,
        csvcross=False,
    )

    def start(self):
        pass

    def stop(self):
        pass

    def log(self, txt, dt=None):
        # 记录日志
        if self.p.printout:
            dt = dt or self.data.datetime[0]
            dt = bt.num2date(dt)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # To control operation entries
        self.orderid = None

        # Create SMA on 2nd data
        sma = btind.MovAv.SMA(self.data, period=self.p.period)
        # Create a CrossOver Signal from close an moving average
        # 利用：1.close 2.SMA的值 创建CrossOVer信号
        # 收盘价上穿N日均线策略，发出买入信号
        self.signal = btind.CrossOver(self.data.close, sma)
        self.signal.csv = self.p.csvcross

    def next(self):
        # 1.如果有未决订单，不允许产生新的订单
        if self.orderid:
            return  # if an order is active, no new orders are allowed

        # 2.买入信号
        if self.signal > 0.0:  # cross upwards
            # 如果仓位不为空
            if self.position:
                self.log('CLOSE SHORT , %.2f' % self.data.close[0])
                self.close()

            self.log('BUY CREATE , %.2f' % self.data.close[0])
            self.buy(size=self.p.stake) # stake是几手的意思

        # 3.卖出信号
        elif self.signal < 0.0:
            if self.position:
                self.log('CLOSE LONG , %.2f' % self.data.close[0])
                self.close()

            if not self.p.onlylong:
                self.log('SELL CREATE , %.2f' % self.data.close[0])
                self.sell(size=self.p.stake)

    def notify_order(self, order):
        # bt.Order.Submitted - 订单提交
        # bt.Order.Accepted - 订单接受
        if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
            return  # Await further notifications 等待进一步的notifications

        # order.Completed -订单完成
        if order.status == order.Completed:
            # 买单
            if order.isbuy():
                buytxt = 'BUY COMPLETE, %.2f' % order.executed.price
                self.log(buytxt, order.executed.dt)
            # 卖单
            else:
                selltxt = 'SELL COMPLETE, %.2f' % order.executed.price
                self.log(selltxt, order.executed.dt)

        # order.Expired - 订单失效
        # order.Canceled - 订单取消
        # order.Margin - 保证金不足
        elif order.status in [order.Expired, order.Canceled, order.Margin]:
            self.log('%s ,' % order.Status[order.status])
            pass  # Simply log

        # Allow new orders
        # 此时，没有了未决订单，设置self.orderid=None，允许订单
        self.orderid = None

    def notify_trade(self, trade):
        # 交易关闭
        # pnl - profit and loss 利润和损失，收益
        # pnlcomm - 收益 - commission（佣金，手续费）：净收益
        if trade.isclosed:
            self.log('TRADE PROFIT, GROSS %.2f, NET %.2f' %
                     (trade.pnl, trade.pnlcomm))

        elif trade.justopened:
            self.log('TRADE OPENED, SIZE %2d' % trade.size)


def runstrategy():
    args = parse_args()

    # Create a cerebro
    cerebro = bt.Cerebro()

    # Get the dates from the args
    fromdate = datetime.datetime.strptime(args.fromdate, '%Y-%m-%d')
    todate = datetime.datetime.strptime(args.todate, '%Y-%m-%d')

    # Create the 1st data
    data = btfeeds.BacktraderCSVData(
        dataname=args.data,
        fromdate=fromdate,
        todate=todate)

    # Add the 1st data to cerebro
    cerebro.adddata(data)

    # Add the strategy
    cerebro.addstrategy(LongShortStrategy,
                        period=args.period,
                        onlylong=args.onlylong,
                        csvcross=args.csvcross,
                        stake=args.stake)

    # Add the commission - only stocks like a for each operation
    cerebro.broker.setcash(args.cash)

    # Add the commission - only stocks like a for each operation
    # 设置佣金
    cerebro.broker.setcommission(commission=args.comm,
                                 mult=args.mult,
                                 margin=args.margin)

    cerebro.addanalyzer(SQN)

    cerebro.addwriter(bt.WriterFile, csv=args.writercsv, rounding=2)

    # And run it
    cerebro.run()

    # Plot if requested
    if args.plot:
        cerebro.plot(numfigs=args.numfigs, volume=False, zdown=False)


def parse_args():
    parser = argparse.ArgumentParser(description='MultiData Strategy')

    parser.add_argument('--data', '-d',
                        default='../../datas/2006-day-001.txt',
                        help='data to add to the system')

    parser.add_argument('--fromdate', '-f',
                        default='2006-01-01',
                        help='Starting date in YYYY-MM-DD format')

    parser.add_argument('--todate', '-t',
                        default='2006-12-31',
                        help='Starting date in YYYY-MM-DD format')

    parser.add_argument('--period', default=15, type=int,
                        help='Period to apply to the Simple Moving Average')

    parser.add_argument('--onlylong', '-ol', action='store_true',
                        help='Do only long operations')  # 只做长线操作

    parser.add_argument('--writercsv', '-wcsv', action='store_true',
                        help='Tell the writer to produce a csv stream')

    parser.add_argument('--csvcross', action='store_true',
                        help='Output the CrossOver signals to CSV')  # action='store_true'，只要运行时该变量有传参就将该变量设为True

    parser.add_argument('--cash', default=100000, type=int,
                        help='Starting Cash')

    parser.add_argument('--comm', default=2, type=float,
                        help='Commission for operation')  # 佣金率

    parser.add_argument('--mult', default=10, type=int,
                        help='Multiplier for futures') # 期货乘数

    parser.add_argument('--margin', default=2000.0, type=float,
                        help='Margin for each future')  # 每笔期货的保证金金额

    parser.add_argument('--stake', default=1, type=int,
                        help='Stake to apply in each operation')  # 买几手，默认1手

    parser.add_argument('--plot', '-p', action='store_true',
                        help='Plot the read data')

    parser.add_argument('--numfigs', '-n', default=1,
                        help='Plot using numfigs figures')

    return parser.parse_args()


if __name__ == '__main__':
    runstrategy()
