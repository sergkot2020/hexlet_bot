"""
https://docs.telethon.dev/en/latest/basic/quick-start.html
https://my.telegram.org/apps
"""
import logging

from bot.auth_secrets import BOT_AUTH
from bot import ConfigHandler
from bot.bot import run
from bot.reader import read_config


def main():
    logging.basicConfig(level=logging.INFO)
    config = read_config('config.yml')
    bot_config = ConfigHandler(**config['bot_config'])
    run(
        session=BOT_AUTH.session,
        api_id=BOT_AUTH.api_id,
        api_hash=BOT_AUTH.api_hash,
        bot_token=BOT_AUTH.bot_token,
        report_day=bot_config.report_day,
        sleep_time=bot_config.sleep_time,
        )


if __name__ == '__main__':
    main()
