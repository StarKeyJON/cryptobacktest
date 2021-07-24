




'''

As taken from: https://community.backtrader.com/topic/2893/bollingerbands-squeeze

'''


from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from datetime import datetime
from os import cpu_count
from backtrader.sizers import percents_sizer

import pandas as pd
import backtrader as bt
import numpy as np
import csv

results = './optimizer_results/EMA_OPT_SUSHI_3.csv'

now = datetime.now()

current_time = now.strftime("%H:%M:%S")

class KeltnerChannel(bt.Strategy):

    lines = ('mid', 'top', 'bot',)
    params = dict(period=40,devfactor=1.5,fast=7,slow=58,long=153,
              movav= bt.ind.MovAv.Simple,order_count=0,rsi_period=30,lookback=7,
              me1=12,me2=26,psignal=9,movex=bt.ind.MovAv.Exponential,period2=5, movav2=bt.ind.MovAv.SMA,
              tenkan=9, kijun=26, senkou=52, senkou_lead=26, chikou=26)

    plotinfo = dict(subplot=False)
    plotlines = dict(
        mid=dict(ls='--'),
        top=dict(_samecolor=True),
        bot=dict(_samecolor=True),
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt)) 

    def _plotlabel(self):
        plabels = [self.params.period, self.params.devfactor]
        plabels += [self.params.movav] * self.params.notdefault('movav')
        return plabels

    def __init__(self):
        self.in_position=0
        self.dataclose = self.datas[0].close
        self.lines.mid = ma = self.params.movav(self.data, period=self.params.period)
        atr = self.params.devfactor * bt.ind.ATR(self.data, period=self.params.period)
        self.lines.top = ma + atr
        self.lines.bot = ma - atr
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.moving_av = bt.ind.MovingAverageSimple(period=self.params.period)
        self.fast_ema = bt.ind.EMA(period=self.params.fast)
        self.slow_ema = bt.ind.EMA(period=self.params.slow)
        self.long_ema = bt.ind.EMA(period=self.params.long)
        self.rsi = bt.indicators.RSI(period=self.params.rsi_period, lookback=self.params.lookback)
        self.macd = bt.indicators.MACD(period_me1=self.params.me1, period_me2= self.params.me2, period_signal=self.params.psignal, movav= self.params.movex)
        self.order_price = 0
        self.indi = bt.ind.Ichimoku()
        self.tenkan_sen = self.ich.l.tenkan_sen[0]
        self.kijun_sen = self.ich.l.kijun_sen[0]
        self.senkou_span_a = self.ich.l.senkou_span_a[0]
        self.senkou_span_b = self.ich.l.senkou_span_b[0]
        self.ichi = self.ich.l.chikou_span[0]

    def next(self):
            if self.order:
                return  # if an order is active, no new orders are allowed

            # Uptrend
            # Buy when price above long EMA and fast EMA crosses above slow EMA
            if self.dataclose > self.long_ema[0]:
                if self.signal2 > 0.0 and self.rsi < 70 and self.in_position == 0:
                    #self.log('BUY CREATE {0:8.2f}'.format(self.dataclose[0]))
                    self.buy()
                    self.in_position += 1
                    self.order_price = self.dataclose[0]
                    self.params.order_count += 1

                #self.sell_price = (self.data.close[0]-self.long_ema[0]) * 1.5 + self.data.close[0]
                elif self.signal2 < 0:
                    if self.in_position > 0 and self.rsi > 75:
                        if self.dataclose[0] > self.order_price*.1:
                            self.sell()
                            self.in_position -= 1
                            self.params.order_count += 1
                    
            # Downtrend
            # Sell when price below long EMA and fast EMA crosses below slow EMA
            elif self.dataclose < self.long_ema[0]:
                if self.signal2 < 0.0 and self.in_position > 0 and self.rsi > 60:
                #self.log(f'SELL {abs(self.getsizing())} shares '
                #         f'of {self.data._name} at {self.data.close[0]}')
                    if self.dataclose[0] > self.order_price*.1:
                        self.sell()
                        self.in_position-=1
                        self.params.order_count += 1
                #self.buy_price = self.data.close[0] - (self.long_ema[0]-self.data.close[0]) * 1.5
                elif self.signal < 0.0 and self.rsi < 30 and self.in_position == 0:
                    self.buy()
                    self.in_position+=1
                    self.params.order_count +=1


 
    def stop(self):
        self.log('(Fast %2d) ' %
                 (self.params.fast)+'(Slow %2d)'%(self.params.slow)+'(Long %2d) Ending Value %.2f' %
                 (self.params.long, self.broker.getvalue())+' Orders: %2d'%(self.params.order_count))
        f = open(results, 'a')
        f.write('\n%2d,' %
                 (self.params.fast)+'%2d,'%(self.params.slow)+'%2d,%.2f,' %
                 (self.params.long, self.broker.getvalue())+'%2d'%(self.params.order_count)+"\n")
        f.close()
        
 
 
if __name__ == '__main__':

    crypto = csv.reader(open('ticker.csv'))

    for project in crypto:
        print(project)
        #pulling the compiled csv list into a tuple
        symbol, name = project
        f = open(results, 'a')
        f.write(name+"  :  "+current_time+"\n")
        history_filename = './history/{}.csv'.format(symbol)

        #Engage cerebro engine specs
        cerebro = bt.Cerebro()
        cerebro.addstrategy(
            KeltnerChannel)

        dataframe = pd.read_csv(history_filename, index_col=0, parse_dates=True)
        dataframe['openinterest'] = 0
        data = bt.feeds.PandasData(dataname=dataframe)
        cerebro.adddata(data)

        start_cash = 10000.00
        cerebro.broker.setcash(start_cash)
        cerebro.addsizer(bt.sizers.PercentSizer, percents=10)
        cerebro.broker.setcommission(commission=0.03)

        portvalue = cerebro.broker.getvalue()
        pnl = portvalue - start_cash

        print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
        cerebro.run(cpu_count=4)
        print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue()+" %2d"%(pnl))
        figure=cerebro.plot(iplot=False)[0][0]  
        figure.savefig('./pngs/SUSHI_EMA_OPT3.png')
