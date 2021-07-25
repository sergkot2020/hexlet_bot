run:
	poetry run hexlet-bot

lint:
	poetry run mypy bot
	poetry run flake8 bot

install:
	poetry build
	pip3 install --force-reinstall dist/hexlet_bot-0.1.0-py3-none-any.whl