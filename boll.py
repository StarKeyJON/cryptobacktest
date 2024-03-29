# https://backtest-rookies.com/2018/02/23/backtrader-bollinger-mean-reversion-strategy/
import backtrader as bt
from datetime import datetime
import argparse
import pandas as pd
import csv


def parse_args():
    parser = argparse.ArgumentParser(
        description='Pandas test script')

    parser.add_argument('--noheaders', action='store_true', default=False,
                        required=False,
                        help='Do not use header rows')

    parser.add_argument('--noprint', action='store_true', default=False,
                        help='Print the dataframe')

    return parser.parse_args()

class BOLLStrat(bt.Strategy):

    '''
    This is a simple mean reversion bollinger band strategy.

    Entry Critria:
        - Long:
            - Price closes below the lower band
            - Stop Order entry when price crosses back above the lower band
        - Short:
            - Price closes above the upper band
            - Stop order entry when price crosses back below the upper band
    Exit Critria
        - Long/Short: Price touching the median line
    '''

    params = (
        ("period", 100),
        ("devfactor", 1.5),
        ("size", 20),
        ("debug", False),
        ("rsi_period",30),
        ("lookback",7)
        )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.boll = bt.indicators.BollingerBands(period=self.p.period, devfactor=self.p.devfactor)
        self.sx = bt.indicators.CrossDown(self.data.close, self.boll.lines.top)
        self.lx = bt.indicators.CrossUp(self.data.close, self.boll.lines.bot)
        self.order_price = 0
        self.in_position = 0
        self.rsi = bt.indicators.RSI(period=self.params.rsi_period, lookback=self.params.lookback)

    def next(self):

        orders = self.broker.get_orders_open()

        # Cancel open orders so we can track the median line
        # if orders:
        #     for order in orders:
        #         self.broker.cancel(order)

        if not self.in_position:

            if self.sx > 0 and self.in_position >= 1 and self.rsi > 80:

                self.sell(exectype=bt.Order.Market, price=self.boll.lines.top[0])
                self.in_position -= 1

            if self.lx > 0 and self.rsi < 20:
                self.buy(exectype=bt.Order.Market, price=self.boll.lines.bot[0])
                self.in_position += 1
                self.order_price = self.dataclose[0]


        else:


            if self.in_position >= 1 and self.sx > 0 and self.rsi > 80:
                self.sell(exectype=bt.Order.Limit, price=self.boll.lines.mid[0])
                self.in_position -= 1

            elif self.lx > 0 and self.rsi < 20:
                self.buy(exectype=bt.Order.Limit, price=self.boll.lines.mid[0])
                self.order_price = self.dataclose[0]
                self.in_position += 1

        if self.p.debug:
            print('---------------------------- NEXT ----------------------------------')
            print("1: Data Name:                            {}".format(data._name))
            print("2: Bar Num:                              {}".format(len(data)))
            print("3: Current date:                         {}".format(data.datetime.datetime()))
            print('4: Open:                                 {}'.format(data.open[0]))
            print('5: High:                                 {}'.format(data.high[0]))
            print('6: Low:                                  {}'.format(data.low[0]))
            print('7: Close:                                {}'.format(data.close[0]))
            print('8: Volume:                               {}'.format(data.volume[0]))
            print('9: Position Size:                       {}'.format(self.position.size))
            print('--------------------------------------------------------------------')

    def notify_trade(self,trade):
        if trade.isclosed:
            dt = self.data.datetime.date()

            print('---------------------------- TRADE ---------------------------------')
            print("1: Data Name:                            {}".format(trade.data._name))
            print("2: Bar Num:                              {}".format(len(trade.data)))
            print("3: Current date:                         {}".format(dt))
            print('4: Status:                               Trade Complete')
            print('5: Ref:                                  {}'.format(trade.ref))
            print('6: PnL:                                  {}'.format(round(trade.pnl,2)))
            print('--------------------------------------------------------------------')


#Variable for our starting cash
startcash = 10000

# Create an instance of cerebro
cerebro = bt.Cerebro()

# Add our strategy
cerebro.addstrategy(BOLLStrat)

# Get a pandas dataframe

datapath = './history/ADA-USD.csv'
# Simulate the header row if noheaders requested
args = parse_args()
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

# Add the data to Cerebro
cerebro.adddata(data)

# Add a sizer
cerebro.addsizer(bt.sizers.PercentSizer, percents=.3)

# Run over everything
cerebro.run()

#Get final portfolio Value
portvalue = cerebro.broker.getvalue()
pnl = portvalue - startcash

#Print out the final result
print('Final Portfolio Value: ${}'.format(round(portvalue,2)))
print('P/L: ${}'.format(round(pnl,2)))

# Finally plot the end results
cerebro.plot(style='candlestick')

