FROM alpine:latest
LABEL maintainer="docker@ix.ai"

ARG PORT=9119

ENV PORT=${PORT}

COPY src/alertmanager-telegram-bot.py /

RUN apk --no-cache upgrade && \
    apk --no-cache add \
      python3 \
      gcc \
      musl-dev \
      libffi-dev \
      openssl-dev \
      python3-dev \
      py3-flask \
      py3-setuptools \
      py3-waitress \
    && \
    pip3 install --no-cache-dir python-telegram-bot prometheus_client pygelf

EXPOSE ${PORT}

ENTRYPOINT ["python3", "/alertmanager-telegram-bot.py"]
