FROM alpine:latest
LABEL maintainer="docker@ix.ai"

WORKDIR /app

COPY src/ /app

RUN apk --no-cache upgrade && \
    apk --no-cache add python3 gcc musl-dev libffi-dev openssl-dev python3-dev && \
    pip3 install --no-cache-dir -r requirements.txt && \
    apk del --purge --no-cache gcc musl-dev libffi-dev openssl-dev python3-dev

EXPOSE 9119

ENTRYPOINT ["python3", "/app/alertmanager-telegram-bot.py"]
