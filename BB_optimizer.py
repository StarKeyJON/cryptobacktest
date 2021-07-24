# -*- coding: utf-8 -*-
 
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
 
import datetime  # For datetime objects
import pandas as pd
import backtrader as bt
import numpy as np
 
# Create a Stratey
class MyStrategy(bt.Strategy):
    params = (
        ('pband', 20),
        ('pbfactor', 3),
        ('size', .5)
    )
 
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
 
    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
 
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

 
        # Calculating Bollinger Bands
        self.boll = bt.indicators.BollingerBands(period=self.params.pband, devfactor=self.params.pbfactor)

        # # Add a MovingAverageSimple indicator
        # # self.ssa = ssa_index_ind(
        # #     self.datas[0], ssa_window=self.params.ssa_window)
        # self.sma = bt.indicators.SimpleMovingAverage(
        #     self.datas[0], period=self.params.maperiod)
 
 
    def next(self):
        if self.order:
            return

        if not self.position:    
            if self.dataclose < self.boll.lines.bot:
                self.buy(exectype=bt.Order.Market, price=self.boll.lines.bot[0], size=self.params.size)
        else:
            if self.position.size > 0:
                if self.dataclose > self.boll.lines.top:
                    self.sell(exectype=bt.Order.Market, price=self.boll.lines.top[0], size=self.params.size)
 
    def stop(self):
        self.log('(Period %2d) ' %
                 (self.params.pband)+'(Factor %2d) Ending Value %.2f' %
                 (self.params.pbfactor, self.broker.getvalue()))
        f = open('BB_OPT.csv', 'a')
        f.write('\n%2d,' %
                 (self.params.pband)+'%2d,%.2f' %
                 (self.params.pbfactor, self.broker.getvalue()))
        f.close()
        
 
 
if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.optstrategy(
        MyStrategy,
        pband=range(50, 100),
        pbfactor=range(1,5))
    dataframe = pd.read_csv('./history/FIL-USD.csv', index_col=0, parse_dates=True)
    dataframe['openinterest'] = 0
    data = bt.feeds.PandasData(dataname=dataframe)
    cerebro.adddata(data)
    cerebro.broker.setcash(10000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    cerebro.broker.setcommission(commission=0.03)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # cerebro.plot()