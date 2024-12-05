import asyncio

from loguru import logger
from playwright.async_api import BrowserContext, expect

from data.models import Wallet
import settings


async def restore_wallet(context: BrowserContext, wallet: Wallet) -> bool:
    for num in range(1, settings.ATTEMPTS_NUMBER_RESTORE + 1):
        try:
            logger.info(f'{wallet.address} | Starting recover wallet')
            page = context.pages[0]
            await page.goto(f'chrome-extension://{settings.EXTENTION_IDENTIFIER}/onboarding/onboarding.html')
            titles = [await p.title() for p in context.pages]
            while "Martian wallet" not in titles:
                titles = [await p.title() for p in context.pages]
            await page.wait_for_load_state()

            # Import Wallet
            await page.locator(
                '//*[@id="root"]/div/div/main/div/div/div[3]'
            ).click()

            # Import private key
            await page.locator(
                '//*[@id="root"]/div/div/main/div/div/div[3]/div/div[2]'
            ).click()

            # Enter private key
            await page.get_by_placeholder(
                'Private Key'
            ).fill(
                f'{wallet.private_key}'
            )

            # # Import
            await page.locator(
                '//*[@id="root"]/div/div/main/div/div/div[5]'
            ).click()

            # fill password
            await page.locator(
                '//*[@id="root"]/div/div/main/div/div/div[3]/div/input'
            ).type(
                settings.EXTENTION_PASSWORD
            )
            # fill password 2
            await page.locator(
                '//*[@id="root"]/div/div/main/div/div/div[4]/div/input'
            ).type(
                settings.EXTENTION_PASSWORD
            )

            # agree
            await page.locator('//*[@id="root"]/div/div/main/div/div/div[5]/span/input').click()

            # continue
            await page.locator(
                '//*[@id="root"]/div/div/main/div/div/div[7]'
            ).click()

            # continue
            await page.locator(
                '//*[@id="root"]/div/div/main/div/div/div[5]'
            ).click()
            # continue
            await page.locator(
                '//*[@id="root"]/div/div/main/div/div/div[4]/div'
            ).click()

            logger.success(f'{wallet.address} | Wallet Ready To Work')
            await page.close()
            page = context.pages[0]
            await page.close()
            return True

        except Exception as err:
            logger.error(f'{wallet.address} | Not Recovered ({err})')
            logger.info(f'Error when getting an account, trying again, attempt No.{num}')

    return False
