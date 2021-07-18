import asyncio
import logging

from pytest import mark
from telethon import TelegramClient, events
from telethon.tl.custom.message import Message

from bot import DEV_CHANNEL_ID
from bot.bot import message_handler


@mark.asyncio
async def test_help(bot_client: TelegramClient, test_server_client: TelegramClient):
    bot_client.on(events.NewMessage)(message_handler)
    bot_data = await bot_client.get_me()
    async with test_server_client.conversation(bot_data.username) as conv:
        await conv.send_message('hello')
        resp: Message = await conv.get_response()
        assert 'Hi!' == resp.raw_text
