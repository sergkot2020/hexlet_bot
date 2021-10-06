run:
	poetry run hexlet-bot

lint:
	poetry run flake8 bot

build:
	poetry build

install:
	pip3 install --user --force-reinstall dist/*.whl

test:
	poetry run pytest -vv

coverage:
	poetry run coverage xml