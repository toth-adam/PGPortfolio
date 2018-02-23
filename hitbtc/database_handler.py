import os
import sqlite3
from dateutil import parser
import datetime


class DatabaseHandler(object):
    def __init__(self, path="database/hitbtc_data.db"):
        self.is_data_base = False
        self.path = path
        self._init_data_base()


    '''
    ###########################
    ###    Database stuff   ###
    ###########################
    '''
    def _init_data_base(self):
        print('-----------------------------------------------------------------')
        print(datetime.datetime.now().isoformat(), '  DB connection initialization...')
        connection = sqlite3.connect(os.path.join(os.getcwd(), self.path))
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
        print(datetime.datetime.now().isoformat(), '  Persisting tickers...')
        assert len(tickers) > 0, 'Tickers list length shouldnt be 0'
        connection = sqlite3.connect(os.path.join(os.getcwd(), self.path))
        cursor = connection.cursor()
        try:
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
                                db_ticker["timestamp"],))
        finally:
            connection.commit()
            connection.close()
