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

from backtrader import Indicator
from backtrader.functions import *

# The modules below should/must define __all__ with the Indicator objects
# of prepend an "_" (underscore) to private classes/variables

from .basicops import *

#--------------------------------------------------------
# PART-1 移动均线类
# 总的来看，移动均线的用法就是利用均线的上穿或者下穿，来发出信号
# 其他各种指标线，无非是找到更好的一条线，来规避均线滞后性的问题
#--------------------------------------------------------
# base for moving averages
from .mabase import *  # 简单移动平均的基类

# moving averages (so envelope and oscillators can be auto-generated)
from .sma import *  # 简单移动平均 
from .ema import *  # 指数平滑
from .smma import * # 指数平滑算法 - smma - 影响到alpha的计算
from .wma import *  # 加权移动平均 - w - weighted  - 近期的权重大
from .dema import * # 双指数移动平均线(DEMA),三重指数移动平均线(TEMA)
from .kama import * # KAMA指标,自适用的alpha
from .zlema import * # 零滞后项的指数移动平均，zlema
from .hma import * # 赫尔移动平均，hma，降低移动平均线的滞后性,并且保持平滑性
from .zlind import * # 降低移动平均线的滞后性
from .dma import * # 综合了hma，zlind，取二者的平均数

# depends on moving averages
# 波动：收盘价和移动均线（作为均值）之间的标准差，ABS线
from .deviation import *

# depend on basicops, moving averages and deviations
from .atr import *  # 平均真实波动范围 - ATR - 价格波动幅度/判断市场交易氛围
from .aroon import * # 黎明之光指标 - aroon - 上线、下线/判断市场方向
from .bollinger import * # Bolling线
from .cci import *
from .crossover import *
from .dpo import *
from .directionalmove import *
from .envelope import *
from .heikinashi import *
from .lrsi import *
from .macd import *
from .momentum import *
from .oscillator import *
from .percentchange import *
from .percentrank import *
from .pivotpoint import *
from .prettygoodoscillator import *
from .priceoscillator import *
from .psar import *
from .rsi import * # 相对强弱指标RSI
from .stochastic import * # KD
from .trix import *
from .tsi import *
from .ultimateoscillator import *
from .williams import *
from .rmi import * # 设定好参数的RSI指标
from .awesomeoscillator import *
from .accdecoscillator import *


from .dv2 import *  # depends on percentrank

# Depends on Momentum
from .kst import *

from .ichimoku import *

from .hurst import *
from .ols import *
from .hadelta import *
