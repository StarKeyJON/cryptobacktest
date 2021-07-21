from datetime import datetime
import yfinance as yf
from pycoingecko import CoinGeckoAPI
import pandas as pd
import csv
import time
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json


# Set current UNIX time
current_time = int(time.time())



# https://github.com/ranaroussi/yfinance
def yfinance(period="1mo", interval="30m", location='history'):
    #creating a variable crypto and pointing the list of top 50 crypto by market cap to it
    crypto = csv.reader(open('tickers.csv'))

    for project in crypto:
        print(project)

    # #pulling the compiled csv list into a tuple
        symbol, name = project

    # #creating individual files for each project
        history_filename = './{}/{}.csv'.format(location, symbol)

    # #open the file for writing
        f = open(history_filename, 'w')

    # #using yfinance to screen the selected list
        ticker = yf.Ticker(symbol)

    # #creating dataframe consisting of specified period
        # fetch data by interval (including intraday if period < 60 days)
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        # (optional, default is '1d')
            # use "period" instead of start/end
            # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            # (optional, default is '1mo')
        df = ticker.history(period, interval)

    # #writing to the csv file and creating the history
        f.write(df.to_csv())
        f.close()




# https://github.com/man-c/pycoingecko
# CoinGecko-    /simple/price endpoint with the required parameters
#               OR (lists can be used for multiple-valued arguments)
def coinGecko(ids='bitcoin', vs_currencies='usd', days=1):
    cg = CoinGeckoAPI()

# /simple/token_price/{id} (Get current price of tokens (using contract addresses) 
#     for a given platform in any other currency that you need) 
    
# Candle's body:
#     1 - 2 days: 30 minutes
#     3 - 30 days: 4 hours
#     31 and before: 4 days

    history_filename = './CG/bitcoin.csv'.format()
    OHLC = cg.get_coin_ohlc_by_id(ids, vs_currencies, days)

    # prices = cg.get_price(ids, vs_currencies)

    df = pd.DataFrame(OHLC)
    df.columns = ['Datetime', 'Open', 'High', 'Low', 'Close']
    i = 0
    for each in df['Datetime']:
        df.loc[i, 'Datetime'] = datetime.fromtimestamp(each/1000).strftime('%Y-%m-%d %H:%M:%S')  
        i = i+1        
    df.to_csv(history_filename)
    print(df.head())

    # print(current_time)



def coin_gecko():
    cg = CoinGeckoAPI()
    coins = cg.get_exchanges_tickers_by_id(id='uniswap_v2')
    # print(coins)
    df = pd.DataFrame(coins['tickers'])

#base,target,market,last,volume,converted_last,converted_volume,trust_score,bid_ask_spread_percentage,timestamp,last_traded_at,last_fetch_at,is_anomaly,is_stale,trade_url,token_info_url,coin_id,target_coin_id


    print(df)

    # i=1
    # for each in df:
    #     current_rank = df['market_cap_rank'][i]
    #     if current_rank > 250:
    #         df.drop()


    #df.columns = ['base', 'volume' 'coin_id', 'target_coin_id']
    df1 = df.drop(df.columns[[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]], axis=1)  
    df1.to_csv('coin_tickers.csv')
    # print(df.head())


# API key: 3c908924-ad5d-4c94-aab0-9581f8c1f33c
def coin_market_cap():
      #This example uses Python 2.7 and the python-request library.


  url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
  parameters = {
    'start':'1',
    'limit':'5000',
    'convert':'USD'
  }
  headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': '3c908924-ad5d-4c94-aab0-9581f8c1f33c',
  }

  session = Session()
  session.headers.update(headers)

  try:
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    print(data)
    df = pd.json_normalize(data['data'])
    df.to_csv('coin_MC_tickers.csv')
  except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)
  



if __name__ == "__main__":
    yfinance()

    # print("File one __name__ is set to: {}" .format(__name__))