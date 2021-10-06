import asyncio
from datetime import datetime

from pytest import mark

from bot.const import DAY_MAP
from tests.monkey_patches import Bot, Event, Message as Msg, User, Chat

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


@mark.asyncio
async def test_process_report(app):
    u = User(
        id=NEW_CHAT_USER_ID,
        bot=False,
        username='new user',
    )
    event = Event(
        message=Msg(datetime.now(), '#daily I`m the best', sender=u),
        chat_id=CHAT_ID,
        sender_id=NEW_CHAT_USER_ID,
        chat=Chat(CHAT_ID, CHAT_TITLE),
        user=u
    )
    # waiting notice event
    await asyncio.sleep(2)

    await app.process_report(event)
    row = await app.db.pool.fetchrow(
        '''\
select users
from meeting
left join chat c on c.id = meeting.chat_id
where telegram_id = $1
''',
        CHAT_ID
    )
    users = row['users']

    row = await app.db.pool.fetchrow(
        '''\
select id
from "user"
where telegram_id = $1
''',
        NEW_CHAT_USER_ID,
    )
    id_ = row['id']

    assert id_ in users


@mark.asyncio
async def test_check_daily_report(app):
    now = datetime.now()
    yestrday = now.weekday() - 1
    kwargs = {DAY_MAP[yestrday]: True}
    chat_id = list(app.chats)[0]
    id_ = await app.db.get_chat_id(chat_id)

    await app.db.update_chat_settings(id_, **kwargs)
    await app.db.pool.execute(
        '''\
update notice_log
set day = $1
where chat_id = $2
''',
        yestrday,
        id_,
    )
    await asyncio.sleep(2)
    bot: Bot = app.bot
    message = [m for (id_, m) in bot.sent_messages if 'you are missing' in m][0]
    assert message == '@test_user_0, @test_user_1, @test_user_2, @test_user_3, @test_user_4, @new user, you are missing ours daily 😞'