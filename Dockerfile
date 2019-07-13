FROM alpine
LABEL maintainer "docker@ix.ai"

COPY src/alertmanager-telegram-bot.py /

RUN apk --no-cache add gcc musl-dev libffi-dev openssl-dev python3 python3-dev py3-flask py3-setuptools py3-waitress && \
    pip3 install python-telegram-bot

EXPOSE 9119

ENTRYPOINT ["python3", "/alertmanager-telegram-bot.py"]
