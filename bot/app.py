__all__ = ['App', 'WELCOME_MSG']

import asyncio
import logging
from datetime import datetime, timedelta

from telethon import TelegramClient, Button, events
from telethon.tl.types import ChannelParticipantsAdmins

from bot.const import Notice
from bot.db.db import Db
from bot.const import DAY_MAP, Day

logger = logging.getLogger(__name__)

WELCOME_MSG = 'Welcome to the group!'

BUTTON_DONE = 'done'
BUTTON_BACK = '<<'

# conversation states
SELECT_CHAT = 'chat'
SELECT_DAYS = 'day'
CANCEL = 'cancel'


def get_tail(data: bytes):
    data = data.decode('utf-8')
    tail = data.split('_')[-1]
    try:
        return int(tail)
    except:
        return tail


def choise_chat(user_id):
    def _filter(event: events.CallbackQuery):
        if user_id != event.sender_id:
            return False
        return 'chat' in event.data.decode('utf-8')
    return events.CallbackQuery(func=_filter)


def choise_day(user_id):
    def _filter(event: events.CallbackQuery):
        if user_id != event.sender_id:
            return False
        return 'day' in event.data.decode('utf-8')
    return events.CallbackQuery(func=_filter)


class App:

    _instance = None

    def __init__(
            self,
            *,
            name,
            sleep_time,
            db_pool_size,
            api_id,
            api_hash,
            session,
            bot_token,
            db,
            client=TelegramClient,
            events=events,
    ):
        self.name = name
        self.sleep_time = sleep_time
        self.db_pool_size = db_pool_size
        self.bot_token = bot_token
        self.bot_id = None
        self.users = set()
        self.chats = set()
        self.bot = client(session, api_id, api_hash)
        self.events = events
        self.stopping = asyncio.Event()
        self.stopped = asyncio.Event()
        self.db = Db(**db)
        self.tasks = []

        self.chat_handlers = [
            self.greet,
            self.add_to_chat
        ]
        self.message_handlers = [
            self.process_report,
            self.check_new_user,
            self.set_schedule,
        ]
        self.scheduled_tasks = [
            self.send_notice,
            self.check_daily_report,
        ]
        self.__class__._instance = self

    def stop(self):
        self.stopping.set()

    async def wait_stopped(self):
        await self.stopped.wait()

    async def run(self):
        for handler in self.chat_handlers:
            self.bot.on(self.events.ChatAction)(handler)

        for handler in self.message_handlers:
            self.bot.on(self.events.NewMessage)(handler)

        await self.db.create_conn_pool(max_size=self.db_pool_size)
        await self.bot.start(bot_token=self.bot_token)

        rowset = await self.db.get_all_users()
        for telegram_id, _ in rowset:
            self.users.add(telegram_id)

        await self.get_bot_settings()

        self.tasks.extend([
            asyncio.create_task(self._create_task(task))
            for task in self.scheduled_tasks
        ])

        await self.stopping.wait()

        for task in self.tasks:
            task.cancel()

        await self.db.pool.close()
        await self.bot.disconnect()

        self.stopped.set()

    async def _create_task(self, task):
        try:
            return await task()
        except asyncio.CancelledError:
            raise
        except:
            logger.exception(f'Error in {task.__name__}')

    async def _generate_day_keybord(self, chat_pk):
        row = await self.db.get_chat_setting_days(chat_pk)
        keybord = []
        for i, (day, enabled) in enumerate(zip(Day.List, row)):
            if enabled:
                b = [Button.inline(f'{day} ☑️', f'day_{i}')]
            else:
                b = [Button.inline(day, f'day_{i}')]
            keybord.append(b)
        keybord.append([Button.inline('<<', f'day_{BUTTON_BACK}')])
        return self.bot.build_reply_markup(keybord)

    async def get_bot_settings(self):
        bot = await self.bot.get_me()
        self.bot_id = bot.id
        logger.info(f'Bot run: {bot.id}')

    async def add_to_chat(self, event: events.ChatAction):
        if not (event.user_joined or event.user_added):
            return

        if event.user_id != self.bot_id:
            return

        if event.is_private:
            return

        chat_pk = await self.db.add_chat_if_not_exist(
            chat_id=event.chat_id,
            title=event.chat.title,
        )
        logger.info(f'Bot added in new chat: chat_id={event.chat_id}, title={event.chat.title}')

        async for participant in self.bot.iter_participants(event.chat_id):
            if not participant.bot:
                user_pk = await self.db.add_user_if_not_exist(
                    telegram_id=participant.id,
                    is_bot=False,
                    first_name=participant.first_name,
                    last_name=participant.last_name,
                    lang_code=participant.lang_code,
                    phone=participant.phone,
                    username=participant.username,

                )
                await self.db.add_chat_user_relation_if_not_exist(chat_pk, user_pk)
                self.users.add(participant.id)

        await self.bot.send_message(
            event.chat_id,
            'Hi guys! I will be holding meetings, '
            'the admin of this chat can set up a schedule in a private conversation'
        )

        self.chats.add(event.chat_id)

    async def greet(self, event: events.ChatAction):
        if not (event.user_joined or event.user_added):
            return

        if event.user_id == self.bot_id:
            return

        if event.is_private:
            return

        if event.user.bot:
            return
        logging.info(f'New user join: {event.user_id}')

        user_pk = await self.db.add_user_if_not_exist(
            telegram_id=event.user.id,
            is_bot=False,
            first_name=event.user.first_name,
            last_name=event.user.last_name,
            lang_code=event.user.lang_code,
            phone=event.user.phone,
            username=event.user.username,

        )
        chat_pk = await self.db.add_chat_if_not_exist(
            chat_id=event.chat_id,
            title=event.chat.title,
        )
        await self.db.add_chat_user_relation_if_not_exist(chat_pk, user_pk)

        self.chats.add(event.chat_id)
        self.users.add(event.user.id)
        await event.reply(WELCOME_MSG)

    async def set_schedule(self, event: events.NewMessage):
        if not event.is_private:
            return

        text = event.raw_text

        if text != '/start':
            return

        user = event.message.sender

        chats = await self.db.get_user_chats(telegram_id=user.id)
        access_chats = []
        for chat_pk, chat_id, title in chats:
            async for user_ in self.bot.iter_participants(chat_id, filter=ChannelParticipantsAdmins):
                if user_.id == user.id:
                    access_chats.append((chat_pk, title))

        if not access_chats:
            return

        chat_map = {pk: title for (pk, title) in access_chats}
        buttons = [
            [Button.inline(title, f'chat_{chat_pk}')]
            for chat_pk, title in access_chats
        ]
        buttons.append(
            [Button.inline('DONE', f'chat_{BUTTON_DONE}')]
        )
        chat_keyboard = self.bot.build_reply_markup(buttons)

        logger.info(f'Start conversation with {user.username or user.first_name}')

        state = SELECT_CHAT
        chat_pk = None
        async with self.bot.conversation(event.chat_id, timeout=3600) as conv:
            msg = await conv.send_message('You can set schedule for chats:', buttons=chat_keyboard)
            msg_id = msg.id

            while state != CANCEL:
                if state == SELECT_CHAT:
                    event = await conv.wait_event(choise_chat(user.id))
                    chat_pk = get_tail(event.data)

                    if chat_pk == BUTTON_DONE:
                        await event.answer('Saved new settings')
                        await msg.delete()
                        state = CANCEL
                        continue

                    await event.answer(f'Chat "{chat_map[chat_pk]}"')

                    logger.info(f'Set schedule for chat with pk={chat_pk}')
                    day_keyboard = await self._generate_day_keybord(chat_pk)
                    await self.bot.edit_message(
                        event.chat_id, msg_id,
                        'Choose days for meetings:',
                        buttons=day_keyboard,
                    )
                    state = SELECT_DAYS
                    continue

                if state == SELECT_DAYS:
                    event = await conv.wait_event(choise_day(user.id))
                    day_number = get_tail(event.data)

                    logger.info(f'Choose day={day_number}')

                    if day_number == BUTTON_BACK:
                        await self.bot.edit_message(
                            event.chat_id, msg_id,
                            'You can set schedule for chats:',
                            buttons=chat_keyboard,
                        )
                        state = SELECT_CHAT
                        continue

                    await event.answer(f'{DAY_MAP[day_number]}')
                    await self.db.switch_chat_settings_by_day(chat_pk, DAY_MAP[day_number])
                    day_keyboard = await self._generate_day_keybord(chat_pk)
                    await self.bot.edit_message(
                        event.chat_id, msg_id,
                        'Choose days for meetings:',
                        buttons=day_keyboard,
                    )
                    state = SELECT_DAYS
                    continue

                if state == CANCEL:
                    await self.bot.edit_message(
                        event.chat_id, msg_id,
                        'I saved new settings',
                        buttons=chat_keyboard,
                    )

    async def check_new_user(self, event: events.NewMessage):
        if event.is_private:
            return

        if event.sender_id in self.users:
            return

        user = event.message.sender
        chat_pk = await self.db.add_chat_if_not_exist(
            chat_id=event.chat_id,
            title=event.chat.title
        )

        user_pk = await self.db.add_user_if_not_exist(
            telegram_id=event.sender_id,
            is_bot=user.bot,
            first_name=user.first_name,
            last_name=user.last_name,
            lang_code=user.lang_code,
            phone=user.phone,
            username=user.username,
        )
        await self.db.add_chat_user_relation_if_not_exist(chat_pk, user_pk)

        self.chats.add(event.chat_id)
        self.users.add(event.sender_id)
        logger.info(f'Added new user: telegram_id={event.sender_id}')

    async def process_report(self, event: events.NewMessage):
        if event.is_private:
            return

        text = event.raw_text

        if '#daily' not in text:
            return
        user = event.message.sender

        logging.info(f'Get report: message={text}, chat_id={event.chat_id}, sender_id={event.sender_id}')

        chat_pk = await self.db.add_chat_if_not_exist(
            chat_id=event.chat_id,
            title=event.chat.title
        )

        user_pk = await self.db.add_user_if_not_exist(
            telegram_id=event.sender_id,
            is_bot=user.bot,
            first_name=user.first_name,
            last_name=user.last_name,
            lang_code=user.lang_code,
            phone=user.phone,
            username=user.username,
        )
        await self.db.add_chat_user_relation_if_not_exist(chat_pk, user_pk)
        await self.db.add_report(chat_pk, user_pk, text)
        await self.db.add_user_to_meeting(chat_pk, user_pk)
        self.chats.add(event.chat_id)
        self.users.add(event.sender_id)
        logger.info('Save report ')

    async def check_daily_report(self):
        while True:
            yesterday = datetime.now() - timedelta(days=1)
            day = yesterday.weekday()
            rowset = await self.db.get_settings(
                day=day,
                notice_type=Notice.CENSURE,
                meeting_date=yesterday,
            )
            if not rowset:
                await asyncio.sleep(self.sleep_time)
                continue

            logging.info('Check for daily report started.')
            for chat_pk, chat_id, notice_msg, congratulation_msg, censure_msg, users in rowset:
                if users:
                    good_users = set(users)
                else:
                    good_users = set()

                await self.db.add_notice_log(chat_pk, day, Notice.CENSURE)
                rowset = await self.db.get_users(chat_pk)

                if not rowset:
                    await asyncio.sleep(self.sleep_time)
                    continue

                criminals = []
                for user_pk, _, first_name, last_name, username, _, _ in rowset:
                    if user_pk not in good_users:  # noqa: E501
                        name = username or ' '.join(filter(None, [first_name, last_name]))
                        criminals.append(f'@{name}')

                if criminals:
                    members = ', '.join(criminals)
                    message = censure_msg.format(members)
                else:
                    message = congratulation_msg

                await self.bot.send_message(chat_id, message)
                logger.info(f'CENSURE was sent: telegram_chat={chat_id}, notice_msg={message}')

            await asyncio.sleep(self.sleep_time)

    async def send_notice(self):
        while True:
            now = datetime.now()
            day = now.weekday()
            rowset = await self.db.get_settings(
                day=day,
                notice_type=Notice.NOTICE,
                meeting_date=now,
            )
            for chat_pk, chat_id, notice_msg, _, _, _ in rowset:
                await self.db.add_notice_log(chat_pk, day, Notice.NOTICE)
                await self.db.start_meeting(chat_pk)
                await self.bot.send_message(chat_id, notice_msg)
                logger.info(f'NOTICE was sent: telegram_chat_id={chat_id}, notice_msg={notice_msg}')

    async def delete_old_report(self):
        # TODO delete old notice logs (7 days)
        # TODO delete old reports (1 month)
        return
