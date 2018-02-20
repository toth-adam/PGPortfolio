from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from pgportfolio.marketdata.poloniex import Poloniex
from pgportfolio.marketdata.hitbtc import Hitbtc
from pgportfolio.tools.data import get_chart_until_success
import pandas as pd
from datetime import datetime
import logging
from pgportfolio.constants import *

class CoinList(object):
    def __init__(self, end, volume_average_days=1, volume_forward=0):
        self.end = end
        self.volume_average_days = volume_average_days
        self.volume_forward = volume_forward

        self.is_polo = 1

        if self.is_polo:
            coins, pairs, volumes, prices = self.poloniex_coin_list()
        else:
            coins, pairs, volumes, prices = self.hitbtc_coin_list()


        self._df = pd.DataFrame({'coin': coins, 'pair': pairs, 'volume': volumes, 'price':prices})
        self._df = self._df.set_index('coin')

    def poloniex_coin_list(self):
        self._trading_platform = Poloniex()
        # connect the internet to accees volumes
        vol = self._trading_platform.marketVolume()
        ticker = self._trading_platform.marketTicker()
        pairs = []
        coins = []
        volumes = []
        prices = []

        logging.info("select coin online from %s to %s" % (datetime.fromtimestamp(self.end - (DAY * self.volume_average_days) -
                                                                                  self.volume_forward).
                                                           strftime('%Y-%m-%d %H:%M'),
                                                           datetime.fromtimestamp(self.end - self.volume_forward).
                                                           strftime('%Y-%m-%d %H:%M')))

        for k, v in vol.items():
            if k.startswith("BTC_") or k.endswith("_BTC"):
                pairs.append(k)
                for c, val in v.items():
                    if c != 'BTC':
                        if k.endswith('_BTC'):
                            coins.append('reversed_' + c)
                            prices.append(1.0 / float(ticker[k]['last']))
                        else:
                            coins.append(c)
                            prices.append(float(ticker[k]['last']))
                    else:
                        volumes.append(self.__get_total_volume(pair=k, global_end=self.end,
                                                               days=self.volume_average_days,
                                                               forward=self.volume_forward))

        return (coins, pairs, volumes, prices)

    def hitbtc_coin_list(self):
        self._trading_platform = Hitbtc()
        # connect the internet to accees volumes
        vol = self._trading_platform.marketVolume()
        ticker = self._trading_platform.marketTicker()
        pairs = []
        coins = []
        volumes = []
        prices = []

        logging.info("select coin online from %s to %s" % (datetime.fromtimestamp(self.end - (DAY * self.volume_average_days) -
                                                                                  self.volume_forward).
                                                           strftime('%Y-%m-%d %H:%M'),
                                                           datetime.fromtimestamp(self.end - self.volume_forward).
                                                           strftime('%Y-%m-%d %H:%M')))

        for k, v in vol.items():
            if k.startswith("BTC/") or k.endswith("/BTC"):
                pairs.append(k)
                for c, val in v.items():
                    if c != 'BTC':
                        # BREKO: ez itt nalunk meg van forditva, nalunk minden valami/BTC kiveve BTC/USDT
                        if k.endswith('/BTC'):
                            coins.append(c)
                            prices.append(float(ticker[k]['last']))
                        else:
                            coins.append('reversed_' + c)
                            prices.append(1.0 / float(ticker[k]['last']))
                    else:
                        volumes.append(self.__get_total_volume(pair=k, global_end=self.end,
                                                               days=self.volume_average_days,
                                                               forward=self.volume_forward))

        return (coins, pairs, volumes, prices)

    @property
    def allActiveCoins(self):
        return self._df

    @property
    def allCoins(self):
        return self._trading_platform.marketStatus().keys()

    @property
    def polo(self):
        return self._trading_platform

    def get_chart_until_success(self, pair, start, period, end):
        return get_chart_until_success(self._trading_platform, pair, start, period, end)

    # get several days volume
    def __get_total_volume(self, pair, global_end, days, forward):
        start = global_end-(DAY*days)-forward
        end = global_end-forward
        # 30 napnyi candle adat, napi bontasban, ez a 30 nap benne van a net_configban
        if self.is_polo:
            chart = self.get_chart_until_success(pair=pair, period=DAY, start=start, end=end)
        else:
            # end=limit, amennyi a limit annyiszor 1 napos bontasu adatot szed le a start timetol kezdve
            chart = self.get_chart_until_success(pair=pair, period=DAY, start=start, end=days-1)
        result = 0
        for one_day in chart:
            if pair.startswith("BTC_"): # or pair.startswith("BTC/"):
                result += one_day['volume']
            else:
                result += one_day["quoteVolume"]
        return result


    def topNVolume(self, n=5, order=True, minVolume=0):
        if minVolume == 0:
            r = self._df.loc[self._df['price'] > 2e-6]
            r = r.sort_values(by='volume', ascending=False)[:n]
            print(r)
            if order:
                return r
            else:
                return r.sort_index()
        else:
            return self._df[self._df.volume >= minVolume]
