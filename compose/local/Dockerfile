FROM python:3.9

RUN mkdir /app
RUN mkdir /app/yamls

WORKDIR /app

COPY ./requirements/base.txt ./base.txt
COPY ./requirements/local.txt ./requirements.txt
RUN ["pip", "install", "-r", "requirements.txt"]

COPY ./src/ /app/src/
COPY ./manage.py /app/