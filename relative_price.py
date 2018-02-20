from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json
import os
import sqlite3
from datetime import datetime
from dateutil import parser
import numpy as np
import matplotlib.pyplot as plt
from time import sleep


class RelativePrice(object):

    def __init__(self):
        self.window_size = 100
        assert self.window_size % 2 == 0, 'Should be even'
        self.is_data_base = False
        self.endpoints = ['candles', 'trades']
        self.pairs = ['XRPBTC', 'XMRBTC']
        self.candles_memory = {}
        self.trades_memory = {}
        self.request_counter = 0
        self.failed_request_counter = 0

        self.init_data_base()

        for pair in self.pairs:
            ret = self.fetch_candles(pair)
            self.candles_memory[pair] = ret

            self.trades_memory[pair] = {
                "buy": [],
                "sell": []
            }

        for pair, candles in self.candles_memory.items():
            for candle in candles:
                candle_date_obj = parser.parse(candle['timestamp'])
                candle_timestamp = candle_date_obj.timestamp()
                trades_list_before_timestamp = self.fetch_trades(pair=pair, timestamp=candle_timestamp)
                trades_list_after_timestamp = self.fetch_trades(pair=pair, timestamp=(candle_timestamp + self.window_size / 2))
                self._create_relative_trade_points(trades=trades_list_before_timestamp, pair=pair, candle=candle, candle_timestamp=candle_timestamp)
                self._create_relative_trade_points(trades=trades_list_after_timestamp, pair=pair, candle=candle, candle_timestamp=candle_timestamp)

        plot_points1 = self.one_pair_side_plot('XRPBTC', 'buy')
        plot_points2 = self.one_pair_side_plot('XRPBTC', 'sell')
        plot_points3 = self.one_pair_side_plot('XMRBTC', 'buy')
        plot_points4 = self.one_pair_side_plot('XMRBTC', 'sell')

        half_window = int(self.window_size / 2)
        fig = plt.figure()

        plot_one_buy = fig.add_subplot(221)
        plot_one_buy.set_title('BCHBTC BUY')
        plot_one_sell = fig.add_subplot(222)
        plot_one_sell.set_title('BCHBTC SELL')
        plot_two_buy = fig.add_subplot(223)
        plot_two_buy.set_title('ETHBTC BUY')
        plot_two_sell = fig.add_subplot(224)
        plot_two_sell.set_title('ETHBTC SELL')
        plot_one_buy.plot([ind for ind in range(-half_window, half_window)]
                      , [el for el in plot_points1], 'ro')
        plot_one_sell.plot([ind for ind in range(-half_window, half_window)]
                      , [el for el in plot_points2], 'ro')
        plot_two_buy.plot([ind for ind in range(-half_window, half_window)]
                      , [el for el in plot_points3], 'ro')
        plot_two_sell.plot([ind for ind in range(-half_window, half_window)]
                      , [el for el in plot_points4], 'ro')
        plt.ylabel('Relative Price')
        plt.xlabel('Time Offset')
        plt.axis([-half_window - 10, half_window + 10, 0.97, 1.03])
        plt.show()

        # self.save_candles()
        print('--------------------------------------------------------')
        print('Number of Requests:  ', self.request_counter)
        print('Number of failed Requests:  ', self.failed_request_counter)
        print('--------------------------------------------------------')


    def one_pair_side_plot(self, pair, side):
        plot_points = []
        half_window = int(self.window_size/2)
        for i in range(-half_window, half_window):
            average_list = []
            for el in self.trades_memory[pair][side]:
                if i < el['offset'] < i + 1:
                    average_list.append(el['rp'])

            b = np.array(average_list)
            if len(b) > 0:
                plot_points.append(b.mean())
            else:
                plot_points.append(0.98)

        return plot_points


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

    def init_data_base(self):
        connection = sqlite3.connect(os.path.join(os.getcwd(), "database/hitbtc_data.db"))
        try:
            cursor = connection.cursor()
            cursor.execute('CREATE TABLE IF NOT EXISTS Candles (timestamp INTEGER,'
                           ' open FLOAT, close FLOAT,'
                           ' min FLOAT, max FLOAT,'
                           ' volume FLOAT, volumeQuote FLOAT, PRIMARY KEY(timestamp));')
            cursor.execute('CREATE TABLE IF NOT EXISTS Trades (id INTEGER,'
                           ' price FLOAT, quantity FLOAT,'
                           ' side TEXT, timestamp INTEGER, PRIMARY KEY(id));')
            self.is_data_base = True
        finally:
            connection.commit()
            connection.close()

    def fetch_candles(self, pair, limit=1000, period='M30', command='candles'):
        return self._api(pair, {
                "limit": limit,
                "period": period,
                "command": command
            })

    def fetch_trades(self, pair=None, limit=100, sort='DESC', command='trades', timestamp=None):
        assert timestamp is not None, 'Timestamp should be given as param'
        assert pair is not None, 'Pair should be given as param'
        return self._api(pair, {
            'limit': limit,
            'command': command,
            'sort': sort,
            'by': 'timestamp',
            'till': timestamp
        })

    def persist_candles(self, candles):
        connection = sqlite3.connect(os.path.join(os.getcwd(), "database/hitbtc_data.db"))
        try:
            cursor = connection.cursor()
            cursor.execute('')
        except:
            pass
        finally:
            connection.commit()
            connection.close()

    def draw_graph(self):
        pass

    def _api(self, pair, args={}):
        assert 'command' in args, 'There is no command in args'
        assert args['command'], 'Command in error is falsy'
        if self.is_data_base:
            url = 'https://api.hitbtc.com/api/2/public/' + str(args['command'] + '/' + str(pair) + '?')
            # print(url)
            request_success = False
            while not request_success:
                # sleep(0.01)
                try:
                    ret = urlopen(Request(url + urlencode(args)))
                    request_success = True
                except Exception as Exc:
                    self.failed_request_counter+= 1
                    print(Exc)
                    print('Requested URL:  ', url + urlencode(args))
            self.request_counter += 1
            if self.request_counter % 10 == 0:
                print('Number of Requests: ', self.request_counter)
            return json.loads(ret.read().decode(encoding='UTF-8'))
        else:
            return False

    def prepare_data_for_db(self):
        pass

rp = RelativePrice()