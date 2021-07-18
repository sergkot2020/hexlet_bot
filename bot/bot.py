"""
https://docs.telethon.dev/en/latest/basic/quick-start.html
https://my.telegram.org/apps
"""
import logging

from telethon import TelegramClient, events

from bot import DEV_CHANNEL_ID


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
    send_message(bot, DEV_CHANNEL_ID, 'But successfully started.')
    for participant in bot.iter_participants(DEV_CHANNEL_ID):
        logging.info(f'{participant.first_name:10}:\t{participant.id} '
                     f'{"(bot)" if participant.bot else ""}')
    bot.run_until_disconnected()


def send_message(client: TelegramClient, channel, message: str):
    client.loop.run_until_complete(client.send_message(channel, message))


async def chat_handler(event):
    if event.user_joined:
        logging.info(f'user_joined: {event.user_joined}')
        await event.reply('Welcome to the group!')

    chat = await event.get_chat()
    print(chat.stringify())
    # await event.reply('hi!')


async def message_handler(event):
    # chat = await event.get_chat()
    # await bot.download_profile_photo(sender)
    chat_id = event.chat_id
    sender_id = event.sender_id
    text = event.raw_text
    logging.info(f'incoming message: {text}')
    logging.info(f'chat_id: {chat_id}')
    logging.info(f'sender_id: {sender_id}')
    if text.lower() == 'hello':
        await event.reply('Hi!')
