import threading
import time
import datetime
import json
from urllib.request import Request, urlopen


class AssetThread(threading.Thread):
    def __init__(self, b_url, cur_asset, delay):
        threading.Thread.__init__(self)
        self.asset = cur_asset
        self.delay = delay
        self.url_of_asset = b_url + asset
        self.ticker_data_container = []

    def run(self):
        print("Starting " + self.asset)
        self.get_asset_ticker(self.url_of_asset, self.delay, 3)
        print(self.asset + ":", self.ticker_data_container)
        print("Exiting " + self.asset)

    def get_asset_ticker(self, asset_url, delay, counter):
        while counter:
            start_t = time.time()
            ret = urlopen(Request(asset_url))
            data = json.loads(ret.read().decode(encoding='UTF-8'))
            self.ticker_data_container.append(data)
            counter -= 1
            end_t = time.time()
            run_time = end_t - start_t
            time.sleep(delay - run_time)

base_url = "https://api.hitbtc.com/api/2/public/ticker/"
pair_list = ["ETHBTC" , "BCHBTC"] # , "DASHBTC", "XMRBTC", "XRPBTC", "LTCBTC", "BCNBTC", "ZECBTC", "XEMBTC", "XDNBTC",
             # "ETCBTC", "WAXBTC", "DOGEBTC", "ORMEBTC", "LSKBTC", "EOSBTC", "ARDRBTC"]

# Create new threads
threads_list = []
for asset in pair_list:
    threads_list.append(AssetThread(base_url, asset, 1))

# Start new threads
for i_thread in threads_list:
    i_thread.start()

# Join threads
for i_thread in threads_list:
    i_thread.join()

print("Exiting Main Thread")
