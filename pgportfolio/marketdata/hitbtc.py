import json
import time
from datetime import datetime
from pgportfolio.ccxt.hitbtc import HitbtcCustom

from urllib.request import Request, urlopen
from urllib.parse import urlencode

minute = 60
hour = minute*60
day = hour*24
week = day*7
month = day*30
year = day*365

HITBTC_RATE_LIMIT = 1000

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
        self.api = HitbtcCustom({'verbose': True})

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
        self.marketChart = lambda pair, period="1d", start=time.time()-(week*1), end=1: self.fetch_chart_data(pair, period, start, end)
        self.marketTradeHist = lambda pair: self.api('returnTradeHistory',{'currencyPair':pair}) # NEEDS TO BE FIXED ON Poloniex

    #####################
    # Cutom Api Function #
    #####################
    def api(self, command, args={}):
        """
        returns 'False' if invalid command or if no APIKey or Secret is specified (if command is "private")
        returns {"error":"<error message>"} if API error
        """
        if command in PUBLIC_COMMANDS:
            url = 'https://api.hitbtc.com/api/2/public/'
            args['command'] = command
            ret = urlopen(Request(url + urlencode(args)))
            return json.loads(ret.read().decode(encoding='UTF-8'))
        else:
            return False

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

        _volumes = {}

        for k, v in volumes.items():
            for x, y in v.items():
                if y:
                    _volumes[k] = v

        return _volumes

    def fetch_chart_data(self, pair, period, start, end):

        # ez itt lehet, hogy kurvaszar, quoteVolume vagy volume?
        feature_names_list = ["date", "open", "high", "low", "close", "quoteVolume", "volume"]
        periods_dict = {
            86400: "1d",
            300: "5m",
            1800: "30m"
        }

        string_period = periods_dict[period]

        # hitbtc has rate limit 1000
        # start/end values grouped by 1000 requests
        # 1000 * 300(5min) in seconds the biggest timespan
        if end > 1000:
            parsed_ohlcvs = []
            desired_limit = (end - start)/period
            number_of_requests = int(desired_limit // HITBTC_RATE_LIMIT)
            REMAINDER = int(desired_limit % HITBTC_RATE_LIMIT)
            while number_of_requests:
                number_of_requests -= 1
                if len(parsed_ohlcvs) == 0:
                    current_raw_ohlcv = self.api.fetch_ohlcv(pair, string_period, start, HITBTC_RATE_LIMIT)
                else:
                    start_timestamp = int(parsed_ohlcvs[-1]["date"]) + period
                    current_raw_ohlcv = self.api.fetch_ohlcv(pair, string_period, start_timestamp, HITBTC_RATE_LIMIT)

                current_parsed_ohlcvs = list(map(lambda current_period:
                                                {feature_names_list[i]: feature for i, feature in enumerate(current_period)},
                                                current_raw_ohlcv))
                parsed_ohlcvs = parsed_ohlcvs + current_parsed_ohlcvs
                if number_of_requests == 0:
                    if REMAINDER > 0:
                        start_timestamp = int(parsed_ohlcvs[-1]["date"]) + period
                        remainder_raw_ohlcv = self.api.fetch_ohlcv(pair, string_period, start_timestamp, REMAINDER)
                        current_parsed_ohlcvs = list(map(
                            lambda current_period: {feature_names_list[i]: feature for i, feature in
                                                    enumerate(current_period)}, remainder_raw_ohlcv))
                        parsed_ohlcvs = parsed_ohlcvs + current_parsed_ohlcvs
                    #     just to check if current_start and end matches
                    #     current_start = current_start + (REMAINDER) * period
                    #     print("Is difference 0?:", end-current_start)

                        lista = {}
                        for d in parsed_ohlcvs:
                            if d["date"] not in lista:
                                lista[d["date"]] = 1

                        print(len(lista))
                        print("done")

                    break
        # this part is called when we need to define the top traded currencies, end is already transformed to limit
        else:
            # the returned timestamp need to be transformed
            raw_ohlcv = self.api.fetch_ohlcv(pair, string_period, start, end)
            parsed_ohlcvs = list(map(lambda day: {feature_names_list[i]: feature for i, feature in enumerate(day)}, raw_ohlcv))

        return parsed_ohlcvs
