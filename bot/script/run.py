"""
https://docs.telethon.dev/en/latest/basic/quick-start.html
https://my.telegram.org/apps
"""
from bot.reader import read_config
from bot.bot import run


def main():
    config = read_config('config.yml')
    run(**config['bot'])


if __name__ == '__main__':
    main()
