__all__ = [
    'READ_CONFIG_DIRS',
    'read_config'
]

import logging
import os
from typing import Set, Dict

import yaml

READ_CONFIG_DIRS = ('.', './', '../', 'bot')


def read_config(filename: str, dirs: Set = READ_CONFIG_DIRS) -> Dict:
    file_full_path: str
    file_found_flag = False
    if os.path.dirname(filename) == '':
        logging.info(f'Started search of config file in {os.getcwd()}')
        for dir in dirs:
            file_full_path = os.path.join(dir, filename)
            if os.path.exists(file_full_path):
                file_found_flag = True
                break
    else:
        file_found_flag = True
        file_full_path = filename
    if not file_found_flag:
        logging.error('Configuration file was not found')
        raise FileNotFoundError()
    with open(file_full_path) as file:
        if hasattr(yaml, 'full_load'):
            config = yaml.full_load(file)
        else:
            config = yaml.load(file)
    return config
