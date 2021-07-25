"""
https://docs.telethon.dev/en/latest/basic/quick-start.html
https://my.telegram.org/apps
"""
import asyncio
import logging
from collections import defaultdict
from datetime import datetime
from typing import Set

from telethon import TelegramClient, events  # type: ignore

from bot import DEV_CHANNEL_ID

'''
daily_message = {
    'sender_id': {
        datetime_obj: '#daily text'
    }
}
'''

WARNING_MSG = '{0}\nГоспода, вы пропустил наш еженедельный чат-митинг 😞'

# TODO: avoid use of globals
#  not sure where to place them to have differentiation per chat
daily_message = defaultdict(list)
weekly_board: Set = set()


def run(
        *,
        session: str,
        api_id: int,
        api_hash: str,
        bot_token: str,
        report_day: int,
        sleep_time: int,
        ):
    # with bot:
    #     bot.loop.run_until_complete(main())
    bot = TelegramClient(session, api_id, api_hash)
    bot.on(events.ChatAction)(chat_handler)
    bot.on(events.NewMessage)(message_handler)
    bot.start(bot_token=bot_token)
    bot.loop.create_task(
        bot.send_message(DEV_CHANNEL_ID, 'Bot successfully started.')
        )
    bot.loop.create_task(
        check_daily_report(bot, report_day, DEV_CHANNEL_ID, sleep_time)
        )

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


async def check_daily_report(
        bot: TelegramClient,
        report_day: int,
        chat_id: int,
        sleep_time: int,
        ):
    report_was_send = False
    while True:
        logging.info('Check for daily report started.')
        day = datetime.now().weekday()
        if day == report_day:
            if not report_was_send:
                criminals = []
                async for participant in bot.iter_participants(chat_id):
                    if participant.id not in weekly_board and not participant.bot:  # noqa: E501
                        criminals.append(f'@{participant.username}')
                if criminals:
                    members = ', '.join(criminals)
                    message = WARNING_MSG.format(members)
                    await bot.send_message(chat_id, message)
                else:
                    await bot.send_message(chat_id, 'Good job, guys!')
                report_was_send = True
                logging.info('Daily report was sent. New cycle started.')
                weekly_board.clear()
            else:
                logging.info('Daily report was not sent as '
                             'it has been sent already today.')
        else:
            logging.info(
                f'Daily report was not sent as today is {datetime.today().weekday()}'  # noqa: E501
                f' vs specified {report_day}.'
                )
            report_was_send = False

        await asyncio.sleep(sleep_time)


async def message_handler(event: events.NewMessage):
    # chat = await event.get_chat()
    # await bot.download_profile_photo(sender)
    chat_id = event.chat_id
    sender_id = event.sender_id
    date = event.message.date
    text = event.raw_text
    logging.info(f'incoming message: {text}')
    logging.info(f'chat_id: {chat_id}')
    logging.info(f'sender_id: {sender_id}')
    if text.lower() == 'hello':
        await event.reply('Hi!')
    elif '#daily' in text:
        daily_message[sender_id].append(
            (date, text)
            )
        weekly_board.add(sender_id)
