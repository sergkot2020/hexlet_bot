"""
https://docs.telethon.dev/en/latest/basic/quick-start.html
https://my.telegram.org/apps
"""
import asyncio
from telethon import TelegramClient, events


async def chat_handler(event):
    # if event.user_joined:
    print(f'user_joined: {event.user_joined}')
    await event.reply('Welcome to the group!')

    chat = await event.get_chat()
    print(chat.stringify())
    # await event.reply('hi!')


async def message_handler(event):
    chat = await event.get_chat()
    # await bot.download_profile_photo(sender)

    chat_id = event.chat_id
    sender_id = event.sender_id
    print(f'incoming message: {event.raw_text}')
    print(f'chat_id: {chat_id}')
    print(f'sender_id: {sender_id}')
    await event.reply('hi!')


def run(
        *,
        session: str,
        api_id: int,
        api_hash: str,
        bot_token: str
):
    # with bot:
    #     bot.loop.run_until_complete(main())
    bot = TelegramClient(session, api_id, api_hash)
    bot.on(events.ChatAction)(chat_handler)
    bot.on(events.NewMessage)(message_handler)
    bot.start(bot_token=bot_token)
    bot.run_until_disconnected()
