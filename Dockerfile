FROM alpine:latest
LABEL maintainer="docker@ix.ai"

WORKDIR /app

COPY src/ /app
COPY templates/ /templates

RUN apk --no-cache upgrade && \
    apk --no-cache add python3 py3-pip py3-waitress py3-flask py3-cryptography py3-jinja2 && \
    pip3 install --no-cache-dir -r requirements.txt

EXPOSE 9119

ENTRYPOINT ["python3", "/app/alertmanager-telegram-bot.py"]
