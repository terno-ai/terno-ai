FROM node:20-slim as frontend-builder
WORKDIR /code/terno-ai/frontend-build
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

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

COPY --from=frontend-builder /code/terno-ai/frontend-build/dist/index.html /code/terno-ai/terno/frontend/templates/frontend/
COPY --from=frontend-builder /code/terno-ai/frontend-build/dist/terno-ai-assets/ /code/terno-ai/terno/frontend/static/

WORKDIR /code/terno-ai/terno
