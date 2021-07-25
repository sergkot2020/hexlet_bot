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
from datetime import datetime

from pytest import mark

from bot.bot import message_handler, check_daily_report, WARNING_MSG
from monkey_patches import Event, Bot, Participant, Message


@mark.asyncio
async def test_daily_check():
    message_without_daily = Event(
        message=Message(datetime.now(), 'some text'),
        chat_id=123,
        sender_id=1,
        )
    message_with_daily = Event(
        message=Message(datetime.now(), '#daily ...'),
        chat_id=123,
        sender_id=2,
        )
    message_with_daily_but_different_chat = Event(
        message=Message(datetime.now(), '#daily ...'),
        chat_id=456,
        sender_id=1,
        )
    bad_chat_member = Participant(
        id=1,
        bot=False,
        username='bad_chat_member'
        )
    good_chat_member = Participant(
        id=2,
        bot=False,
        username='good_chat_member'
        )
    bot = Bot(
        chat_id=123,
        participants=[bad_chat_member, good_chat_member]
        )
    today = datetime.now().weekday()
    await message_handler(message_without_daily)
    await message_handler(message_with_daily)
    await message_handler(message_with_daily_but_different_chat)
    daily_check_task = asyncio.create_task(
        check_daily_report(
            bot=bot,
            report_day=today,
            chat_id=123,
            sleep_time=1,
            )
        )
    await asyncio.sleep(0)
    assert len(bot.sent_messages) == 1

    chat_id, message = bot.sent_messages[0]

    daily_check_task.cancel()
    daily_check_task = asyncio.create_task(
        check_daily_report(
            bot=bot,
            report_day=today + 1,
            chat_id=123,
            sleep_time=1,
            )
        )
    await asyncio.sleep(0)
    daily_check_task.cancel()
    assert chat_id == chat_id
    assert message == WARNING_MSG.format('@bad_chat_member')

    # TODO: test for reset in one week (needs datetime patching)
    # TODO: test for all submitted
