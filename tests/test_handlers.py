from pytest import mark
from telethon import TelegramClient
from telethon.tl.custom.message import Message


@mark.asyncio
async def test_help(bot_client: TelegramClient):
    # Create a conversation
    with bot_client.conversation("@myReplicaLikeBot", timeout=5) as conv:
        # Send a command
        await conv.send_message("/help")
        # Get response
        resp: Message = await conv.get_response()
        # Make assertions
        assert "@myReplicaLikeBot" in resp.raw_text
        assert "👍" in resp.raw_text
        assert "👎" in resp.raw_text
