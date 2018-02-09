# import json
import time
# import sys
from datetime import datetime
import ccxt

# if sys.version_info[0] == 3:
#     from urllib.request import Request, urlopen
#     from urllib.parse import urlencode
# else:
#     from urllib2 import Request, urlopen
#     from urllib import urlencode

minute = 60
hour = minute*60
day = hour*24
week = day*7
month = day*30
year = day*365

# Possible Commands
# PUBLIC_COMMANDS = ['returnTicker',
#                    'return24hVolume',
#                    'returnOrderBook',
#                    'returnTradeHistory',
#                    'returnChartData',
#                    'returnCurrencies',
#                    'returnLoanOrders']

PUBLIC_COMMANDS = ['fetch_tickers',
                   'fetch_volumes',
                   'returnOrderBook',
                   'returnTradeHistory',
                   'returnChartData',
                   'returnCurrencies',
                   'returnLoanOrders']

class Hitbtc:
    def __init__(self, APIKey='', Secret=''):
        self.APIKey = APIKey.encode()
        self.Secret = Secret.encode()
        self.api = ccxt.hitbtc2({'verbose': True})

        self.tickers = None

        # Conversions
        self.timestamp_str = lambda timestamp=time.time(), format="%Y-%m-%d %H:%M:%S": datetime.fromtimestamp(timestamp).strftime(format)
        self.str_timestamp = lambda datestr=self.timestamp_str(), format="%Y-%m-%d %H:%M:%S": int(time.mktime(time.strptime(datestr, format)))
        self.float_roundPercent = lambda floatN, decimalP=2: str(round(float(floatN) * 100, decimalP))+"%"

        # PUBLIC COMMANDS
        self.marketTicker = lambda x=0: self.fetch_tickers()
        self.marketVolume = lambda x=0: self.fetch_volumes()
        self.marketStatus = lambda x=0: self.api('returnCurrencies')
        self.marketLoans = lambda coin: self.api('returnLoanOrders',{'currency':coin})
        self.marketOrders = lambda pair='all', depth=10:\
            self.api('returnOrderBook', {'currencyPair':pair, 'depth':depth})
        # self.marketChart = lambda pair, period=day, start=time.time()-(week*1), end=time.time(): self.api('returnChartData', {'currencyPair':pair, 'period':period, 'start':start, 'end':end})
        self.marketChart = lambda pair, period=day, start=time.time()-(week*1), end=time.time(): self.api.fetch_ohlcv(pair, )
        self.marketTradeHist = lambda pair: self.api('returnTradeHistory',{'currencyPair':pair}) # NEEDS TO BE FIXED ON Poloniex

    def fetch_tickers(self):
        self.tickers = self.api.fetch_tickers()

        return self.tickers

    def fetch_volumes(self):
        tickers = self.api.fetch_tickers()
        volumes = {}
        for k, v in tickers.items():
            pairs = k.split("/")
            if len(pairs) > 1:
                volume_tuple_list = filter(lambda x: x[0] == "baseVolume" or x[0] == "quoteVolume", v.items())
                volumes[k] = dict((pairs[0] if b == "baseVolume" else pairs[1], q) for b, q in volume_tuple_list)

        return volumes
