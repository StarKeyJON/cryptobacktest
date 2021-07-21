from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
# -*- coding: utf-8 -*-
import matplotlib
import matplotlib.pyplot as plt
import csv
from datetime import datetime
import argparse
import backtrader.analyzers as btanalyzers
import backtrader as bt
import backtrader.feeds as btfeeds
from pandas.core.frame import DataFrame
import qgrid
import pandas as pd

# matplotlib.use('Qt5Agg')
# plt.switch_backend('Qt5Agg')

# Create a Stratey
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        if self.dataclose[0] < self.dataclose[-1]:
            # current close less than previous close

            if self.dataclose[-1] < self.dataclose[-2]:
                # previous close less than the previous close

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.buy()
            else:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.sell()





# SMA Cross Strategy
class SmaCross(bt.SignalStrategy):
    def __init__(self):
        sma1, sma2 = bt.ind.SMA(period=10), bt.ind.SMA(period=30)
        crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_LONG, crossover)






class firstStrategy(bt.Strategy):
    params = (
        ('period',21),
        )

    def __init__(self):
        self.startcash = self.broker.getvalue()
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=self.params.period)

    def next(self):
        if not self.position:
            if self.rsi < 30:
                self.buy(size=100)
        else:
            if self.rsi > 70:
                self.sell(size=100)

    def stop(self):
        pnl = round(self.broker.getvalue() - self.startcash,2)
        print('RSI Period: {} Final PnL: {}'.format(
            self.params.period, pnl))



# https://intelligentonlinetools.com/blog/2019/10/13/comparing-strategies-detecting-buy-signal/
# Create a subclass of Strategy to define the indicators and logic
class SmaCross(bt.Strategy):
    # parameters which are configurable for the strategy
    params = dict(
        pfast=3,  # period for the fast moving average
        pslow=25,   # period for the slow moving average
        pband=4,
        pbfactor=4,
        size=10,
        fast=13,
        slow=48,
        long=200,
        longonly=False,
    )
    params['tr_strategy'] = None
    
    def log(self, txt, dt=None):
        if self.p.printout:
            dt = dt or self.data.datetime[0]
            dt = bt.num2date(dt)
            print(f'{dt.isoformat()}, {txt}')
    
    def __init__(self):

        self.orderid = None  # to control operation entries

        self.fast_ema = bt.ind.EMA(period=self.p.fast)
        self.slow_ema = bt.ind.EMA(period=self.p.slow)
        self.long_ema = bt.ind.EMA(period=self.p.long)
        self.signal = bt.ind.CrossOver(self.fast_ema, self.slow_ema)
        self.dataclose= self.datas[0].close    # Keep a reference to 
        self.stoch = bt.ind.Stochastic() # stochastic RSI
        self.boll = bt.indicators.BollingerBands(period=self.p.pband, devfactor=self.p.pbfactor)
        self.sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        self.sma2 = bt.ind.SMA(period=self.p.pslow)  # slow moving average
        self.crossover = bt.ind.CrossOver(self.sma1, self.sma2)  # crossover signal
        self.tr_strategy = self.params.tr_strategy
        self.rsi = bt.indicators.RelativeStrengthIndex()
        self.macd = bt.indicators.MACD()
        self.ind = bt.indicators.DicksonMovingAverage()

 
    def next(self, strategy_type=""):
        tr_str = self.tr_strategy
        print (self.tr_strategy)
        
        # Log the closing prices of the series
        self.log("Close, {0:8.2f} ".format(self.dataclose[0]))
        self.log('Lows, {0:8.2f}'.format(self.sma1[0]))
         
        if tr_str == "cross":
            if not self.position:  # not in the market
                if self.crossover > 0:  # if fast crosses slow to the upside
                    self.order = self.buy()  # enter long
                elif self.crossover < 0: # else go short
                    self.order = self.sell()
            else:
                if self.position.size > 0:
                    if self.crossover > 0:  # if fast crosses slow to the upside
                        self.order = self.buy()  # enter long
                    elif self.crossover < 0: # else go short
                        self.order = self.sell()
 
               
        if tr_str == "simple1":
           
            if not self.position: # not in the market
                if self.dataclose[0] < self.dataclose[-1]:
                    if self.dataclose[-1] < self.dataclose[-2]:
                        self.log('BUY CREATE {0:8.2f}'.format(self.dataclose[0]))
                        self.order = self.buy()
                    elif self.dataclose[-1] > self.dataclose[-2]:
                        self.log('SELL CREATE {0:8.2f}'.format(self.dataclose[0]))
                        self.order = self.sell()
                else:
                    if self.position.size > 0:
                        if self.dataclose[0] < self.dataclose[-1]:
                            if self.dataclose[-1] < self.dataclose[-2]:
                                self.log('BUY CREATE {0:8.2f}'.format(self.dataclose[0]))
                                self.order = self.buy()
                            elif self.dataclose[-1] > self.dataclose[-2]:
                                self.log('SELL CREATE {0:8.2f}'.format(self.dataclose[0]))
                                self.order = self.sell()
                         
        if tr_str == "simple2":
            
            if not self.position: # not in the market
                if (self.dataclose[0] - self.dataclose[-1]) < -0.05*self.dataclose[0] or (self.dataclose[0] - self.dataclose[-2]) < -0.05*self.dataclose[0] or (self.dataclose[0] - self.dataclose[-3]) < -0.05*self.dataclose[0] or (self.dataclose[0] - self.dataclose[-4]) < -0.05*self.dataclose[0]:
                   
                        self.log('BUY CREATE {0:8.2f}'.format(self.dataclose[0]))
                        self.order = self.buy()
                elif (self.dataclose[0] - self.dataclose[-1]) > -0.05*self.dataclose[0] or (self.dataclose[0] - self.dataclose[-2]) > -0.05*self.dataclose[0] or (self.dataclose[0] - self.dataclose[-3]) > -0.05*self.dataclose[0] or (self.dataclose[0] - self.dataclose[-4]) > -0.05*self.dataclose[0]:
                        self.log('SELL CREATE {0:8.2f}'.format(self.dataclose[0]))
                        self.order = self.sell()
            else:
                if self.position.size > 0:
                    if (self.dataclose[0] - self.dataclose[-1]) < -0.05*self.dataclose[0] or (self.dataclose[0] - self.dataclose[-2]) < -0.05*self.dataclose[0] or (self.dataclose[0] - self.dataclose[-3]) < -0.05*self.dataclose[0] or (self.dataclose[0] - self.dataclose[-4]) < -0.05*self.dataclose[0]:

                            self.log('BUY CREATE {0:8.2f}'.format(self.dataclose[0]))
                            self.order = self.buy()
                    elif (self.dataclose[0] - self.dataclose[-1]) > -0.05*self.dataclose[0] or (self.dataclose[0] - self.dataclose[-2]) > -0.05*self.dataclose[0] or (self.dataclose[0] - self.dataclose[-3]) > -0.05*self.dataclose[0] or (self.dataclose[0] - self.dataclose[-4]) > -0.05*self.dataclose[0]:
                            self.log('SELL CREATE {0:8.2f}'.format(self.dataclose[0]))
                            self.order = self.sell()

        if tr_str == "rsi":
            if not self.position:
                    if (self.rsi[0] < 20):
                        self.log('BUY CREATE {0:8.2f}'.format(self.dataclose[0]))
                        self.order = self.buy()
                    else:
                        if (self.rsi[0] > 80):
                            self.log('SELL CREATE {0:8.2f}'.format(self.dataclose[0]))
                            self.order = self.sell()
            else:
                if self.position.size > 0:
                    if (self.rsi[0] < 20):
                        self.log('BUY CREATE {0:8.2f}'.format(self.dataclose[0]))
                        self.order = self.buy()
                    else:
                        if (self.rsi[0] > 80):
                            self.log('SELL CREATE {0:8.2f}'.format(self.dataclose[0]))
                            self.order = self.sell()                    

        if tr_str == "BB":

            if not self.position:    
                if self.data.close > self.boll.lines.top:
                    self.sell(exectype=bt.Order.Market, price=self.boll.lines.top[0], size=self.p.size)
                if self.data.close < self.boll.lines.bot:
                    self.buy(exectype=bt.Order.Market, price=self.boll.lines.bot[0], size=self.p.size)
            else:
                if self.position.size > 0:
                    if self.data.close > self.boll.lines.top:
                        self.sell(exectype=bt.Order.Market, price=self.boll.lines.mid[0], size=self.p.size)
                else:
                    if self.data.close < self.boll.lines.bot:
                        self.buy(exectype=bt.Order.Market, price=self.boll.lines.mid[0], size=self.p.size) 

            # if not self.position:
            #     if self.data.close < self.boll.lines.bot:
            #         self.log('BUY CREATE {0:8.2f}'.format(self.dataclose[0]))
            #         self.order = self.buy()   
            #     elif self.data.close > self.boll.lines.top:
            #         self.log('SELL CREATE {0:8.2f}'.format(self.dataclose[0]))
            #         self.order = self.sell() 

            # else:
            #     if self.data.close < self.boll.lines.bot:
            #         self.log('BUY CREATE {0:8.2f}'.format(self.dataclose[0]))
            #         self.order = self.buy()   
            #     elif self.data.close > self.boll.lines.top:
            #         self.log('SELL CREATE {0:8.2f}'.format(self.dataclose[0]))
            #         self.order = self.sell()                  


        if tr_str == "BB_RSI":
            if not self.position:           
                if self.data.close < self.boll.lines.bot and (self.rsi[0] < 20):
                    self.log('BUY CREATE {0:8.2f}'.format(self.dataclose[0]))
                    self.order = self.buy(exectype=bt.Order.Market, price=self.boll.lines.bot[0], size=self.p.size)   
                elif self.data.close > self.boll.lines.top and (self.rsi[0] > 78):
                    self.log('SELL CREATE {0:8.2f}'.format(self.dataclose[0]))
                    self.order = self.sell(exectype=bt.Order.Market, price=self.boll.lines.top[0], size=self.p.size) 
            else:
                if self.position.size > 0 :
                    if self.data.close < self.boll.lines.bot and (self.rsi[0] < 20):
                        self.log('BUY CREATE {0:8.2f}'.format(self.dataclose[0]))
                        self.order = self.buy(exectype=bt.Order.Market, price=self.boll.lines.bot[0], size=self.p.size)   
                    elif self.data.close > self.boll.lines.top and (self.rsi[0] > 78):
                        self.log('SELL CREATE {0:8.2f}'.format(self.dataclose[0]))
                        self.order = self.sell(exectype=bt.Order.Market, price=self.boll.lines.top[0], size=self.p.size)                    
                 
        if tr_str == "CrossOver":
            if self.orderid:
                return  # if an order is active, no new orders are allowed

            # Buy when price above long EMA and fast EMA crosses above slow EMA
            if self.data.close[0] > self.long_ema[0] and self.signal > 0.0:
                self.log('BUY CREATE {0:8.2f}'.format(self.dataclose[0]))
                self.buy()
                self.orderid = 1
                self.sell_price = (self.data.close[0]-self.long_ema[0]) * 1.5 + self.data.close[0]

            # Sell when price below long EMA and fast EMA crosses below slow EMA
            elif self.data.close[0] < self.long_ema[0] and self.signal < 0.0:
                if not self.p.longonly:
                    self.log(f'SELL {abs(self.getsizing())} shares '
                             f'of {self.data._name} at {self.data.close[0]}')
                    self.sell()
                    self.orderid = 2
                    self.buy_price = self.data.close[0] - (self.long_ema[0]-self.data.close[0]) * 1.5
                    if self.buy_price < 0:
                        raise Exception("ERROR")

            # Close long position
            elif self.orderid == 1 and self.data.close[0] >= self.sell_price:
                if self.position:
                    self.log(f'CLOSE LONG position of {self.position.size} shares '
                             f'of {self.data._name} at {self.data.close[0]:.2f}')
                    self.close()
                    self.orderid = None

            # Close short position
            elif self.orderid == 2 and self.data.close[0] >= self.sell_price:
                if self.position:
                    self.log(f'CLOSE SHORT position of {abs(self.position.size)} shares '
                             f'of {self.data._name} at {self.data.close[0]:.2f}')
                    self.close()
                    self.orderid = None


        #print('Current Portfolio Value: %.2f' % cerebro.broker.getvalue())            
         
    def log(self, txt, dt=None):
        # Logging function for the strategy.  'txt' is the statement and 'dt' can be used to specify a specific datetime
        dt = dt or self.datas[0].datetime.date(0)
        print('{0},{1}'.format(dt.isoformat(),txt))
      
         
    def notify_trade(self,trade):
        if not trade.isclosed:
            return
         
        self.log('OPERATION PROFIT, GROSS {0:8.2f}, NET {1:8.2f}'.format(trade.pnl, trade.pnlcomm))    
  




# https://randlow.github.io/posts/trading/trading-strat-parameter-opt/
class Strat2_BGTMA_SLSMA(bt.Strategy):
    
    params = (
        ('maperiod',15), # Tuple of tuples containing any variable settings required by the strategy.
        ('printlog',False), # Stop printing the log of the trading strategy
        
    )
    
    def __init__(self):
        self.dataclose= self.datas[0].close    # Keep a reference to the "close" line in the data[0] dataseries
        self.order = None # Property to keep track of pending orders.  There are no orders when the strategy is initialized.
        self.buyprice = None
        self.buycomm = None
        
        # Add SimpleMovingAverage indicator for use in the trading strategy
        self.sma = bt.indicators.SimpleMovingAverage( 
            self.datas[0], period=self.params.maperiod)
    
    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint: # Add if statement to only log of printlog or doprint is True
            dt = dt or self.datas[0].datetime.date(0)
            print('{0},{1}'.format(dt.isoformat(),txt))
    
    def notify_order(self, order):
        # 1. If order is submitted/accepted, do nothing 
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 2. If order is buy/sell executed, report price executed
        if order.status in [order.Completed]: 
            if order.isbuy():
                self.log('BUY EXECUTED, Price: {0:8.2f}, Size: {1:8.2f} Cost: {2:8.2f}, Comm: {3:8.2f}'.format(
                    order.executed.price,
                    order.executed.size,
                    order.executed.value,
                    order.executed.comm))
                
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log('SELL EXECUTED, {0:8.2f}, Size: {1:8.2f} Cost: {2:8.2f}, Comm{3:8.2f}'.format(
                    order.executed.price, 
                    order.executed.size, 
                    order.executed.value,
                    order.executed.comm))
            
            self.bar_executed = len(self) #when was trade executed
        # 3. If order is canceled/margin/rejected, report order canceled
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            
        self.order = None
    
    def notify_trade(self,trade):
        if not trade.isclosed:
            return
        
        self.log('OPERATION PROFIT, GROSS {0:8.2f}, NET {1:8.2f}'.format(
            trade.pnl, trade.pnlcomm))
    
    def next(self):
        # Log the closing prices of the series from the reference
        self.log('Close, {0:8.2f}'.format(self.dataclose[0]))

        if self.order: # check if order is pending, if so, then break out
            return
                
        # since there is no order pending, are we in the market?    
        if not self.position: # not in the market
            if self.dataclose[0] > self.sma[0]:
                self.log('BUY CREATE {0:8.2f}'.format(self.dataclose[0]))
                self.order = self.buy()           
        else: # in the market
            if self.dataclose[0] < self.sma[0]:
                self.log('SELL CREATE, {0:8.2f}'.format(self.dataclose[0]))
                self.order = self.sell()
                
    def stop(self):
        self.log('MA Period: {0:8.2f} Ending Value: {1:8.2f}'.format(
            self.params.maperiod, 
            self.broker.getvalue()),
                 doprint=True)






class MaCrossStrategy(bt.Strategy):
     
    params = (
        ('fast_length', 10),
        ('slow_length', 50)
    )
     
    def __init__(self):
        ma_fast = bt.ind.SMA(period = self.params.fast_length)
        ma_slow = bt.ind.SMA(period = self.params.slow_length)
         
        self.crossover = bt.ind.CrossOver(ma_fast, ma_slow)
 
    def next(self):
        if not self.position:
            if self.crossover > 0: 
                self.buy()
        elif self.crossover < 0: 
            self.close()




def run_strat():
             
    # strategy_final_values=[0,0,0,0,0,0]
    # strategies = ["cross", "simple1", "simple2", "rsi", "BB", "BB_RSI"]

    strategy_final_values=[0,0,0]
    strategies = ["BB","BB_RSI","CrossOver"]
 
    crypto = csv.reader(open('ticker.csv'))

    for project in crypto:
        print(project)
        #pulling the compiled csv list into a tuple
        symbol, name = project
        f = open('bakca.csv', 'a')
        f.write("\n")
        f.write("\n"+name)
        f.write("\n")
        f.close()

    # #creating individual files for each project
        history_filename = './history/{}.csv'.format(symbol)
        for tr_strategy in strategies:         
            args = parse_args()
            cerebro = bt.Cerebro()  # create a "Cerebro" engine instance

            # Get a pandas dataframe
            datapath = (history_filename)
            # Simulate the header row if noheaders requested
            skiprows = 1 if args.noheaders else 0
            header = None if args.noheaders else 0
            dataframe = pd.read_csv(datapath,
                                        skiprows=skiprows,
                                        header=header,
                                        parse_dates=True,
                                        index_col=0)
            if not args.noprint:
                print('--------------------------------------------------')
                print(dataframe)
                print('--------------------------------------------------')
            # Pass it to the backtrader datafeed and add it to the cerebro
            data = bt.feeds.PandasData(dataname=dataframe)

            cerebro.adddata(data)  # Add the data feed

            # Print out the starting conditions
            print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
            f = open('bakca.csv', 'a')
            f.write('\n'+tr_strategy+'\n')

            cerebro.broker.setcommission(commission=.35) 
            cerebro.addsizer(bt.sizers.PercentSizer, percents =10)
            cerebro.addanalyzer(btanalyzers.SharpeRatio, _name = "sharpe")
            cerebro.addanalyzer(btanalyzers.DrawDown, _name = "drawdown")
            cerebro.addanalyzer(btanalyzers.Returns, _name = "returns")
            cerebro.addstrategy(SmaCross, tr_strategy=tr_strategy)  # Add the trading strategy
            cerebro.run()  # run it all
            # print(result)
            # figure=cerebro.plot(iplot=False)[0][0]  
            #figure.savefig('example.png')

            # Print out the final result
            print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
            f.write('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
            f.close
            ind=strategies.index(tr_strategy)
            strategy_final_values[ind] = cerebro.broker.getvalue()


        print ("Final Vaues for Strategies")
        for tr_strategy in strategies: 
            ind=strategies.index(tr_strategy)
            print ("{} {}  ". format(tr_strategy, strategy_final_values[ind]))  
            # #writing to the csv file and creating the history
            f = open('bakca.csv', 'a')
            f.write("\n{} {}  ". format(tr_strategy, strategy_final_values[ind]))
            f.close()
        # f = open('bakca.csv', 'a')
        # f.write('Final Portfolio Value: %.2f' % cerebro.broker.getvalue()+'\n')
        # f.close()






def runstrat():
    args = parse_args()

    #Variable for our starting cash
    startcash = 10000.00

    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Get a pandas dataframe
    datapath = ('/home/jon/Desktop/Backtester/history/AAVE-USD.csv')
    # Simulate the header row if noheaders requested
    skiprows = 1 if args.noheaders else 0
    header = None if args.noheaders else 0
    dataframe = pd.read_csv(datapath,
                                skiprows=skiprows,
                                header=header,
                                parse_dates=True,
                                index_col=0)
    if not args.noprint:
        print('--------------------------------------------------')
        print(dataframe)
        print('--------------------------------------------------')
    # Pass it to the backtrader datafeed and add it to the cerebro
    data = bt.feeds.PandasData(dataname=dataframe)

    cerebro.adddata(data)

    #Add our strategy
    #cerebro.addstrategy(Strat2_BGTMA_SLSMA)
    # strats = cerebro.optstrategy(
    #     MaCrossStrategy,
    #     fast_length = range(1, 11), 
    #     slow_length = range(25, 76, 5))
    
    strats = cerebro.optstrategy(Strat2_BGTMA_SLSMA,maperiod=range(1-15))

    # Set our desired cash start
    cerebro.broker.setcash(startcash)
    cerebro.broker.setcommission(commission=.03)

    cerebro.addsizer(bt.sizers.PercentSizer, percents = 10)
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name = "sharpe")
    cerebro.addanalyzer(btanalyzers.DrawDown, _name = "drawdown")
    cerebro.addanalyzer(btanalyzers.Returns, _name = "returns")
    

    # Run over everything
    back = cerebro.run()

    # #Get final portfolio Value
    portvalue = cerebro.broker.getvalue()
    pnl = portvalue - startcash

    par_list = [[x[0].analyzers.returns.get_analysis()['rnorm100'], 
             x[0].analyzers.drawdown.get_analysis()['max']['drawdown'],
             x[0].analyzers.sharpe.get_analysis()['sharperatio']
            ] for x in back]

    par_df = pd.DataFrame(par_list, columns = ['return', 'dd', 'sharpe'])
	
    qgrid.show_grid(par_df)
    f = open('optim.csv', 'a')
    f.write("\n{} {}  ". format(par_list, par_df))
    f.close()
    # Plot the result
    #cerebro.plot(style='bar')


def parse_args():
    parser = argparse.ArgumentParser(
        description='Pandas test script')

    parser.add_argument('--noheaders', action='store_true', default=False,
                        required=False,
                        help='Do not use header rows')

    parser.add_argument('--noprint', action='store_true', default=False,
                        help='Print the dataframe')

    return parser.parse_args()


if __name__ == '__main__':
    run_strat()
