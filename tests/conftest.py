import asyncio

import pytest
from telethon import TelegramClient

# Your API ID, hash and session string here
api_id = 6708374
api_hash = '123'
bot_token = '123'
session_str = 'test_bot'


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
@pytest.mark.asyncio
async def bot_client(event_loop):
    bot = TelegramClient(
        session_str,
        api_id,
        api_hash,
        sequential_updates=True,
        loop=event_loop,
    )
    # bot.start(bot_token=bot_token)
    # Connect to the server
    await bot.connect()
    # Issue a high level command to start receiving message
    # await bot.get_me()
    # # Fill the entity cache
    # await bot.get_dialogs()

    yield bot

    await bot.disconnect()
    await bot.disconnected
