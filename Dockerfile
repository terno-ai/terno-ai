FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc git default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code/terno-ai
COPY requirements.txt /code//terno-ai
RUN pip install --upgrade pip \
    && pip3 install -r requirements.txt --no-cache-dir
COPY . /code/terno-ai
WORKDIR /code/terno-ai/terno
