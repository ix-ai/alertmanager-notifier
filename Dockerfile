FROM registry.gitlab.com/ix.ai/alpine:latest
LABEL MAINTAINER="docker@ix.ai"

ARG PORT

ENV PORT=${PORT}

COPY src/alertmanager-telegram-bot.py /

RUN apk --no-cache add libffi-dev openssl-dev python3-dev py3-flask py3-setuptools py3-waitress && \
    pip3 install --no-cache-dir python-telegram-bot

EXPOSE ${PORT}

ENTRYPOINT ["python3", "/alertmanager-telegram-bot.py"]
