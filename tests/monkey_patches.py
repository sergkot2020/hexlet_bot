from typing import List
from datetime import datetime

BOT_ID = 123456789


class Message:
    def __init__(self, date: datetime, raw_text: str):
        self.date = date
        self.raw_text = raw_text


class Chat:
    def __init__(self, id, title):
        self.id = id
        self.title = title


class User:
    def __init__(
            self,
            id: int,
            bot: bool,
            username: str,
            first_name: str = None,
            last_name: str = None,
    ):
        self.id = id
        self.bot = bot
        self.username = username
        self.telegram_id = id
        self.is_bot = bot
        self.first_name = first_name
        self.last_name = last_name
        self.lang_code = 'en'
        self.phone = None


class Event:
    def __init__(
            self,
            message: Message,
            chat_id: int,
            sender_id: int,
            chat: Chat,
            user: User,
    ):
        self.chat_id = chat_id
        self.sender_id = self.user_id = sender_id
        self.message = message
        self.raw_text = message.raw_text
        self.reply_was_call_with_arg = None
        self.user_joined = None
        self.user_added = None
        self.is_private = False
        self.chat = chat
        self.user = user

    async def reply(self, *args):
        self.reply_was_call_with_arg = args[0]
        return


class Bot:
    def __init__(
            self,
            session: str,
            api_id: int,
            api_hash: str,
            participants: List[User] = None,
            chat_id: int = None
    ):
        self.session = session
        self.api_id = api_id
        self.api_hash = api_hash
        self.participants = participants
        self.chat_id = chat_id
        self.reply_was_call_with_arg = None
        self.bot_token = None
        self.bot_id = None
        self.sent_messages = []
        self.handlers = []
        self.user_cache = {}

    def set_participants(self, chat_id, users):
        self.user_cache[chat_id] = users

    async def iter_participants(self, chat_id):
        for participant in self.user_cache[chat_id]:
            yield participant

    async def send_message(self, chat_id, text):
        self.sent_messages.append((
            chat_id, text
        ))
        return

    async def start(self, bot_token):
        self.bot_token = bot_token
        return

    async def get_me(self):
        class B:
            id = BOT_ID

        return B()

    async def disconnect(self):
        return

    def on(self, event):
        def wrapper(f):
            self.handlers.append(f)
        return wrapper
