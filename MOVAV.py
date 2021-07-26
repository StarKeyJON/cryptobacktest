'''

As taken from: https://community.backtrader.com/topic/2893/bollingerbands-squeeze

'''


from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from datetime import datetime
from os import cpu_count, stat_result
from backtrader.sizers import percents_sizer
from backtrader.trade import TradeHistory

import pandas as pd
import backtrader as bt
import numpy as np
import csv

results = './optimizer_results/RSI__OPT__3.csv'

now = datetime.now()

current_time = now.strftime("%H:%M:%S")

class KeltnerChannel(bt.Strategy):

    lines = ('mid', 'top', 'bot',)
    params = dict(period=34,devfactor=1.5,fast=8,slow=50,long=253, xlong=553,
              movav= bt.ind.MovAv.Simple,order_count=0,rsi_period=25,lookback=7,
              me1=12,me2=26,psignal=9,movex=bt.ind.MovAv.Exponential,period2=5, movav2=bt.ind.MovAv.SMA)

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
        self.xlong_ema = bt.ind.EMA(period=self.params.xlong)
        self.signal = bt.ind.CrossOver(self.fast_ema, self.slow_ema)
        self.signal2 = bt.ind.CrossOver(self.fast_ema, self.xlong_ema)
        self.signal3 = bt.ind.CrossOver(self.dataclose, self.moving_av)
        self.rsi = bt.indicators.RSI(period=self.params.rsi_period, lookback=self.params.lookback)
        self.macd = bt.indicators.MACD(period_me1=self.params.me1, period_me2= self.params.me2, period_signal=self.params.psignal, movav= self.params.movex)
        self.order_price = 0

    def next(self):
            if self.order:
                return  # if an order is active, no new orders are allowed

            # Uptrend
            # Buy when price is above long EMA and fast EMA crosses above slow EMA
            if self.dataclose > self.long_ema[0]:
                if self.signal2 < 0.0 and self.rsi > 50:
                    #self.log('BUY CREATE {0:8.2f}'.format(self.dataclose[0]))
                    self.buy()
                    self.in_position += 1
                    self.order_price = self.dataclose[0]
                    self.params.order_count += 1
                    # self.sell_price = (self.data.close[0]-self.long_ema[0]) * 1.5 + self.data.close[0]
                elif self.signal < 0.0 and self.rsi < 50 and self.macd < 0:
                    if self.in_position > 0:
                            self.sell()
                            self.in_position -= 1
                            self.params.order_count += 1
                    
            # Downtrend
            # Sell when price is below long EMA and fast EMA crosses below slow EMA
            elif self.dataclose < self.long_ema[0]:
                if self.signal2 < 0 and self.in_position > 0 and self.rsi > 60 and self.macd < 0:
                    if self.in_position > 0:
                #self.log(f'SELL {abs(self.getsizing())} shares '
                #         f'of {self.data._name} at {self.data.close[0]}')
                        self.sell()
                        self.in_position-=1
                        self.params.order_count += 1
                        # self.buy_price = self.data.close[0] - (self.long_ema[0]-self.data.close[0]) * 1.5
                # elif self.signal2 > 0 and self.rsi > 50:
                #     self.buy()
                #     self.in_position+=1
                #     self.params.order_count +=1

                else:
                    if self.signal > 0 and self.rsi > 50 and self.macd > 0:
                        self.buy()
                        self.in_position+=1
                        self.params.order_count +=1

            # If the rsi is extremely overbought or oversold(a rare opportunity), execute buy/sell orders.        
            # if self.rsi < 2: 
            #     self.buy()
            #     self.in_position+=1
            #     self.params.order_count+=1
            # if self.signal3 > 0 and self.rsi < 5: 
            #     self.buy()
            #     self.in_position+=1
            #     self.params.order_count+=1
            # if self.signal3 < 0 and self.rsi < 5: 
            #     self.buy()
            #     self.in_position+=1
            #     self.params.order_count+=1

            # if self.rsi > 98 and self.in_position>0:
            #     self.sell()
            #     self.in_position-=1
            #     self.params.order_count+=1
            # if self.signal3 > 0 and self.rsi > 95 and self.in_position>0:
            #     self.sell()
            #     self.in_position-=1
            #     self.params.order_count+=1
            # elif self.signal3 < 0 and self.rsi > 95 and self.in_position>0:
            #     self.sell()
            #     self.in_position-=1
            #     self.params.order_count+=1

    # def notify_trade(self,trade):
    #     if trade.isclosed:
    #         dt = self.data.datetime.date()

    #         print('---------------------------- TRADE ---------------------------------')
    #         print("1: Data Name:                            {}".format(trade.data._name))
    #         print("2: Bar Num:                              {}".format(len(trade.data)))
    #         print("3: Current date:                         {}".format(dt))
    #         print('4: Status:                               Trade Complete')
    #         print('5: Ref:                                  {}'.format(trade.ref))
    #         print('6: PnL:                                  {}'.format(round(trade.pnl,2)))
    #         print('7: Position Size:                       {}'.format(trade.commission))            
    #         print('--------------------------------------------------------------------')


 
    def stop(self):
        self.log('(Fast %2d) ' %
                 (self.params.fast)+'(Slow %2d)'%(self.params.slow)+'(Long %2d) Ending Value %.2f' %
                 (self.params.long, self.broker.getvalue())+' Orders: %2d'%(self.params.order_count) + " Remaining Units: " + str(self.in_position))
        f = open(results, 'a')
        f.write('\n%2d,' %
                 (self.params.fast)+'%2d,'%(self.params.slow)+'%2d,%.2f,' %
                 (self.params.long, self.broker.getvalue())+'%2d'%(self.params.order_count)+",%2d"%(self.params.rsi_period)+"\n")
        f.close()
        
 
 
if __name__ == '__main__':

    crypto = csv.reader(open('ticker.csv'))
