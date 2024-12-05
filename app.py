import asyncio
from loguru import logger
import sys

import settings
# from format_proxy import format_proxy
from wallets import WALLETS
from parser import parse_price
from withdrawal import withdrawal
from telegram_bot import parsing


logger.remove()  # Видаляємо стандартний обробник
# Додаємо логування в консоль
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
    colorize=True
)
# Додаємо логування у файл
logger.add(
    "logs/log.log",  # Файл буде створюватися для кожного дня
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    level="WARNING",
    rotation="00:00",  # Новий файл кожного дня
    compression="zip",  # Стиснення старих файлів
    retention="30 days",  # Зберігання логів протягом 30 днів
    encoding="utf-8"
)


async def main():
    logger.success("\033[7;38;5;122mБот запущений\033[0m")
    wallet = WALLETS[0]
    while True:
        try:
            current_price = float(await parse_price())
            if current_price < settings.BOTTOM_PRICE:
                logger.warning(
                    f"\033[91mAllert! Current price SUI is down:{current_price:.10f} "
                    f"Start withdrawing\033[0m"
                )
                await withdrawal(wallet=wallet)
                logger.warning(f"SUI: liquidity was added again")
                break
            elif current_price > settings.TOP_PRICE:
                logger.warning(
                    f"\033[91mAllert! Current price SUI is up:{current_price:.10f} "
                    f"Start withdrawing\033[0m"
                )
                await withdrawal(wallet=wallet)
                logger.warning(f"SUI: liquidity was added again")
                break
            elif settings.BOTTOM_PRICE <= current_price <= (settings.TOP_PRICE - settings.BOTTOM_PRICE) * 0.05 + settings.BOTTOM_PRICE:
                logger.warning(
                    f"\033[33mAttention! Current price SUI: {current_price:.10f}"
                    f" 5% left to the bottom of the range\033[0m"
                )
            elif settings.BOTTOM_PRICE < current_price < settings.TOP_PRICE:
                logger.success(
                    f"Current price SUI: {current_price:.10f} | Continue checking"
                )
            await asyncio.sleep(settings.sleep_for_parsing)
        except KeyboardInterrupt:
            print()
            break
        except ValueError as err:
            logger.error(f'Value error: {err}')
            await asyncio.sleep(20)
            continue
        except BaseException as e:
            logger.error(f'Something went wrong: {e}')
            await asyncio.sleep(60)
            continue

if __name__ == '__main__':
    asyncio.run(main())
