run:
	poetry run hexlet-bot

lint:
	poetry run flake8 bot

build:
	poetry build

install:
	poetry install

test:
	poetry run coverage run -m pytest -v

coverage:
	poetry run coverage xml