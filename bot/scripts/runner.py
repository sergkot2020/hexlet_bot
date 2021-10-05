#!/usr/bin/env python3
import argparse
import asyncio
import logging
import signal

import uvloop

from bot.app import App
from bot.logger import set_logging, reopen_logs
from bot.reader import read_config

logger = logging.getLogger(__name__)


def handle_sighup(signame, app, config_file):
    logger.info('Received signal %s', signame)
    config = read_config(config_file)
    set_logging(**config['logging'])
    app.set_config(**config)


def handle_sigterm(signame, app):
    logger.info('Received signal %s', signame)
    app.stop()


def handle_sigusr1(signame):
    logger.info('Received signal %s', signame)
    reopen_logs()


def handle_asyncio_exception(loop, context):
    logger.error(
        'Asyncio error: %s, exception: %s',
        context['message'],
        context.get('exception')
    )


async def run_app(config_file, **kwargs):
    config = read_config(config_file)

    set_logging(**config.pop('logging'))

    logger.info('=' * 40)
    logger.info('STARTED')

    loop = asyncio.get_running_loop()
    loop.set_exception_handler(handle_asyncio_exception)

    if kwargs:
        config.update(**kwargs)

    app = App(name='bot', **config)

    loop.add_signal_handler(signal.SIGHUP, handle_sighup, 'SIGHUP', app, config_file)
    loop.add_signal_handler(signal.SIGINT, handle_sigterm, 'SIGINT', app)
    loop.add_signal_handler(signal.SIGTERM, handle_sigterm, 'SIGTERM', app)
    loop.add_signal_handler(signal.SIGUSR1, handle_sigusr1, 'SIGUSR1')

    await app.run()

    logger.info('FINISHED')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type=str, default='config.yml', help='Configuration file')
    args = parser.parse_args()
    config_file = args.config
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(run_app(config_file))


if __name__ == '__main__':
    main()
