FROM python:3.10-slim-bullseye as build

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN python download.py