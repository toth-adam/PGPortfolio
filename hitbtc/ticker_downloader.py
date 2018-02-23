from aiohttp import ClientSession
import asyncio
import time
from datetime import datetime
from database_handler import DatabaseHandler
import threading
import traceback

# DB worker instance
def db_worker(tickers):
    """thread worker function"""
    dbh = DatabaseHandler('../database/hitbtc_data.db')
    dbh.persist_tickers(tickers=tickers)
    return

class TickerDownloader(object):
    def __init__(self, timespan=None, pairs=["DASHBTC", "XMRBTC", "XRPBTC", "LTCBTC"]):

        self.pairs = pairs

        db_save_sec = 60
        counter = 0
        tickers = []
        if timespan is None:
            should_count = False
            timespan = 31536000
        else:
            should_count = True


        start = time.time()
        last_save = start
        loop = asyncio.get_event_loop()
        print('Start downloading')
        while counter < timespan:
            future = asyncio.Future()
            loop.run_until_complete(self.fetch_ticker(future))
            a = future.result()
            tickers.extend(a)

            if should_count:
                counter += 1

            if len(tickers) > 0 and time.time() - last_save > db_save_sec:
                last_save = time.time()
                threading.Thread(target=db_worker, args=(tickers,)).start()
                tickers = []

            while datetime.now().microsecond < 970000:
                pass

        loop.close()

        end = time.time()

        print(str(timespan), " call with 1 sec delay took: ", end - start)


    async def _async_fetch(self, session, url, params={}):
        request_success = False
        while not request_success:
            try:
                async with session.get(url, params=params) as response:
                    result = await response.json()
                    return result
                    request_success = True
            except Exception as Exc:
                print(Exc)
                print('Requested URL:  ', url)
                print('generic exception: ' + traceback.format_exc())


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

if __name__ == "__main__":
    TickerDownloader(pairs=symbols)
