import json
from urllib.request import Request, urlopen
import numpy as np
import time
import aiohttp
import asyncio

base_url = "https://api.hitbtc.com/api/2/public/ticker/"
pair_list = ["ETHBTC", "BCHBTC", "DASHBTC", "XMRBTC", "XRPBTC", "LTCBTC", "BCNBTC", "ZECBTC",
             "XEMBTC", "XDNBTC", "ETCBTC", "WAXBTC", "DOGEBTC", "ORMEBTC", "LSKBTC", "EOSBTC",
             "ARDRBTC"]
url_list = [base_url + pair for pair in pair_list]

async def call_url(url):
    print('Starting {}'.format(url))
    response = await aiohttp.get(url)
    data = await json.loads(response.read().decode(encoding='UTF-8'))
    print('Ending {}'.format(url))
    return data

futures = [call_url(url) for url in url_list]

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(futures))

print(futures)










"""
async def get_data(list_of_pairs):
    actual_data = []
    for pair in list_of_pairs:
        actual_url = base_url + pair
        ret = urlopen(Request(actual_url))
        data = json.loads(ret.read().decode(encoding='UTF-8'))
        actual_data.append(data)
    return actual_data

for iter_num in range(50):
    i = 0
    data_container = []
    start_time = time.time()
    while (time.time() - start_time) < (3600 * 4):
        get_spread_start_time = time.time()
        i += 1
        if (i % 50 == 0) or i == 1:
            print("Iteration: ", i)
        act_data = get_data(pair_list)
        data_container.append(act_data)
        get_spread_whole_time = time.time() - get_spread_start_time
        if get_spread_whole_time > 15:
            get_spread_whole_time == 15
        time.sleep(15 - get_spread_whole_time)
    np.save("D:/RL/portfolio/tickers_data_" + str(iter_num + 1), np.array(data_container))
    print("LEFUTOTT A " + str(iter_num + 1) + " ITERÁCIÓ")
print("-------------------------VÉGE-------------------------")
"""