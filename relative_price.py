from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError,ContentTooShortError
from urllib.parse import urlencode
import json
import os, traceback
import sqlite3
from datetime import datetime
from dateutil import parser
import numpy as np
import asyncio
from aiohttp import ClientSession
import matplotlib.pyplot as plt
from time import sleep


class RelativePrice(object):

    def __init__(self):
        self.window_size = 60
        assert self.window_size % 2 == 0, 'Should be even'
        self.is_data_base = False
        self.endpoints = ['candles', 'trades']
        self.pairs = ['XRPBTC', 'XMRBTC']
        self.candles_memory = {}
        self.trades_memory = {}
        self.request_counter = 0
        self.failed_request_counter = 0

        self.init_data_base()

        self.persist_tickers([
            {
                "ask": "0.00009215",
                "bid": "0.00009209",
                "last": "0.00009206",
                "open": "0.00009191",
                "low": "0.00009000",
                "high": "0.00009368",
                "volume": "34269633",
                "volumeQuote": "3141.86360431",
                "timestamp": "2018-02-21T20:36:59.595Z",
                "symbol": "XRPBTC"
            },
            {
                "ask": "0.00009206",
                "bid": "0.00009205",
                "last": "0.00009207",
                "open": "0.00009102",
                "low": "0.00009000",
                "high": "0.00009368",
                "volume": "34159592",
                "volumeQuote": "3131.92561035",
                "timestamp": "2018-02-21T21:46:57.608Z",
                "symbol": "XRPBTC"
            }
        ])

        loop = asyncio.get_event_loop()
        future = asyncio.Future()
        loop.run_until_complete(self.fetch_ticker(future))
        a = future.result()
        loop.close()

        # Fetching candles
        for pair in self.pairs:
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


        self.plot_data()

        # self.save_candles()
        print('--------------------------------------------------------')
        print('Number of Requests:  ', self.request_counter)
        print('Number of failed Requests:  ', self.failed_request_counter)
        print('--------------------------------------------------------')

    '''
    ###########################
    ###      Plot stuff     ###
    ###########################
    '''
    def plot_data(self):
        figure = plt.figure()
        half_window = int(self.window_size / 2)
        order_types = ['buy', 'sell']
        plot_matrix = int(str(len(self.pairs)) + "21")

        for i, pair in enumerate(self.pairs):
            for y, side in enumerate(order_types):
                fig = figure.add_subplot((plot_matrix + i * 2 + y))
                fig.set_title(pair + ' ' + side)

                plot_points = self._one_pair_side_plot(pair, side)
                fig.plot([ind for ind in range(-half_window, half_window)]
                          , [el for el in plot_points], 'ro')

        plt.ylabel('Relative Price')
        plt.xlabel('Time Offset')
        plt.axis([-half_window - 10, half_window + 10, 0.97, 1.03])
        plt.show()

    def _one_pair_side_plot(self, pair, side):
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

    '''
    ###########################
    ###    Database stuff   ###
    ###########################
    Ticker {
      "symbol": "string",
      "ask": "string",
      "bid": "string",
      "last": "string",
      "low": "string",
      "high": "string",
      "open": "string",
      "volume": "string",
      "volumeQuoute": "string",
      "timestamp": "2018-02-21T20:26:40.567Z"
    }
    '''
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
            cursor.execute('CREATE TABLE IF NOT EXISTS Ticker (id INTEGER,'
                           ' r_timestamp INTEGER, symbol TEXT, ask FLOAT, bid FLOAT, last FLOAT,'
                           ' low FLOAT, high FLOAT, open FLOAT, volume FLOAT, volumeQuoute FLOAT,'
                           ' timestamp FLOAT, PRIMARY KEY(id));')
            self.is_data_base = True
        finally:
            connection.commit()
            connection.close()

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

    def _prepare_ticker(self, symbol, ask, bid, last, low, high, open, volume, volumeQuote, timestamp):
        date_obj = parser.parse(timestamp)
        return {
            "symbol": symbol,
            "ask": float(ask),
            "bid": float(bid),
            "last": float(last),
            "low": float(low),
            "high": float(high),
            "open": float(open),
            "volume": float(volume),
            "volumeQuoute": float(volumeQuote),
            "timestamp": date_obj.timestamp()
        }

    def persist_tickers(self, tickers):
        connection = sqlite3.connect(os.path.join(os.getcwd(), "database/hitbtc_data.db"))
        cursor = connection.cursor()
        # cursor.execute('BEGIN TRANSACTION')
        for ticker in tickers:
            db_ticker = self._prepare_ticker(**ticker)
            cursor.execute('INSERT INTO Ticker VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?)',
                           (0,
                           db_ticker["symbol"],
                           db_ticker["ask"],
                           db_ticker["bid"],
                           db_ticker["last"],
                           db_ticker["low"],
                           db_ticker["high"],
                           db_ticker["open"],
                           db_ticker["volume"],
                           db_ticker["volumeQuoute"],
                           db_ticker["timestamp"],)
                           )
        # cursor.execute('COMMIT')
        try:
            pass
        except Exception as e:
            print(e)
        finally:
            pass
        connection.commit()
        connection.close()


    '''
    ###########################
    ### Communication stuff ###
    ###########################
    '''
    async def fetch_ticker(self, future):
        params = {

        }
        tasks = []
        async with ClientSession() as session:
            for pair in self.pairs:
                url = 'https://api.hitbtc.com/api/2/public/ticker/' + str(pair)
                task = asyncio.ensure_future(self.async_fetch(session, url))
                tasks.append(task)

            responses = await asyncio.gather(*tasks)

            future.set_result(responses)

    def fetch_trades(self, pair=None, limit=20, sort='DESC', command='trades', timestamp=None):
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

    async def async_fetch(self, session, url, params={}):
        async with session.get(url, params=params) as response:
            result = await response.json()
            return result

    def _fetch(self, pair, args={}):
        assert 'command' in args, 'There is no command in args'
        assert args['command'], 'Command in error is falsy'

        if self.is_data_base:
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

        else:
            return False

    def prepare_data_for_db(self):
        pass

rp = RelativePrice()