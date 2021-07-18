import asyncio

import pytest
import os
from telethon import TelegramClient

from bot.reader import read_config

TEST_FOLDER = 'tests'
CONFIG_FILENAME = 'test_config.yml'
CONFIG = read_config(os.path.join(TEST_FOLDER, CONFIG_FILENAME))


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
@pytest.mark.asyncio
async def bot_client(event_loop):
    bot = TelegramClient(
        **CONFIG['bot'],
        sequential_updates=True,
        loop=event_loop,
    )
    # bot.start(bot_token=bot_token)
    # Connect to the server
    await bot.start()
    # Issue a high level command to start receiving message
    # await bot.get_me()
    # # Fill the entity cache
    # await bot.get_dialogs()

    yield bot

    await bot.disconnect()
    await bot.disconnected
