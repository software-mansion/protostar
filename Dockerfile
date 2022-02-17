FROM python:3.7.12-alpine

WORKDIR /app

RUN apk add build-base
RUN apk add libffi-dev
RUN apk add gmp-dev
RUN apk add zlib-dev
RUN pip install poetry

COPY ../pyproject.toml ../poetry.lock ./

RUN poetry install

COPY .. .

CMD [ "/bin/sh" ]