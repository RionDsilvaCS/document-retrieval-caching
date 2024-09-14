FROM python:3.10.12-alpine3.18

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt
