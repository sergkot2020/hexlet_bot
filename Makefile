run:
	poetry run hexlet-bot

lint:
	poetry run flake8 bot

build:
	poetry build

install:
	poetry install

test:
	poetry run pytest -vv

coverage:
	poetry run coverage xml