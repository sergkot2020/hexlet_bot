'''
Дано:
- сейчас Понедельник
- В боте зарегано 2 пользователя
- Один пользователь отправляет сообщение с тегом #daily
Когда:
- наступает вторник
Тогда:
- Бот присылает предупреждение тому пользователю который не написал сообщение с #daily
'''
import asyncio
import datetime

from pytest import mark
from bot.bot import message_handler, check_daily_report, WARNING_MSG
from monkey_patches import Event, Bot, Participant, Message
from datetime import datetime


@mark.asyncio
async def test_daily_check():
    event1 = Event(
        message=Message(datetime.now(), 'some text'),
        chat_id=13,
        sender_id=1,
    )
    event2 = Event(
        message=Message(datetime.now(), '#daily ...'),
        chat_id=123,
        sender_id=2,
    )
    p1 = Participant(
        id=1,
        bot=False,
        username='user1'
    )
    p2 = Participant(
        id=2,
        bot=False,
        username='user2'
    )
    bot = Bot(
        chat_id=123,
        participants=[p1, p2]
    )
    today = datetime.now().weekday()
    await message_handler(event1)
    await message_handler(event2)
    asyncio.create_task(
        check_daily_report(
            bot=bot,
            report_day=today,
            chat_id=123,
            sleep_time=1
        )
    )
    await asyncio.sleep(3)
    assert len(bot.sent_messages) == 1

    chat_id, message = bot.sent_messages[0]

    daily_check_task.cancel()
    assert chat_id == chat_id
    assert message == WARNING_MSG.format('@user1')


