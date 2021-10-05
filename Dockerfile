FROM python:3.9-slim as base

RUN apt update
RUN apt-get -y install build-essential
RUN apt-get -y install python3-pip && apt-get -y install python3-setuptools

RUN mkdir -p /var/log/hexlet

RUN mkdir -p /app

COPY bot /app/bot
COPY pyproject.toml /app/pyproject.toml
COPY poetry.lock /app/poetry.lock

WORKDIR /app
RUN pip install poetry &&\
    poetry config virtualenvs.create false &&\
    poetry build &&\
    pip install dist/*.whl

CMD ["poetry", "run", "hexlet-bot"]
