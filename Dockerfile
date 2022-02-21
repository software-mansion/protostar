FROM python:3.7.12-alpine

WORKDIR /app

RUN apk add build-base
RUN apk add libffi-dev
RUN apk add gmp-dev
RUN apk add zlib-dev
RUN apk add git

RUN pip install poetry

COPY ../pyproject.toml ../poetry.lock ./

RUN poetry install

COPY .. .

ENTRYPOINT [ "/bin/sh"]

