# _*_ coding:utf-8 _*_

"""
@File    :   stock_screen.py    
@Contact :   chenkai<chenkai15@geely.com>

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/3/4 下午4:40   chenkai      1.0        https://www.backtrader.com/blog/posts/2016-08-15-stock-screening/stock-screening/
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import datetime

import backtrader as bt


class Screener_SMA(bt.Analyzer):
    params = dict(period=10)

    def start(self):
        self.smas = {data: bt.indicators.SMA(data, period=self.p.period)
                     for data in self.datas}

    def stop(self):
        self.rets['over'] = list()
        self.rets['under'] = list()

        for data, sma in self.smas.items():
            node = data._name, data.close[0], sma[0]
            if data > sma:  # if data.close[0] > sma[0]
                self.rets['over'].append(node)
            else:
                self.rets['under'].append(node)


DEFAULTTICKERS = ['YHOO', 'IBM', 'AAPL', 'TSLA', 'ORCL', 'NVDA']


def run(args=None):
    args = parse_args(args)
    todate = datetime.date.today()
    # Get from date from period +X% for weekeends/bank/holidays: let's double
    fromdate = todate - datetime.timedelta(days=args.period * 2)

    cerebro = bt.Cerebro()
    for ticker in args.tickers.split(','):
        data = bt.feeds.YahooFinanceData(dataname=ticker,
                                         fromdate=fromdate, todate=todate)
        cerebro.adddata(data)

    cerebro.addanalyzer(Screener_SMA, period=args.period)
    cerebro.run(runonce=False, stdstats=False, writer=True)


def parse_args(pargs=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='SMA Stock Screener')

    parser.add_argument('--tickers', required=False, action='store',
                        default=','.join(DEFAULTTICKERS),
                        help='Yahoo Tickers to consider, COMMA separated')

    parser.add_argument('--period', required=False, action='store',
                        type=int, default=10,
                        help=('SMA period'))

    if pargs is not None:
        return parser.parse_args(pargs)

    return parser.parse_args()


if __name__ == '__main__':
    run()
