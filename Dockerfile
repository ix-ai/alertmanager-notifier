FROM alpine:latest
LABEL maintainer="docker@ix.ai" \
      ai.ix.repository="ix.ai/alertmanager-telegram-bot"

COPY alertmanager-telegram-bot/requirements.txt /alertmanager-telegram-bot/requirements.txt

RUN apk --no-cache upgrade && \
    apk --no-cache add python3 py3-pip py3-waitress py3-flask py3-cryptography && \
    pip3 install --no-cache-dir -r /alertmanager-telegram-bot/requirements.txt

COPY alertmanager-telegram-bot/ /alertmanager-telegram-bot
COPY templates/ /templates

EXPOSE 9119

ENTRYPOINT ["python3", "-m", "alertmanager-telegram-bot"]
