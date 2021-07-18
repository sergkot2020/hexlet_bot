import pytest
import os
from telethon import TelegramClient
from telethon.sessions import StringSession

# Your API ID, hash and session string here
api_id = 6708374
api_hash = '123'
bot_token = '123'
session_str = 'test_bot'


@pytest.fixture(scope="session")
async def bot_client():
    bot = TelegramClient(
        StringSession(session_str), api_id, api_hash,
        sequential_updates=True
    )
    # bot.start(bot_token=bot_token)
    # Connect to the server
    await bot.connect()
    # Issue a high level command to start receiving message
    await bot.get_me()
    # Fill the entity cache
    await bot.get_dialogs()

    yield bot

    await bot.disconnect()
    await bot.disconnected

