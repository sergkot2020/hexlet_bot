import asyncio
from datetime import datetime

from pytest import mark

from bot.const import DAY_MAP
from tests.monkey_patches import Bot

CHAT_ID = 111222
NEW_CHAT_USER_ID = 999888
CHAT_TITLE = 'test chat'


@mark.asyncio
async def test_notice(app):
    now = datetime.now()
    day = DAY_MAP[now.weekday()]
    chat_id = list(app.chats)[0]

    kwargs = {day: True}

    id_ = await app.db.get_chat_id(chat_id)

    bot: Bot = app.bot
    await app.db.update_chat_settings(id_, **kwargs)
    await asyncio.sleep(2)

    chat_id, message = bot.sent_messages[0]
    assert chat_id == chat_id
    assert message == 'Hi everyone, time to daily meeting 💪'

#     # TODO: test for reset in one week (needs datetime patching)
#     # TODO: test for all submitted
