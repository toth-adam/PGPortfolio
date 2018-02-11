from ccxt import hitbtc2


class HitbtcCustom(hitbtc2):

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1d', since=None, limit=None):
        timestamp = self.parse8601(ohlcv['timestamp'])
        return [
            int(timestamp / 1000),
            float(ohlcv['open']),
            float(ohlcv['max']),
            float(ohlcv['min']),
            float(ohlcv['close']),
            float(ohlcv['volumeQuote']),
            float(ohlcv['volume'])
        ]
