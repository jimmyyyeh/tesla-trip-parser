FROM python:3.8-slim-buster

LABEL maintainer="Jimmy chienfeng0719@hotmail.com"

ARG WORKDIR="app"
RUN apt-get update
RUN apt-get install -y tzdata bash g++ gcc screen vim python3-dev

ENV TZ=Asia/Taipei

RUN mkdir -p ${WORKDIR}
WORKDIR ${WORKDIR}
COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt
RUN rm requirements.txt
