import asyncio
import logging
import subprocess
import time
import pytest
from bot.scripts.runner import run_app
from bot.app import App
import os
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

# def after_scenario(context, scenario):
#     conf: dict = context.ds_config
#     dump_path = os.path.join(ROOT_DIR, 'features', 'fixtures', 'dump.sql')
#     for name, settings in conf.items():
#
#         user = settings['user']
#         db = settings['database']
#         password = settings['password']
#         schema = settings['schema']
#
#         fnull = open(os.devnull, 'w')
#         subprocess.run(
#             f'docker-compose exec -T db psql -U {user} -d {db} --command "DROP SCHEMA {schema} CASCADE"',
#             shell=True,
#             stdout=fnull,
#             stderr=subprocess.STDOUT,
#             env={'PGPASSWORD': password},
#         )
#
#         subprocess.run(
#             f"docker-compose exec -T db psql -U {user} -d {db} < {dump_path}",
#             stdout=fnull,
#             stderr=subprocess.STDOUT,
#             shell=True,
#             env={'PGPASSWORD': password},
#         )
#         fnull.close()
#         return