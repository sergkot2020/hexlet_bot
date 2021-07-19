import os

from telethon.sessions import StringSession
from telethon.sync import TelegramClient

from bot.reader import read_config

config_folder = 'tests'
config_filename = 'test_config.yml'
config_name = 'test_server'

config = read_config(os.path.join(config_folder, config_filename))

client = TelegramClient(
    StringSession(),
    config[config_name]['api_id'],
    config[config_name]['api_hash'],
)
client.session.set_dc(3, config['test_server']['test_sever_ip'], 443)
client.start()
print("Your session string is:", client.session.save())
me = client.get_me()
print(me.stringify())
client.disconnect()
