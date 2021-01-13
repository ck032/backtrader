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

import backtrader as bt
import backtrader.indicators as btind
import backtrader.feeds as btfeeds
import backtrader.filters as btfilters


def runstrat():
    args = parse_args()

    # 1.Create a cerebro entity
    # 1.创建一个cerebro实体（ cerebro - brain的意思）
    cerebro = bt.Cerebro(stdstats=False)

    # 2.Add a strategy
    # 2.添加一个测量
    cerebro.addstrategy(bt.Strategy)

    # 3.Get the dates from the args
    # 3.从args中获取fromdate和todate,并且进行format
    fromdate = datetime.datetime.strptime(args.fromdate, '%Y-%m-%d')
    todate = datetime.datetime.strptime(args.todate, '%Y-%m-%d')

    data = btfeeds.YahooFinanceData(
        dataname=args.data,
        fromdate=fromdate,
        todate=todate)

    # 4.Add the resample data instead of the original
    # 4.添加采样数据（限定了fromdate和todate)
    cerebro.adddata(data)

    # 5.Add a simple moving average if requirested
    # 5.添加一个简单的btind.SMA,其中args.period是SMA的参数
    cerebro.addindicator(btind.SMA, period=args.period)

    # 6.Add a writer with CSV
    # 6.把结果写入args.wrcsv
    if args.writer:
        cerebro.addwriter(bt.WriterFile, csv=args.wrcsv)

    # 7.Run over everything
    # 7.跑数据
    cerebro.run()

    # 8.Plot if requested
    # 8.plot
    if args.plot:
        cerebro.plot(style='bar', numfigs=args.numfigs, volume=False)


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Calendar Days Filter Sample')

    parser.add_argument('--data', '-d',
                        default='YHOO',
                        help='Ticker to download from Yahoo')

    parser.add_argument('--fromdate', '-f',
                        default='2006-01-01',
                        help='Starting date in YYYY-MM-DD format')

    parser.add_argument('--todate', '-t',
                        default='2006-12-31',
                        help='Starting date in YYYY-MM-DD format')

    parser.add_argument('--period', default=15, type=int,
                        help='Period to apply to the Simple Moving Average')

    parser.add_argument('--writer', '-w', action='store_true',
                        help='Add a writer to cerebro')

    parser.add_argument('--wrcsv', '-wc', action='store_true',
                        help='Enable CSV Output in the writer')

    parser.add_argument('--plot', '-p', action='store_true',
                        help='Plot the read data')

    parser.add_argument('--numfigs', '-n', default=1, type=int,
                        help='Plot using numfigs figures')

    return parser.parse_args()


if __name__ == '__main__':
    runstrat()
