FROM python:3.13.7-slim-bookworm

ARG MODE
ARG APP_HOME=/server

RUN apt-get update && \
    apt-get install --no-install-recommends -y libpq-dev build-essential && \
    apt-get clean

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

COPY . ${APP_HOME}
WORKDIR ${APP_HOME}

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install ${MODE} --no-interaction --no-ansi
