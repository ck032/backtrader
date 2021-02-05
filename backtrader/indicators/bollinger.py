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

from . import Indicator, MovAv, StdDev

# A.从这个脚本中，可以看到，定义一个指标，只需要：
# 1.继承Indicator
# 2.定义线、定义好线的绘图方式
# 3.定义线，包括：线的别名、名称、参数、计算方法

# B.BollingerBands：布林线。中线-简单移动均线（20，26），标准差系数（2，可以微调为1.9,2.1等）

class BollingerBands(Indicator):
    '''
    Defined by John Bollinger in the 80s. It measures volatility by defining
    upper and lower bands at distance x standard deviations

    Formula:
      - midband = SimpleMovingAverage(close, period)
      - topband = midband + devfactor * StandardDeviation(data, period)
      - botband = midband - devfactor * StandardDeviation(data, period)

    See:
      - http://en.wikipedia.org/wiki/Bollinger_Bands
    '''
    alias = ('BBands',) # alias定义别名

    lines = ('mid', 'top', 'bot',) # 定义线（指标）的名称，这是一个元组；然后在init部分定义线的计算方式
    params = (('period', 20), ('devfactor', 2.0), ('movav', MovAv.Simple),) # params定义参数，带有默认值

    plotinfo = dict(subplot=False) # subplot默认为True；绘图的全局信息
    plotlines = dict(
        mid=dict(ls='--'),
        top=dict(_samecolor=True),
        bot=dict(_samecolor=True),
    )  # 绘图-线的展示形式

    def _plotlabel(self):
        # 利用_plotlabel可以传参（用户自定义的label）
        plabels = [self.p.period, self.p.devfactor]
        plabels += [self.p.movav] * self.p.notdefault('movav')
        return plabels

    def __init__(self):
        self.lines.mid = ma = self.p.movav(self.data, period=self.p.period)
        stddev = self.p.devfactor * StdDev(self.data, ma, period=self.p.period,
                                           movav=self.p.movav)
        self.lines.top = ma + stddev
        self.lines.bot = ma - stddev

        super(BollingerBands, self).__init__()


class BollingerBandsPct(BollingerBands):
    '''
    Extends the Bollinger Bands with a Percentage line
    '''
    lines = ('pctb',)
    plotlines = dict(pctb=dict(_name='%B'))  # display the line as %B on chart 绘图名称

    def __init__(self):
        super(BollingerBandsPct, self).__init__()
        self.l.pctb = (self.data - self.l.bot) / (self.l.top - self.l.bot) # 利用top/bottom/self.data构造出来一个衍生的pctb指标，绘图的名称是 ‘%B’
