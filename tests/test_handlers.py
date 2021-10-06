from datetime import datetime

from pytest import mark

from bot.app import App, WELCOME_MSG
from tests.monkey_patches import Event, Message as Msg, BOT_ID, Chat, User, Bot

CHAT_ID = 111222
NEW_CHAT_USER_ID = 999888
CHAT_TITLE = 'test chat'


@mark.asyncio
async def test_add_to_chat(app: App):
    bot: Bot = app.bot
    users = [
        User(
            id=100 + i,
            bot=False,
            username=f'test_user_{i}',
        )
        for i in range(5)
    ]
    event = Event(
        message=Msg(datetime.now(), ''),
        chat_id=CHAT_ID,
        sender_id=BOT_ID,
        chat=Chat(CHAT_ID, CHAT_TITLE),
        user=User(
            id=BOT_ID,
            bot=True,
            username='test_bot'
        )
    )
    event.user_joined = True
    bot.set_participants(CHAT_ID, users)

    await app.add_to_chat(event)

    assert CHAT_ID in app.chats
    assert set([u.id for u in users]) == app.users


@mark.asyncio
async def test_greet(app: App):
    event = Event(
        message=Msg(datetime.now(), ''),
        chat_id=CHAT_ID,
        sender_id=NEW_CHAT_USER_ID,
        chat=Chat(CHAT_ID, CHAT_TITLE),
        user=User(
            id=NEW_CHAT_USER_ID,
            bot=False,
            username='new user',
        )
    )
    event.user_joined = True

    await app.greet(event)

    assert NEW_CHAT_USER_ID in app.users
    assert event.reply_was_call_with_arg == WELCOME_MSG
