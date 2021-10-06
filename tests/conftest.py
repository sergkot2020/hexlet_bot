import asyncio
import logging
import os
import subprocess
import time

import pytest

from bot.app import App
from bot.scripts.runner import run_app
from tests.monkey_patches import Bot

TEST_FOLDER = 'tests'
CONFIG_FILENAME = 'test_config.yml'
ROOT_DIR = os.getcwd()
CONFIG_PATH = os.path.join(ROOT_DIR, TEST_FOLDER, CONFIG_FILENAME)

logging.basicConfig(level=logging.INFO)


@pytest.fixture(scope="session")
def create_db():
    subprocess.run(
        f'docker-compose up -d db',
        stdout=subprocess.PIPE,
        shell=True
    )
    time.sleep(5)
    yield
    result = subprocess.run(
        f'docker-compose down -v',
        stdout=subprocess.PIPE,
        shell=True
    )
    return result


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def created_app(create_db, event_loop):
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(
        run_app(
            CONFIG_PATH,
            client=Bot,
        )
    )


@pytest.fixture(scope="session")
async def app(created_app):
    await asyncio.sleep(1)
    app = App._instance
    yield app
    app.stop()
    await app.wait_stopped()
