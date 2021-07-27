import asyncio
import logging
import os

import pytest
from telethon import TelegramClient, events
from telethon.sessions import StringSession

from bot.reader import read_config

TEST_FOLDER = 'tests'
CONFIG_FILENAME = 'test_config.yml'
# CONFIG = read_config(os.path.join(TEST_FOLDER, CONFIG_FILENAME))

logging.basicConfig(level=logging.INFO)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


# @pytest.fixture(scope="session")
# @pytest.mark.asyncio
# async def bot_client(event_loop):
#     logging.info('>> Creating bot.')
#     bot = TelegramClient(
#         None,
#         CONFIG['test_server']['api_id'],
#         CONFIG['test_server']['api_hash'],
#         loop=event_loop,
#     )
#     bot.session.set_dc(2, CONFIG['test_server']['test_sever_ip'], 443)
#     await bot.start(bot_token=CONFIG['test_server']['bot_token'])
#     # Issue a high level command to start receiving message
#     # await bot.get_me()
#     # # Fill the entity cache
#     # await bot.get_dialogs()
#
#     yield bot
#
#     await bot.disconnect()
#     await bot.disconnected
#
#
# @pytest.fixture(scope="session")
# @pytest.mark.asyncio
# async def test_server_client(event_loop):
#     logging.info('>> Creating client.')
#     client = TelegramClient(
#         StringSession(CONFIG['test_server']['session_string']),
#         CONFIG['test_server']['api_id'],
#         CONFIG['test_server']['api_hash'],
#         loop=event_loop,
#     )
#     client.session.set_dc(2, CONFIG['test_server']['test_sever_ip'], 443)
#     await client.start()
#     yield client
#     await client.disconnect()
#     await client.disconnected




