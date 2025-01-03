FROM alpine:latest@sha256:beefdbd8a1da6d2915566fde36db9db0b524eb737fc57cd1367effd16dc0d06d as builder

COPY alertmanager-notifier/requirements.txt /work/alertmanager-notifier/requirements.txt

ENV CRYPTOGRAPHY_DONT_BUILD_RUST="1"

RUN set -xeu; \
    mkdir -p /work/wheels; \
    apk add \
      python3-dev \
      py3-pip \
      openssl-dev \
      gcc \
      musl-dev \
      libffi-dev \
      make \
      openssl-dev \
      cargo \
    ; \
    pip3 install -U --break-system-packages \
      wheel \
      pip

RUN pip3 wheel --prefer-binary -r /work/alertmanager-notifier/requirements.txt -w /work/wheels

FROM alpine:latest@sha256:beefdbd8a1da6d2915566fde36db9db0b524eb737fc57cd1367effd16dc0d06d

LABEL maintainer="docker@ix.ai" \
      ai.ix.repository="ix.ai/alertmanager-notifier" \
      org.opencontainers.image.source="https://gitlab.com/ix.ai/alertmanager-notifier"

COPY --from=builder /work /

RUN set -xeu; \
    ls -lashi /wheels; \
    apk add --no-cache py3-pip; \
    pip3 install \
      -U \
      --break-system-packages \
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
