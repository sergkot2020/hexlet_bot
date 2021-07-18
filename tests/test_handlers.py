import asyncio
import logging

from pytest import mark
from telethon import TelegramClient, events

from bot import DEV_CHANNEL_ID
from bot.bot import message_handler


@mark.asyncio
async def test_help(bot_client: TelegramClient, caplog):
    caplog.set_level(logging.DEBUG)
    bot_client.on(events.NewMessage)(message_handler)
    await bot_client.send_message(DEV_CHANNEL_ID, 'timer started')
    await asyncio.sleep(5)
    await bot_client.send_message(DEV_CHANNEL_ID, 'done')
    # messages = await bot_client.get_messages(DEV_CHANNEL_ID)  # no permission
    # logging.DEBUG(messages)

