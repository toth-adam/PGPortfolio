import aiohttp
import asyncio
import async_timeout

base_url = "https://api.hitbtc.com/api/2/public/ticker/"
pair_list = ["ETHBTC", "BCHBTC", "DASHBTC", "XMRBTC", "XRPBTC", "LTCBTC", "BCNBTC", "ZECBTC",
             "XEMBTC", "XDNBTC", "ETCBTC", "WAXBTC", "DOGEBTC", "ORMEBTC", "LSKBTC", "EOSBTC",
             "ARDRBTC"]
url_list = [base_url + pair for pair in pair_list]

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def main(loop):
    async with aiohttp.ClientSession(loop=loop) as session:
        for url in url_list:
            data = await fetch(session, url)
            print(data)


loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))