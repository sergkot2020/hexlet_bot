__all__ = [
	'READ_CONFIG_DIRS',
	'read_config'
]

import os.path
import yaml

READ_CONFIG_DIRS = ('.', './', '../')


def read_config(filename, dirs=READ_CONFIG_DIRS):

	if os.path.dirname(filename) == '':
		f = None
		ex = None

		for d in dirs:
			try:
				f = open(os.path.join(d, filename))
				break
			except Exception as e:
				ex = e

		if f is None:
			raise ex

	else:
		f = open(filename)

	if hasattr(yaml, 'full_load'):
		result = yaml.full_load(f)
	else:
		result = yaml.load(f)

	f.close()

	return result
