FROM alpine:latest

RUN mkdir -p /usr/src
WORKDIR /usr/src
COPY src/. .

RUN apk add python3-dev py3-pip build-base
RUN pip3 install -r requirements.txt

ARG OPENAI_API_KEY
ENV OPENAI_API_KEY $OPENAI_API_KEY

VOLUME /usr/idx

ENTRYPOINT python main.py