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
    params = (('sma_period', 15),
              ('stake', 1),
              ('printout', False),
              ('onlylong', False),
              ('csvcross', False))

    def start(self):
        pass

    def stop(self):
        self.log(u'(金叉死叉有用吗) Ending Value %.2f' %
                 (self.broker.getvalue()))

    def log(self, txt, dt=None):
        if self.p.printout:
            dt = dt or self.data.datetime[0]
            dt = bt.num2date(dt)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):

        # To control operation entries
        self.orderid = None

        # Create SMA on 2nd data
        sma = btind.MovAv.SMA(self.data, period=self.p.sma_period)
        # Create a CrossOver Signal from close an moving average
        self.signal = btind.CrossOver(self.data.close, sma)
        self.signal.csv = self.p.csvcross

    def next(self):
        if self.orderid:
            return  # if an order is active, no new orders are allowed

        if self.signal > 0.0:  # cross upwards
            if self.position:
                self.log('CLOSE SHORT , %.2f' % self.data.close[0])
                self.close()

            self.log('BUY CREATE , %.2f' % self.data.close[0])
            self.buy(size=self.p.stake)

        elif self.signal < 0.0:
            if self.position:
                self.log('CLOSE LONG , %.2f' % self.data.close[0])
                self.close()

            if not self.p.onlylong:
                self.log('SELL CREATE , %.2f' % self.data.close[0])
                self.sell(size=self.p.stake)

    def notify_order(self, order):
        if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
            return  # Await further notifications

        if order.status == order.Completed:
            if order.isbuy():
                buytxt = 'BUY COMPLETE, %.2f' % order.executed.price
                self.log(buytxt, order.executed.dt)
            else:
                selltxt = 'SELL COMPLETE, %.2f' % order.executed.price
                self.log(selltxt, order.executed.dt)

        elif order.status in [order.Expired, order.Canceled, order.Margin]:
            self.log('%s ,' % order.Status[order.status])
            pass  # Simply log

        # Allow new orders
        self.orderid = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log('TRADE PROFIT, GROSS %.2f, NET %.2f' %
                     (trade.pnl, trade.pnlcomm))

        elif trade.justopened:
            self.log('TRADE OPENED, SIZE %2d' % trade.size)


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
        sma_period=range(args.ma_low, args.ma_high),
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

    # 1手-100股
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)

    # 金额
    cerebro.broker.setcash(args.cash)

    # 佣金
    cerebro.broker.setcommission(commission=args.comm)

    # 添加分析
    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.addanalyzer(bt.analyzers.AnnualReturn)  # 年化收益
    cerebro.addanalyzer(bt.analyzers.DrawDown)  # 最大回撤

    # 绘图
    cerebro.addobserver(bt.observers.DrawDown)  # visualize the drawdown evol

    # clock the start of the process
    tstart = time.clock()

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    stratruns = cerebro.run()

    # 剩余本金与收益率
    money_left = cerebro.broker.getvalue()
    returns = float(money_left - args.cash) / args.cash
    print('Money_left {},Returns:{}'.format(float(money_left), returns))

    # clock the end of the process
    tend = time.clock()

    for stratrun in stratruns:
        print('**************************************************')
        for strat in stratrun:
            print('--------------------------------------------------')
            print(strat.p._getkwargs())  # 打印参数
            print('--------------------------------------------------')
            analyzers = strat.analyzers
            print('total analyzer:', len(analyzers))

            # 结果分析
            for analyzer in analyzers:
                print(analyzer.__class__.__name__)
                analysis = analyzer.get_analysis()
                print(analysis)

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
        default='2006-12-30',
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
        default=15, required=False,
        help='SMA range high to optimize')

    parser.add_argument('--cash', default=10000, type=int,
                        help='Starting Cash')

    parser.add_argument('--comm', default=2, type=float,
                        help='Commission for operation')

    return parser.parse_args()


if __name__ == '__main__':
    runstrat()
