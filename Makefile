run:
	poetry run hexlet-bot

lint:
	poetry run flake8 bot

install:
	poetry build
	pip3 install --user --force-reinstall dist/*.whl

test:
	poetry run mypy bot
	poetry run pytest
