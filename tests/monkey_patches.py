from typing import List
from datetime import datetime


class Message:
    def __init__(self, date: datetime, raw_text: str):
        self.date = date
        self.raw_text = raw_text


class Event:
    def __init__(
            self,
            message: Message,
            chat_id: int,
            sender_id: int
    ):
        self.chat_id = chat_id
        self.sender_id = sender_id
        self.message = message
        self.raw_text = message.raw_text
        self.reply_was_call_with_arg = None

    async def reply(self, *args):
        self.reply_was_call_with_arg = args[0]
        return


class Participant:
    def __init__(self,
                 id: int,
                 bot: bool,
                 username: str = None,
                 first_name: str = None,
                 last_name: str = None,
                 ):
        self.id = id
        self.bot = bot
        self.username = username
        self.first_name = first_name
        self.last_name = last_name


class Bot:
    def __init__(
            self,
            participants: List[Participant],
            chat_id: int
    ):
        self.participants = participants
        self.chat_id = chat_id
        self.reply_was_call_with_arg = None
        self.sent_messages = []

    async def iter_participants(self, chat_id):
        if chat_id == self.chat_id:
            for participant in self.participants:
                yield participant

    async def send_message(self, chat_id, text):
        self.sent_messages.append((
            chat_id, text
        ))
        return
