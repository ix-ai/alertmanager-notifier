FROM alpine:latest as builder

COPY alertmanager-notifier/requirements.txt /work/alertmanager-notifier/requirements.txt

ENV CRYPTOGRAPHY_DONT_BUILD_RUST="1"

RUN set -xeu; \
    mkdir -p /work/wheels; \
    apk add \
      python3-dev \
      openssl-dev \
      gcc \
      musl-dev \
      libffi-dev \
      make \
      openssl-dev \
      cargo \
    ; \
    python3 -m ensurepip; \
    pip3 install -U \
      wheel \
      pip

RUN pip3 wheel --prefer-binary -r /work/alertmanager-notifier/requirements.txt -w /work/wheels

FROM alpine:latest

LABEL maintainer="docker@ix.ai" \
      ai.ix.repository="ix.ai/alertmanager-notifier"

COPY --from=builder /work /

RUN set -xeu; \
    ls -lashi /wheels; \
    apk add --no-cache python3; \
    python3 -m ensurepip; \
    pip3 install --no-cache-dir -U pip;\
    pip3 install \
      --no-index \
      --no-cache-dir \
      --find-links /wheels \
      --requirement /alertmanager-notifier/requirements.txt \
    ; \
    rm -rf /wheels

COPY alertmanager-notifier/ /alertmanager-notifier
COPY templates/ /templates
COPY alertmanager-notifier.sh /usr/local/bin/alertmanager-notifier.sh

EXPOSE 9119

ENTRYPOINT ["/usr/local/bin/alertmanager-notifier.sh"]
