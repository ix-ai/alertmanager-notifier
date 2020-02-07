FROM alpine:latest
LABEL maintainer="docker@ix.ai" \
      ai.ix.repository="ix.ai/alertmanager-notifier"

COPY alertmanager-notifier/requirements.txt /alertmanager-notifier/requirements.txt

RUN apk --no-cache upgrade && \
    apk --no-cache add python3 py3-pip py3-waitress py3-flask py3-cryptography && \
    pip3 install --no-cache-dir -r /alertmanager-notifier/requirements.txt

COPY alertmanager-notifier/ /alertmanager-notifier
COPY templates/ /templates
COPY alertmanager-notifier.sh /usr/local/bin/alertmanager-notifier.sh

EXPOSE 9119

ENTRYPOINT ["/usr/local/bin/alertmanager-notifier.sh"]
