import asyncio
import aiohttp
from fake_useragent import FakeUserAgent


async def parse_price():
    headers = {
        'user-agent': FakeUserAgent().random
    }

    try:
        binance = f"https://api.binance.com/api/v3/depth?limit=1&symbol=SUIUSDC"
        async with aiohttp.ClientSession() as session:
            async with session.get(binance, headers=headers) as r:
                data = await r.json()

                if not isinstance(data, dict):
                    raise ValueError("Invalid response format")

                current_price = float(data["asks"][0][0])

                if current_price == 0:
                    raise ValueError("Price not found for specified pair")

                return current_price

    except aiohttp.ClientError as e:
        raise ValueError(f"Request error: {e}")
    except ValueError as e:
        raise e
    except Exception as e:
        raise ValueError(f"Unexpected error: {str(e)}")


async def main():
    print(await parse_price())


if __name__ == '__main__':
    asyncio.run(main())