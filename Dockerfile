FROM python:3.14-slim

WORKDIR /api

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /api/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .