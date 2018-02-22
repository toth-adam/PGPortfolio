from aiohttp import ClientSession
import asyncio
import time
from datetime import datetime
from hitbtc.database_handler import DatabaseHandler

class TickerDownloader(object):
    def __init__(self, timespan, pairs=["DASHBTC", "XMRBTC", "XRPBTC", "LTCBTC"]):
        if not isinstance(timespan, int):
            raise Exception('Timespan should be int')

        self.pairs = pairs
        counter = 0
        tickers = []
        start = time.time()
        loop = asyncio.get_event_loop()
        while counter < timespan:
            future = asyncio.Future()
            loop.run_until_complete(self.fetch_ticker(future))
            a = future.result()
            tickers.extend(a)
            counter += 1
            while datetime.now().microsecond < 970000:
                pass

        loop.close()

        end = time.time()

        print(str(timespan), " call with 1 sec delay took: ", end - start)

        dbh = DatabaseHandler()
        dbh.persist_tickers(tickers=tickers)

    async def _async_fetch(self, session, url, params={}):
        async with session.get(url, params=params) as response:
            result = await response.json()
            return result

    async def fetch_ticker(self, future):
        params = {

        }
        tasks = []
        async with ClientSession() as session:
            for pair in self.pairs:
                url = 'https://api.hitbtc.com/api/2/public/ticker/' + str(pair)
                task = asyncio.ensure_future(self._async_fetch(session, url))
                tasks.append(task)

            responses = await asyncio.gather(*tasks)

            future.set_result(responses)


symbols = ["ETHBTC", "DASHBTC", "XMRBTC", "XRPBTC", "LTCBTC", "BCNBTC", "ZECBTC", "XEMBTC", "XDNBTC",
                      "ETCBTC", "WAXBTC", "DOGEBTC", "ORMEBTC", "LSKBTC", "EOSBTC", "ARDRBTC"]

a = TickerDownloader(10, symbols)
