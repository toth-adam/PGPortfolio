from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json
import traceback
from dateutil import parser
from hitbtc.plotter import plot_data


class CandlesAndTrades(object):

    def __init__(self):
        self.window_size = 60
        assert self.window_size % 2 == 0, 'Should be even'
        self.endpoints = ['candles', 'trades']
        self.pairs = ["DASHBTC", "XMRBTC", "XRPBTC", "LTCBTC", "BCNBTC", "ZECBTC", "XEMBTC", "XDNBTC",
                      "ETCBTC", "WAXBTC", "DOGEBTC", "ORMEBTC", "LSKBTC", "EOSBTC", "ARDRBTC"]
        self.pairs_test_for_plot = self.pairs[:4]
        self.candles_memory = {}
        self.trades_memory = {}
        self.request_counter = 0
        self.failed_request_counter = 0


        # Fetching candles
        for pair in self.pairs_test_for_plot:
            ret = self.fetch_candles(pair)
            self.candles_memory[pair] = ret

            self.trades_memory[pair] = {
                "buy": [],
                "sell": []
            }

        # Fetching trades around given candle timestamp
        for pair, candles in self.candles_memory.items():
            for candle in candles:
                candle_date_obj = parser.parse(candle['timestamp'])
                candle_timestamp = candle_date_obj.timestamp()
                trades_list_before_timestamp = self.fetch_trades(pair=pair, timestamp=candle_timestamp)
                trades_list_after_timestamp = self.fetch_trades(pair=pair, timestamp=(candle_timestamp + self.window_size / 2))
                self._create_relative_trade_points(trades=trades_list_before_timestamp, pair=pair, candle=candle, candle_timestamp=candle_timestamp)
                self._create_relative_trade_points(trades=trades_list_after_timestamp, pair=pair, candle=candle, candle_timestamp=candle_timestamp)

        plot_data(self.pairs_test_for_plot, self.trades_memory, self.window_size)

        # self.save_candles()
        print('--------------------------------------------------------')
        print('Number of Requests:  ', self.request_counter)
        print('Number of failed Requests:  ', self.failed_request_counter)
        print('--------------------------------------------------------')

    '''
    ###########################
    ###    Transform data   ###
    ###########################
    '''
    def _create_relative_trade_points(self, trades, candle_timestamp, candle, pair):
        for trade in trades:
            trade_date_obj = parser.parse(trade['timestamp'])
            trade_timestamp = trade_date_obj.timestamp()
            offset = trade_timestamp - candle_timestamp
            relative_price = float(trade['price']) / float(candle['close'])
            trade['offset'] = offset

            if trade['side'] == 'buy':
                self.trades_memory[pair]['buy'].append({'offset': offset, 'rp': relative_price})
            else:
                self.trades_memory[pair]['sell'].append({'offset': offset, 'rp': relative_price})

    '''
    ###########################
    ### Communication stuff ###
    ###########################
    '''
    def fetch_trades(self, pair=None, limit=5, sort='DESC', command='trades', timestamp=None):
        assert timestamp is not None, 'Timestamp should be given as param'
        assert pair is not None, 'Pair should be given as param'
        return self._fetch(pair, {
            'limit': limit,
            'command': command,
            'sort': sort,
            'by': 'timestamp',
            'till': timestamp
        })

    def fetch_candles(self, pair, limit=10, period='M30', command='candles'):
        return self._fetch(pair, {
            "limit": limit,
            "period": period,
            "command": command
        })

    def _fetch(self, pair, args={}):
        assert 'command' in args, 'There is no command in args'
        assert args['command'], 'Command in error is falsy'

        url = 'https://api.hitbtc.com/api/2/public/' + str(args['command'] + '/' + str(pair) + '?')
        request_success = False

        while not request_success:
            try:
                ret = urlopen(Request(url + urlencode(args)))
                request_success = True
            except Exception as Exc:
                self.failed_request_counter+= 1
                print(Exc)
                print('Requested URL:  ', url + urlencode(args))
                print('generic exception: ' + traceback.format_exc())

        self.request_counter += 1

        if self.request_counter % 10 == 0:
            print('Number of Requests: ', self.request_counter)

        return json.loads(ret.read().decode(encoding='UTF-8'))

CandlesAndTrades()