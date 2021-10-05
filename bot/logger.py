__all__ = [
	'VERBOSE',
	'set_logging',
	'signame',
	'reopen_logs'
]

import logging
import logging.config
import logging.handlers
import signal

VERBOSE = logging.DEBUG - 1
logging.addLevelName(VERBOSE, 'VERBOSE')
logging.Formatter.default_msec_format = '%s.%03d'

DEFAULT_LOG_FORMAT = '{asctime} [{process}] {levelname:5} {name}: {message}'


def set_logging(
	*,
	format=DEFAULT_LOG_FORMAT,
	level='INFO',
	filename=None,
	loggers=None
):
	if filename in (None, '-'):
		handler = {
			'class': 'logging.StreamHandler',
			'stream': 'ext://sys.stdout',
			'formatter': 'f'
		}
	else:
		handler = {
			'class': 'logging.handlers.WatchedFileHandler',
			'filename': filename,
			'formatter': 'f'
		}

	if loggers is None:
		loggers = {}

	config = {
		'version': 1,
		'disable_existing_loggers': False,
		'formatters': {
			'f': {
				'format': format,
				'style': '{'
			}
		},
		'handlers': {
			'h': handler
		},
		'root': {
			'level': level,
			'handlers': ['h']
		},
		'loggers': {
			logger_name: {
				'level': logger_level,
				'handlers': ['h'],
				'propagate': False
			}
			for logger_name, logger_level in loggers.items()
		}
	}

	logging.config.dictConfig(config)


def reopen_logs():
	for handler in logging.root.handlers:
		if isinstance(handler, logging.handlers.WatchedFileHandler):
			handler.reopenIfNeeded()


def signame(signum):
	return signal.Signals(signum).name
